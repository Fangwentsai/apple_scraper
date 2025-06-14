#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
增強版 Apple 整修品爬蟲程式
專門提取產品詳細規格和概覽資訊
"""

import asyncio
import json
import re
import os
from datetime import datetime
from playwright.async_api import async_playwright
import logging
from typing import Dict, List, Optional
import time

# 設定日誌
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class EnhancedAppleScraper:
    def __init__(self):
        """初始化增強版爬蟲"""
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
            'Accept-Language': 'zh-TW,zh;q=0.9,en-US;q=0.8,en;q=0.7',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
            'Cache-Control': 'max-age=0'
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
        """設定瀏覽器上下文"""
        context = await browser.new_context(
            user_agent=self.headers['User-Agent'],
            extra_http_headers=self.headers,
            viewport={'width': 1920, 'height': 1080},
            locale='zh-TW',
            timezone_id='Asia/Taipei'
        )
        
        await context.set_geolocation({'latitude': 25.0330, 'longitude': 121.5654})
        return context

    async def extract_product_overview(self, page, product_url: str) -> str:
        """從產品詳細頁面提取完整的產品概覽"""
        try:
            logger.info(f"🔍 提取產品概覽: {product_url}")
            
            # 訪問產品詳細頁面
            await page.goto(product_url, wait_until='networkidle', timeout=30000)
            await asyncio.sleep(2)
            
            # 嘗試多種選擇器來找到產品概覽區域
            overview_selectors = [
                '.rc-pdsection-mainpanel.column.large-9.small-12',
                '.rc-pdsection-mainpanel',
                '.pd-overview',
                '.pd-highlights',
                '[data-module-template="pd/overview"]',
                '.pd-overview-content',
                '.rf-pdp-overview'
            ]
            
            overview_text = ""
            
            for selector in overview_selectors:
                try:
                    elements = await page.query_selector_all(selector)
                    if elements:
                        logger.info(f"✅ 找到概覽區域: {selector}")
                        
                        for element in elements:
                            # 提取文字內容
                            text = await element.inner_text()
                            if text and len(text.strip()) > 50:  # 確保有足夠的內容
                                overview_text += text.strip() + "\n\n"
                        
                        if overview_text:
                            break
                            
                except Exception as e:
                    logger.debug(f"選擇器 {selector} 失敗: {e}")
                    continue
            
            # 如果沒有找到概覽區域，嘗試提取產品規格
            if not overview_text:
                logger.info("🔄 嘗試提取產品規格...")
                overview_text = await self.extract_product_specs(page)
            
            # 清理和格式化文字
            if overview_text:
                overview_text = self.clean_overview_text(overview_text)
                logger.info(f"✅ 成功提取概覽 ({len(overview_text)} 字元)")
                return overview_text
            else:
                logger.warning("⚠️ 未能提取到產品概覽")
                return ""
                
        except Exception as e:
            logger.error(f"❌ 提取產品概覽失敗: {e}")
            return ""

    async def extract_product_specs(self, page) -> str:
        """提取產品規格資訊"""
        specs_text = ""
        
        # 嘗試多種規格選擇器
        spec_selectors = [
            '.rf-pdp-techspecs',
            '.pd-techspecs',
            '.rf-pdp-highlights',
            '.pd-highlights',
            '.rf-pdp-overview-content',
            '.pd-overview-content',
            '[data-module-template="pd/techspecs"]',
            '.rf-pdp-content'
        ]
        
        for selector in spec_selectors:
            try:
                elements = await page.query_selector_all(selector)
                if elements:
                    logger.info(f"✅ 找到規格區域: {selector}")
                    
                    for element in elements:
                        text = await element.inner_text()
                        if text and len(text.strip()) > 30:
                            specs_text += text.strip() + "\n\n"
                    
                    if specs_text:
                        break
                        
            except Exception as e:
                logger.debug(f"規格選擇器 {selector} 失敗: {e}")
                continue
        
        return specs_text

    def clean_overview_text(self, text: str) -> str:
        """清理和格式化概覽文字"""
        if not text:
            return ""
        
        # 移除多餘的空白和換行
        text = re.sub(r'\n\s*\n', '\n', text)
        text = re.sub(r'\s+', ' ', text)
        
        # 移除不需要的內容
        unwanted_patterns = [
            r'加入購物車.*',
            r'立即購買.*',
            r'選擇.*',
            r'Cookie.*',
            r'隱私權.*',
            r'使用條款.*',
            r'©.*Apple.*',
            r'台灣.*'
        ]
        
        for pattern in unwanted_patterns:
            text = re.sub(pattern, '', text, flags=re.IGNORECASE)
        
        # 限制長度
        if len(text) > 1000:
            text = text[:1000] + "..."
        
        return text.strip()

    async def scrape_category_with_details(self, category: str, limit: int = 5) -> List[Dict]:
        """爬取指定類別的產品並提取詳細概覽"""
        logger.info(f"🚀 開始爬取 {category.upper()} 類別的詳細資訊...")
        
        products = []
        
        async with async_playwright() as p:
            browser = await p.chromium.launch(
                headless=False,
                args=[
                    '--no-sandbox',
                    '--disable-blink-features=AutomationControlled',
                    '--disable-web-security'
                ]
            )
            
            context = await self.setup_browser_context(browser)
            page = await context.new_page()
            
            try:
                # 訪問類別頁面
                category_url = self.categories.get(category)
                if not category_url:
                    logger.error(f"❌ 未知類別: {category}")
                    return products
                
                logger.info(f"📱 訪問類別頁面: {category_url}")
                await page.goto(category_url, wait_until='networkidle', timeout=60000)
                await asyncio.sleep(3)
                
                # 尋找產品連結
                product_selectors = [
                    'a[href*="/product/"]',
                    '.rf-serp-productcard a',
                    '.rf-serp-productcard-link',
                    '[data-testid="product-tile"] a'
                ]
                
                product_links = []
                
                for selector in product_selectors:
                    try:
                        elements = await page.query_selector_all(selector)
                        if elements:
                            logger.info(f"✅ 找到 {len(elements)} 個產品連結 (選擇器: {selector})")
                            
                            for element in elements[:limit]:  # 限制數量
                                href = await element.get_attribute('href')
                                if href and '/product/' in href:
                                    if not href.startswith('http'):
                                        href = 'https://www.apple.com' + href
                                    product_links.append(href)
                            
                            break
                            
                    except Exception as e:
                        logger.debug(f"產品連結選擇器 {selector} 失敗: {e}")
                        continue
                
                if not product_links:
                    logger.warning(f"⚠️ 未找到 {category} 類別的產品連結")
                    return products
                
                logger.info(f"🔗 找到 {len(product_links)} 個產品連結")
                
                # 提取每個產品的詳細資訊
                for i, product_url in enumerate(product_links, 1):
                    try:
                        logger.info(f"📦 處理產品 {i}/{len(product_links)}")
                        
                        # 提取基本產品資訊
                        product_info = await self.extract_basic_product_info(page, product_url)
                        
                        # 提取詳細概覽
                        detailed_overview = await self.extract_product_overview(page, product_url)
                        
                        if product_info:
                            product_info['產品概覽'] = detailed_overview or product_info.get('產品標題', '')
                            product_info['category'] = category
                            product_info['序號'] = i
                            products.append(product_info)
                            
                            logger.info(f"✅ 成功處理產品: {product_info.get('產品標題', '')[:50]}...")
                        
                        # 避免被封鎖
                        await asyncio.sleep(2)
                        
                    except Exception as e:
                        logger.error(f"❌ 處理產品失敗 {product_url}: {e}")
                        continue
                
            except Exception as e:
                logger.error(f"❌ 爬取類別 {category} 失敗: {e}")
            finally:
                await page.close()
                await context.close()
                await browser.close()
        
        logger.info(f"🎉 {category.upper()} 類別爬取完成，共 {len(products)} 個產品")
        return products

    async def extract_basic_product_info(self, page, product_url: str) -> Optional[Dict]:
        """提取基本產品資訊"""
        try:
            await page.goto(product_url, wait_until='networkidle', timeout=30000)
            await asyncio.sleep(1)
            
            # 提取產品標題
            title_selectors = [
                'h1.rf-pdp-title',
                'h1[data-autom="pdp-product-name"]',
                '.rf-pdp-title',
                'h1.pd-title',
                'h1'
            ]
            
            title = ""
            for selector in title_selectors:
                try:
                    element = await page.query_selector(selector)
                    if element:
                        title = await element.inner_text()
                        if title:
                            break
                except:
                    continue
            
            # 提取價格
            price_selectors = [
                '.rf-pdp-price',
                '.pd-price',
                '[data-autom="price"]',
                '.price'
            ]
            
            price = ""
            for selector in price_selectors:
                try:
                    element = await page.query_selector(selector)
                    if element:
                        price = await element.inner_text()
                        if 'NT$' in price:
                            break
                except:
                    continue
            
            if title:
                return {
                    '產品標題': title.strip(),
                    '產品售價': price.strip() if price else 'N/A',
                    '產品URL': product_url
                }
            
            return None
            
        except Exception as e:
            logger.error(f"❌ 提取基本產品資訊失敗: {e}")
            return None

    def save_enhanced_products(self, products: List[Dict], category: str):
        """儲存增強版產品資料"""
        if not products:
            logger.warning(f"⚠️ {category} 類別沒有產品資料可儲存")
            return
        
        try:
            # 確保 data 目錄存在
            os.makedirs('data', exist_ok=True)
            
            # 儲存到對應的檔案
            filename = f'data/apple_refurbished_{category}_enhanced.json'
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(products, f, ensure_ascii=False, indent=2)
            
            logger.info(f"💾 {category.upper()} 增強版資料已儲存到 {filename}")
            logger.info(f"📊 共儲存 {len(products)} 個產品")
            
            # 顯示範例
            if products:
                sample = products[0]
                logger.info(f"📝 範例產品概覽:")
                logger.info(f"   標題: {sample.get('產品標題', '')[:50]}...")
                logger.info(f"   概覽: {sample.get('產品概覽', '')[:100]}...")
            
        except Exception as e:
            logger.error(f"❌ 儲存產品資料失敗: {e}")

async def main():
    """主程式"""
    print("🍎 增強版 Apple 整修品爬蟲程式")
    print("專門提取產品詳細規格和概覽資訊")
    print("=" * 60)
    
    scraper = EnhancedAppleScraper()
    
    # 選擇要爬取的類別
    print("\n可用類別:")
    for i, category in enumerate(scraper.categories.keys(), 1):
        print(f"{i}. {category.upper()}")
    
    try:
        choice = input("\n請選擇類別 (輸入數字，或按 Enter 爬取 Mac): ").strip()
        
        if not choice:
            category = 'mac'
        else:
            categories = list(scraper.categories.keys())
            category = categories[int(choice) - 1]
        
        limit = input(f"\n請輸入要爬取的產品數量 (預設 5): ").strip()
        limit = int(limit) if limit.isdigit() else 5
        
        print(f"\n🚀 開始爬取 {category.upper()} 類別，限制 {limit} 個產品...")
        
        # 執行爬取
        products = await scraper.scrape_category_with_details(category, limit)
        
        if products:
            # 儲存結果
            scraper.save_enhanced_products(products, category)
            
            print(f"\n🎉 爬取完成！")
            print(f"📊 成功爬取 {len(products)} 個產品")
            print(f"💾 資料已儲存到 data/apple_refurbished_{category}_enhanced.json")
        else:
            print(f"\n❌ 未能爬取到任何產品資料")
    
    except KeyboardInterrupt:
        print("\n\n⏹️ 使用者中斷程式")
    except Exception as e:
        print(f"\n❌ 程式執行錯誤: {e}")

if __name__ == "__main__":
    asyncio.run(main()) 