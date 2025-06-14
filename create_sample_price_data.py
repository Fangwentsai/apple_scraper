#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
建立範例價格歷史資料
用於測試價格追蹤和分析系統
"""

import json
import os
from datetime import datetime, date, timedelta
import random
from chatgpt_query import AppleRefurbishedQuery

def create_sample_price_history():
    """建立範例價格歷史資料"""
    
    # 建立價格歷史目錄
    price_history_dir = "price_history"
    if not os.path.exists(price_history_dir):
        os.makedirs(price_history_dir)
    
    # 載入現有產品資料
    query_system = AppleRefurbishedQuery()
    all_products = []
    
    for category in query_system.categories.keys():
        products = query_system.search_by_category(category)
        for product in products:
            all_products.append({
                'product_id': f"{category}_{hash(product.get('產品標題', ''))%10000:04d}",
                'title': product.get('產品標題', ''),
                'category': category,
                'base_price': int(product.get('產品售價', 'NT$0').replace('NT$', '').replace(',', '') or 0),
                'url': product.get('產品URL', '')
            })
    
    print(f"📦 載入 {len(all_products)} 個產品")
    
    # 生成過去30天的價格資料
    for i in range(30, 0, -1):
        target_date = date.today() - timedelta(days=i)
        
        tracking_data = {
            'date': target_date.isoformat(),
            'timestamp': datetime.combine(target_date, datetime.min.time()).isoformat(),
            'categories': {},
            'total_products': len(all_products),
            'price_changes': [],
            'new_products': [],
            'discontinued_products': []
        }
        
        # 按類別組織產品
        categories_data = {}
        for product in all_products:
            category = product['category']
            if category not in categories_data:
                categories_data[category] = {
                    'product_count': 0,
                    'products': []
                }
            
            # 模擬價格變化
            base_price = product['base_price']
            if base_price > 0:
                # 隨機價格變化 (-10% 到 +5%)
                price_variation = random.uniform(-0.10, 0.05)
                current_price = int(base_price * (1 + price_variation))
                
                # 確保價格合理
                current_price = max(current_price, int(base_price * 0.8))
                current_price = min(current_price, int(base_price * 1.2))
            else:
                current_price = base_price
            
            product_data = {
                'product_id': product['product_id'],
                'title': product['title'],
                'price': current_price,
                'price_str': f"NT${current_price:,}" if current_price > 0 else "NT$0",
                'url': product['url'],
                'category': category
            }
            
            categories_data[category]['products'].append(product_data)
            categories_data[category]['product_count'] += 1
        
        tracking_data['categories'] = categories_data
        
        # 儲存資料
        filename = f"price_tracking_{target_date.isoformat()}.json"
        filepath = os.path.join(price_history_dir, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(tracking_data, f, ensure_ascii=False, indent=2)
        
        print(f"✅ 已建立 {target_date} 的價格資料")
    
    print(f"🎉 完成！已建立30天的範例價格歷史資料")

def create_price_changes_sample():
    """建立包含價格變化的範例資料"""
    
    price_history_dir = "price_history"
    
    # 讀取最新的資料檔案
    files = [f for f in os.listdir(price_history_dir) if f.endswith('.json')]
    if not files:
        print("❌ 沒有找到價格歷史檔案")
        return
    
    latest_file = sorted(files)[-1]
    filepath = os.path.join(price_history_dir, latest_file)
    
    with open(filepath, 'r', encoding='utf-8') as f:
        latest_data = json.load(f)
    
    # 建立今天的資料，包含一些價格變化
    today = date.today()
    today_data = {
        'date': today.isoformat(),
        'timestamp': datetime.now().isoformat(),
        'categories': {},
        'total_products': latest_data['total_products'],
        'price_changes': [],
        'new_products': [],
        'discontinued_products': []
    }
    
    # 複製並修改產品資料
    for category, category_data in latest_data['categories'].items():
        new_category_data = {
            'product_count': category_data['product_count'],
            'products': []
        }
        
        for product in category_data['products']:
            new_product = product.copy()
            
            # 隨機選擇一些產品進行價格變化
            if random.random() < 0.2:  # 20% 機率價格變化
                old_price = product['price']
                if old_price > 0:
                    # 隨機降價或漲價
                    if random.random() < 0.7:  # 70% 機率降價
                        change_percent = random.uniform(-0.15, -0.05)  # 降價5-15%
                    else:
                        change_percent = random.uniform(0.05, 0.10)   # 漲價5-10%
                    
                    new_price = int(old_price * (1 + change_percent))
                    new_product['price'] = new_price
                    new_product['price_str'] = f"NT${new_price:,}"
                    
                    # 記錄價格變化
                    price_change = {
                        'product_id': product['product_id'],
                        'title': product['title'],
                        'category': category,
                        'old_price': old_price,
                        'new_price': new_price,
                        'change_amount': new_price - old_price,
                        'change_percentage': round(change_percent * 100, 2)
                    }
                    today_data['price_changes'].append(price_change)
            
            new_category_data['products'].append(new_product)
        
        today_data['categories'][category] = new_category_data
    
    # 儲存今天的資料
    filename = f"price_tracking_{today.isoformat()}.json"
    filepath = os.path.join(price_history_dir, filename)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(today_data, f, ensure_ascii=False, indent=2)
    
    print(f"✅ 已建立今天的價格資料，包含 {len(today_data['price_changes'])} 個價格變化")

def main():
    """主程式"""
    print("🔧 建立範例價格歷史資料")
    print("=" * 50)
    
    print("1. 建立基礎價格歷史資料（30天）...")
    create_sample_price_history()
    
    print("\n2. 建立包含價格變化的今日資料...")
    create_price_changes_sample()
    
    print("\n🎉 範例資料建立完成！")
    print("現在可以測試價格追蹤和分析功能了。")

if __name__ == "__main__":
    main() 