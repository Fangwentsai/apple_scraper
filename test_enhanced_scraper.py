#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
增強版爬蟲測試腳本
測試從 rc-pdsection-mainpanel 區域提取詳細產品概覽的功能
"""

import asyncio
import json
from enhanced_apple_scraper import EnhancedAppleScraper
from update_product_overview import ProductOverviewUpdater

async def test_enhanced_scraper():
    """測試增強版爬蟲"""
    print("🧪 測試增強版 Apple 爬蟲")
    print("=" * 50)
    
    scraper = EnhancedAppleScraper()
    
    # 測試爬取 Mac 類別的前 2 個產品
    print("\n🚀 測試爬取 Mac 類別 (限制 2 個產品)...")
    products = await scraper.scrape_category_with_details('mac', limit=2)
    
    if products:
        print(f"\n✅ 成功爬取 {len(products)} 個產品")
        
        for i, product in enumerate(products, 1):
            print(f"\n📦 產品 {i}:")
            print(f"   標題: {product.get('產品標題', 'N/A')}")
            print(f"   價格: {product.get('產品售價', 'N/A')}")
            print(f"   URL: {product.get('產品URL', 'N/A')[:80]}...")
            
            overview = product.get('產品概覽', '')
            if overview and len(overview) > 100:
                print(f"   概覽: {overview[:200]}...")
            else:
                print(f"   概覽: {overview}")
            print("-" * 50)
        
        # 儲存測試結果
        scraper.save_enhanced_products(products, 'mac_test')
        print(f"\n💾 測試結果已儲存到 data/apple_refurbished_mac_test_enhanced.json")
    else:
        print("\n❌ 未能爬取到任何產品")

async def test_overview_updater():
    """測試概覽更新器"""
    print("\n\n🔄 測試產品概覽更新器")
    print("=" * 50)
    
    updater = ProductOverviewUpdater()
    
    # 測試更新 Mac 類別的前 2 個產品
    print("\n🚀 測試更新 Mac 類別概覽 (限制 2 個產品)...")
    updated_products = await updater.update_products_overview('mac', limit=2)
    
    if updated_products:
        print(f"\n✅ 成功更新 {len(updated_products)} 個產品")
        
        for i, product in enumerate(updated_products, 1):
            print(f"\n📦 更新後產品 {i}:")
            print(f"   標題: {product.get('產品標題', 'N/A')}")
            print(f"   價格: {product.get('產品售價', 'N/A')}")
            
            overview = product.get('產品概覽', '')
            if overview and len(overview) > 100:
                print(f"   概覽: {overview[:200]}...")
            else:
                print(f"   概覽: {overview}")
            print("-" * 50)
        
        # 儲存測試結果
        with open('data/mac_overview_test_result.json', 'w', encoding='utf-8') as f:
            json.dump(updated_products, f, ensure_ascii=False, indent=2)
        
        print(f"\n💾 測試結果已儲存到 data/mac_overview_test_result.json")
    else:
        print("\n❌ 未能更新任何產品")

def compare_overview_quality():
    """比較概覽品質"""
    print("\n\n📊 比較概覽品質")
    print("=" * 50)
    
    try:
        # 載入原始資料
        with open('data/apple_refurbished_mac.json', 'r', encoding='utf-8') as f:
            original_products = json.load(f)
        
        # 載入測試結果
        test_files = [
            'data/apple_refurbished_mac_test_enhanced.json',
            'data/mac_overview_test_result.json'
        ]
        
        for test_file in test_files:
            try:
                with open(test_file, 'r', encoding='utf-8') as f:
                    enhanced_products = json.load(f)
                
                print(f"\n📁 分析檔案: {test_file}")
                
                if enhanced_products:
                    sample_original = original_products[0] if original_products else {}
                    sample_enhanced = enhanced_products[0]
                    
                    print(f"\n🔍 概覽比較:")
                    print(f"原始概覽長度: {len(sample_original.get('產品概覽', ''))}")
                    print(f"增強概覽長度: {len(sample_enhanced.get('產品概覽', ''))}")
                    
                    print(f"\n📝 原始概覽:")
                    print(f"{sample_original.get('產品概覽', 'N/A')[:100]}...")
                    
                    print(f"\n📝 增強概覽:")
                    enhanced_overview = sample_enhanced.get('產品概覽', 'N/A')
                    print(f"{enhanced_overview[:300]}...")
                    
                    # 檢查是否包含詳細規格
                    specs_keywords = ['顯示器', '記憶體', 'SSD', 'CPU', 'GPU', '相機', '埠', '推出']
                    found_specs = [keyword for keyword in specs_keywords if keyword in enhanced_overview]
                    
                    print(f"\n🎯 找到的規格關鍵字: {', '.join(found_specs) if found_specs else '無'}")
                    
                    if len(enhanced_overview) > len(sample_original.get('產品概覽', '')):
                        print("✅ 增強版概覽更詳細")
                    else:
                        print("⚠️ 增強版概覽未明顯改善")
                
            except FileNotFoundError:
                print(f"⚠️ 找不到測試檔案: {test_file}")
            except Exception as e:
                print(f"❌ 分析檔案 {test_file} 失敗: {e}")
    
    except Exception as e:
        print(f"❌ 比較概覽品質失敗: {e}")

async def main():
    """主測試程式"""
    print("🧪 增強版 Apple 爬蟲測試套件")
    print("測試從 rc-pdsection-mainpanel 區域提取詳細產品概覽")
    print("=" * 80)
    
    try:
        # 測試 1: 增強版爬蟲
        await test_enhanced_scraper()
        
        # 測試 2: 概覽更新器
        await test_overview_updater()
        
        # 測試 3: 比較概覽品質
        compare_overview_quality()
        
        print("\n\n🎉 所有測試完成！")
        print("📊 請檢查生成的測試檔案以驗證結果")
        
    except KeyboardInterrupt:
        print("\n\n⏹️ 測試被使用者中斷")
    except Exception as e:
        print(f"\n\n❌ 測試過程中發生錯誤: {e}")

if __name__ == "__main__":
    asyncio.run(main()) 