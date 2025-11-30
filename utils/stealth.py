"""
Anti-detection and stealth utilities for bypassing bot detection
"""
import random
import asyncio
from typing import Optional
from playwright.async_api import Page, BrowserContext


class StealthHelper:
    """Helper class for anti-detection measures"""
    
    @staticmethod
    async def add_stealth_scripts(context: BrowserContext):
        """Add stealth scripts to bypass detection"""
        await context.add_init_script("""
            // Overwrite the `plugins` property to use a custom getter.
            Object.defineProperty(navigator, 'plugins', {
                get: () => [1, 2, 3, 4, 5]
            });
            
            // Overwrite the `languages` property to use a custom getter.
            Object.defineProperty(navigator, 'languages', {
                get: () => ['tr-TR', 'tr', 'en-US', 'en']
            });
            
            // Overwrite the `webdriver` property to return undefined
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            });
            
            // Mock chrome object
            window.chrome = {
                runtime: {}
            };
            
            // Mock permissions
            const originalQuery = window.navigator.permissions.query;
            window.navigator.permissions.query = (parameters) => (
                parameters.name === 'notifications' ?
                    Promise.resolve({ state: Notification.permission }) :
                    originalQuery(parameters)
            );
        """)
    
    @staticmethod
    async def random_delay(min_seconds: float = 0.5, max_seconds: float = 2.0):
        """Add random human-like delay"""
        delay = random.uniform(min_seconds, max_seconds)
        await asyncio.sleep(delay)
    
    @staticmethod
    async def human_like_typing(page: Page, selector: str, text: str, delay_range: tuple = (0.05, 0.15)):
        """Type text with human-like delays between keystrokes"""
        element = await page.wait_for_selector(selector, timeout=10000)
        await element.click()
        
        for char in text:
            await element.type(char)
            await asyncio.sleep(random.uniform(*delay_range))
    
    @staticmethod
    async def random_mouse_movement(page: Page):
        """Simulate random mouse movements"""
        viewport_size = page.viewport_size
        if not viewport_size:
            return
        
        for _ in range(random.randint(2, 5)):
            x = random.randint(0, viewport_size['width'])
            y = random.randint(0, viewport_size['height'])
            await page.mouse.move(x, y)
            await asyncio.sleep(random.uniform(0.1, 0.3))
    
    @staticmethod
    async def scroll_randomly(page: Page):
        """Scroll page randomly to simulate human behavior"""
        scroll_amount = random.randint(100, 500)
        await page.evaluate(f"window.scrollBy(0, {scroll_amount})")
        await asyncio.sleep(random.uniform(0.3, 0.8))
    
    @staticmethod
    def get_random_viewport():
        """Get random viewport size to avoid fingerprinting"""
        viewports = [
            {'width': 1920, 'height': 1080},
            {'width': 1366, 'height': 768},
            {'width': 1536, 'height': 864},
            {'width': 1440, 'height': 900},
        ]
        return random.choice(viewports)
    
    @staticmethod
    def get_user_agent():
        """Get realistic user agent"""
        user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        ]
        return random.choice(user_agents)
    
    @staticmethod
    async def wait_for_element_safely(page: Page, selector: str, timeout: int = 30000) -> Optional[any]:
        """Wait for element with error handling"""
        try:
            element = await page.wait_for_selector(selector, timeout=timeout, state='visible')
            return element
        except Exception as e:
            return None
    
    @staticmethod
    async def click_with_retry(page: Page, selector: str, max_retries: int = 3):
        """Click element with retry mechanism"""
        for attempt in range(max_retries):
            try:
                await page.click(selector, timeout=10000)
                await StealthHelper.random_delay(0.3, 0.7)
                return True
            except Exception as e:
                if attempt == max_retries - 1:
                    raise
                await asyncio.sleep(1)
        return False
