"""
Browser management with Playwright and anti-detection features
"""
import asyncio
from pathlib import Path
from typing import Optional
from playwright.async_api import async_playwright, Browser, BrowserContext, Page, Playwright
from utils.logger import logger
from utils.stealth import StealthHelper


class BrowserManager:
    """Manages browser lifecycle with stealth features"""
    
    def __init__(self, headless: bool = True, user_data_dir: str = "./browser_data"):
        self.headless = headless
        self.user_data_dir = Path(user_data_dir)
        self.user_data_dir.mkdir(exist_ok=True)
        
        self.playwright: Optional[Playwright] = None
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        self.page: Optional[Page] = None
        
        self.stealth = StealthHelper()
    
    async def start(self) -> Page:
        """Start browser with stealth configuration"""
        try:
            logger.info("🚀 Starting browser with anti-detection features...")
            
            self.playwright = await async_playwright().start()
            
            # Launch browser with stealth args
            self.browser = await self.playwright.chromium.launch(
                headless=self.headless,
                args=[
                    '--disable-blink-features=AutomationControlled',
                    '--disable-dev-shm-usage',
                    '--no-sandbox',
                    '--disable-setuid-sandbox',
                    '--disable-web-security',
                    '--disable-features=IsolateOrigins,site-per-process',
                    '--disable-infobars',
                    '--window-position=0,0',
                    '--ignore-certificate-errors',
                    '--ignore-certificate-errors-spki-list',
                    '--disable-blink-features=AutomationControlled'
                ]
            )
            
            # Create context with realistic settings
            viewport = self.stealth.get_random_viewport()
            self.context = await self.browser.new_context(
                viewport=viewport,
                user_agent=self.stealth.get_user_agent(),
                locale='tr-TR',
                timezone_id='Europe/Istanbul',
                permissions=['geolocation'],
                geolocation={'latitude': 40.1826, 'longitude': 29.0665},  # Bursa coordinates
                color_scheme='light',
                device_scale_factor=1,
                has_touch=False,
                is_mobile=False,
                java_script_enabled=True,
                accept_downloads=True,
                ignore_https_errors=True
            )
            
            # Add stealth scripts
            await self.stealth.add_stealth_scripts(self.context)
            
            # Create page
            self.page = await self.context.new_page()
            
            # Set extra headers
            await self.page.set_extra_http_headers({
                'Accept-Language': 'tr-TR,tr;q=0.9,en-US;q=0.8,en;q=0.7',
                'Accept-Encoding': 'gzip, deflate, br',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1'
            })
            
            logger.success("Browser started successfully")
            return self.page
            
        except Exception as e:
            logger.error(f"Failed to start browser: {str(e)}", exc_info=True)
            await self.close()
            raise
    
    async def save_screenshot(self, name: str = "error"):
        """Save screenshot for debugging"""
        try:
            if self.page:
                screenshot_path = Path("logs") / f"{name}_{asyncio.get_event_loop().time()}.png"
                await self.page.screenshot(path=str(screenshot_path), full_page=True)
                logger.info(f"📸 Screenshot saved: {screenshot_path}")
                return str(screenshot_path)
        except Exception as e:
            logger.error(f"Failed to save screenshot: {str(e)}")
        return None
    
    async def save_cookies(self, filepath: str = "cookies.json"):
        """Save cookies for session persistence"""
        try:
            if self.context:
                cookies = await self.context.cookies()
                import json
                with open(filepath, 'w') as f:
                    json.dump(cookies, f)
                logger.debug(f"Cookies saved to {filepath}")
        except Exception as e:
            logger.error(f"Failed to save cookies: {str(e)}")
    
    async def load_cookies(self, filepath: str = "cookies.json"):
        """Load cookies to restore session"""
        try:
            if self.context and Path(filepath).exists():
                import json
                with open(filepath, 'r') as f:
                    cookies = json.load(f)
                await self.context.add_cookies(cookies)
                logger.debug(f"Cookies loaded from {filepath}")
                return True
        except Exception as e:
            logger.error(f"Failed to load cookies: {str(e)}")
        return False
    
    async def check_session(self) -> bool:
        """Check if session is still valid"""
        try:
            if not self.page:
                return False
            
            # Try to access current URL
            current_url = self.page.url
            if "login" in current_url.lower():
                return False
            
            return True
        except Exception:
            return False
    
    async def close(self):
        """Close browser and cleanup"""
        try:
            if self.page:
                await self.page.close()
            if self.context:
                await self.context.close()
            if self.browser:
                await self.browser.close()
            if self.playwright:
                await self.playwright.stop()
            
            logger.info("Browser closed successfully")
        except Exception as e:
            logger.error(f"Error closing browser: {str(e)}")
    
    async def restart(self) -> Page:
        """Restart browser (useful for recovery)"""
        logger.warning("Restarting browser...")
        await self.close()
        await asyncio.sleep(2)
        return await self.start()
