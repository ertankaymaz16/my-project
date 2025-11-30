"""
Telegram bot integration for notifications and human-in-the-loop interactions
"""
import asyncio
from typing import Optional
from telegram import Bot, Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from utils.logger import logger


class TelegramNotifier:
    """Handles Telegram notifications and user interactions"""
    
    def __init__(self, bot_token: str, chat_id: str):
        self.bot_token = bot_token
        self.chat_id = chat_id
        self.bot: Optional[Bot] = None
        self.application: Optional[Application] = None
        self.waiting_for_sms = False
        self.sms_code: Optional[str] = None
        self.sms_event = asyncio.Event()
    
    async def initialize(self):
        """Initialize Telegram bot"""
        try:
            self.bot = Bot(token=self.bot_token)
            self.application = Application.builder().token(self.bot_token).build()
            
            # Add message handler for SMS codes
            self.application.add_handler(
                MessageHandler(filters.TEXT & ~filters.COMMAND, self._handle_message)
            )
            
            # Start polling in background
            await self.application.initialize()
            await self.application.start()
            asyncio.create_task(self._start_polling())
            
            logger.success("Telegram bot initialized")
            
            # Send startup message
            await self.send_message("🤖 Vize Randevu Botu başlatıldı!\n\n✅ Sistem aktif ve randevu taraması başlıyor...")
            
        except Exception as e:
            logger.error(f"Failed to initialize Telegram bot: {str(e)}", exc_info=True)
            raise
    
    async def _start_polling(self):
        """Start polling for updates"""
        try:
            await self.application.updater.start_polling(
                allowed_updates=Update.ALL_TYPES,
                drop_pending_updates=True
            )
        except Exception as e:
            logger.error(f"Polling error: {str(e)}")
    
    async def _handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle incoming messages"""
        try:
            if update.message and update.message.text:
                message_text = update.message.text.strip()
                
                # If waiting for SMS code
                if self.waiting_for_sms:
                    # Extract numeric code (usually 6 digits)
                    import re
                    code_match = re.search(r'\b\d{4,8}\b', message_text)
                    if code_match:
                        self.sms_code = code_match.group()
                        self.waiting_for_sms = False
                        self.sms_event.set()
                        await update.message.reply_text(f"✅ SMS kodu alındı: {self.sms_code}\n\nİşlem devam ediyor...")
                        logger.info(f"SMS code received: {self.sms_code}")
                    else:
                        await update.message.reply_text("❌ Geçerli bir kod bulunamadı. Lütfen sadece SMS kodunu gönderin.")
                
        except Exception as e:
            logger.error(f"Error handling message: {str(e)}")
    
    async def send_message(self, message: str, parse_mode: str = None) -> bool:
        """Send message to user"""
        try:
            await self.bot.send_message(
                chat_id=self.chat_id,
                text=message,
                parse_mode=parse_mode
            )
            logger.debug(f"Telegram message sent: {message[:50]}...")
            return True
        except Exception as e:
            logger.error(f"Failed to send Telegram message: {str(e)}")
            return False
    
    async def send_photo(self, photo_path: str, caption: str = None) -> bool:
        """Send photo to user"""
        try:
            with open(photo_path, 'rb') as photo:
                await self.bot.send_photo(
                    chat_id=self.chat_id,
                    photo=photo,
                    caption=caption
                )
            logger.debug(f"Telegram photo sent: {photo_path}")
            return True
        except Exception as e:
            logger.error(f"Failed to send Telegram photo: {str(e)}")
            return False
    
    async def notify_appointment_found(self, details: dict):
        """Notify user that appointment was found"""
        message = (
            "🎯 RANDEVU BULUNDU!\n\n"
            f"📍 Lokasyon: {details.get('location', 'N/A')}\n"
            f"📅 Tarih: {details.get('date', 'N/A')}\n"
            f"⏰ Saat: {details.get('time', 'N/A')}\n"
            f"👥 Kişi Sayısı: {details.get('people', 'N/A')}\n\n"
            "⚡ Rezervasyon işlemi başlatılıyor..."
        )
        await self.send_message(message)
    
    async def notify_reservation_success(self):
        """Notify user that reservation was successful"""
        message = (
            "✅ REZERVASYON BAŞARILI!\n\n"
            "Randevu bilgileri form alanlarına dolduruldu.\n"
            "Ödeme aşamasına geçiliyor..."
        )
        await self.send_message(message)
    
    async def request_sms_code(self) -> str:
        """Request SMS code from user and wait for response"""
        try:
            self.waiting_for_sms = True
            self.sms_code = None
            self.sms_event.clear()
            
            message = (
                "💳 3D SECURE DOĞRULAMA\n\n"
                "Bankanızdan gelen SMS kodunu bu sohbete gönderin.\n"
                "⏱️ Bekleniyor..."
            )
            await self.send_message(message)
            
            logger.info("Waiting for SMS code from user...")
            
            # Wait for SMS code with timeout (5 minutes)
            try:
                await asyncio.wait_for(self.sms_event.wait(), timeout=300)
                return self.sms_code
            except asyncio.TimeoutError:
                self.waiting_for_sms = False
                await self.send_message("⏱️ SMS kodu bekleme süresi doldu. İşlem iptal edildi.")
                logger.warning("SMS code timeout")
                return None
                
        except Exception as e:
            logger.error(f"Error requesting SMS code: {str(e)}")
            self.waiting_for_sms = False
            return None
    
    async def notify_payment_success(self):
        """Notify user that payment was successful"""
        message = (
            "🎉 ÖDEME TAMAMLANDI!\n\n"
            "✅ Randevunuz başarıyla alındı.\n"
            "📧 E-posta adresinize onay mesajı gönderilecektir.\n\n"
            "İyi günler dileriz! 🇳🇱"
        )
        await self.send_message(message)
    
    async def notify_error(self, error_message: str, screenshot_path: str = None):
        """Notify user about errors"""
        message = f"❌ HATA OLUŞTU\n\n{error_message}"
        await self.send_message(message)
        
        if screenshot_path:
            await self.send_photo(screenshot_path, caption="Hata ekran görüntüsü")
    
    async def notify_polling_status(self, attempt: int):
        """Notify user about polling status (every 10 attempts)"""
        if attempt % 10 == 0:
            message = f"🔍 Tarama devam ediyor... (Deneme #{attempt})\n\n⏳ Randevu bekleniyor..."
            await self.send_message(message)
    
    async def shutdown(self):
        """Shutdown Telegram bot"""
        try:
            if self.application:
                await self.application.stop()
                await self.application.shutdown()
            logger.info("Telegram bot shutdown")
        except Exception as e:
            logger.error(f"Error shutting down Telegram bot: {str(e)}")
