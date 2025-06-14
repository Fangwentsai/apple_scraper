#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Apple 整修品價格追蹤系統
記錄每件商品每天的價格變化
"""

import json
import os
from datetime import datetime, date
import hashlib
import re
from typing import Dict, List, Optional, Tuple
import firebase_admin
from firebase_admin import credentials, firestore
from chatgpt_query import AppleRefurbishedQuery

class PriceTracker:
    def __init__(self):
        """初始化價格追蹤系統"""
        self.query_system = AppleRefurbishedQuery()
        
        # 初始化 Firebase
        try:
            if not firebase_admin._apps:
                cred = credentials.Certificate('firebase-service-account.json')
                firebase_admin.initialize_app(cred)
            self.db = firestore.client()
            print("✅ Firebase 初始化成功")
        except Exception as e:
            print(f"❌ Firebase 初始化失敗: {e}")
            self.db = None
        
        # 本地價格歷史檔案
        self.price_history_dir = "price_history"
        if not os.path.exists(self.price_history_dir):
            os.makedirs(self.price_history_dir)
    
    def generate_product_id(self, product: Dict) -> str:
        """為產品生成唯一ID"""
        title = product.get('產品標題', '')
        # 移除價格和日期相關資訊，只保留核心產品資訊
        clean_title = re.sub(r'\(整修品\)', '', title)
        clean_title = re.sub(r'NT\$[\d,]+', '', clean_title)
        clean_title = clean_title.strip()
        
        # 使用 MD5 生成短 ID
        product_hash = hashlib.md5(clean_title.encode('utf-8')).hexdigest()[:12]
        return f"{product.get('category', 'unknown')}_{product_hash}"
    
    def extract_price_number(self, price_str: str) -> Optional[int]:
        """從價格字串中提取數字"""
        if not price_str:
            return None
        
        price_match = re.search(r'NT\$?([\d,]+)', price_str)
        if price_match:
            return int(price_match.group(1).replace(',', ''))
        return None
    
    def track_daily_prices(self) -> Dict:
        """追蹤今日所有產品價格"""
        today = date.today().isoformat()
        print(f"🔍 開始追蹤 {today} 的產品價格...")
        
        tracking_result = {
            'date': today,
            'timestamp': datetime.now().isoformat(),
            'categories': {},
            'total_products': 0,
            'price_changes': [],
            'new_products': [],
            'discontinued_products': []
        }
        
        # 載入昨日價格資料（如果存在）
        yesterday_prices = self.load_yesterday_prices()
        
        # 追蹤每個類別的產品
        for category in self.query_system.categories.keys():
            print(f"📱 追蹤 {category.upper()} 類別...")
            
            products = self.query_system.search_by_category(category)
            category_data = {
                'product_count': len(products),
                'products': []
            }
            
            for product in products:
                product_id = self.generate_product_id(product)
                current_price = self.extract_price_number(product.get('產品售價', ''))
                
                product_data = {
                    'product_id': product_id,
                    'title': product.get('產品標題', ''),
                    'price': current_price,
                    'price_str': product.get('產品售價', ''),
                    'url': product.get('產品URL', ''),
                    'category': category
                }
                
                category_data['products'].append(product_data)
                
                # 檢查價格變化
                if product_id in yesterday_prices:
                    yesterday_price = yesterday_prices[product_id]['price']
                    if current_price and yesterday_price and current_price != yesterday_price:
                        price_change = {
                            'product_id': product_id,
                            'title': product.get('產品標題', ''),
                            'category': category,
                            'old_price': yesterday_price,
                            'new_price': current_price,
                            'change_amount': current_price - yesterday_price,
                            'change_percentage': round(((current_price - yesterday_price) / yesterday_price) * 100, 2)
                        }
                        tracking_result['price_changes'].append(price_change)
                        print(f"💰 價格變化: {product.get('產品標題', '')[:30]}... {yesterday_price} → {current_price}")
                else:
                    # 新產品
                    tracking_result['new_products'].append(product_data)
                    print(f"🆕 新產品: {product.get('產品標題', '')[:30]}...")
            
            tracking_result['categories'][category] = category_data
            tracking_result['total_products'] += len(products)
        
        # 檢查停產產品
        for product_id, yesterday_product in yesterday_prices.items():
            if not any(product_id == p['product_id'] 
                      for cat_data in tracking_result['categories'].values() 
                      for p in cat_data['products']):
                tracking_result['discontinued_products'].append(yesterday_product)
                print(f"❌ 停產產品: {yesterday_product.get('title', '')[:30]}...")
        
        # 儲存追蹤結果
        self.save_daily_tracking(tracking_result)
        
        # 儲存到 Firebase
        if self.db:
            self.save_to_firebase(tracking_result)
        
        print(f"✅ 價格追蹤完成！")
        print(f"   總產品數: {tracking_result['total_products']}")
        print(f"   價格變化: {len(tracking_result['price_changes'])} 個")
        print(f"   新產品: {len(tracking_result['new_products'])} 個")
        print(f"   停產產品: {len(tracking_result['discontinued_products'])} 個")
        
        return tracking_result
    
    def load_yesterday_prices(self) -> Dict:
        """載入昨日價格資料"""
        try:
            # 嘗試載入最近的價格資料
            files = [f for f in os.listdir(self.price_history_dir) if f.endswith('.json')]
            if not files:
                return {}
            
            # 取得最新的檔案
            latest_file = sorted(files)[-1]
            filepath = os.path.join(self.price_history_dir, latest_file)
            
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # 轉換為 product_id -> product_data 的格式
            yesterday_prices = {}
            for category_data in data.get('categories', {}).values():
                for product in category_data.get('products', []):
                    yesterday_prices[product['product_id']] = product
            
            print(f"📊 載入昨日價格資料: {len(yesterday_prices)} 個產品")
            return yesterday_prices
            
        except Exception as e:
            print(f"⚠️ 載入昨日價格資料失敗: {e}")
            return {}
    
    def save_daily_tracking(self, tracking_data: Dict):
        """儲存每日追蹤資料到本地檔案"""
        try:
            filename = f"price_tracking_{tracking_data['date']}.json"
            filepath = os.path.join(self.price_history_dir, filename)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(tracking_data, f, ensure_ascii=False, indent=2)
            
            print(f"💾 已儲存價格追蹤資料: {filepath}")
            
        except Exception as e:
            print(f"❌ 儲存價格追蹤資料失敗: {e}")
    
    def save_to_firebase(self, tracking_data: Dict):
        """儲存追蹤資料到 Firebase"""
        try:
            # 儲存到 price_tracking collection
            doc_ref = self.db.collection('price_tracking').document(tracking_data['date'])
            doc_ref.set(tracking_data)
            
            # 如果有價格變化，也儲存到 price_changes collection
            if tracking_data['price_changes']:
                for change in tracking_data['price_changes']:
                    change_doc = {
                        **change,
                        'date': tracking_data['date'],
                        'timestamp': tracking_data['timestamp']
                    }
                    self.db.collection('price_changes').add(change_doc)
            
            print(f"☁️ 已備份價格追蹤資料到 Firebase")
            
        except Exception as e:
            print(f"❌ Firebase 備份失敗: {e}")
    
    def get_product_price_history(self, product_id: str, days: int = 30) -> List[Dict]:
        """取得特定產品的價格歷史"""
        price_history = []
        
        try:
            # 從本地檔案讀取
            files = [f for f in os.listdir(self.price_history_dir) if f.endswith('.json')]
            files = sorted(files)[-days:]  # 取最近N天
            
            for filename in files:
                filepath = os.path.join(self.price_history_dir, filename)
                with open(filepath, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # 尋找指定產品
                for category_data in data.get('categories', {}).values():
                    for product in category_data.get('products', []):
                        if product['product_id'] == product_id:
                            price_history.append({
                                'date': data['date'],
                                'price': product['price'],
                                'price_str': product['price_str']
                            })
                            break
            
            return price_history
            
        except Exception as e:
            print(f"❌ 取得價格歷史失敗: {e}")
            return []
    
    def get_price_changes_summary(self, days: int = 7) -> Dict:
        """取得最近N天的價格變化摘要"""
        try:
            files = [f for f in os.listdir(self.price_history_dir) if f.endswith('.json')]
            files = sorted(files)[-days:]
            
            all_changes = []
            total_products = 0
            
            for filename in files:
                filepath = os.path.join(self.price_history_dir, filename)
                with open(filepath, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                all_changes.extend(data.get('price_changes', []))
                total_products = max(total_products, data.get('total_products', 0))
            
            # 統計分析
            price_drops = [c for c in all_changes if c['change_amount'] < 0]
            price_increases = [c for c in all_changes if c['change_amount'] > 0]
            
            summary = {
                'period_days': days,
                'total_changes': len(all_changes),
                'price_drops': len(price_drops),
                'price_increases': len(price_increases),
                'avg_drop_amount': sum(c['change_amount'] for c in price_drops) / len(price_drops) if price_drops else 0,
                'avg_increase_amount': sum(c['change_amount'] for c in price_increases) / len(price_increases) if price_increases else 0,
                'biggest_drop': min(all_changes, key=lambda x: x['change_amount']) if all_changes else None,
                'biggest_increase': max(all_changes, key=lambda x: x['change_amount']) if all_changes else None,
                'most_volatile_products': self.get_most_volatile_products(all_changes)
            }
            
            return summary
            
        except Exception as e:
            print(f"❌ 取得價格變化摘要失敗: {e}")
            return {}
    
    def get_most_volatile_products(self, changes: List[Dict], top_n: int = 5) -> List[Dict]:
        """取得價格變化最頻繁的產品"""
        product_changes = {}
        
        for change in changes:
            product_id = change['product_id']
            if product_id not in product_changes:
                product_changes[product_id] = {
                    'product_id': product_id,
                    'title': change['title'],
                    'category': change['category'],
                    'change_count': 0,
                    'total_change': 0
                }
            
            product_changes[product_id]['change_count'] += 1
            product_changes[product_id]['total_change'] += abs(change['change_amount'])
        
        # 按變化次數排序
        volatile_products = sorted(
            product_changes.values(),
            key=lambda x: x['change_count'],
            reverse=True
        )
        
        return volatile_products[:top_n]
    
    def generate_price_report(self, days: int = 7) -> str:
        """生成價格追蹤報告"""
        summary = self.get_price_changes_summary(days)
        
        if not summary:
            return "❌ 無法生成價格報告"
        
        report = f"""
📊 Apple 整修品價格追蹤報告 ({days} 天)
{'=' * 50}

📈 總體統計:
• 總價格變化次數: {summary['total_changes']}
• 降價次數: {summary['price_drops']}
• 漲價次數: {summary['price_increases']}

💰 價格變化分析:
• 平均降價金額: NT${abs(summary['avg_drop_amount']):,.0f}
• 平均漲價金額: NT${summary['avg_increase_amount']:,.0f}

🏆 極值記錄:"""
        
        if summary['biggest_drop']:
            drop = summary['biggest_drop']
            report += f"""
• 最大降價: {drop['title'][:40]}...
  降價 NT${abs(drop['change_amount']):,} ({drop['change_percentage']:.1f}%)"""
        
        if summary['biggest_increase']:
            increase = summary['biggest_increase']
            report += f"""
• 最大漲價: {increase['title'][:40]}...
  漲價 NT${increase['change_amount']:,} ({increase['change_percentage']:.1f}%)"""
        
        if summary['most_volatile_products']:
            report += f"""

🔄 價格變化最頻繁的產品:"""
            for i, product in enumerate(summary['most_volatile_products'], 1):
                report += f"""
{i}. {product['title'][:40]}...
   變化次數: {product['change_count']} 次, 總變化金額: NT${product['total_change']:,}"""
        
        return report

def main():
    """主程式"""
    tracker = PriceTracker()
    
    print("🍎 Apple 整修品價格追蹤系統")
    print("=" * 50)
    
    while True:
        print("\n請選擇功能:")
        print("1. 執行今日價格追蹤")
        print("2. 查看產品價格歷史")
        print("3. 生成價格變化報告")
        print("4. 查看價格變化摘要")
        print("0. 退出")
        
        choice = input("\n請輸入選項 (0-4): ").strip()
        
        if choice == '0':
            print("👋 感謝使用！")
            break
        elif choice == '1':
            tracker.track_daily_prices()
        elif choice == '2':
            product_id = input("請輸入產品ID: ").strip()
            days = int(input("請輸入查詢天數 (預設30): ").strip() or "30")
            history = tracker.get_product_price_history(product_id, days)
            
            if history:
                print(f"\n📊 產品價格歷史 ({len(history)} 天):")
                for record in history:
                    print(f"  {record['date']}: {record['price_str']}")
            else:
                print("❌ 找不到該產品的價格歷史")
        elif choice == '3':
            days = int(input("請輸入報告天數 (預設7): ").strip() or "7")
            report = tracker.generate_price_report(days)
            print(report)
        elif choice == '4':
            days = int(input("請輸入查詢天數 (預設7): ").strip() or "7")
            summary = tracker.get_price_changes_summary(days)
            
            if summary:
                print(f"\n📊 價格變化摘要 ({days} 天):")
                print(f"總變化次數: {summary['total_changes']}")
                print(f"降價次數: {summary['price_drops']}")
                print(f"漲價次數: {summary['price_increases']}")
            else:
                print("❌ 無法取得價格變化摘要")
        else:
            print("❌ 無效選項，請重新選擇")

if __name__ == "__main__":
    main() 