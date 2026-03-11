#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
小红书每日数据自动化分析器
使用官方 API 抓取数据，无需浏览器
每天自动执行，飞书推送报告
"""

import json
import hashlib
import time
import requests
from datetime import datetime, timedelta
from pathlib import Path
import logging

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/xiaohongshu_analyzer.log', encoding='utf-8', mode='a'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class XiaohongshuAPI:
    """小红书开放平台 API 客户端"""
    
    def __init__(self, app_key, app_secret):
        self.app_key = app_key
        self.app_secret = app_secret
        self.base_url = "https://api.xiaohongshu.com"
        self.access_token = None
        self.token_expiry = 0
        
    def get_sign(self, params):
        """生成 API 签名"""
        sorted_params = sorted(params.items())
        param_str = '&'.join([f"{k}={v}" for k, v in sorted_params])
        sign_str = f"{param_str}{self.app_secret}"
        return hashlib.md5(sign_str.encode()).hexdigest().upper()
    
    def get_access_token(self):
        """获取访问令牌（使用授权码）"""
        if self.access_token and time.time() < self.token_expiry:
            return self.access_token
        
        # 使用授权码换取 access_token
        url = f"{self.base_url}/oauth2/token"
        params = {
            'app_key': self.app_key,
            'grant_type': 'authorization_code',
            'code': 'YOUR_AUTH_CODE',  # 需要用户提供的授权码
            'redirect_uri': 'https://your-domain.com/callback'
        }
        params['sign'] = self.get_sign(params)
        
        try:
            response = requests.post(url, data=params, timeout=10)
            data = response.json()
            
            if data.get('success'):
                self.access_token = data['data']['access_token']
                self.token_expiry = time.time() + data['data']['expires_in'] - 300
                logger.info("✅ Access Token 获取成功")
                return self.access_token
            else:
                logger.error(f"❌ Access Token 获取失败：{data}")
                return None
        except Exception as e:
            logger.error(f"❌ 请求异常：{e}")
            return None
    
    def get_shop_data(self, date):
        """获取电商数据"""
        url = f"{self.base_url}/ecommerce/shop/data"
        params = {
            'app_key': self.app_key,
            'access_token': self.access_token,
            'date': date,
            'timestamp': int(time.time() * 1000)
        }
        params['sign'] = self.get_sign(params)
        
        try:
            response = requests.get(url, params=params, timeout=10)
            data = response.json()
            
            if data.get('success'):
                return data.get('data', {})
            else:
                logger.error(f"❌ 电商数据获取失败：{data}")
                return None
        except Exception as e:
            logger.error(f"❌ 请求异常：{e}")
            return None
    
    def get_note_data(self, date):
        """获取笔记数据"""
        url = f"{self.base_url}/content/note/data"
        params = {
            'app_key': self.app_key,
            'access_token': self.access_token,
            'date': date,
            'timestamp': int(time.time() * 1000)
        }
        params['sign'] = self.get_sign(params)
        
        try:
            response = requests.get(url, params=params, timeout=10)
            data = response.json()
            
            if data.get('success'):
                return data.get('data', {})
            else:
                logger.error(f"❌ 笔记数据获取失败：{data}")
                return None
        except Exception as e:
            logger.error(f"❌ 请求异常：{e}")
            return None
    
    def get_fans_data(self, date):
        """获取粉丝数据"""
        url = f"{self.base_url}/user/fans/data"
        params = {
            'app_key': self.app_key,
            'access_token': self.access_token,
            'date': date,
            'timestamp': int(time.time() * 1000)
        }
        params['sign'] = self.get_sign(params)
        
        try:
            response = requests.get(url, params=params, timeout=10)
            data = response.json()
            
            if data.get('success'):
                return data.get('data', {})
            else:
                logger.error(f"❌ 粉丝数据获取失败：{data}")
                return None
        except Exception as e:
            logger.error(f"❌ 请求异常：{e}")
            return None


class DataAnalyzer:
    """数据分析器"""
    
    @staticmethod
    def analyze(all_data):
        """分析数据，生成优化建议"""
        suggestions = []
        
        # 电商数据分析
        ecommerce = all_data.get('ecommerce', {})
        gmv = ecommerce.get('gmv', 0)
        orders = ecommerce.get('order_count', 0)
        conversion = ecommerce.get('conversion_rate', 0)
        
        if gmv > 1000:
            suggestions.append(f"✅ GMV ¥{gmv} 表现优秀！")
        elif gmv > 500:
            suggestions.append(f"👍 GMV ¥{gmv} 良好，可继续优化")
        else:
            suggestions.append(f"⚠️ GMV ¥{gmv} 偏低，建议增加投流或优化商品页")
        
        if conversion > 15:
            suggestions.append(f"✅ 转化率 {conversion}% 超出行业平均！")
        elif conversion > 10:
            suggestions.append(f"👍 转化率 {conversion}% 正常")
        else:
            suggestions.append(f"⚠️ 转化率 {conversion}% 偏低，建议优化商品详情页")
        
        # 笔记数据分析
        notes = all_data.get('notes', {})
        views = notes.get('total_views', 0)
        interaction = notes.get('interaction_rate', 0)
        
        if interaction > 10:
            suggestions.append(f"✅ 互动率 {interaction}% 优秀！继续保持内容质量")
        elif interaction > 5:
            suggestions.append(f"👍 互动率 {interaction}% 良好")
        else:
            suggestions.append(f"⚠️ 互动率 {interaction}% 偏低，建议优化封面和标题")
        
        # 粉丝数据分析
        fans = all_data.get('fans', {})
        net_growth = fans.get('net_growth', 0)
        
        if net_growth > 50:
            suggestions.append(f"✅ 粉丝增长 +{net_growth} 表现优秀！")
        elif net_growth > 20:
            suggestions.append(f"👍 粉丝增长 +{net_growth} 稳定")
        else:
            suggestions.append(f"⚠️ 粉丝增长 +{net_growth} 较慢，建议增加干货内容")
        
        # 通用建议
        suggestions.append("🕐 最佳发布时间：19:00-21:00（晚间高峰）")
        suggestions.append("📝 建议增加产品使用场景展示（办公室、宿舍等）")
        
        return suggestions
    
    @staticmethod
    def generate_report(all_data, suggestions):
        """生成日报"""
        ecommerce = all_data.get('ecommerce', {})
        notes = all_data.get('notes', {})
        fans = all_data.get('fans', {})
        
        report = f"""
📊 小红书店铺日报 - 悉世药业
━━━━━━━━━━━━━━━━━━━━
日期：{datetime.now().strftime('%Y-%m-%d')}

💰 电商数据
  GMV: ¥{ecommerce.get('gmv', 0):,}
  订单数：{ecommerce.get('order_count', 0)}
  转化率：{ecommerce.get('conversion_rate', 0):.1f}%

📝 笔记数据
  总阅读：{notes.get('total_views', 0):,}
  互动率：{notes.get('interaction_rate', 0):.1f}%
  新增笔记：{notes.get('note_count', 0)} 篇

👥 粉丝数据
  粉丝总数：{fans.get('total_fans', 0):,}
  净增长：{fans.get('net_growth', 0):+d}

💡 AI 优化建议
"""
        for i, suggestion in enumerate(suggestions, 1):
            report += f"  {i}. {suggestion}\n"
        
        report += f"""
━━━━━━━━━━━━━━━━━━━━
生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
        return report


class FeishuNotifier:
    """飞书推送"""
    
    def __init__(self, webhook):
        self.webhook = webhook
    
    def send(self, message):
        """发送消息到飞书"""
        if not self.webhook:
            logger.warning("⚠️ 未配置飞书 Webhook")
            return False
        
        try:
            payload = {
                "msg_type": "text",
                "content": {"text": message}
            }
            
            response = requests.post(self.webhook, json=payload, timeout=10)
            
            if response.status_code == 200:
                logger.info("✅ 飞书推送成功")
                return True
            else:
                logger.error(f"❌ 飞书推送失败：{response.text}")
                return False
        except Exception as e:
            logger.error(f"❌ 推送异常：{e}")
            return False


def main():
    """主函数"""
    logger.info("=" * 60)
    logger.info("开始执行小红书数据自动化分析")
    logger.info("=" * 60)
    
    # 加载配置
    config_path = Path('config.json')
    if not config_path.exists():
        logger.error("❌ config.json 不存在")
        return
    
    with open(config_path, 'r', encoding='utf-8') as f:
        config = json.load(f)
    
    # 初始化 API 客户端
    api = XiaohongshuAPI(
        app_key=config['app_key'],
        app_secret=config['app_secret']
    )
    
    # 获取访问令牌
    if not api.get_access_token():
        logger.error("❌ 无法获取 Access Token")
        return
    
    # 获取昨天日期
    yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
    
    # 抓取数据
    logger.info(f"📊 抓取 {yesterday} 数据...")
    
    all_data = {
        'ecommerce': api.get_shop_data(yesterday) or {},
        'notes': api.get_note_data(yesterday) or {},
        'fans': api.get_fans_data(yesterday) or {}
    }
    
    # 分析数据
    logger.info("🤖 AI 分析数据...")
    analyzer = DataAnalyzer()
    suggestions = analyzer.analyze(all_data)
    
    # 生成报告
    report = analyzer.generate_report(all_data, suggestions)
    
    # 保存报告
    data_dir = Path('data')
    data_dir.mkdir(exist_ok=True)
    report_path = data_dir / f"report_{yesterday}.txt"
    
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(report)
    
    logger.info(f"✅ 报告已保存到 {report_path}")
    
    # 飞书推送
    notifier = FeishuNotifier(config.get('feishu_webhook'))
    notifier.send(report)
    
    # 打印报告
    print(report)
    
    logger.info("✅ 数据分析完成")
    logger.info("=" * 60)


if __name__ == "__main__":
    main()
