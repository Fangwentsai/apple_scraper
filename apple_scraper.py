#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Apple 整修品爬蟲程式 - 包含完整 Headers
模擬正常使用者瀏覽行為
"""

import asyncio
import json
import re
from datetime import datetime
from playwright.async_api import async_playwright
import logging
import random

# 設定日誌
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class AppleRefurbishedScraperWithHeaders:
    def __init__(self):
        # 完整的 Headers 模擬真實瀏覽器
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'Accept-Language': 'zh-TW,zh;q=0.9,en-US;q=0.8,en;q=0.7',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
            'Cache-Control': 'max-age=0',
            'sec-ch-ua': '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"macOS"',
            'Referer': 'https://www.apple.com/tw/',
            'Origin': 'https://www.apple.com'
        }
        
        self.categories = {
            'mac': 'https://www.apple.com/tw/shop/refurbished/mac',
            'ipad': 'https://www.apple.com/tw/shop/refurbished/ipad',
            'iphone': 'https://www.apple.com/tw/shop/refurbished/iphone',
            'airpods': 'https://www.apple.com/tw/shop/refurbished/airpods',
            'homepod': 'https://www.apple.com/tw/shop/refurbished/homepod',
            'appletv': 'https://www.apple.com/tw/shop/refurbished/appletv',
            'accessories': 'https://www.apple.com/tw/shop/refurbished/accessories'
        }

    async def setup_browser_context(self, browser):
        """設定瀏覽器上下文，包含完整的 Headers"""
        context = await browser.new_context(
            user_agent=self.headers['User-Agent'],
            extra_http_headers=self.headers,
            viewport={'width': 1920, 'height': 1080},
            locale='zh-TW',
            timezone_id='Asia/Taipei'
        )
        
        # 設定地理位置為台灣
        await context.set_geolocation({'latitude': 25.0330, 'longitude': 121.5654})
        
        return context

    async def human_like_delay(self, min_seconds=1, max_seconds=3):
        """模擬人類行為的隨機延遲"""
        delay = random.uniform(min_seconds, max_seconds)
        await asyncio.sleep(delay)

    async def scrape_with_headers(self, url, category_name):
        """使用完整 Headers 爬取指定 URL"""
        logger.info(f"開始爬取 {category_name}: {url}")
        
        async with async_playwright() as p:
            browser = await p.chromium.launch(
                headless=False,
                args=[
                    '--no-sandbox',
                    '--disable-blink-features=AutomationControlled',
                    '--disable-web-security',
                    '--disable-features=VizDisplayCompositor',
                    '--disable-dev-shm-usage'
                ]
            )
            
            context = await self.setup_browser_context(browser)
            page = await context.new_page()
            
            try:
                # 訪問頁面
                logger.info(f"訪問 {url}")
                await page.goto(url, wait_until='networkidle', timeout=60000)
                
                # 模擬人類行為
                await self.human_like_delay(2, 4)
                
                # 模擬滾動
                await page.evaluate('window.scrollTo(0, document.body.scrollHeight/2)')
                await self.human_like_delay(1, 2)
                await page.evaluate('window.scrollTo(0, 0)')
                await self.human_like_delay(1, 2)
                
                # 取得頁面標題
                title = await page.title()
                logger.info(f"頁面標題: {title}")
                
                # 取得頁面內容
                content = await page.content()
                
                # 檢查是否有產品
                if '整修品' in content or 'refurbished' in content.lower():
                    logger.info(f"✅ {category_name} 頁面載入成功，包含整修品資訊")
                    
                    # 嘗試找到產品元素
                    selectors = [
                        'div[data-testid="product-tile"]',
                        '.rf-serp-productcard',
                        'a[href*="/product/"]'
                    ]
                    
                    for selector in selectors:
                        elements = await page.query_selector_all(selector)
                        if elements:
                            logger.info(f"找到 {len(elements)} 個產品元素 (選擇器: {selector})")
                            break
                    
                    # 檢查是否有特定產品
                    if category_name == 'homepod':
                        if 'HomePod (第 2 代)' in content:
                            logger.info("✅ 確認找到 HomePod (第 2 代) 產品")
                    elif category_name == 'accessories':
                        if 'AirPods' in content and 'HomePod' in content:
                            logger.info("✅ 確認找到 AirPods 和 HomePod 配件")
                    
                else:
                    logger.warning(f"⚠️ {category_name} 頁面可能沒有整修品或載入失敗")
                
                return True
                
            except Exception as e:
                logger.error(f"爬取 {category_name} 時發生錯誤: {e}")
                return False
            finally:
                await page.close()
                await context.close()
                await browser.close()

    async def test_all_categories(self):
        """測試所有類別的爬取"""
        logger.info("🚀 開始測試所有類別的爬取...")
        logger.info(f"📅 測試時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        logger.info(f"🌐 使用者代理: {self.headers['User-Agent']}")
        
        results = {}
        
        for category_name, url in self.categories.items():
            logger.info(f"\n{'='*50}")
            logger.info(f"測試 {category_name}")
            logger.info(f"{'='*50}")
            
            success = await self.scrape_with_headers(url, category_name)
            results[category_name] = success
            
            # 休息一下避免被封鎖
            await self.human_like_delay(3, 6)
        
        # 顯示結果
        print("\n" + "="*60)
        print("📊 Headers 測試結果")
        print("="*60)
        
        for category_name, success in results.items():
            status = "✅ 成功" if success else "❌ 失敗"
            print(f"{status} {category_name}: {self.categories[category_name]}")
        
        successful_count = sum(results.values())
        print(f"\n🎉 成功測試 {successful_count}/{len(results)} 個類別")
        
        if successful_count == len(results):
            print("✅ 所有類別都可以正常訪問，Headers 設定正確！")
        else:
            print("⚠️ 部分類別訪問失敗，可能需要調整 Headers 或處理反爬蟲機制")

async def main():
    scraper = AppleRefurbishedScraperWithHeaders()
    await scraper.test_all_categories()

if __name__ == "__main__":
    asyncio.run(main()) 