#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
產品概覽更新工具
將現有產品資料的概覽欄位從簡單標題更新為詳細規格
"""

import asyncio
import json
import os
import re
from datetime import datetime
from playwright.async_api import async_playwright
import logging
from typing import Dict, List, Optional

# 設定日誌
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ProductOverviewUpdater:
    def __init__(self):
        """初始化概覽更新器"""
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

    async def extract_detailed_overview(self, page, product_url: str) -> str:
        """從產品頁面提取詳細概覽"""
        try:
            logger.info(f"🔍 提取詳細概覽: {product_url}")
            
            # 訪問產品頁面
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
                '.rf-pdp-overview',
                '.rf-pdp-highlights',
                '.rf-pdp-techspecs'
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
                            if text and len(text.strip()) > 50:
                                overview_text += text.strip() + "\n\n"
                        
                        if overview_text:
                            break
                            
                except Exception as e:
                    logger.debug(f"選擇器 {selector} 失敗: {e}")
                    continue
            
            # 如果沒有找到概覽，嘗試提取產品特色和規格
            if not overview_text:
                logger.info("🔄 嘗試提取產品特色和規格...")
                overview_text = await self.extract_product_features(page)
            
            # 清理和格式化文字
            if overview_text:
                overview_text = self.clean_overview_text(overview_text)
                logger.info(f"✅ 成功提取概覽 ({len(overview_text)} 字元)")
                return overview_text
            else:
                logger.warning("⚠️ 未能提取到詳細概覽")
                return ""
                
        except Exception as e:
            logger.error(f"❌ 提取詳細概覽失敗: {e}")
            return ""

    async def extract_product_features(self, page) -> str:
        """提取產品特色和規格"""
        features_text = ""
        
        # 嘗試多種特色和規格選擇器
        feature_selectors = [
            '.rf-pdp-techspecs',
            '.pd-techspecs',
            '.rf-pdp-highlights',
            '.pd-highlights',
            '.rf-pdp-overview-content',
            '.pd-overview-content',
            '[data-module-template="pd/techspecs"]',
            '.rf-pdp-content',
            '.pd-features',
            '.product-features',
            '.tech-specs',
            '.product-highlights'
        ]
        
        for selector in feature_selectors:
            try:
                elements = await page.query_selector_all(selector)
                if elements:
                    logger.info(f"✅ 找到特色區域: {selector}")
                    
                    for element in elements:
                        text = await element.inner_text()
                        if text and len(text.strip()) > 30:
                            features_text += text.strip() + "\n\n"
                    
                    if features_text:
                        break
                        
            except Exception as e:
                logger.debug(f"特色選擇器 {selector} 失敗: {e}")
                continue
        
        return features_text

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
            r'台灣.*',
            r'Apple Store.*',
            r'購買.*',
            r'比較.*',
            r'瞭解更多.*'
        ]
        
        for pattern in unwanted_patterns:
            text = re.sub(pattern, '', text, flags=re.IGNORECASE)
        
        # 格式化文字，保留重要的換行
        lines = text.split('\n')
        formatted_lines = []
        
        for line in lines:
            line = line.strip()
            if line and len(line) > 5:  # 過濾太短的行
                formatted_lines.append(line)
        
        # 重新組合，限制長度
        formatted_text = '\n'.join(formatted_lines)
        
        if len(formatted_text) > 1000:
            formatted_text = formatted_text[:1000] + "..."
        
        return formatted_text.strip()

    def load_existing_products(self, category: str) -> List[Dict]:
        """載入現有的產品資料"""
        filename = f'data/apple_refurbished_{category}.json'
        
        if not os.path.exists(filename):
            logger.error(f"❌ 找不到檔案: {filename}")
            return []
        
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                products = json.load(f)
            
            logger.info(f"📂 載入 {len(products)} 個 {category.upper()} 產品")
            return products
            
        except Exception as e:
            logger.error(f"❌ 載入產品資料失敗: {e}")
            return []

    async def update_products_overview(self, category: str, limit: int = None) -> List[Dict]:
        """更新產品的概覽欄位"""
        logger.info(f"🚀 開始更新 {category.upper()} 產品概覽...")
        
        # 載入現有產品
        products = self.load_existing_products(category)
        if not products:
            return []
        
        # 限制處理數量
        if limit:
            products = products[:limit]
            logger.info(f"🔢 限制處理 {limit} 個產品")
        
        updated_products = []
        
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
                for i, product in enumerate(products, 1):
                    try:
                        logger.info(f"📦 處理產品 {i}/{len(products)}: {product.get('產品標題', '')[:50]}...")
                        
                        product_url = product.get('產品URL', '')
                        if not product_url:
                            logger.warning(f"⚠️ 產品 {i} 沒有 URL，跳過")
                            updated_products.append(product)
                            continue
                        
                        # 提取詳細概覽
                        detailed_overview = await self.extract_detailed_overview(page, product_url)
                        
                        # 更新產品資料
                        updated_product = product.copy()
                        if detailed_overview:
                            updated_product['產品概覽'] = detailed_overview
                            logger.info(f"✅ 成功更新概覽 ({len(detailed_overview)} 字元)")
                        else:
                            logger.warning(f"⚠️ 未能提取概覽，保持原有標題")
                            # 保持原有的產品標題作為概覽
                        
                        updated_products.append(updated_product)
                        
                        # 避免被封鎖
                        await asyncio.sleep(3)
                        
                    except Exception as e:
                        logger.error(f"❌ 處理產品 {i} 失敗: {e}")
                        updated_products.append(product)  # 保持原有資料
                        continue
                
            except Exception as e:
                logger.error(f"❌ 更新過程中發生錯誤: {e}")
            finally:
                await page.close()
                await context.close()
                await browser.close()
        
        logger.info(f"🎉 {category.upper()} 概覽更新完成，共處理 {len(updated_products)} 個產品")
        return updated_products

    def save_updated_products(self, products: List[Dict], category: str):
        """儲存更新後的產品資料"""
        if not products:
            logger.warning(f"⚠️ {category} 類別沒有產品資料可儲存")
            return
        
        try:
            # 備份原始檔案
            original_filename = f'data/apple_refurbished_{category}.json'
            backup_filename = f'data/apple_refurbished_{category}_backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
            
            if os.path.exists(original_filename):
                import shutil
                shutil.copy2(original_filename, backup_filename)
                logger.info(f"💾 原始檔案已備份到: {backup_filename}")
            
            # 儲存更新後的資料
            with open(original_filename, 'w', encoding='utf-8') as f:
                json.dump(products, f, ensure_ascii=False, indent=2)
            
            logger.info(f"💾 {category.upper()} 更新後資料已儲存到 {original_filename}")
            logger.info(f"📊 共儲存 {len(products)} 個產品")
            
            # 顯示範例
            if products:
                sample = products[0]
                logger.info(f"📝 範例更新後概覽:")
                logger.info(f"   標題: {sample.get('產品標題', '')[:50]}...")
                overview = sample.get('產品概覽', '')
                if len(overview) > 100:
                    logger.info(f"   概覽: {overview[:100]}...")
                else:
                    logger.info(f"   概覽: {overview}")
            
        except Exception as e:
            logger.error(f"❌ 儲存更新後產品資料失敗: {e}")

async def main():
    """主程式"""
    print("🔄 Apple 產品概覽更新工具")
    print("將產品概覽從簡單標題更新為詳細規格")
    print("=" * 60)
    
    updater = ProductOverviewUpdater()
    
    # 顯示可用類別
    categories = ['mac', 'ipad', 'iphone', 'airpods', 'homepod', 'appletv', 'accessories']
    
    print("\n可用類別:")
    for i, category in enumerate(categories, 1):
        print(f"{i}. {category.upper()}")
    
    try:
        choice = input("\n請選擇類別 (輸入數字，或按 Enter 更新 Mac): ").strip()
        
        if not choice:
            category = 'mac'
        else:
            category = categories[int(choice) - 1]
        
        limit = input(f"\n請輸入要更新的產品數量 (預設全部，輸入數字限制數量): ").strip()
        limit = int(limit) if limit.isdigit() else None
        
        print(f"\n🚀 開始更新 {category.upper()} 類別的產品概覽...")
        if limit:
            print(f"🔢 限制更新 {limit} 個產品")
        
        # 執行更新
        updated_products = await updater.update_products_overview(category, limit)
        
        if updated_products:
            # 儲存結果
            updater.save_updated_products(updated_products, category)
            
            print(f"\n🎉 更新完成！")
            print(f"📊 成功更新 {len(updated_products)} 個產品")
            print(f"💾 資料已儲存，原始檔案已備份")
        else:
            print(f"\n❌ 未能更新任何產品資料")
    
    except KeyboardInterrupt:
        print("\n\n⏹️ 使用者中斷程式")
    except Exception as e:
        print(f"\n❌ 程式執行錯誤: {e}")

if __name__ == "__main__":
    asyncio.run(main()) 