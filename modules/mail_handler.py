"""
Email handler for OTP code extraction
"""
import imaplib
import email
import re
import asyncio
from typing import Optional
from email.header import decode_header
from utils.logger import logger


class MailHandler:
    """Handles email operations for OTP retrieval"""
    
    def __init__(self, email_address: str, password: str, imap_server: str, imap_port: int = 993):
        self.email_address = email_address
        self.password = password
        self.imap_server = imap_server
        self.imap_port = imap_port
        self.mail: Optional[imaplib.IMAP4_SSL] = None
    
    def connect(self) -> bool:
        """Connect to email server"""
        try:
            logger.info(f"Connecting to {self.imap_server}...")
            self.mail = imaplib.IMAP4_SSL(self.imap_server, self.imap_port)
            self.mail.login(self.email_address, self.password)
            logger.success("Email connection established")
            return True
        except Exception as e:
            logger.error(f"Failed to connect to email: {str(e)}", exc_info=True)
            return False
    
    def disconnect(self):
        """Disconnect from email server"""
        try:
            if self.mail:
                self.mail.logout()
                logger.debug("Email connection closed")
        except Exception as e:
            logger.error(f"Error disconnecting from email: {str(e)}")
    
    def get_latest_otp(self, sender_filter: str = None, subject_filter: str = None, timeout: int = 60) -> Optional[str]:
        """
        Get latest OTP code from email
        
        Args:
            sender_filter: Filter emails by sender (e.g., 'vfs', 'visa')
            subject_filter: Filter emails by subject (e.g., 'verification', 'code')
            timeout: Maximum time to wait for email (seconds)
        
        Returns:
            OTP code as string or None
        """
        try:
            if not self.mail:
                if not self.connect():
                    return None
            
            self.mail.select('INBOX')
            
            # Build search criteria
            search_criteria = 'UNSEEN'  # Only unread emails
            
            logger.info(f"Searching for OTP email (timeout: {timeout}s)...")
            
            start_time = asyncio.get_event_loop().time()
            
            while (asyncio.get_event_loop().time() - start_time) < timeout:
                # Search for emails
                status, messages = self.mail.search(None, search_criteria)
                
                if status != 'OK':
                    logger.warning("Failed to search emails")
                    asyncio.get_event_loop().run_until_complete(asyncio.sleep(5))
                    continue
                
                email_ids = messages[0].split()
                
                if not email_ids:
                    logger.debug("No new emails, waiting...")
                    asyncio.get_event_loop().run_until_complete(asyncio.sleep(5))
                    continue
                
                # Check latest emails (last 5)
                for email_id in reversed(email_ids[-5:]):
                    otp = self._extract_otp_from_email(email_id, sender_filter, subject_filter)
                    if otp:
                        logger.success(f"OTP code found: {otp}")
                        return otp
                
                asyncio.get_event_loop().run_until_complete(asyncio.sleep(5))
            
            logger.warning(f"OTP not found within {timeout} seconds")
            return None
            
        except Exception as e:
            logger.error(f"Error getting OTP: {str(e)}", exc_info=True)
            return None
    
    def _extract_otp_from_email(self, email_id: bytes, sender_filter: str = None, subject_filter: str = None) -> Optional[str]:
        """Extract OTP code from a specific email"""
        try:
            # Fetch email
            status, msg_data = self.mail.fetch(email_id, '(RFC822)')
            
            if status != 'OK':
                return None
            
            # Parse email
            email_body = msg_data[0][1]
            email_message = email.message_from_bytes(email_body)
            
            # Get sender
            sender = email_message.get('From', '')
            
            # Get subject
            subject = email_message.get('Subject', '')
            if subject:
                decoded_subject = decode_header(subject)[0]
                if isinstance(decoded_subject[0], bytes):
                    subject = decoded_subject[0].decode(decoded_subject[1] or 'utf-8')
                else:
                    subject = decoded_subject[0]
            
            # Apply filters
            if sender_filter and sender_filter.lower() not in sender.lower():
                return None
            
            if subject_filter and subject_filter.lower() not in subject.lower():
                return None
            
            logger.debug(f"Checking email from: {sender}, subject: {subject}")
            
            # Extract email body
            body = self._get_email_body(email_message)
            
            if not body:
                return None
            
            # Extract OTP using regex patterns
            otp_patterns = [
                r'\b(\d{6})\b',  # 6-digit code
                r'\b(\d{4})\b',  # 4-digit code
                r'\b(\d{8})\b',  # 8-digit code
                r'code[:\s]+(\d{4,8})',  # "code: 123456"
                r'verification[:\s]+(\d{4,8})',  # "verification: 123456"
                r'OTP[:\s]+(\d{4,8})',  # "OTP: 123456"
            ]
            
            for pattern in otp_patterns:
                match = re.search(pattern, body, re.IGNORECASE)
                if match:
                    otp = match.group(1)
                    logger.debug(f"OTP extracted: {otp}")
                    return otp
            
            return None
            
        except Exception as e:
            logger.error(f"Error extracting OTP from email: {str(e)}")
            return None
    
    def _get_email_body(self, email_message) -> str:
        """Extract email body text"""
        body = ""
        
        try:
            if email_message.is_multipart():
                for part in email_message.walk():
                    content_type = part.get_content_type()
                    content_disposition = str(part.get("Content-Disposition"))
                    
                    if content_type == "text/plain" and "attachment" not in content_disposition:
                        try:
                            body = part.get_payload(decode=True).decode()
                            break
                        except:
                            pass
                    elif content_type == "text/html" and not body:
                        try:
                            body = part.get_payload(decode=True).decode()
                        except:
                            pass
            else:
                body = email_message.get_payload(decode=True).decode()
            
            return body
            
        except Exception as e:
            logger.error(f"Error getting email body: {str(e)}")
            return ""
    
    async def wait_for_otp_async(self, sender_filter: str = None, subject_filter: str = None, timeout: int = 60) -> Optional[str]:
        """Async wrapper for getting OTP"""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self.get_latest_otp, sender_filter, subject_filter, timeout)
