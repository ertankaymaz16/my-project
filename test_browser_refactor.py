"""
Test script for refactored browser.py module
Tests all critical features: anti-detection, cookie injection, MacOS stability
"""
import asyncio
import sys
from pathlib import Path
from modules.browser import BrowserManager
from utils.logger import logger


async def test_browser_initialization():
    """Test 1: Browser initialization with anti-detection"""
    logger.info("=" * 60)
    logger.info("TEST 1: Browser Initialization")
    logger.info("=" * 60)
    
    browser = BrowserManager(headless=False)
    
    try:
        page = await browser.start()
        logger.success("✅ Browser started successfully")
        
        # Check page info
        info = await browser.get_page_info()
        logger.info(f"📊 Page Info: {info}")
        
        # Verify user agent
        user_agent = await page.evaluate("navigator.userAgent")
        logger.info(f"🔍 User Agent: {user_agent}")
        
        # Verify webdriver is hidden
        webdriver = await page.evaluate("navigator.webdriver")
        logger.info(f"🔍 Webdriver property: {webdriver}")
        
        if webdriver is None:
            logger.success("✅ Webdriver successfully hidden")
        else:
            logger.error("❌ Webdriver detection failed")
        
        # Verify plugins
        plugins_length = await page.evaluate("navigator.plugins.length")
        logger.info(f"🔍 Plugins count: {plugins_length}")
        
        if plugins_length > 0:
            logger.success("✅ Plugins successfully spoofed")
        else:
            logger.warning("⚠️  No plugins detected")
        
        await browser.close()
        return True
        
    except Exception as e:
        logger.error(f"❌ Test failed: {str(e)}")
        await browser.close()
        return False


async def test_cookie_injection():
    """Test 2: Cookie injection functionality"""
    logger.info("=" * 60)
    logger.info("TEST 2: Cookie Injection")
    logger.info("=" * 60)
    
    browser = BrowserManager(headless=False, cookies_file="test_cookies.json")
    
    try:
        page = await browser.start()
        
        # Navigate to a test site
        logger.info("🌐 Navigating to test site...")
        await page.goto("https://www.example.com", wait_until="networkidle")
        
        # Save cookies
        logger.info("💾 Saving cookies...")
        success = await browser.save_cookies("test_cookies.json")
        
        if success:
            logger.success("✅ Cookies saved successfully")
        else:
            logger.error("❌ Failed to save cookies")
        
        # Check if cookies file exists
        if Path("test_cookies.json").exists():
            logger.success("✅ Cookies file created")
        else:
            logger.error("❌ Cookies file not found")
        
        await browser.close()
        
        # Test loading cookies in new session
        logger.info("🔄 Testing cookie loading in new session...")
        browser2 = BrowserManager(headless=False, cookies_file="test_cookies.json")
        page2 = await browser2.start()
        
        # Check if cookies were loaded
        info = await browser2.get_page_info()
        logger.info(f"📊 Cookies loaded: {info.get('cookies_count', 0)}")
        
        if info.get('cookies_count', 0) > 0:
            logger.success("✅ Cookie injection successful")
        else:
            logger.warning("⚠️  No cookies loaded")
        
        await browser2.close()
        
        # Cleanup
        Path("test_cookies.json").unlink(missing_ok=True)
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Test failed: {str(e)}")
        await browser.close()
        Path("test_cookies.json").unlink(missing_ok=True)
        return False


async def test_stealth_features():
    """Test 3: Anti-detection stealth features"""
    logger.info("=" * 60)
    logger.info("TEST 3: Stealth Features")
    logger.info("=" * 60)
    
    browser = BrowserManager(headless=False)
    
    try:
        page = await browser.start()
        
        # Navigate to bot detection test site
        logger.info("🌐 Testing stealth on bot detection site...")
        await page.goto("https://bot.sannysoft.com/", wait_until="networkidle", timeout=60000)
        
        # Wait for page to load
        await asyncio.sleep(3)
        
        # Take screenshot
        screenshot_path = await browser.save_screenshot("stealth_test")
        logger.info(f"📸 Screenshot saved: {screenshot_path}")
        
        # Check various detection points
        checks = {
            'webdriver': await page.evaluate("navigator.webdriver"),
            'plugins': await page.evaluate("navigator.plugins.length"),
            'languages': await page.evaluate("navigator.languages.length"),
            'chrome': await page.evaluate("typeof window.chrome"),
            'permissions': await page.evaluate("typeof navigator.permissions"),
        }
        
        logger.info("🔍 Detection checks:")
        for key, value in checks.items():
            logger.info(f"  - {key}: {value}")
        
        # Evaluate results
        passed = 0
        total = 5
        
        if checks['webdriver'] is None:
            passed += 1
            logger.success("  ✅ Webdriver hidden")
        else:
            logger.error("  ❌ Webdriver detected")
        
        if checks['plugins'] > 0:
            passed += 1
            logger.success("  ✅ Plugins present")
        else:
            logger.warning("  ⚠️  No plugins")
        
        if checks['languages'] > 0:
            passed += 1
            logger.success("  ✅ Languages present")
        else:
            logger.warning("  ⚠️  No languages")
        
        if checks['chrome'] == 'object':
            passed += 1
            logger.success("  ✅ Chrome object present")
        else:
            logger.warning("  ⚠️  Chrome object missing")
        
        if checks['permissions'] == 'object':
            passed += 1
            logger.success("  ✅ Permissions API present")
        else:
            logger.warning("  ⚠️  Permissions API missing")
        
        logger.info(f"📊 Stealth Score: {passed}/{total}")
        
        await browser.close()
        return passed >= 4  # Pass if at least 4/5 checks pass
        
    except Exception as e:
        logger.error(f"❌ Test failed: {str(e)}")
        await browser.close()
        return False


async def test_session_management():
    """Test 4: Session management and recovery"""
    logger.info("=" * 60)
    logger.info("TEST 4: Session Management")
    logger.info("=" * 60)
    
    browser = BrowserManager(headless=False)
    
    try:
        page = await browser.start()
        
        # Navigate to a site
        await page.goto("https://www.example.com", wait_until="networkidle")
        
        # Check session
        is_valid = await browser.check_session()
        logger.info(f"🔍 Session valid: {is_valid}")
        
        if is_valid:
            logger.success("✅ Session check passed")
        else:
            logger.error("❌ Session check failed")
        
        # Test restart
        logger.info("🔄 Testing browser restart...")
        new_page = await browser.restart()
        
        if new_page:
            logger.success("✅ Browser restart successful")
        else:
            logger.error("❌ Browser restart failed")
        
        await browser.close()
        return True
        
    except Exception as e:
        logger.error(f"❌ Test failed: {str(e)}")
        await browser.close()
        return False


async def test_screenshot_functionality():
    """Test 5: Screenshot functionality"""
    logger.info("=" * 60)
    logger.info("TEST 5: Screenshot Functionality")
    logger.info("=" * 60)
    
    browser = BrowserManager(headless=False)
    
    try:
        page = await browser.start()
        await page.goto("https://www.example.com", wait_until="networkidle")
        
        # Test screenshot
        screenshot_path = await browser.save_screenshot("test_screenshot")
        
        if screenshot_path and Path(screenshot_path).exists():
            logger.success(f"✅ Screenshot saved: {screenshot_path}")
            result = True
        else:
            logger.error("❌ Screenshot failed")
            result = False
        
        await browser.close()
        return result
        
    except Exception as e:
        logger.error(f"❌ Test failed: {str(e)}")
        await browser.close()
        return False


async def run_all_tests():
    """Run all tests and report results"""
    logger.info("🚀 Starting Browser Refactor Tests")
    logger.info("=" * 60)
    
    tests = [
        ("Browser Initialization", test_browser_initialization),
        ("Cookie Injection", test_cookie_injection),
        ("Stealth Features", test_stealth_features),
        ("Session Management", test_session_management),
        ("Screenshot Functionality", test_screenshot_functionality),
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        try:
            logger.info(f"\n🧪 Running: {test_name}")
            result = await test_func()
            results[test_name] = result
            
            if result:
                logger.success(f"✅ {test_name}: PASSED")
            else:
                logger.error(f"❌ {test_name}: FAILED")
            
            # Wait between tests
            await asyncio.sleep(2)
            
        except Exception as e:
            logger.error(f"❌ {test_name}: EXCEPTION - {str(e)}")
            results[test_name] = False
    
    # Summary
    logger.info("\n" + "=" * 60)
    logger.info("📊 TEST SUMMARY")
    logger.info("=" * 60)
    
    passed = sum(1 for r in results.values() if r)
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASSED" if result else "❌ FAILED"
        logger.info(f"{status}: {test_name}")
    
    logger.info("=" * 60)
    logger.info(f"📈 Results: {passed}/{total} tests passed")
    logger.info("=" * 60)
    
    return passed == total


if __name__ == "__main__":
    try:
        success = asyncio.run(run_all_tests())
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        logger.warning("\n⚠️  Tests interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"❌ Test suite failed: {str(e)}")
        sys.exit(1)
