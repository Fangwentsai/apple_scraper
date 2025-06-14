#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
查價功能測試腳本
"""

import json
import os
from chatgpt_query import AppleRefurbishedQuery

def test_price_query_system():
    """測試查價系統"""
    print("🍎 測試 Apple 整修品查價系統")
    print("=" * 50)
    
    # 初始化查詢系統
    query_system = AppleRefurbishedQuery()
    
    # 測試1: 顯示總覽
    print("📊 測試1: 系統總覽")
    summary = query_system.get_summary()
    print(f"總產品數: {summary['total_products']}")
    print("各類別產品數:")
    for category, count in summary['categories'].items():
        print(f"  {category.upper()}: {count} 個")
    print(f"價格範圍: NT${summary['price_range']['min']:,} - NT${summary['price_range']['max']:,}")
    print()
    
    # 測試2: 按類別查詢
    print("📱 測試2: 按類別查詢")
    categories = ['mac', 'ipad', 'iphone', 'appletv', 'accessories']
    for category in categories:
        products = query_system.search_by_category(category)
        print(f"{category.upper()}: {len(products)} 個產品")
    print()
    
    # 測試3: 價格區間測試
    print("💰 測試3: 價格區間查詢")
    price_ranges = [
        (0, 20000, "20,000以內"),
        (20001, 50000, "50,000以內"), 
        (50001, 999999, "50,000以上")
    ]
    
    for min_price, max_price, label in price_ranges:
        products = query_system.search_by_price_range(min_price, max_price)
        print(f"{label}: {len(products)} 個產品")
        
        # 顯示前3個產品
        for i, product in enumerate(products[:3], 1):
            title = product.get('產品標題', 'N/A')[:30]
            price = product.get('產品售價', 'N/A')
            category = product.get('category', 'N/A').upper()
            print(f"  {i}. [{category}] {title}... - {price}")
        if len(products) > 3:
            print(f"  ... 還有 {len(products) - 3} 個產品")
        print()
    
    # 測試4: 模擬用戶需求解析
    print("🔍 測試4: 用戶需求解析")
    test_requirements = [
        "我想要 MacBook Air 預算30000元",
        "想買 iPad 價格25000以內",
        "需要 iPhone 預算40000",
        "想要配件 預算10000元",
        "MacBook Pro 50000元以內"
    ]
    
    for requirement in test_requirements:
        # 模擬解析邏輯
        import re
        
        # 提取價格
        price_match = re.search(r'(\d+(?:,\d+)*)', requirement)
        price = int(price_match.group(1).replace(',', '')) if price_match else None
        
        # 提取產品關鍵字
        product_keywords = ['macbook', 'mac', 'ipad', 'iphone', 'airpods', 'homepod', 'apple tv', '配件']
        product = None
        
        requirement_lower = requirement.lower()
        for keyword in product_keywords:
            if keyword in requirement_lower:
                if keyword == 'macbook' or keyword == 'mac':
                    product = 'mac'
                elif keyword == 'ipad':
                    product = 'ipad'
                elif keyword == 'iphone':
                    product = 'iphone'
                elif keyword == '配件':
                    product = 'accessories'
                else:
                    product = keyword
                break
        
        print(f"需求: {requirement}")
        print(f"解析結果: 產品={product}, 價格={price}")
        
        # 查詢符合條件的產品
        if product and price:
            category_products = query_system.search_by_category(product)
            matching_products = []
            
            for prod in category_products:
                prod_price = query_system.extract_price(prod.get('產品售價', ''))
                if prod_price and prod_price <= price:
                    matching_products.append(prod)
            
            print(f"找到 {len(matching_products)} 個符合條件的產品")
            
            # 顯示前2個產品
            for i, prod in enumerate(matching_products[:2], 1):
                title = prod.get('產品標題', 'N/A')[:40]
                prod_price = prod.get('產品售價', 'N/A')
                print(f"  {i}. {title}... - {prod_price}")
        else:
            print("❌ 解析失敗")
        print()
    
    # 測試5: 最便宜和最昂貴產品
    print("🏆 測試5: 極值產品")
    cheapest = query_system.get_cheapest_products(3)
    print("最便宜的3個產品:")
    for i, product in enumerate(cheapest, 1):
        title = product.get('產品標題', 'N/A')[:40]
        price = product.get('產品售價', 'N/A')
        category = product.get('category', 'N/A').upper()
        print(f"  {i}. [{category}] {title}... - {price}")
    
    print()
    
    expensive = query_system.get_most_expensive_products(3)
    print("最昂貴的3個產品:")
    for i, product in enumerate(expensive, 1):
        title = product.get('產品標題', 'N/A')[:40]
        price = product.get('產品售價', 'N/A')
        category = product.get('category', 'N/A').upper()
        print(f"  {i}. [{category}] {title}... - {price}")
    
    print("\n✅ 測試完成！")

def test_firebase_structure():
    """測試 Firebase 資料結構"""
    print("\n🔥 Firebase 資料結構測試")
    print("=" * 30)
    
    # 模擬用戶請求資料結構
    sample_request = {
        'userid': 'U1234567890abcdef',
        'product': 'mac',
        'price': 30000,
        'notice': False,
        'created_at': '2024-01-01T10:00:00',
        'updated_at': '2024-01-01T10:00:00'
    }
    
    print("用戶請求資料結構:")
    print(json.dumps(sample_request, indent=2, ensure_ascii=False))
    
    # 模擬通知後的資料結構
    notified_request = sample_request.copy()
    notified_request.update({
        'notice': True,
        'updated_at': '2024-01-01T11:00:00',
        'notified_products': 3
    })
    
    print("\n通知後的資料結構:")
    print(json.dumps(notified_request, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    test_price_query_system()
    test_firebase_structure() 