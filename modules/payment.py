"""
Payment processing module with 3D Secure support
"""
import asyncio
from typing import Optional
from playwright.async_api import Page
from utils.logger import logger
from utils.stealth import StealthHelper
from modules.telegram_bot import TelegramNotifier


class PaymentManager:
    """Manages payment processing and 3D Secure verification"""
    
    def __init__(self, page: Page, payment_info: dict, telegram: TelegramNotifier):
        self.page = page
        self.payment_info = payment_info
        self.telegram = telegram
        self.stealth = StealthHelper()
    
    async def process_payment(self) -> bool:
        """
        Process payment with 3D Secure verification
        
        Returns:
            True if payment successful
        """
        try:
            logger.phase("FAZ 4", "Starting payment process")
            
            # Fill payment form
            if not await self._fill_payment_form():
                logger.error("Failed to fill payment form")
                return False
            
            # Click pay button
            if not await self._click_pay_button():
                logger.error("Failed to click pay button")
                return False
            
            # Handle 3D Secure
            if await self._is_3d_secure_required():
                logger.info("3D Secure verification required")
                if not await self._handle_3d_secure():
                    logger.error("3D Secure verification failed")
                    return False
            
            # Verify payment success
            if await self._verify_payment_success():
                logger.success("Payment completed successfully!")
                await self.telegram.notify_payment_success()
                return True
            else:
                logger.error("Payment verification failed")
                return False
            
        except Exception as e:
            logger.error(f"Error processing payment: {str(e)}", exc_info=True)
            return False
    
    async def _fill_payment_form(self) -> bool:
        """Fill credit card payment form"""
        try:
            logger.info("Filling payment form...")
            
            # Wait for payment form to load
            await asyncio.sleep(2)
            
            # Card number
            card_number_selectors = [
                'input[name="cardNumber"]',
                'input[name="card_number"]',
                'input#cardNumber',
                'input[placeholder*="Card Number"]',
                'input[placeholder*="Kart Numarası"]',
                'input[autocomplete="cc-number"]'
            ]
            
            for selector in card_number_selectors:
                try:
                    element = await self.stealth.wait_for_element_safely(self.page, selector, timeout=5000)
                    if element:
                        await element.fill('')
                        await self.stealth.human_like_typing(
                            self.page, 
                            selector, 
                            self.payment_info['card_number'],
                            delay_range=(0.03, 0.08)
                        )
                        logger.debug("Card number filled")
                        break
                except:
                    continue
            
            await self.stealth.random_delay(0.3, 0.6)
            
            # Card holder name
            card_holder_selectors = [
                'input[name="cardHolder"]',
                'input[name="card_holder"]',
                'input#cardHolderName',
                'input[placeholder*="Card Holder"]',
                'input[placeholder*="Kart Sahibi"]',
                'input[autocomplete="cc-name"]'
            ]
            
            for selector in card_holder_selectors:
                try:
                    element = await self.stealth.wait_for_element_safely(self.page, selector, timeout=5000)
                    if element:
                        await element.fill('')
                        await self.stealth.human_like_typing(
                            self.page,
                            selector,
                            self.payment_info['card_holder'],
                            delay_range=(0.05, 0.1)
                        )
                        logger.debug("Card holder name filled")
                        break
                except:
                    continue
            
            await self.stealth.random_delay(0.3, 0.6)
            
            # Expiry month
            expiry_month_selectors = [
                'select[name="expiryMonth"]',
                'select#expiryMonth',
                'input[name="expiryMonth"]',
                'input[placeholder*="MM"]',
                'select[autocomplete="cc-exp-month"]'
            ]
            
            for selector in expiry_month_selectors:
                try:
                    element = await self.stealth.wait_for_element_safely(self.page, selector, timeout=5000)
                    if element:
                        tag_name = await element.evaluate('el => el.tagName')
                        
                        if tag_name.lower() == 'select':
                            await element.select_option(value=self.payment_info['expiry_month'])
                        else:
                            await element.fill(self.payment_info['expiry_month'])
                        
                        logger.debug("Expiry month filled")
                        break
                except:
                    continue
            
            await self.stealth.random_delay(0.2, 0.4)
            
            # Expiry year
            expiry_year_selectors = [
                'select[name="expiryYear"]',
                'select#expiryYear',
                'input[name="expiryYear"]',
                'input[placeholder*="YY"]',
                'select[autocomplete="cc-exp-year"]'
            ]
            
            for selector in expiry_year_selectors:
                try:
                    element = await self.stealth.wait_for_element_safely(self.page, selector, timeout=5000)
                    if element:
                        tag_name = await element.evaluate('el => el.tagName')
                        
                        if tag_name.lower() == 'select':
                            await element.select_option(value=self.payment_info['expiry_year'])
                        else:
                            await element.fill(self.payment_info['expiry_year'])
                        
                        logger.debug("Expiry year filled")
                        break
                except:
                    continue
            
            await self.stealth.random_delay(0.2, 0.4)
            
            # CVV
            cvv_selectors = [
                'input[name="cvv"]',
                'input[name="cvc"]',
                'input#cvv',
                'input#securityCode',
                'input[placeholder*="CVV"]',
                'input[placeholder*="CVC"]',
                'input[autocomplete="cc-csc"]'
            ]
            
            for selector in cvv_selectors:
                try:
                    element = await self.stealth.wait_for_element_safely(self.page, selector, timeout=5000)
                    if element:
                        await element.fill('')
                        await self.stealth.human_like_typing(
                            self.page,
                            selector,
                            self.payment_info['cvv'],
                            delay_range=(0.05, 0.1)
                        )
                        logger.debug("CVV filled")
                        break
                except:
                    continue
            
            await self.stealth.random_delay(0.5, 1)
            
            logger.success("Payment form filled successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error filling payment form: {str(e)}", exc_info=True)
            return False
    
    async def _click_pay_button(self) -> bool:
        """Click the pay/submit button"""
        try:
            logger.info("Clicking pay button...")
            
            pay_button_selectors = [
                'button:has-text("Pay")',
                'button:has-text("Ödeme Yap")',
                'button:has-text("Submit Payment")',
                'button:has-text("Complete Payment")',
                'button[type="submit"]',
                '.btn-pay',
                '#btnPay',
                '#submitPayment'
            ]
            
            for selector in pay_button_selectors:
                try:
                    await self.page.click(selector, timeout=5000)
                    await self.stealth.random_delay(2, 3)
                    logger.debug("Pay button clicked")
                    return True
                except:
                    continue
            
            logger.warning("Pay button not found")
            return False
            
        except Exception as e:
            logger.error(f"Error clicking pay button: {str(e)}", exc_info=True)
            return False
    
    async def _is_3d_secure_required(self) -> bool:
        """Check if 3D Secure verification is required"""
        try:
            await asyncio.sleep(3)  # Wait for redirect
            
            # Check for 3D Secure indicators
            secure_3d_indicators = [
                'iframe[name*="3ds"]',
                'iframe[name*="secure"]',
                'iframe[id*="3ds"]',
                'text=3D Secure',
                'text=Doğrulama Kodu',
                'text=SMS Code',
                'text=Verification Code',
                'input[name*="otp"]',
                'input[placeholder*="SMS"]'
            ]
            
            for indicator in secure_3d_indicators:
                try:
                    element = await self.page.wait_for_selector(indicator, timeout=5000, state='visible')
                    if element:
                        logger.info(f"3D Secure detected: {indicator}")
                        return True
                except:
                    continue
            
            # Check URL for 3D Secure
            current_url = self.page.url
            if any(keyword in current_url.lower() for keyword in ['3ds', '3dsecure', 'secure', 'verification']):
                logger.info("3D Secure detected in URL")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error checking 3D Secure: {str(e)}")
            return False
    
    async def _handle_3d_secure(self) -> bool:
        """Handle 3D Secure verification with human-in-the-loop"""
        try:
            logger.info("Handling 3D Secure verification...")
            
            # Check if we need to switch to iframe
            iframe_selectors = [
                'iframe[name*="3ds"]',
                'iframe[name*="secure"]',
                'iframe[id*="3ds"]'
            ]
            
            frame = None
            for selector in iframe_selectors:
                try:
                    frame_element = await self.page.wait_for_selector(selector, timeout=5000)
                    if frame_element:
                        frame = await frame_element.content_frame()
                        if frame:
                            logger.debug(f"Switched to 3D Secure iframe: {selector}")
                            break
                except:
                    continue
            
            # Use frame if found, otherwise use main page
            target = frame if frame else self.page
            
            # Request SMS code from user via Telegram
            sms_code = await self.telegram.request_sms_code()
            
            if not sms_code:
                logger.error("SMS code not received from user")
                return False
            
            logger.info(f"SMS code received: {sms_code}")
            
            # Find SMS code input field
            sms_input_selectors = [
                'input[name="otp"]',
                'input[name="sms"]',
                'input[name="code"]',
                'input[placeholder*="SMS"]',
                'input[placeholder*="Code"]',
                'input[placeholder*="Kod"]',
                'input[type="text"]',
                'input[type="tel"]'
            ]
            
            sms_field = None
            for selector in sms_input_selectors:
                try:
                    sms_field = await target.wait_for_selector(selector, timeout=5000, state='visible')
                    if sms_field:
                        logger.debug(f"SMS input field found: {selector}")
                        break
                except:
                    continue
            
            if not sms_field:
                logger.error("SMS input field not found")
                return False
            
            # Enter SMS code
            await sms_field.fill('')
            await sms_field.type(sms_code, delay=100)
            await self.stealth.random_delay(0.5, 1)
            
            logger.info("SMS code entered")
            
            # Click submit button
            submit_button_selectors = [
                'button[type="submit"]',
                'button:has-text("Submit")',
                'button:has-text("Verify")',
                'button:has-text("Doğrula")',
                'button:has-text("Onayla")',
                'input[type="submit"]',
                '.btn-submit',
                '#btnSubmit'
            ]
            
            for selector in submit_button_selectors:
                try:
                    await target.click(selector, timeout=5000)
                    await self.stealth.random_delay(2, 3)
                    logger.info("3D Secure submit button clicked")
                    break
                except:
                    continue
            
            # Wait for verification to complete
            await asyncio.sleep(5)
            
            logger.success("3D Secure verification completed")
            return True
            
        except Exception as e:
            logger.error(f"Error handling 3D Secure: {str(e)}", exc_info=True)
            return False
    
    async def _verify_payment_success(self) -> bool:
        """Verify that payment was successful"""
        try:
            await asyncio.sleep(3)
            
            # Check for success indicators
            success_indicators = [
                'text=Payment Successful',
                'text=Ödeme Başarılı',
                'text=Success',
                'text=Başarılı',
                'text=Confirmed',
                'text=Onaylandı',
                '.payment-success',
                '.success-message',
                '#paymentSuccess'
            ]
            
            for indicator in success_indicators:
                try:
                    element = await self.page.wait_for_selector(indicator, timeout=10000, state='visible')
                    if element:
                        logger.info(f"Payment success indicator found: {indicator}")
                        return True
                except:
                    continue
            
            # Check URL for success
            current_url = self.page.url
            if any(keyword in current_url.lower() for keyword in ['success', 'confirmation', 'complete', 'thank']):
                logger.info("Payment success detected in URL")
                return True
            
            # Check for error indicators
            error_indicators = [
                'text=Payment Failed',
                'text=Ödeme Başarısız',
                'text=Error',
                'text=Hata',
                'text=Declined',
                'text=Reddedildi',
                '.payment-error',
                '.error-message'
            ]
            
            for indicator in error_indicators:
                try:
                    element = await self.page.wait_for_selector(indicator, timeout=3000, state='visible')
                    if element:
                        error_text = await element.inner_text()
                        logger.error(f"Payment error: {error_text}")
                        return False
                except:
                    continue
            
            # If no clear indicators, check page content
            page_content = await self.page.content()
            if any(keyword in page_content.lower() for keyword in ['success', 'successful', 'confirmed', 'başarılı']):
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error verifying payment: {str(e)}", exc_info=True)
            return False
