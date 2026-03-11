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

# 忽略 SSL 警告
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

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

    def __init__(self, app_key, app_secret, auth_code):
        self.app_key = app_key
        self.app_secret = app_secret
        self.auth_code = auth_code
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
            logger.info("✅ 使用缓存的 Access Token")
            return self.access_token

        logger.info("🔑 正在获取 Access Token...")
        
        url = f"{self.base_url}/oauth2/token"
        params = {
            'app_key': self.app_key,
            'grant_type': 'authorization_code',
            'code': self.auth_code,
            'redirect_uri': 'http://127.0.0.1:8080/callback'
        }
        params['sign'] = self.get_sign(params)

        try:
            response = requests.post(url, data=params, timeout=30, verify=False)
            data = response.json()

            if data.get('success'):
                self.access_token = data['data']['access_token']
                self.token_expiry = time.time() + data['data']['expires_in'] - 300
                logger.info("✅ Access Token 获取成功")
                return self.access_token
            else:
                logger.error(f"❌ Access Token 获取失败：{data}")
                logger.error("请检查授权码是否正确，或联系小红书开放平台")
                return None
        except requests.exceptions.SSLError as e:
            logger.error(f"❌ SSL 错误：{e}")
            logger.error("尝试忽略 SSL 验证...")
            return None
        except Exception as e:
            logger.error(f"❌ 请求异常：{e}")
            return None

    def get_shop_data(self, date):
        """获取电商数据"""
        logger.info(f"📊 获取电商数据 ({date})...")
        url = f"{self.base_url}/ecommerce/shop/data"
        params = {
            'app_key': self.app_key,
            'access_token': self.access_token,
            'date': date,
            'timestamp': int(time.time() * 1000)
        }
        params['sign'] = self.get_sign(params)

        try:
            response = requests.get(url, params=params, timeout=30, verify=False)
            data = response.json()

            if data.get('success'):
                logger.info("✅ 电商数据获取成功")
                return data.get('data', {})
            else:
                logger.warning(f"⚠️ 电商数据获取失败：{data}")
                return {}
        except Exception as e:
            logger.error(f"❌ 请求异常：{e}")
            return {}

    def get_note_data(self, date):
        """获取笔记数据"""
        logger.info(f"📝 获取笔记数据 ({date})...")
        url = f"{self.base_url}/content/note/data"
        params = {
            'app_key': self.app_key,
            'access_token': self.access_token,
            'date': date,
            'timestamp': int(time.time() * 1000)
        }
        params['sign'] = self.get_sign(params)

        try:
            response = requests.get(url, params=params, timeout=30, verify=False)
            data = response.json()

            if data.get('success'):
                logger.info("✅ 笔记数据获取成功")
                return data.get('data', {})
            else:
                logger.warning(f"⚠️ 笔记数据获取失败：{data}")
                return {}
        except Exception as e:
            logger.error(f"❌ 请求异常：{e}")
            return {}

    def get_fans_data(self, date):
        """获取粉丝数据"""
        logger.info(f"👥 获取粉丝数据 ({date})...")
        url = f"{self.base_url}/user/fans/data"
        params = {
            'app_key': self.app_key,
            'access_token': self.access_token,
            'date': date,
            'timestamp': int(time.time() * 1000)
        }
        params['sign'] = self.get_sign(params)

        try:
            response = requests.get(url, params=params, timeout=30, verify=False)
            data = response.json()

            if data.get('success'):
                logger.info("✅ 粉丝数据获取成功")
                return data.get('data', {})
            else:
                logger.warning(f"⚠️ 粉丝数据获取失败：{data}")
                return {}
        except Exception as e:
            logger.error(f"❌ 请求异常：{e}")
            return {}


class DataAnalyzer:
    """数据分析器"""

    @staticmethod
    def analyze(all_data):
        """分析数据，生成优化建议"""
        suggestions = []

        ecommerce = all_data.get('ecommerce', {})
        gmv = ecommerce.get('gmv', 0) if isinstance(ecommerce.get('gmv'), (int, float)) else 0
        orders = ecommerce.get('order_count', 0) if isinstance(ecommerce.get('order_count'), (int, float)) else 0
        conversion = ecommerce.get('conversion_rate', 0) if isinstance(ecommerce.get('conversion_rate'), (int, float)) else 0

        if gmv > 1000:
            suggestions.append(f"✅ GMV ¥{gmv:,.0f} 表现优秀！")
        elif gmv > 500:
            suggestions.append(f"👍 GMV ¥{gmv:,.0f} 良好，可继续优化")
        elif gmv > 0:
            suggestions.append(f"⚠️ GMV ¥{gmv:,.0f} 偏低，建议增加投流或优化商品页")
        else:
            suggestions.append("⚠️ 今日无 GMV 数据，请检查 API 权限或店铺状态")

        if conversion > 15:
            suggestions.append(f"✅ 转化率 {conversion:.1f}% 超出行业平均！")
        elif conversion > 10:
            suggestions.append(f"👍 转化率 {conversion:.1f}% 正常")
        elif conversion > 0:
            suggestions.append(f"⚠️ 转化率 {conversion:.1f}% 偏低，建议优化商品详情页")

        notes = all_data.get('notes', {})
        views = notes.get('total_views', 0) if isinstance(notes.get('total_views'), (int, float)) else 0
        interaction = notes.get('interaction_rate', 0) if isinstance(notes.get('interaction_rate'), (int, float)) else 0

        if interaction > 10:
            suggestions.append(f"✅ 互动率 {interaction:.1f}% 优秀！继续保持内容质量")
        elif interaction > 5:
            suggestions.append(f"👍 互动率 {interaction:.1f}% 良好")
        elif interaction > 0:
            suggestions.append(f"⚠️ 互动率 {interaction:.1f}% 偏低，建议优化封面和标题")

        fans = all_data.get('fans', {})
        net_growth = fans.get('net_growth', 0) if isinstance(fans.get('net_growth'), (int, float)) else 0

        if net_growth > 50:
            suggestions.append(f"✅ 粉丝增长 +{int(net_growth)} 表现优秀！")
        elif net_growth > 20:
            suggestions.append(f"👍 粉丝增长 +{int(net_growth)} 稳定")
        elif net_growth > 0:
            suggestions.append(f"⚠️ 粉丝增长 +{int(net_growth)} 较慢，建议增加干货内容")
        else:
            suggestions.append("⚠️ 粉丝无增长或负增长，建议优化内容策略")

        suggestions.append("🕐 最佳发布时间：19:00-21:00（晚间高峰）")
        suggestions.append("📝 建议增加产品使用场景展示（办公室、宿舍等）")

        return suggestions

    @staticmethod
    def generate_report(all_data, suggestions):
        """生成日报"""
        ecommerce = all_data.get('ecommerce', {})
        notes = all_data.get('notes', {})
        fans = all_data.get('fans', {})

        gmv = ecommerce.get('gmv', 0) if isinstance(ecommerce.get('gmv'), (int, float)) else 0
        orders = ecommerce.get('order_count', 0) if isinstance(ecommerce.get('order_count'), (int, float)) else 0
        conversion = ecommerce.get('conversion_rate', 0) if isinstance(ecommerce.get('conversion_rate'), (int, float)) else 0

        views = notes.get('total_views', 0) if isinstance(notes.get('total_views'), (int, float)) else 0
        interaction = notes.get('interaction_rate', 0) if isinstance(notes.get('interaction_rate'), (int, float)) else 0
        note_count = notes.get('note_count', 0) if isinstance(notes.get('note_count'), (int, float)) else 0

        total_fans = fans.get('total_fans', 0) if isinstance(fans.get('total_fans'), (int, float)) else 0
        net_growth = fans.get('net_growth', 0) if isinstance(fans.get('net_growth'), (int, float)) else 0

        report = f"""
📊 小红书店铺日报 - 悉世药业
━━━━━━━━━━━━━━━━━━━━
日期：{datetime.now().strftime('%Y-%m-%d')}

💰 电商数据
  GMV: ¥{gmv:,.0f}
  订单数：{int(orders)}
  转化率：{conversion:.1f}%

📝 笔记数据
  总阅读：{int(views):,}
  互动率：{interaction:.1f}%
  新增笔记：{int(note_count)} 篇

👥 粉丝数据
  粉丝总数：{int(total_fans):,}
  净增长：{int(net_growth):+d}

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
            logger.warning("⚠️ 未配置飞书 Webhook，跳过推送")
            return False

        try:
            payload = {
                "msg_type": "text",
                "content": {"text": message}
            }

            response = requests.post(self.webhook, json=payload, timeout=10, verify=False)

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

    config_path = Path('config.json')
    if not config_path.exists():
        logger.error("❌ config.json 不存在")
        return

    with open(config_path, 'r', encoding='utf-8') as f:
        config = json.load(f)

    auth_code = config.get('authorization_code', '')
    if not auth_code:
        logger.error("❌ 授权码未配置，请在 config.json 中填写 authorization_code")
        return

    api = XiaohongshuAPI(
        app_key=config['app_key'],
        app_secret=config['app_secret'],
        auth_code=auth_code
    )

    if not api.get_access_token():
        logger.error("❌ 无法获取 Access Token，程序终止")
        logger.error("请检查：")
        logger.error("  1. 授权码是否正确")
        logger.error("  2. 应用是否已上线或有测试店铺")
        logger.error("  3. 网络连接是否正常")
        return

    yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')

    logger.info(f"📊 抓取 {yesterday} 数据...")

    all_data = {
        'ecommerce': api.get_shop_data(yesterday),
        'notes': api.get_note_data(yesterday),
        'fans': api.get_fans_data(yesterday)
    }

    logger.info("🤖 AI 分析数据...")
    analyzer = DataAnalyzer()
    suggestions = analyzer.analyze(all_data)

    report = analyzer.generate_report(all_data, suggestions)

    data_dir = Path('data')
    data_dir.mkdir(exist_ok=True)
    report_path = data_dir / f"report_{yesterday}.txt"

    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(report)

    logger.info(f"✅ 报告已保存到 {report_path}")

    notifier = FeishuNotifier(config.get('feishu_webhook'))
    notifier.send(report)

    print("\n" + report)

    logger.info("✅ 数据分析完成")
    logger.info("=" * 60)


if __name__ == "__main__":
    main()
