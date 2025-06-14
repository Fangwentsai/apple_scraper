#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Apple 整修品價格分析工具
提供價格趨勢分析和統計功能
"""

import json
import os
from datetime import datetime, date, timedelta
from typing import Dict, List, Optional, Tuple
import statistics
from collections import defaultdict

class PriceAnalyzer:
    def __init__(self):
        """初始化價格分析器"""
        self.price_history_dir = "price_history"
    
    def load_price_history_data(self, days: int = 30) -> List[Dict]:
        """載入指定天數的價格歷史資料"""
        try:
            if not os.path.exists(self.price_history_dir):
                print(f"❌ 價格歷史目錄不存在: {self.price_history_dir}")
                return []
            
            files = [f for f in os.listdir(self.price_history_dir) if f.endswith('.json')]
            files = sorted(files)[-days:]  # 取最近N天
            
            history_data = []
            for filename in files:
                filepath = os.path.join(self.price_history_dir, filename)
                with open(filepath, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    history_data.append(data)
            
            return history_data
            
        except Exception as e:
            print(f"❌ 載入價格歷史資料失敗: {e}")
            return []
    
    def analyze_price_trends(self, days: int = 30) -> Dict:
        """分析價格趨勢"""
        history_data = self.load_price_history_data(days)
        
        if not history_data:
            return {}
        
        # 按產品ID組織資料
        product_trends = defaultdict(list)
        
        for day_data in history_data:
            for category_data in day_data.get('categories', {}).values():
                for product in category_data.get('products', []):
                    product_id = product['product_id']
                    product_trends[product_id].append({
                        'date': day_data['date'],
                        'price': product['price'],
                        'title': product['title'],
                        'category': product['category']
                    })
        
        # 分析每個產品的趨勢
        trend_analysis = {}
        
        for product_id, price_history in product_trends.items():
            if len(price_history) < 2:
                continue
            
            prices = [p['price'] for p in price_history if p['price']]
            if not prices:
                continue
            
            # 計算趨勢統計
            first_price = prices[0]
            last_price = prices[-1]
            min_price = min(prices)
            max_price = max(prices)
            avg_price = statistics.mean(prices)
            
            # 計算價格變化
            total_change = last_price - first_price
            total_change_percent = (total_change / first_price) * 100 if first_price else 0
            
            # 計算波動性（標準差）
            volatility = statistics.stdev(prices) if len(prices) > 1 else 0
            volatility_percent = (volatility / avg_price) * 100 if avg_price else 0
            
            # 判斷趨勢方向
            if total_change_percent > 5:
                trend_direction = "上漲"
            elif total_change_percent < -5:
                trend_direction = "下跌"
            else:
                trend_direction = "穩定"
            
            trend_analysis[product_id] = {
                'title': price_history[0]['title'],
                'category': price_history[0]['category'],
                'first_price': first_price,
                'last_price': last_price,
                'min_price': min_price,
                'max_price': max_price,
                'avg_price': round(avg_price, 0),
                'total_change': total_change,
                'total_change_percent': round(total_change_percent, 2),
                'volatility': round(volatility, 0),
                'volatility_percent': round(volatility_percent, 2),
                'trend_direction': trend_direction,
                'data_points': len(prices),
                'price_history': price_history
            }
        
        return trend_analysis
    
    def get_category_statistics(self, days: int = 30) -> Dict:
        """取得各類別的價格統計"""
        history_data = self.load_price_history_data(days)
        
        if not history_data:
            return {}
        
        category_stats = {}
        
        # 取最新一天的資料
        latest_data = history_data[-1] if history_data else {}
        
        for category, category_data in latest_data.get('categories', {}).items():
            products = category_data.get('products', [])
            prices = [p['price'] for p in products if p['price']]
            
            if not prices:
                continue
            
            category_stats[category] = {
                'product_count': len(products),
                'min_price': min(prices),
                'max_price': max(prices),
                'avg_price': round(statistics.mean(prices), 0),
                'median_price': round(statistics.median(prices), 0),
                'price_range': max(prices) - min(prices),
                'std_deviation': round(statistics.stdev(prices), 0) if len(prices) > 1 else 0
            }
        
        return category_stats
    
    def find_best_deals(self, days: int = 30, top_n: int = 10) -> List[Dict]:
        """尋找最佳優惠（價格下降最多的產品）"""
        trend_analysis = self.analyze_price_trends(days)
        
        # 篩選出降價的產品
        price_drops = []
        for product_id, analysis in trend_analysis.items():
            if analysis['total_change'] < 0:  # 降價
                price_drops.append({
                    'product_id': product_id,
                    'title': analysis['title'],
                    'category': analysis['category'],
                    'price_drop': abs(analysis['total_change']),
                    'price_drop_percent': abs(analysis['total_change_percent']),
                    'current_price': analysis['last_price'],
                    'original_price': analysis['first_price']
                })
        
        # 按降價金額排序
        price_drops.sort(key=lambda x: x['price_drop'], reverse=True)
        
        return price_drops[:top_n]
    
    def generate_market_report(self, days: int = 7) -> str:
        """生成市場分析報告"""
        trend_analysis = self.analyze_price_trends(days)
        category_stats = self.get_category_statistics(days)
        best_deals = self.find_best_deals(days, 5)
        
        if not trend_analysis:
            return "❌ 無法生成市場報告，沒有足夠的價格歷史資料"
        
        report = f"""
📊 Apple 整修品市場分析報告 ({days} 天)
{'=' * 60}

📈 市場概況:
• 追蹤產品數量: {len(trend_analysis)}
• 分析期間: {days} 天
• 報告生成時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

💰 各類別價格統計:"""
        
        for category, stats in category_stats.items():
            report += f"""
• {category.upper()}:
  - 產品數量: {stats['product_count']} 個
  - 價格範圍: NT${stats['min_price']:,} - NT${stats['max_price']:,}
  - 平均價格: NT${stats['avg_price']:,}
  - 中位數價格: NT${stats['median_price']:,}"""
        
        # 趨勢分析
        upward_trends = [a for a in trend_analysis.values() if a['trend_direction'] == '上漲']
        downward_trends = [a for a in trend_analysis.values() if a['trend_direction'] == '下跌']
        stable_trends = [a for a in trend_analysis.values() if a['trend_direction'] == '穩定']
        
        report += f"""

📊 價格趨勢分析:
• 上漲產品: {len(upward_trends)} 個 ({len(upward_trends)/len(trend_analysis)*100:.1f}%)
• 下跌產品: {len(downward_trends)} 個 ({len(downward_trends)/len(trend_analysis)*100:.1f}%)
• 穩定產品: {len(stable_trends)} 個 ({len(stable_trends)/len(trend_analysis)*100:.1f}%)"""
        
        # 最佳優惠
        if best_deals:
            report += f"""

🔥 最佳優惠 (前5名):"""
            for i, deal in enumerate(best_deals[:5], 1):
                report += f"""
{i}. {deal['title'][:40]}...
   降價: NT${deal['price_drop']:,} ({deal['price_drop_percent']:.1f}%)
   現價: NT${deal['current_price']:,}"""
        
        return report

def main():
    """主程式"""
    analyzer = PriceAnalyzer()
    
    print("📊 Apple 整修品價格分析工具")
    print("=" * 50)
    
    while True:
        print("\n請選擇功能:")
        print("1. 價格趨勢分析")
        print("2. 類別價格統計")
        print("3. 最佳優惠查詢")
        print("4. 生成市場報告")
        print("0. 退出")
        
        choice = input("\n請輸入選項 (0-4): ").strip()
        
        if choice == '0':
            print("👋 感謝使用！")
            break
        elif choice == '1':
            days = int(input("請輸入分析天數 (預設30): ").strip() or "30")
            trends = analyzer.analyze_price_trends(days)
            
            if trends:
                print(f"\n📈 價格趨勢分析 ({len(trends)} 個產品):")
                for product_id, analysis in list(trends.items())[:10]:
                    print(f"• {analysis['title'][:40]}...")
                    print(f"  趨勢: {analysis['trend_direction']} ({analysis['total_change_percent']:+.1f}%)")
                    print(f"  價格: NT${analysis['first_price']:,} → NT${analysis['last_price']:,}")
                    print()
            else:
                print("❌ 沒有足夠的價格歷史資料進行分析")
        
        elif choice == '2':
            days = int(input("請輸入統計天數 (預設30): ").strip() or "30")
            stats = analyzer.get_category_statistics(days)
            
            if stats:
                print(f"\n💰 各類別價格統計:")
                for category, stat in stats.items():
                    print(f"• {category.upper()}:")
                    print(f"  產品數量: {stat['product_count']} 個")
                    print(f"  價格範圍: NT${stat['min_price']:,} - NT${stat['max_price']:,}")
                    print(f"  平均價格: NT${stat['avg_price']:,}")
                    print()
            else:
                print("❌ 沒有足夠的價格歷史資料進行統計")
        
        elif choice == '3':
            days = int(input("請輸入查詢天數 (預設30): ").strip() or "30")
            top_n = int(input("請輸入顯示數量 (預設10): ").strip() or "10")
            deals = analyzer.find_best_deals(days, top_n)
            
            if deals:
                print(f"\n🔥 最佳優惠 (前{len(deals)}名):")
                for i, deal in enumerate(deals, 1):
                    print(f"{i}. {deal['title'][:40]}...")
                    print(f"   降價: NT${deal['price_drop']:,} ({deal['price_drop_percent']:.1f}%)")
                    print(f"   現價: NT${deal['current_price']:,}")
                    print()
            else:
                print("❌ 目前沒有發現降價產品")
        
        elif choice == '4':
            days = int(input("請輸入報告天數 (預設7): ").strip() or "7")
            report = analyzer.generate_market_report(days)
            print(report)
        
        else:
            print("❌ 無效選項，請重新選擇")

if __name__ == "__main__":
    main() 