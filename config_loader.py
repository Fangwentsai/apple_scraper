#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
設定檔案載入器 - 統一管理 API 金鑰和設定參數
"""

import json
import os
from typing import Dict, Any, Optional

class ConfigLoader:
    def __init__(self, config_file: str = 'config.json'):
        """
        初始化設定載入器
        
        Args:
            config_file: 設定檔案路徑
        """
        self.config_file = config_file
        self.config = {}
        self.load_config()
    
    def load_config(self):
        """載入設定檔案"""
        try:
            # 優先從檔案載入
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    self.config = json.load(f)
                print(f"✅ 設定檔案載入成功: {self.config_file}")
            else:
                print(f"⚠️ 設定檔案不存在: {self.config_file}")
                self.config = {}
            
            # 從環境變數覆蓋設定
            self.load_from_env()
            
        except Exception as e:
            print(f"❌ 載入設定檔案失敗: {e}")
            self.config = {}
            self.load_from_env()
    
    def load_from_env(self):
        """從環境變數載入設定"""
        env_mappings = {
            # Line Bot
            'LINE_CHANNEL_ACCESS_TOKEN': ['line_bot', 'channel_access_token'],
            'LINE_CHANNEL_SECRET': ['line_bot', 'channel_secret'],
            'LINE_WEBHOOK_URL': ['line_bot', 'webhook_url'],
            
            # OpenAI
            'OPENAI_API_KEY': ['openai', 'api_key'],
            'OPENAI_MODEL': ['openai', 'model'],
            'OPENAI_MAX_TOKENS': ['openai', 'max_tokens'],
            'OPENAI_TEMPERATURE': ['openai', 'temperature'],
            
            # Firebase
            'FIREBASE_SERVICE_ACCOUNT_PATH': ['firebase', 'service_account_path'],
            'FIREBASE_PROJECT_ID': ['firebase', 'project_id'],
            'GOOGLE_APPLICATION_CREDENTIALS': ['firebase', 'service_account_path'],
            
            # Render
            'RENDER_APP_URL': ['render', 'app_url'],
            'ENABLE_SCRAPING': ['render', 'enable_scraping'],
            'SCRAPE_INTERVAL_MINUTES': ['render', 'scrape_interval_minutes'],
            
            # Scraper
            'USER_AGENT': ['scraper', 'user_agent'],
            'DELAY_BETWEEN_REQUESTS': ['scraper', 'delay_between_requests'],
            'MAX_RETRIES': ['scraper', 'max_retries']
        }
        
        for env_key, config_path in env_mappings.items():
            env_value = os.getenv(env_key)
            if env_value:
                self.set_nested_config(config_path, env_value)
    
    def set_nested_config(self, path: list, value: str):
        """設定巢狀設定值"""
        current = self.config
        
        # 確保路徑存在
        for key in path[:-1]:
            if key not in current:
                current[key] = {}
            current = current[key]
        
        # 設定值（嘗試轉換型別）
        final_key = path[-1]
        if value.lower() in ['true', 'false']:
            current[final_key] = value.lower() == 'true'
        elif value.isdigit():
            current[final_key] = int(value)
        elif value.replace('.', '').isdigit():
            current[final_key] = float(value)
        else:
            current[final_key] = value
    
    def get(self, *path, default=None) -> Any:
        """
        取得設定值
        
        Args:
            *path: 設定路徑，例如 get('line_bot', 'channel_access_token')
            default: 預設值
            
        Returns:
            設定值或預設值
        """
        current = self.config
        
        try:
            for key in path:
                current = current[key]
            return current
        except (KeyError, TypeError):
            return default
    
    def get_line_bot_config(self) -> Dict[str, str]:
        """取得 Line Bot 設定"""
        return {
            'channel_access_token': self.get('line_bot', 'channel_access_token', default=''),
            'channel_secret': self.get('line_bot', 'channel_secret', default=''),
            'webhook_url': self.get('line_bot', 'webhook_url', default='')
        }
    
    def get_openai_config(self) -> Dict[str, Any]:
        """取得 OpenAI 設定"""
        return {
            'api_key': self.get('openai', 'api_key', default=''),
            'model': self.get('openai', 'model', default='gpt-3.5-turbo'),
            'max_tokens': self.get('openai', 'max_tokens', default=1000),
            'temperature': self.get('openai', 'temperature', default=0.7)
        }
    
    def get_firebase_config(self) -> Dict[str, str]:
        """取得 Firebase 設定"""
        return {
            'service_account_path': self.get('firebase', 'service_account_path', default='firebase-service-account.json'),
            'project_id': self.get('firebase', 'project_id', default='')
        }
    
    def get_render_config(self) -> Dict[str, Any]:
        """取得 Render 設定"""
        return {
            'app_url': self.get('render', 'app_url', default='http://localhost:5000'),
            'enable_scraping': self.get('render', 'enable_scraping', default=True),
            'scrape_interval_minutes': self.get('render', 'scrape_interval_minutes', default=5)
        }
    
    def get_scraper_config(self) -> Dict[str, Any]:
        """取得爬蟲設定"""
        return {
            'user_agent': self.get('scraper', 'user_agent', default='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'),
            'delay_between_requests': self.get('scraper', 'delay_between_requests', default=3),
            'max_retries': self.get('scraper', 'max_retries', default=3)
        }
    
    def is_line_bot_configured(self) -> bool:
        """檢查 Line Bot 是否已設定"""
        config = self.get_line_bot_config()
        return bool(config['channel_access_token'] and config['channel_secret'])
    
    def is_openai_configured(self) -> bool:
        """檢查 OpenAI 是否已設定"""
        config = self.get_openai_config()
        return bool(config['api_key'])
    
    def is_firebase_configured(self) -> bool:
        """檢查 Firebase 是否已設定"""
        config = self.get_firebase_config()
        return bool(config['service_account_path'] and os.path.exists(config['service_account_path']))
    
    def get_status(self) -> Dict[str, Any]:
        """取得設定狀態"""
        return {
            'config_file': self.config_file,
            'config_file_exists': os.path.exists(self.config_file),
            'line_bot_configured': self.is_line_bot_configured(),
            'openai_configured': self.is_openai_configured(),
            'firebase_configured': self.is_firebase_configured(),
            'total_settings': len(str(self.config))
        }
    
    def create_template_config(self, output_file: str = 'config_template.json'):
        """建立範本設定檔案"""
        template = {
            "line_bot": {
                "channel_access_token": "YOUR_LINE_CHANNEL_ACCESS_TOKEN_HERE",
                "channel_secret": "YOUR_LINE_CHANNEL_SECRET_HERE",
                "webhook_url": "https://your-app.onrender.com/webhook"
            },
            "openai": {
                "api_key": "YOUR_OPENAI_API_KEY_HERE",
                "model": "gpt-3.5-turbo",
                "max_tokens": 1000,
                "temperature": 0.7
            },
            "firebase": {
                "service_account_path": "firebase-service-account.json",
                "project_id": "your-firebase-project-id"
            },
            "render": {
                "app_url": "https://your-app.onrender.com",
                "enable_scraping": True,
                "scrape_interval_minutes": 5
            },
            "scraper": {
                "user_agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                "delay_between_requests": 3,
                "max_retries": 3
            }
        }
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(template, f, ensure_ascii=False, indent=2)
        
        print(f"✅ 範本設定檔案已建立: {output_file}")

# 建立全域設定實例
config = ConfigLoader()

def main():
    """主程式 - 測試設定載入器"""
    print("🔧 設定載入器測試")
    print("=" * 50)
    
    # 顯示設定狀態
    status = config.get_status()
    print("📊 設定狀態:")
    for key, value in status.items():
        print(f"  {key}: {value}")
    
    print("\n🔑 API 設定檢查:")
    print(f"  Line Bot: {'✅ 已設定' if config.is_line_bot_configured() else '❌ 未設定'}")
    print(f"  OpenAI: {'✅ 已設定' if config.is_openai_configured() else '❌ 未設定'}")
    print(f"  Firebase: {'✅ 已設定' if config.is_firebase_configured() else '❌ 未設定'}")
    
    # 建立範本檔案
    if not os.path.exists('config_template.json'):
        config.create_template_config()
    
    print("\n💡 使用說明:")
    print("1. 複製 config_template.json 為 config.json")
    print("2. 填入你的 API 金鑰和設定")
    print("3. 或使用環境變數設定")

if __name__ == "__main__":
    main() 