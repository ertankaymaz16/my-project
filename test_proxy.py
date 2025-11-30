#!/usr/bin/env python3
"""
Proxy Test Script
Quick test to verify proxy configuration is working correctly
"""
import asyncio
import json
import sys
from pathlib import Path
from modules.browser import BrowserManager
from utils.logger import logger


async def test_proxy_connection():
    """Test proxy connection and IP address"""
    
    logger.info("=" * 60)
    logger.info("🧪 PROXY CONNECTION TEST")
    logger.info("=" * 60)
    
    # Load config
    config_file = Path("config.json")
    if not config_file.exists():
        logger.error("❌ config.json not found!")
        logger.info("Please copy config.json.example to config.json and configure proxy settings")
        return False
    
    with open(config_file, 'r') as f:
        config = json.load(f)
    
    # Check if proxy is enabled
    proxy_enabled = config.get('proxy', {}).get('enabled', False)
    
    if not proxy_enabled:
        logger.warning("⚠️  Proxy is DISABLED in config.json")
        logger.info("Set 'proxy.enabled' to true to test proxy")
        return False
    
    # Prepare proxy config
    proxy_config = {
        'server': config['proxy']['server'],
        'username': config['proxy'].get('username'),
        'password': config['proxy'].get('password')
    }
    
    logger.info(f"🌐 Testing proxy: {proxy_config['server']}")
    
    try:
        # Test 1: Check IP without proxy
        logger.info("\n📍 Test 1: Checking IP WITHOUT proxy...")
        browser_no_proxy = BrowserManager(
            headless=True,
            proxy_config=None,
            clear_cache_on_start=False
        )
        page_no_proxy = await browser_no_proxy.start()
        
        await page_no_proxy.goto('https://api.ipify.org?format=json', timeout=30000)
        content_no_proxy = await page_no_proxy.content()
        
        # Extract IP from JSON response
        import re
        ip_match = re.search(r'"ip":"([^"]+)"', content_no_proxy)
        original_ip = ip_match.group(1) if ip_match else "Unknown"
        
        logger.success(f"✅ Your original IP: {original_ip}")
        
        await browser_no_proxy.close()
        
        # Test 2: Check IP with proxy
        logger.info("\n📍 Test 2: Checking IP WITH proxy...")
        browser_with_proxy = BrowserManager(
            headless=True,
            proxy_config=proxy_config,
            clear_cache_on_start=False
        )
        page_with_proxy = await browser_with_proxy.start()
        
        await page_with_proxy.goto('https://api.ipify.org?format=json', timeout=30000)
        content_with_proxy = await page_with_proxy.content()
        
        # Extract IP from JSON response
        ip_match = re.search(r'"ip":"([^"]+)"', content_with_proxy)
        proxy_ip = ip_match.group(1) if ip_match else "Unknown"
        
        logger.success(f"✅ Your proxy IP: {proxy_ip}")
        
        # Test 3: Check VFS Global access
        logger.info("\n📍 Test 3: Testing VFS Global access...")
        
        await page_with_proxy.goto('https://visa.vfsglobal.com/tur/tr/nld/', timeout=60000)
        
        # Wait for page to load
        await asyncio.sleep(3)
        
        # Check page title
        title = await page_with_proxy.title()
        current_url = page_with_proxy.url
        
        logger.info(f"Page title: {title}")
        logger.info(f"Current URL: {current_url}")
        
        # Check for 403 error
        if '403' in title or 'access denied' in title.lower() or 'kısıtlandı' in title.lower():
            logger.error("❌ Still getting 403 error - proxy may be blacklisted")
            logger.info("Try a different proxy server or IP")
            success = False
        else:
            logger.success("✅ VFS Global accessible - no 403 error!")
            success = True
        
        # Take screenshot
        screenshot_path = await browser_with_proxy.save_screenshot('proxy_test_vfs')
        if screenshot_path:
            logger.info(f"📸 Screenshot saved: {screenshot_path}")
        
        await browser_with_proxy.close()
        
        # Summary
        logger.info("\n" + "=" * 60)
        logger.info("📊 TEST SUMMARY")
        logger.info("=" * 60)
        logger.info(f"Original IP: {original_ip}")
        logger.info(f"Proxy IP: {proxy_ip}")
        logger.info(f"IP Changed: {'✅ YES' if original_ip != proxy_ip else '❌ NO'}")
        logger.info(f"VFS Access: {'✅ SUCCESS' if success else '❌ FAILED'}")
        logger.info("=" * 60)
        
        if original_ip == proxy_ip:
            logger.warning("⚠️  WARNING: IP did not change - proxy may not be working!")
            logger.info("Check your proxy configuration and credentials")
            return False
        
        return success
        
    except Exception as e:
        logger.error(f"❌ Test failed: {str(e)}", exc_info=True)
        return False


async def test_proxy_speed():
    """Test proxy connection speed"""
    
    logger.info("\n" + "=" * 60)
    logger.info("⚡ PROXY SPEED TEST")
    logger.info("=" * 60)
    
    # Load config
    config_file = Path("config.json")
    if not config_file.exists():
        return False
    
    with open(config_file, 'r') as f:
        config = json.load(f)
    
    if not config.get('proxy', {}).get('enabled', False):
        return False
    
    proxy_config = {
        'server': config['proxy']['server'],
        'username': config['proxy'].get('username'),
        'password': config['proxy'].get('password')
    }
    
    try:
        import time
        
        browser = BrowserManager(
            headless=True,
            proxy_config=proxy_config,
            clear_cache_on_start=False
        )
        page = await browser.start()
        
        # Test page load time
        start_time = time.time()
        await page.goto('https://www.google.com', timeout=30000)
        load_time = time.time() - start_time
        
        logger.info(f"⏱️  Page load time: {load_time:.2f} seconds")
        
        if load_time < 3:
            logger.success("✅ Proxy speed: EXCELLENT")
        elif load_time < 5:
            logger.success("✅ Proxy speed: GOOD")
        elif load_time < 10:
            logger.warning("⚠️  Proxy speed: ACCEPTABLE")
        else:
            logger.warning("⚠️  Proxy speed: SLOW - consider using a faster proxy")
        
        await browser.close()
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Speed test failed: {str(e)}")
        return False


async def main():
    """Main test runner"""
    
    try:
        # Test connection
        connection_ok = await test_proxy_connection()
        
        if connection_ok:
            # Test speed
            await test_proxy_speed()
            
            logger.info("\n" + "=" * 60)
            logger.success("🎉 ALL TESTS PASSED!")
            logger.info("=" * 60)
            logger.info("Your proxy is configured correctly and working.")
            logger.info("You can now run the main bot: python main.py")
            return 0
        else:
            logger.info("\n" + "=" * 60)
            logger.error("❌ TESTS FAILED")
            logger.info("=" * 60)
            logger.info("Please check your proxy configuration in config.json")
            logger.info("See PROXY_SETUP_GUIDE.md for detailed instructions")
            return 1
            
    except KeyboardInterrupt:
        logger.warning("\n⚠️  Test interrupted by user")
        return 1
    except Exception as e:
        logger.critical(f"❌ Unexpected error: {str(e)}", exc_info=True)
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
