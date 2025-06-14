#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
簡化版概覽測試工具
模擬從 Apple 產品頁面提取詳細概覽的過程
"""

import json
import requests
from bs4 import BeautifulSoup
import re
import time
from typing import Dict, List, Optional

class SimpleOverviewExtractor:
    def __init__(self):
        """初始化簡化版概覽提取器"""
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

    def extract_overview_from_url(self, product_url: str) -> str:
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

    def test_single_product(self, product: Dict) -> Dict:
        """測試單一產品的概覽提取"""
        print(f"\n📦 測試產品: {product.get('產品標題', '')[:50]}...")
        
        product_url = product.get('產品URL', '')
        if not product_url:
            print("⚠️ 產品沒有 URL")
            return product
        
        # 提取詳細概覽
        detailed_overview = self.extract_overview_from_url(product_url)
        
        # 更新產品資料
        updated_product = product.copy()
        if detailed_overview:
            updated_product['產品概覽'] = detailed_overview
            print(f"✅ 概覽更新成功")
        else:
            print(f"⚠️ 概覽提取失敗，保持原有內容")
        
        return updated_product

    def load_sample_products(self, limit: int = 3) -> List[Dict]:
        """載入範例產品"""
        try:
            with open('data/apple_refurbished_mac.json', 'r', encoding='utf-8') as f:
                products = json.load(f)
            
            # 只取前幾個產品進行測試
            sample_products = products[:limit]
            print(f"📂 載入 {len(sample_products)} 個範例產品")
            return sample_products
            
        except Exception as e:
            print(f"❌ 載入產品資料失敗: {e}")
            return []

def main():
    """主測試程式"""
    print("🧪 簡化版 Apple 產品概覽提取測試")
    print("=" * 60)
    
    extractor = SimpleOverviewExtractor()
    
    # 載入範例產品
    sample_products = extractor.load_sample_products(limit=3)
    
    if not sample_products:
        print("❌ 無法載入測試產品")
        return
    
    updated_products = []
    
    for i, product in enumerate(sample_products, 1):
        print(f"\n{'='*60}")
        print(f"測試產品 {i}/{len(sample_products)}")
        print(f"{'='*60}")
        
        # 顯示原始資料
        print(f"📝 原始概覽:")
        print(f"   {product.get('產品概覽', 'N/A')}")
        
        # 測試概覽提取
        updated_product = extractor.test_single_product(product)
        updated_products.append(updated_product)
        
        # 顯示更新後的概覽
        new_overview = updated_product.get('產品概覽', '')
        if new_overview != product.get('產品概覽', ''):
            print(f"\n📝 更新後概覽:")
            if len(new_overview) > 200:
                print(f"   {new_overview[:200]}...")
            else:
                print(f"   {new_overview}")
        
        # 避免請求過於頻繁
        if i < len(sample_products):
            print(f"\n⏳ 等待 3 秒...")
            time.sleep(3)
    
    # 儲存測試結果
    try:
        with open('data/simple_overview_test_result.json', 'w', encoding='utf-8') as f:
            json.dump(updated_products, f, ensure_ascii=False, indent=2)
        
        print(f"\n💾 測試結果已儲存到 data/simple_overview_test_result.json")
        
        # 統計結果
        improved_count = 0
        for original, updated in zip(sample_products, updated_products):
            if len(updated.get('產品概覽', '')) > len(original.get('產品概覽', '')):
                improved_count += 1
        
        print(f"\n📊 測試統計:")
        print(f"   總測試產品: {len(sample_products)}")
        print(f"   概覽改善: {improved_count}")
        print(f"   改善率: {improved_count/len(sample_products)*100:.1f}%")
        
    except Exception as e:
        print(f"❌ 儲存測試結果失敗: {e}")

if __name__ == "__main__":
    main() 