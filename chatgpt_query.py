#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Apple 整修品查詢介面 - 專為 ChatGPT 設計
提供結構化的產品查詢功能
"""

import json
import os
from typing import List, Dict, Any, Optional
import re

class AppleRefurbishedQuery:
    def __init__(self, data_dir: str = "data"):
        """初始化查詢系統"""
        self.data_dir = data_dir
        self.categories = {
            'mac': 'apple_refurbished_mac.json',
            'ipad': 'apple_refurbished_ipad.json',
            'airpods': 'apple_refurbished_airpods.json',
            'homepod': 'apple_refurbished_homepod.json',
            'accessories': 'apple_refurbished_accessories.json',
            'iphone': 'apple_refurbished_iphone.json',
            'appletv': 'apple_refurbished_appletv.json'
        }
        self.all_products = []
        self.load_all_data()
    
    def load_all_data(self):
        """載入所有產品資料"""
        self.all_products = []
        
        for category, filename in self.categories.items():
            filepath = os.path.join(self.data_dir, filename)
            if os.path.exists(filepath):
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        if isinstance(data, list) and data:
                            for product in data:
                                product['category'] = category
                                self.all_products.append(product)
                except Exception as e:
                    print(f"載入 {filename} 時發生錯誤: {e}")
        
        print(f"✅ 成功載入 {len(self.all_products)} 個產品")
    
    def get_summary(self) -> Dict[str, Any]:
        """取得產品總覽"""
        summary = {
            'total_products': len(self.all_products),
            'categories': {},
            'price_range': {'min': float('inf'), 'max': 0}
        }
        
        for product in self.all_products:
            category = product.get('category', 'unknown')
            if category not in summary['categories']:
                summary['categories'][category] = 0
            summary['categories'][category] += 1
            
            # 提取價格
            price = self.extract_price(product.get('產品售價', ''))
            if price:
                summary['price_range']['min'] = min(summary['price_range']['min'], price)
                summary['price_range']['max'] = max(summary['price_range']['max'], price)
        
        if summary['price_range']['min'] == float('inf'):
            summary['price_range']['min'] = 0
        
        return summary
    
    def extract_price(self, price_str: str) -> Optional[int]:
        """從價格字串中提取數字"""
        if not price_str:
            return None
        
        # 移除 NT$ 和逗號，提取數字
        price_match = re.search(r'NT\$?([\d,]+)', price_str)
        if price_match:
            return int(price_match.group(1).replace(',', ''))
        return None
    
    def search_by_category(self, category: str) -> List[Dict[str, Any]]:
        """按類別搜尋產品"""
        category = category.lower()
        return [p for p in self.all_products if p.get('category') == category]
    
    def search_by_keyword(self, keyword: str) -> List[Dict[str, Any]]:
        """按關鍵字搜尋產品"""
        keyword = keyword.lower()
        results = []
        
        for product in self.all_products:
            title = product.get('產品標題', '').lower()
            overview = product.get('產品概覽', '').lower()
            
            if keyword in title or keyword in overview:
                results.append(product)
        
        return results
    
    def search_by_price_range(self, min_price: int, max_price: int) -> List[Dict[str, Any]]:
        """按價格範圍搜尋產品"""
        results = []
        
        for product in self.all_products:
            price = self.extract_price(product.get('產品售價', ''))
            if price and min_price <= price <= max_price:
                results.append(product)
        
        return results
    
    def get_cheapest_products(self, limit: int = 5) -> List[Dict[str, Any]]:
        """取得最便宜的產品"""
        products_with_price = []
        
        for product in self.all_products:
            price = self.extract_price(product.get('產品售價', ''))
            if price:
                product_copy = product.copy()
                product_copy['price_numeric'] = price
                products_with_price.append(product_copy)
        
        products_with_price.sort(key=lambda x: x['price_numeric'])
        return products_with_price[:limit]
    
    def get_most_expensive_products(self, limit: int = 5) -> List[Dict[str, Any]]:
        """取得最昂貴的產品"""
        products_with_price = []
        
        for product in self.all_products:
            price = self.extract_price(product.get('產品售價', ''))
            if price:
                product_copy = product.copy()
                product_copy['price_numeric'] = price
                products_with_price.append(product_copy)
        
        products_with_price.sort(key=lambda x: x['price_numeric'], reverse=True)
        return products_with_price[:limit]
    
    def format_products_for_chatgpt(self, products: List[Dict[str, Any]]) -> str:
        """格式化產品資料供 ChatGPT 使用"""
        if not products:
            return "沒有找到符合條件的產品。"
        
        formatted = f"找到 {len(products)} 個產品：\n\n"
        
        for i, product in enumerate(products, 1):
            formatted += f"【產品 {i}】\n"
            formatted += f"標題：{product.get('產品標題', 'N/A')}\n"
            formatted += f"價格：{product.get('產品售價', 'N/A')}\n"
            formatted += f"類別：{product.get('category', 'N/A').upper()}\n"
            if product.get('產品URL'):
                formatted += f"連結：{product.get('產品URL')}\n"
            formatted += "\n"
        
        return formatted
    
    def interactive_query(self):
        """互動式查詢介面"""
        print("🍎 Apple 整修品查詢系統")
        print("=" * 50)
        
        # 顯示總覽
        summary = self.get_summary()
        print(f"📊 總產品數：{summary['total_products']}")
        print("📂 各類別產品數：")
        for category, count in summary['categories'].items():
            print(f"   {category.upper()}: {count} 個")
        print(f"💰 價格範圍：NT${summary['price_range']['min']:,} - NT${summary['price_range']['max']:,}")
        print()
        
        while True:
            print("請選擇查詢方式：")
            print("1. 按類別查詢")
            print("2. 按關鍵字查詢")
            print("3. 按價格範圍查詢")
            print("4. 最便宜產品")
            print("5. 最昂貴產品")
            print("6. 顯示所有產品")
            print("0. 退出")
            
            choice = input("\n請輸入選項 (0-6): ").strip()
            
            if choice == '0':
                print("👋 感謝使用！")
                break
            elif choice == '1':
                print("\n可用類別：", ', '.join(self.categories.keys()))
                category = input("請輸入類別名稱: ").strip()
                results = self.search_by_category(category)
                print("\n" + self.format_products_for_chatgpt(results))
            elif choice == '2':
                keyword = input("請輸入關鍵字: ").strip()
                results = self.search_by_keyword(keyword)
                print("\n" + self.format_products_for_chatgpt(results))
            elif choice == '3':
                try:
                    min_price = int(input("請輸入最低價格: ").strip())
                    max_price = int(input("請輸入最高價格: ").strip())
                    results = self.search_by_price_range(min_price, max_price)
                    print("\n" + self.format_products_for_chatgpt(results))
                except ValueError:
                    print("❌ 請輸入有效的數字")
            elif choice == '4':
                results = self.get_cheapest_products()
                print("\n" + self.format_products_for_chatgpt(results))
            elif choice == '5':
                results = self.get_most_expensive_products()
                print("\n" + self.format_products_for_chatgpt(results))
            elif choice == '6':
                print("\n" + self.format_products_for_chatgpt(self.all_products))
            else:
                print("❌ 無效選項，請重新選擇")
            
            input("\n按 Enter 繼續...")
            print("\n" + "="*50)

def main():
    """主程式"""
    query_system = AppleRefurbishedQuery()
    
    # 如果是直接執行，啟動互動式介面
    if __name__ == "__main__":
        query_system.interactive_query()
    
    return query_system

if __name__ == "__main__":
    main() 