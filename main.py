#!/usr/bin/env python3
"""
Hollanda Vize Randevu Otomasyonu (RPA Bot)
Main orchestrator for the visa appointment automation system
"""
import asyncio
import json
import signal
import sys
from pathlib import Path
from typing import Optional

from modules.browser import BrowserManager
from modules.auth import AuthManager
from modules.mail_handler import MailHandler
from modules.appointment import AppointmentManager
from modules.payment import PaymentManager
from modules.telegram_bot import TelegramNotifier
from utils.logger import logger


class VisaBot:
    """Main orchestrator for visa appointment automation"""
    
    def __init__(self, config_path: str = "config.json"):
        self.config_path = config_path
        self.config = None
        self.running = False
        
        # Components
        self.browser_manager: Optional[BrowserManager] = None
        self.auth_manager: Optional[AuthManager] = None
        self.mail_handler: Optional[MailHandler] = None
        self.appointment_manager: Optional[AppointmentManager] = None
        self.payment_manager: Optional[PaymentManager] = None
        self.telegram: Optional[TelegramNotifier] = None
    
    def load_config(self) -> bool:
        """Load configuration from JSON file"""
        try:
            config_file = Path(self.config_path)
            
            if not config_file.exists():
                logger.error(f"Config file not found: {self.config_path}")
                logger.info("Please copy config.json.example to config.json and fill in your details")
                return False
            
            with open(config_file, 'r', encoding='utf-8') as f:
                self.config = json.load(f)
            
            logger.success("Configuration loaded successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to load config: {str(e)}", exc_info=True)
            return False
    
    async def initialize(self) -> bool:
        """Initialize all components"""
        try:
            logger.info("=" * 60)
            logger.info("🤖 HOLLANDA VİZE RANDEVU OTOMASYONU")
            logger.info("=" * 60)
            
            # Load configuration
            if not self.load_config():
                return False
            
            # Initialize Telegram bot
            logger.info("Initializing Telegram bot...")
            self.telegram = TelegramNotifier(
                bot_token=self.config['telegram']['bot_token'],
                chat_id=self.config['telegram']['chat_id']
            )
            await self.telegram.initialize()
            
            # Initialize mail handler
            logger.info("Initializing email handler...")
            email_config = self.config['email_config']
            self.mail_handler = MailHandler(
                email_address=email_config['email'],
                password=email_config['password'],
                imap_server=email_config['imap_server'],
                imap_port=email_config['imap_port']
            )
            
            # Initialize browser with proxy support
            logger.info("Initializing browser...")
            
            # Prepare proxy configuration
            proxy_config = None
            if self.config.get('proxy', {}).get('enabled', False):
                proxy_config = {
                    'server': self.config['proxy']['server'],
                    'username': self.config['proxy'].get('username'),
                    'password': self.config['proxy'].get('password')
                }
                logger.info(f"🌐 Proxy enabled: {proxy_config['server']}")
            else:
                logger.warning("⚠️  Proxy disabled - may trigger IP ban!")
            
            self.browser_manager = BrowserManager(
                headless=self.config['settings']['headless'],
                proxy_config=proxy_config,
                clear_cache_on_start=self.config['settings'].get('clear_cache_on_start', True)
            )
            page = await self.browser_manager.start()
            
            # Initialize auth manager
            logger.info("Initializing authentication manager...")
            vfs_creds = self.config['vfs_credentials']
            self.auth_manager = AuthManager(
                page=page,
                email=vfs_creds['email'],
                password=vfs_creds['password'],
                mail_handler=self.mail_handler
            )
            
            # Initialize appointment manager
            logger.info("Initializing appointment manager...")
            self.appointment_manager = AppointmentManager(
                page=page,
                criteria=self.config['appointment_criteria'],
                applicants=self.config['applicants']
            )
            
            # Initialize payment manager
            logger.info("Initializing payment manager...")
            self.payment_manager = PaymentManager(
                page=page,
                payment_info=self.config['payment'],
                telegram=self.telegram
            )
            
            logger.success("All components initialized successfully!")
            return True
            
        except Exception as e:
            logger.error(f"Initialization failed: {str(e)}", exc_info=True)
            await self.telegram.notify_error(f"Initialization failed: {str(e)}")
            return False
    
    async def run(self):
        """Main execution loop"""
        try:
            self.running = True
            
            # Phase 1: Login
            logger.info("\n" + "=" * 60)
            logger.phase("FAZ 1", "AUTHENTICATION & LOGIN")
            logger.info("=" * 60)
            
            login_success = await self.auth_manager.login(
                max_retries=self.config['settings']['max_retries']
            )
            
            if not login_success:
                await self.telegram.notify_error("Login failed after multiple attempts")
                return False
            
            # Save session
            await self.browser_manager.save_cookies()
            
            # Phase 2 & 3: Appointment polling and booking
            logger.info("\n" + "=" * 60)
            logger.phase("FAZ 2", "APPOINTMENT POLLING")
            logger.info("=" * 60)
            
            settings = self.config['settings']
            appointment = await self.appointment_manager.start_polling(
                interval_minutes=settings['polling_interval_minutes'],
                random_delay_range=(settings['random_delay_min'], settings['random_delay_max'])
            )
            
            if not appointment:
                logger.error("Polling stopped without finding appointment")
                return False
            
            # Notify user
            await self.telegram.notify_appointment_found(appointment)
            
            # Take screenshot
            if settings['screenshot_on_error']:
                await self.browser_manager.save_screenshot("appointment_found")
            
            # Phase 3: Book appointment
            logger.info("\n" + "=" * 60)
            logger.phase("FAZ 3", "BOOKING APPOINTMENT")
            logger.info("=" * 60)
            
            booking_success = await self.appointment_manager.book_appointment(appointment)
            
            if not booking_success:
                await self.telegram.notify_error("Failed to book appointment")
                return False
            
            await self.telegram.notify_reservation_success()
            
            # Take screenshot
            if settings['screenshot_on_error']:
                await self.browser_manager.save_screenshot("booking_success")
            
            # Phase 4: Payment
            logger.info("\n" + "=" * 60)
            logger.phase("FAZ 4", "PAYMENT PROCESSING")
            logger.info("=" * 60)
            
            payment_success = await self.payment_manager.process_payment()
            
            if not payment_success:
                await self.telegram.notify_error("Payment failed")
                return False
            
            # Take final screenshot
            if settings['screenshot_on_error']:
                await self.browser_manager.save_screenshot("payment_success")
            
            logger.info("\n" + "=" * 60)
            logger.success("🎉 ALL PHASES COMPLETED SUCCESSFULLY!")
            logger.info("=" * 60)
            
            return True
            
        except Exception as e:
            logger.critical(f"Critical error in main loop: {str(e)}", exc_info=True)
            
            # Take error screenshot
            if self.browser_manager and self.config['settings']['screenshot_on_error']:
                screenshot_path = await self.browser_manager.save_screenshot("critical_error")
                await self.telegram.notify_error(f"Critical error: {str(e)}", screenshot_path)
            
            return False
        
        finally:
            self.running = False
    
    async def shutdown(self):
        """Graceful shutdown"""
        try:
            logger.info("Shutting down...")
            
            if self.browser_manager:
                await self.browser_manager.close()
            
            if self.mail_handler:
                self.mail_handler.disconnect()
            
            if self.telegram:
                await self.telegram.shutdown()
            
            logger.info("Shutdown complete")
            
        except Exception as e:
            logger.error(f"Error during shutdown: {str(e)}")
    
    def signal_handler(self, signum, frame):
        """Handle interrupt signals"""
        logger.warning(f"\nReceived signal {signum}. Shutting down gracefully...")
        self.running = False
        asyncio.create_task(self.shutdown())
        sys.exit(0)


async def main():
    """Main entry point"""
    bot = VisaBot(config_path="config.json")
    
    # Setup signal handlers
    signal.signal(signal.SIGINT, bot.signal_handler)
    signal.signal(signal.SIGTERM, bot.signal_handler)
    
    try:
        # Initialize
        if not await bot.initialize():
            logger.error("Failed to initialize bot")
            return 1
        
        # Run
        success = await bot.run()
        
        # Shutdown
        await bot.shutdown()
        
        return 0 if success else 1
        
    except KeyboardInterrupt:
        logger.warning("\nInterrupted by user")
        await bot.shutdown()
        return 1
    
    except Exception as e:
        logger.critical(f"Unhandled exception: {str(e)}", exc_info=True)
        await bot.shutdown()
        return 1


if __name__ == "__main__":
    # Run the bot
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
