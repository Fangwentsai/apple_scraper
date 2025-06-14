#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
生產版本概覽更新工具
基於測試成功的方法，更新所有產品的概覽欄位
從 rc-pdsection-mainpanel 區域提取詳細產品規格
"""

import json
import requests
from bs4 import BeautifulSoup
import re
import time
import os
from datetime import datetime
from typing import Dict, List, Optional
import shutil

class ProductionOverviewUpdater:
    def __init__(self):
        """初始化生產版概覽更新器"""
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
        
        self.categories = ['mac', 'ipad', 'iphone', 'airpods', 'homepod', 'appletv', 'accessories']

    def extract_detailed_overview(self, product_url: str) -> str:
        """從產品 URL 提取詳細概覽"""
        try:
            print(f"🔍 提取概覽: {product_url[:80]}...")
            
            # 發送 HTTP 請求
            response = requests.get(product_url, headers=self.headers, timeout=30)
            response.raise_for_status()
            
            # 解析 HTML
            soup = BeautifulSoup(response.content, 'html.parser')
            
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
                    elements = soup.select(selector)
                    if elements:
                        print(f"✅ 找到概覽區域: {selector}")
                        
                        for element in elements:
                            text = element.get_text(strip=True, separator='\n')
                            if text and len(text.strip()) > 50:
                                overview_text += text.strip() + "\n\n"
                        
                        if overview_text:
                            break
                            
                except Exception as e:
                    print(f"選擇器 {selector} 失敗: {e}")
                    continue
            
            # 如果沒有找到概覽，嘗試提取產品規格
            if not overview_text:
                print("🔄 嘗試提取產品規格...")
                overview_text = self.extract_product_specs(soup)
            
            # 清理和格式化文字
            if overview_text:
                overview_text = self.clean_overview_text(overview_text)
                print(f"✅ 成功提取概覽 ({len(overview_text)} 字元)")
                return overview_text
            else:
                print("⚠️ 未能提取到詳細概覽")
                return ""
                
        except Exception as e:
            print(f"❌ 提取概覽失敗: {e}")
            return ""

    def extract_product_specs(self, soup) -> str:
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
            '.rf-pdp-content',
            '.pd-features',
            '.product-features',
            '.tech-specs',
            '.product-highlights'
        ]
        
        for selector in spec_selectors:
            try:
                elements = soup.select(selector)
                if elements:
                    print(f"✅ 找到規格區域: {selector}")
                    
                    for element in elements:
                        text = element.get_text(strip=True, separator='\n')
                        if text and len(text.strip()) > 30:
                            specs_text += text.strip() + "\n\n"
                    
                    if specs_text:
                        break
                        
            except Exception as e:
                print(f"規格選擇器 {selector} 失敗: {e}")
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
            r'台灣.*',
            r'Apple Store.*',
            r'購買.*',
            r'比較.*',
            r'瞭解更多.*',
            r'這會在新視窗開啟.*',
            r'可另外.*'
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
        
        if len(formatted_text) > 800:
            formatted_text = formatted_text[:800] + "..."
        
        return formatted_text.strip()

    def load_products(self, category: str) -> List[Dict]:
        """載入指定類別的產品"""
        filename = f'data/apple_refurbished_{category}.json'
        
        if not os.path.exists(filename):
            print(f"❌ 找不到檔案: {filename}")
            return []
        
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                products = json.load(f)
            
            print(f"📂 載入 {len(products)} 個 {category.upper()} 產品")
            return products
            
        except Exception as e:
            print(f"❌ 載入產品資料失敗: {e}")
            return []

    def backup_original_file(self, category: str) -> str:
        """備份原始檔案"""
        original_filename = f'data/apple_refurbished_{category}.json'
        backup_filename = f'data/apple_refurbished_{category}_backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
        
        try:
            if os.path.exists(original_filename):
                shutil.copy2(original_filename, backup_filename)
                print(f"💾 原始檔案已備份到: {backup_filename}")
                return backup_filename
            else:
                print(f"⚠️ 原始檔案不存在: {original_filename}")
                return ""
        except Exception as e:
            print(f"❌ 備份檔案失敗: {e}")
            return ""

    def update_category_overview(self, category: str, limit: int = None, start_from: int = 0) -> bool:
        """更新指定類別的產品概覽"""
        print(f"\n🚀 開始更新 {category.upper()} 類別的產品概覽...")
        
        # 載入產品
        products = self.load_products(category)
        if not products:
            return False
        
        # 備份原始檔案
        backup_file = self.backup_original_file(category)
        if not backup_file:
            print("⚠️ 無法備份原始檔案，繼續執行...")
        
        # 限制處理範圍
        if start_from > 0:
            products = products[start_from:]
            print(f"🔢 從第 {start_from + 1} 個產品開始處理")
        
        if limit:
            products = products[:limit]
            print(f"🔢 限制處理 {limit} 個產品")
        
        updated_products = []
        success_count = 0
        failed_count = 0
        
        for i, product in enumerate(products, start_from + 1):
            try:
                print(f"\n{'='*80}")
                print(f"處理產品 {i}/{len(products) + start_from}: {product.get('產品標題', '')[:60]}...")
                print(f"{'='*80}")
                
                product_url = product.get('產品URL', '')
                if not product_url:
                    print("⚠️ 產品沒有 URL，跳過")
                    updated_products.append(product)
                    failed_count += 1
                    continue
                
                # 提取詳細概覽
                detailed_overview = self.extract_detailed_overview(product_url)
                
                # 更新產品資料
                updated_product = product.copy()
                if detailed_overview and len(detailed_overview) > len(product.get('產品概覽', '')):
                    updated_product['產品概覽'] = detailed_overview
                    print(f"✅ 概覽更新成功 ({len(detailed_overview)} 字元)")
                    success_count += 1
                else:
                    print(f"⚠️ 概覽提取失敗或未改善，保持原有內容")
                    failed_count += 1
                
                updated_products.append(updated_product)
                
                # 避免請求過於頻繁
                if i < len(products) + start_from:
                    print(f"⏳ 等待 2 秒...")
                    time.sleep(2)
                
            except Exception as e:
                print(f"❌ 處理產品 {i} 失敗: {e}")
                updated_products.append(product)  # 保持原有資料
                failed_count += 1
                continue
        
        # 如果有 start_from，需要合併原始資料
        if start_from > 0:
            original_products = self.load_products(category)
            final_products = original_products[:start_from] + updated_products
        else:
            final_products = updated_products
        
        # 儲存更新後的資料
        success = self.save_updated_products(final_products, category)
        
        # 顯示統計
        print(f"\n📊 更新統計:")
        print(f"   總處理產品: {len(products)}")
        print(f"   成功更新: {success_count}")
        print(f"   失敗/跳過: {failed_count}")
        print(f"   成功率: {success_count/(success_count+failed_count)*100:.1f}%")
        
        return success

    def save_updated_products(self, products: List[Dict], category: str) -> bool:
        """儲存更新後的產品資料"""
        if not products:
            print(f"⚠️ {category} 類別沒有產品資料可儲存")
            return False
        
        try:
            filename = f'data/apple_refurbished_{category}.json'
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(products, f, ensure_ascii=False, indent=2)
            
            print(f"💾 {category.upper()} 更新後資料已儲存到 {filename}")
            print(f"📊 共儲存 {len(products)} 個產品")
            
            # 顯示範例
            if products:
                sample = products[0]
                print(f"📝 範例更新後概覽:")
                print(f"   標題: {sample.get('產品標題', '')[:50]}...")
                overview = sample.get('產品概覽', '')
                if len(overview) > 100:
                    print(f"   概覽: {overview[:100]}...")
                else:
                    print(f"   概覽: {overview}")
            
            return True
            
        except Exception as e:
            print(f"❌ 儲存更新後產品資料失敗: {e}")
            return False

def main():
    """主程式"""
    print("🔄 生產版 Apple 產品概覽更新工具")
    print("從 rc-pdsection-mainpanel 區域提取詳細產品規格")
    print("=" * 80)
    
    updater = ProductionOverviewUpdater()
    
    # 顯示可用類別
    print("\n可用類別:")
    for i, category in enumerate(updater.categories, 1):
        print(f"{i}. {category.upper()}")
    
    try:
        choice = input("\n請選擇類別 (輸入數字，或按 Enter 更新 Mac): ").strip()
        
        if not choice:
            category = 'mac'
        else:
            category = updater.categories[int(choice) - 1]
        
        limit = input(f"\n請輸入要更新的產品數量 (預設全部，輸入數字限制數量): ").strip()
        limit = int(limit) if limit.isdigit() else None
        
        start_from = input(f"\n請輸入開始位置 (預設從第1個開始，輸入數字指定起始位置): ").strip()
        start_from = int(start_from) - 1 if start_from.isdigit() else 0
        start_from = max(0, start_from)  # 確保不小於0
        
        print(f"\n🚀 開始更新 {category.upper()} 類別的產品概覽...")
        if limit:
            print(f"🔢 限制更新 {limit} 個產品")
        if start_from > 0:
            print(f"🔢 從第 {start_from + 1} 個產品開始")
        
        # 執行更新
        success = updater.update_category_overview(category, limit, start_from)
        
        if success:
            print(f"\n🎉 更新完成！")
            print(f"💾 資料已儲存，原始檔案已備份")
        else:
            print(f"\n❌ 更新失敗")
    
    except KeyboardInterrupt:
        print("\n\n⏹️ 使用者中斷程式")
    except Exception as e:
        print(f"\n❌ 程式執行錯誤: {e}")

if __name__ == "__main__":
    main() 