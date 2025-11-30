"""
Browser management with enhanced anti-detection and MacOS compatibility
Refactored for: WAF/Cloudflare bypass, MacOS stability, Cookie injection
"""
import asyncio
import json
from pathlib import Path
from typing import Optional, Dict, Any
from playwright.async_api import (
    async_playwright, 
    Browser, 
    BrowserContext, 
    Page, 
    Playwright,
    Error as PlaywrightError
)
from utils.logger import logger


class BrowserManager:
    """
    Enhanced browser manager with:
    - Anti-detection features for WAF/Cloudflare bypass
    - MacOS stability (headless=False default)
    - Cookie injection for session persistence
    - Consistent MacOS fingerprint
    """
    
    # Fixed MacOS User-Agent for consistency (prevents fingerprint randomness)
    MACOS_USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36"
    
    # Fixed viewport for consistency
    VIEWPORT = {'width': 1920, 'height': 1080}
    
    # Timeout settings (60 seconds for resilience)
    DEFAULT_TIMEOUT = 60000  # 60 seconds
    NAVIGATION_TIMEOUT = 60000
    
    def __init__(
        self, 
        headless: bool = False,  # Changed default to False for MacOS stability
        user_data_dir: str = "./browser_data",
        cookies_file: str = "cookies.json"
    ):
        """
        Initialize browser manager
        
        Args:
            headless: Run in headless mode (False recommended for MacOS)
            user_data_dir: Directory for browser data persistence
            cookies_file: Path to cookies file for session restoration
        """
        self.headless = headless
        self.user_data_dir = Path(user_data_dir)
        self.user_data_dir.mkdir(exist_ok=True)
        self.cookies_file = Path(cookies_file)
        
        # Browser components
        self.playwright: Optional[Playwright] = None
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        self.page: Optional[Page] = None
        
        logger.info(f"🔧 Browser Manager initialized (headless={headless})")
    
    async def start(self) -> Page:
        """
        Start browser with enhanced anti-detection configuration
        
        Returns:
            Page: Playwright page object ready for automation
            
        Raises:
            Exception: If browser fails to start
        """
        try:
            logger.info("🚀 Starting browser with anti-detection features...")
            
            # Start Playwright
            self.playwright = await async_playwright().start()
            
            # Enhanced launch arguments for stealth and MacOS stability
            launch_args = [
                # CRITICAL: Disable automation detection
                '--disable-blink-features=AutomationControlled',
                
                # Remove "Chrome is being controlled by automated test software" banner
                '--disable-infobars',
                
                # Stability improvements for MacOS
                '--disable-dev-shm-usage',
                '--disable-gpu',  # Helps prevent crashes on MacOS
                '--no-sandbox',
                '--disable-setuid-sandbox',
                
                # Anti-detection enhancements
                '--disable-web-security',
                '--disable-features=IsolateOrigins,site-per-process',
                '--disable-site-isolation-trials',
                
                # Certificate handling
                '--ignore-certificate-errors',
                '--ignore-certificate-errors-spki-list',
                
                # Window positioning
                '--window-position=0,0',
                f'--window-size={self.VIEWPORT["width"]},{self.VIEWPORT["height"]}',
                
                # Additional stealth
                '--disable-blink-features=AutomationControlled',  # Repeated for emphasis
                '--exclude-switches=enable-automation',
                '--disable-extensions',
            ]
            
            # Launch Chromium with stealth configuration
            self.browser = await self.playwright.chromium.launch(
                headless=self.headless,
                args=launch_args,
                # Remove automation flags
                ignore_default_args=['--enable-automation'],
                # Slow down operations slightly for more human-like behavior
                slow_mo=50  # 50ms delay between operations
            )
            
            logger.success(f"✅ Browser launched (headless={self.headless})")
            
            # Create context with cookie injection support
            await self._create_context()
            
            # Create page
            self.page = await self.context.new_page()
            
            # Set default timeouts
            self.page.set_default_timeout(self.DEFAULT_TIMEOUT)
            self.page.set_default_navigation_timeout(self.NAVIGATION_TIMEOUT)
            
            # Apply additional stealth measures
            await self._apply_stealth_scripts()
            
            # Set extra HTTP headers for realism
            await self._set_realistic_headers()
            
            logger.success("✅ Browser ready with anti-detection features")
            return self.page
            
        except Exception as e:
            logger.error(f"❌ Failed to start browser: {str(e)}", exc_info=True)
            await self.close()
            raise
    
    async def _create_context(self):
        """
        Create browser context with cookie injection and realistic settings
        """
        try:
            # Context configuration with fixed MacOS fingerprint
            context_options = {
                'viewport': self.VIEWPORT,
                'user_agent': self.MACOS_USER_AGENT,
                'locale': 'tr-TR',
                'timezone_id': 'Europe/Istanbul',
                'permissions': ['geolocation', 'notifications'],
                'geolocation': {
                    'latitude': 40.1826,  # Bursa coordinates
                    'longitude': 29.0665
                },
                'color_scheme': 'light',
                'device_scale_factor': 1,
                'has_touch': False,
                'is_mobile': False,
                'java_script_enabled': True,
                'accept_downloads': True,
                'ignore_https_errors': True,
                # Additional fingerprint consistency
                'screen': {
                    'width': 1920,
                    'height': 1080
                },
                'extra_http_headers': {
                    'Accept-Language': 'tr-TR,tr;q=0.9,en-US;q=0.8,en;q=0.7',
                }
            }
            
            # Create context
            self.context = await self.browser.new_context(**context_options)
            
            # COOKIE INJECTION: Load cookies if available
            if self.cookies_file.exists():
                await self._inject_cookies()
            else:
                logger.info("ℹ️  No cookies file found, starting fresh session")
            
            logger.success("✅ Browser context created")
            
        except Exception as e:
            logger.error(f"❌ Failed to create context: {str(e)}")
            raise
    
    async def _inject_cookies(self):
        """
        Inject cookies from file to bypass login
        """
        try:
            logger.info(f"🍪 Loading cookies from {self.cookies_file}...")
            
            with open(self.cookies_file, 'r', encoding='utf-8') as f:
                cookies = json.load(f)
            
            if not cookies:
                logger.warning("⚠️  Cookies file is empty")
                return False
            
            # Add cookies to context
            await self.context.add_cookies(cookies)
            
            logger.success(f"✅ Injected {len(cookies)} cookies successfully")
            return True
            
        except json.JSONDecodeError as e:
            logger.error(f"❌ Invalid cookies file format: {str(e)}")
            return False
        except Exception as e:
            logger.error(f"❌ Failed to inject cookies: {str(e)}")
            return False
    
    async def _apply_stealth_scripts(self):
        """
        Apply JavaScript stealth scripts to evade detection
        """
        try:
            await self.context.add_init_script("""
                // Remove webdriver property
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => undefined
                });
                
                // Override plugins to appear as real browser
                Object.defineProperty(navigator, 'plugins', {
                    get: () => [
                        {
                            0: {type: "application/x-google-chrome-pdf", suffixes: "pdf", description: "Portable Document Format"},
                            description: "Portable Document Format",
                            filename: "internal-pdf-viewer",
                            length: 1,
                            name: "Chrome PDF Plugin"
                        },
                        {
                            0: {type: "application/pdf", suffixes: "pdf", description: "Portable Document Format"},
                            description: "Portable Document Format",
                            filename: "mhjfbmdgcfjbbpaeojofohoefgiehjai",
                            length: 1,
                            name: "Chrome PDF Viewer"
                        },
                        {
                            0: {type: "application/x-nacl", suffixes: "", description: "Native Client Executable"},
                            1: {type: "application/x-pnacl", suffixes: "", description: "Portable Native Client Executable"},
                            description: "",
                            filename: "internal-nacl-plugin",
                            length: 2,
                            name: "Native Client"
                        }
                    ]
                });
                
                // Override languages
                Object.defineProperty(navigator, 'languages', {
                    get: () => ['tr-TR', 'tr', 'en-US', 'en']
                });
                
                // Add chrome object
                window.chrome = {
                    runtime: {},
                    loadTimes: function() {},
                    csi: function() {},
                    app: {}
                };
                
                // Override permissions
                const originalQuery = window.navigator.permissions.query;
                window.navigator.permissions.query = (parameters) => (
                    parameters.name === 'notifications' ?
                        Promise.resolve({ state: Notification.permission }) :
                        originalQuery(parameters)
                );
                
                // Mock hardware concurrency
                Object.defineProperty(navigator, 'hardwareConcurrency', {
                    get: () => 8
                });
                
                // Mock device memory
                Object.defineProperty(navigator, 'deviceMemory', {
                    get: () => 8
                });
                
                // Override toString methods to hide proxy
                const originalToString = Function.prototype.toString;
                Function.prototype.toString = function() {
                    if (this === window.navigator.permissions.query) {
                        return 'function query() { [native code] }';
                    }
                    return originalToString.call(this);
                };
                
                // Add connection info
                Object.defineProperty(navigator, 'connection', {
                    get: () => ({
                        effectiveType: '4g',
                        rtt: 50,
                        downlink: 10,
                        saveData: false
                    })
                });
            """)
            
            logger.success("✅ Stealth scripts applied")
            
        except Exception as e:
            logger.error(f"❌ Failed to apply stealth scripts: {str(e)}")
    
    async def _set_realistic_headers(self):
        """
        Set realistic HTTP headers to mimic real browser
        """
        try:
            headers = {
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
                'Accept-Language': 'tr-TR,tr;q=0.9,en-US;q=0.8,en;q=0.7',
                'Accept-Encoding': 'gzip, deflate, br',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
                'Sec-Fetch-Dest': 'document',
                'Sec-Fetch-Mode': 'navigate',
                'Sec-Fetch-Site': 'none',
                'Sec-Fetch-User': '?1',
                'Cache-Control': 'max-age=0',
            }
            
            await self.page.set_extra_http_headers(headers)
            logger.success("✅ Realistic headers set")
            
        except Exception as e:
            logger.error(f"❌ Failed to set headers: {str(e)}")
    
    async def save_cookies(self, filepath: Optional[str] = None) -> bool:
        """
        Save current cookies to file for session persistence
        
        Args:
            filepath: Custom path for cookies file (optional)
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            if not self.context:
                logger.warning("⚠️  No context available to save cookies")
                return False
            
            save_path = Path(filepath) if filepath else self.cookies_file
            
            cookies = await self.context.cookies()
            
            with open(save_path, 'w', encoding='utf-8') as f:
                json.dump(cookies, f, indent=2, ensure_ascii=False)
            
            logger.success(f"✅ Saved {len(cookies)} cookies to {save_path}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to save cookies: {str(e)}")
            return False
    
    async def load_cookies(self, filepath: Optional[str] = None) -> bool:
        """
        Load cookies from file (alternative to automatic injection)
        
        Args:
            filepath: Custom path for cookies file (optional)
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            if not self.context:
                logger.warning("⚠️  No context available to load cookies")
                return False
            
            load_path = Path(filepath) if filepath else self.cookies_file
            
            if not load_path.exists():
                logger.warning(f"⚠️  Cookies file not found: {load_path}")
                return False
            
            with open(load_path, 'r', encoding='utf-8') as f:
                cookies = json.load(f)
            
            await self.context.add_cookies(cookies)
            
            logger.success(f"✅ Loaded {len(cookies)} cookies from {load_path}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to load cookies: {str(e)}")
            return False
    
    async def save_screenshot(self, name: str = "screenshot", full_page: bool = True) -> Optional[str]:
        """
        Save screenshot for debugging
        
        Args:
            name: Base name for screenshot file
            full_page: Capture full page or just viewport
            
        Returns:
            str: Path to saved screenshot, or None if failed
        """
        try:
            if not self.page:
                logger.warning("⚠️  No page available for screenshot")
                return None
            
            # Create logs directory if it doesn't exist
            logs_dir = Path("logs")
            logs_dir.mkdir(exist_ok=True)
            
            # Generate filename with timestamp
            import time
            timestamp = int(time.time())
            screenshot_path = logs_dir / f"{name}_{timestamp}.png"
            
            # Take screenshot
            await self.page.screenshot(
                path=str(screenshot_path), 
                full_page=full_page,
                timeout=30000
            )
            
            logger.success(f"📸 Screenshot saved: {screenshot_path}")
            return str(screenshot_path)
            
        except Exception as e:
            logger.error(f"❌ Failed to save screenshot: {str(e)}")
            return None
    
    async def check_session(self) -> bool:
        """
        Check if current session is still valid
        
        Returns:
            bool: True if session is valid, False otherwise
        """
        try:
            if not self.page:
                return False
            
            # Get current URL
            current_url = self.page.url
            
            # Check if redirected to login page
            if any(keyword in current_url.lower() for keyword in ['login', 'signin', 'auth']):
                logger.warning("⚠️  Session expired - redirected to login page")
                return False
            
            # Additional check: try to access page title
            try:
                title = await self.page.title()
                if title:
                    logger.debug(f"✅ Session valid - Current page: {title}")
                    return True
            except:
                pass
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Session check failed: {str(e)}")
            return False
    
    async def wait_for_navigation(self, timeout: Optional[int] = None):
        """
        Wait for navigation to complete
        
        Args:
            timeout: Custom timeout in milliseconds (optional)
        """
        try:
            wait_timeout = timeout if timeout else self.NAVIGATION_TIMEOUT
            await self.page.wait_for_load_state('networkidle', timeout=wait_timeout)
            logger.debug("✅ Navigation completed")
        except PlaywrightError as e:
            logger.warning(f"⚠️  Navigation timeout: {str(e)}")
    
    async def close(self):
        """
        Close browser and cleanup resources
        """
        try:
            logger.info("🔄 Closing browser...")
            
            if self.page:
                await self.page.close()
                self.page = None
            
            if self.context:
                await self.context.close()
                self.context = None
            
            if self.browser:
                await self.browser.close()
                self.browser = None
            
            if self.playwright:
                await self.playwright.stop()
                self.playwright = None
            
            logger.success("✅ Browser closed successfully")
            
        except Exception as e:
            logger.error(f"❌ Error closing browser: {str(e)}")
    
    async def restart(self) -> Page:
        """
        Restart browser (useful for recovery from errors)
        
        Returns:
            Page: New page object after restart
        """
        logger.warning("🔄 Restarting browser...")
        
        # Close existing browser
        await self.close()
        
        # Wait a moment before restarting
        await asyncio.sleep(2)
        
        # Start fresh browser
        return await self.start()
    
    async def get_page_info(self) -> Dict[str, Any]:
        """
        Get current page information for debugging
        
        Returns:
            dict: Page information including URL, title, cookies count
        """
        try:
            if not self.page:
                return {'error': 'No page available'}
            
            info = {
                'url': self.page.url,
                'title': await self.page.title(),
                'viewport': self.page.viewport_size,
                'cookies_count': len(await self.context.cookies()) if self.context else 0,
                'user_agent': self.MACOS_USER_AGENT
            }
            
            return info
            
        except Exception as e:
            return {'error': str(e)}
    
    def __repr__(self) -> str:
        """String representation of browser manager"""
        status = "active" if self.page else "inactive"
        return f"<BrowserManager status={status} headless={self.headless}>"
