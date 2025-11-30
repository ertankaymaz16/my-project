"""
Authentication module for VFS login and OTP handling
"""
import asyncio
from typing import Optional
from playwright.async_api import Page
from utils.logger import logger
from utils.stealth import StealthHelper
from modules.mail_handler import MailHandler


class AuthManager:
    """Manages authentication flow including OTP"""
    
    # VFS Global URLs (Update these with actual URLs)
    LOGIN_URL = "https://visa.vfsglobal.com/tur/tr/nld/login"
    DASHBOARD_URL = "https://visa.vfsglobal.com/tur/tr/nld/dashboard"
    
    def __init__(self, page: Page, email: str, password: str, mail_handler: MailHandler):
        self.page = page
        self.email = email
        self.password = password
        self.mail_handler = mail_handler
        self.stealth = StealthHelper()
    
    async def login(self, max_retries: int = 3) -> bool:
        """
        Perform login with OTP verification
        
        Returns:
            True if login successful, False otherwise
        """
        for attempt in range(max_retries):
            try:
                logger.phase("FAZ 1", f"Login attempt {attempt + 1}/{max_retries}")
                
                # Navigate to login page
                logger.info(f"Navigating to login page: {self.LOGIN_URL}")
                await self.page.goto(self.LOGIN_URL, wait_until='networkidle', timeout=30000)
                await self.stealth.random_delay(1, 2)
                
                # Fill email
                logger.info("Entering email...")
                email_selector = 'input[type="email"], input[name="email"], input#email, input#mat-input-0'
                await self.stealth.wait_for_element_safely(self.page, email_selector)
                await self.stealth.human_like_typing(self.page, email_selector, self.email)
                await self.stealth.random_delay(0.5, 1)
                
                # Fill password
                logger.info("Entering password...")
                password_selector = 'input[type="password"], input[name="password"], input#password, input#mat-input-1'
                await self.stealth.wait_for_element_safely(self.page, password_selector)
                await self.stealth.human_like_typing(self.page, password_selector, self.password)
                await self.stealth.random_delay(0.5, 1)
                
                # Click login button
                logger.info("Clicking login button...")
                login_button_selectors = [
                    'button[type="submit"]',
                    'button:has-text("Login")',
                    'button:has-text("Sign In")',
                    'button:has-text("Giriş")',
                    'input[type="submit"]',
                    '.btn-login',
                    '#btnLogin'
                ]
                
                clicked = False
                for selector in login_button_selectors:
                    try:
                        await self.page.click(selector, timeout=5000)
                        clicked = True
                        break
                    except:
                        continue
                
                if not clicked:
                    logger.error("Could not find login button")
                    continue
                
                await self.stealth.random_delay(2, 3)
                
                # Check if OTP is required
                if await self._is_otp_required():
                    logger.info("OTP verification required")
                    if not await self._handle_otp():
                        logger.error("OTP verification failed")
                        continue
                
                # Verify login success
                if await self._verify_login():
                    logger.success("Login successful!")
                    return True
                else:
                    logger.warning("Login verification failed")
                    
            except Exception as e:
                logger.error(f"Login attempt {attempt + 1} failed: {str(e)}", exc_info=True)
                await self.stealth.random_delay(2, 3)
        
        logger.failure("All login attempts failed")
        return False
    
    async def _is_otp_required(self) -> bool:
        """Check if OTP verification is required"""
        try:
            # Wait a bit for page to load
            await asyncio.sleep(2)
            
            # Check for OTP input field
            otp_selectors = [
                'input[name="otp"]',
                'input[name="code"]',
                'input[placeholder*="code"]',
                'input[placeholder*="OTP"]',
                'input[type="text"][maxlength="6"]',
                '#otp',
                '#verificationCode'
            ]
            
            for selector in otp_selectors:
                element = await self.stealth.wait_for_element_safely(self.page, selector, timeout=5000)
                if element:
                    logger.info(f"OTP field detected: {selector}")
                    return True
            
            # Check for OTP-related text
            page_content = await self.page.content()
            otp_keywords = ['verification code', 'otp', 'doğrulama kodu', 'verify', 'kod']
            
            for keyword in otp_keywords:
                if keyword.lower() in page_content.lower():
                    logger.info(f"OTP keyword detected: {keyword}")
                    return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error checking OTP requirement: {str(e)}")
            return False
    
    async def _handle_otp(self) -> bool:
        """Handle OTP verification"""
        try:
            logger.info("Waiting for OTP email...")
            
            # Wait for OTP email (60 seconds timeout)
            otp_code = await self.mail_handler.wait_for_otp_async(
                sender_filter='vfs',  # Adjust based on actual sender
                subject_filter='verification',  # Adjust based on actual subject
                timeout=60
            )
            
            if not otp_code:
                logger.error("OTP code not received")
                return False
            
            logger.success(f"OTP code received: {otp_code}")
            
            # Find OTP input field
            otp_selectors = [
                'input[name="otp"]',
                'input[name="code"]',
                'input[placeholder*="code"]',
                'input[placeholder*="OTP"]',
                'input[type="text"][maxlength="6"]',
                '#otp',
                '#verificationCode'
            ]
            
            otp_field = None
            for selector in otp_selectors:
                otp_field = await self.stealth.wait_for_element_safely(self.page, selector, timeout=5000)
                if otp_field:
                    break
            
            if not otp_field:
                logger.error("OTP input field not found")
                return False
            
            # Enter OTP code
            logger.info("Entering OTP code...")
            await self.stealth.human_like_typing(self.page, otp_selectors[0], otp_code)
            await self.stealth.random_delay(0.5, 1)
            
            # Click verify button
            verify_button_selectors = [
                'button[type="submit"]',
                'button:has-text("Verify")',
                'button:has-text("Doğrula")',
                'button:has-text("Submit")',
                '.btn-verify',
                '#btnVerify'
            ]
            
            for selector in verify_button_selectors:
                try:
                    await self.page.click(selector, timeout=5000)
                    break
                except:
                    continue
            
            await self.stealth.random_delay(2, 3)
            
            logger.success("OTP submitted")
            return True
            
        except Exception as e:
            logger.error(f"Error handling OTP: {str(e)}", exc_info=True)
            return False
    
    async def _verify_login(self) -> bool:
        """Verify that login was successful"""
        try:
            await asyncio.sleep(3)
            
            current_url = self.page.url
            logger.debug(f"Current URL: {current_url}")
            
            # Check if redirected to dashboard
            if 'dashboard' in current_url.lower() or 'home' in current_url.lower():
                return True
            
            # Check if login page is still visible
            if 'login' in current_url.lower():
                return False
            
            # Check for dashboard elements
            dashboard_indicators = [
                'text=Dashboard',
                'text=Welcome',
                'text=Hoş geldiniz',
                '.dashboard',
                '#dashboard',
                'text=Book Appointment',
                'text=Randevu Al'
            ]
            
            for indicator in dashboard_indicators:
                try:
                    element = await self.page.wait_for_selector(indicator, timeout=5000, state='visible')
                    if element:
                        return True
                except:
                    continue
            
            # Check for error messages
            error_indicators = [
                'text=Invalid',
                'text=Error',
                'text=Hata',
                'text=Geçersiz',
                '.error-message',
                '.alert-danger'
            ]
            
            for indicator in error_indicators:
                try:
                    element = await self.page.wait_for_selector(indicator, timeout=2000, state='visible')
                    if element:
                        error_text = await element.inner_text()
                        logger.error(f"Login error: {error_text}")
                        return False
                except:
                    continue
            
            # If no clear indicators, assume success
            return True
            
        except Exception as e:
            logger.error(f"Error verifying login: {str(e)}")
            return False
    
    async def check_session_valid(self) -> bool:
        """Check if current session is still valid"""
        try:
            current_url = self.page.url
            
            # If on login page, session is invalid
            if 'login' in current_url.lower():
                return False
            
            # Try to access dashboard
            await self.page.goto(self.DASHBOARD_URL, wait_until='networkidle', timeout=15000)
            await asyncio.sleep(2)
            
            current_url = self.page.url
            
            if 'login' in current_url.lower():
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error checking session: {str(e)}")
            return False
