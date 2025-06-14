from playwright.sync_api import sync_playwright
import json
import time
import re

def clean_price(price_text):
    """清理價格文字，提取 NT$ 價格"""
    if not price_text or price_text == "無價格":
        return None
    
    # 尋找 NT$ 開頭的價格
    price_match = re.search(r'NT\$[\d,]+', price_text)
    if price_match:
        return price_match.group()
    return None

def navigate_all_pages(page):
    """瀏覽所有分頁並收集產品"""
    all_products = []
    current_page = 1
    
    while True:
        print(f"正在處理第 {current_page} 頁...")
        
        # 等待頁面載入完成
        page.wait_for_load_state('networkidle')
        time.sleep(3)
        
        # 收集當前頁面的產品
        page_products = collect_products_from_current_page(page)
        all_products.extend(page_products)
        
        print(f"第 {current_page} 頁找到 {len(page_products)} 個產品")
        
        # 尋找「下一頁」按鈕
        next_button = page.query_selector('button[aria-label="下一頁"], button[data-analytics-pagination="next"]')
        
        if next_button and next_button.is_visible() and next_button.is_enabled():
            print("找到下一頁按鈕，點擊中...")
            try:
                next_button.click()
                time.sleep(3)
                current_page += 1
                
                # 檢查是否成功跳轉到下一頁
                page.wait_for_load_state('networkidle')
                time.sleep(2)
                
            except Exception as e:
                print(f"點擊下一頁失敗: {e}")
                break
        else:
            print("沒有找到下一頁按鈕，已到最後一頁")
            break
        
        # 安全機制：最多處理 10 頁
        if current_page > 10:
            print("已處理 10 頁，停止")
            break
    
    return all_products

def collect_products_from_current_page(page):
    """收集當前頁面的所有產品"""
    products = []
    
    # 先嘗試找到所有包含產品標題的 h3 元素
    h3_elements = page.query_selector_all('h3')
    
    print(f"當前頁面找到 {len(h3_elements)} 個 h3 元素")
    
    for h3 in h3_elements:
        try:
            h3_text = h3.inner_text().strip()
            
            # 檢查是否為產品標題
            if '整修品' in h3_text and any(keyword in h3_text.lower() for keyword in ['mac', 'imac', 'macbook']):
                print(f"找到產品標題: {h3_text}")
                
                # 尋找對應的價格 - 通常在同一個容器或附近
                container = h3
                price = None
                product_url = None
                
                # 向上尋找父容器
                for _ in range(5):  # 最多向上找5層
                    if container:
                        container_text = container.inner_text()
                        price = clean_price(container_text)
                        
                        # 尋找連結
                        link = container.query_selector('a')
                        if link:
                            product_url = link.get_attribute('href')
                            if product_url and not product_url.startswith('http'):
                                product_url = f"https://www.apple.com{product_url}"
                        
                        if price:
                            break
                        
                        container = container.query_selector('..')
                    else:
                        break
                
                if price:
                    product_info = {
                        'title': h3_text,
                        'price': price,
                        'url': product_url or "無連結",
                        'overview': h3_text
                    }
                    
                    products.append(product_info)
                    print(f"成功提取產品: {h3_text} - {price}")
                else:
                    print(f"未找到價格: {h3_text}")
                    
        except Exception as e:
            continue
    
    # 如果 h3 方法沒找到足夠產品，嘗試其他方法
    if len(products) < 10:  # 假設每頁至少應該有10個產品
        print("h3 方法找到的產品較少，嘗試其他選擇器...")
        
        # 嘗試更廣泛的選擇器
        broader_selectors = [
            'div:has-text("整修品")',
            'section:has-text("整修品")',
            '[class*="tile"]',
            '[class*="product"]'
        ]
        
        for selector in broader_selectors:
            elements = page.query_selector_all(selector)
            print(f"選擇器 '{selector}' 找到 {len(elements)} 個元素")
            
            for element in elements:
                try:
                    element_text = element.inner_text().strip()
                    
                    if '整修品' in element_text and any(keyword in element_text.lower() for keyword in ['mac', 'imac', 'macbook']):
                        # 提取標題
                        lines = element_text.split('\n')
                        title = None
                        for line in lines:
                            if '整修品' in line and any(keyword in line.lower() for keyword in ['mac', 'imac', 'macbook']):
                                title = line.strip()
                                break
                        
                        if title and not any(p['title'] == title for p in products):
                            price = clean_price(element_text)
                            if price:
                                # 尋找連結
                                link = element.query_selector('a')
                                product_url = None
                                if link:
                                    product_url = link.get_attribute('href')
                                    if product_url and not product_url.startswith('http'):
                                        product_url = f"https://www.apple.com{product_url}"
                                
                                product_info = {
                                    'title': title,
                                    'price': price,
                                    'url': product_url or "無連結",
                                    'overview': element_text[:200] + "..." if len(element_text) > 200 else element_text
                                }
                                
                                products.append(product_info)
                                print(f"額外找到產品: {title} - {price}")
                                
                except Exception as e:
                    continue
    
    return products

def get_apple_refurbished_products():
    url = "https://www.apple.com/tw/shop/refurbished/mac"
    
    with sync_playwright() as p:
        # 啟動瀏覽器（headless 模式）
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        try:
            # 訪問網頁
            print(f"正在訪問: {url}")
            page.goto(url)
            
            # 等待頁面載入
            page.wait_for_load_state('networkidle')
            time.sleep(5)
            
            # 瀏覽所有分頁並收集產品
            all_products = navigate_all_pages(page)
            
            print(f"\n總共收集到 {len(all_products)} 個產品")
            
            # 去重複處理
            unique_products = []
            seen_combinations = set()  # 改為使用標題+價格的組合來去重
            seen_urls = set()
            
            for product in all_products:
                # 使用標題+價格的組合來避免重複，而不是只用標題
                title_price_combo = f"{product['title']}|{product['price']}"
                
                if title_price_combo in seen_combinations:
                    continue
                
                if product['url'] != "無連結" and product['url'] in seen_urls:
                    continue
                
                if product['url'] != "無連結":
                    seen_urls.add(product['url'])
                seen_combinations.add(title_price_combo)
                
                product_data = {
                    "序號": len(unique_products) + 1,
                    "產品標題": product['title'],
                    "產品售價": product['price'],
                    "產品URL": product['url'],
                    "產品概覽": product['overview']
                }
                
                unique_products.append(product_data)
                
                # 即時輸出
                print(f"\n=== 產品 {len(unique_products)} ===")
                print(f"標題: {product['title']}")
                print(f"價格: {product['price']}")
                print(f"URL: {product['url']}")
            
            # 儲存結果
            if unique_products:
                with open('apple_refurbished_products_final.json', 'w', encoding='utf-8') as f:
                    json.dump(unique_products, f, ensure_ascii=False, indent=2)
                
                print(f"\n✅ 成功抓取 {len(unique_products)} 個有效產品，已儲存至 apple_refurbished_products_final.json")
                
                # 統計產品類型
                product_types = {}
                for product in unique_products:
                    title_lower = product['產品標題'].lower()
                    if 'imac' in title_lower:
                        product_types['iMac'] = product_types.get('iMac', 0) + 1
                    elif 'macbook air' in title_lower:
                        product_types['MacBook Air'] = product_types.get('MacBook Air', 0) + 1
                    elif 'macbook pro' in title_lower:
                        product_types['MacBook Pro'] = product_types.get('MacBook Pro', 0) + 1
                    elif 'mac mini' in title_lower:
                        product_types['Mac mini'] = product_types.get('Mac mini', 0) + 1
                    elif 'mac studio' in title_lower:
                        product_types['Mac Studio'] = product_types.get('Mac Studio', 0) + 1
                    elif 'mac pro' in title_lower:
                        product_types['Mac Pro'] = product_types.get('Mac Pro', 0) + 1
                
                print("\n📊 產品類型統計:")
                for product_type, count in product_types.items():
                    print(f"  {product_type}: {count} 個")
                
                # 價格統計
                prices = []
                for product in unique_products:
                    price_str = product['產品售價'].replace('NT$', '').replace(',', '')
                    try:
                        prices.append(int(price_str))
                    except:
                        continue
                
                if prices:
                    print(f"\n💰 價格範圍:")
                    print(f"  最低價格: NT${min(prices):,}")
                    print(f"  最高價格: NT${max(prices):,}")
                    print(f"  平均價格: NT${sum(prices)//len(prices):,}")
                    
            else:
                print("\n❌ 未找到任何有效產品資訊")
                
        except Exception as e:
            print(f"發生錯誤: {e}")
        finally:
            browser.close()

if __name__ == "__main__":
    get_apple_refurbished_products() 