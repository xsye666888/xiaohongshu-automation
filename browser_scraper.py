#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
小红书数据浏览器自动化抓取
使用已登录的 Chrome 浏览器，无需 API
"""

import json
import time
from datetime import datetime, timedelta
from pathlib import Path
import logging
import os

# 创建目录
os.makedirs('logs', exist_ok=True)
os.makedirs('data', exist_ok=True)

# 日志配置
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/browser_scraper.log', encoding='utf-8', mode='a'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

try:
    from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    logger.error("❌ Playwright 未安装，请先运行：pip install playwright")
    logger.error("然后运行：playwright install chromium")
    PLAYWRIGHT_AVAILABLE = False


class XiaohongshuScraper:
    """小红书数据抓取器"""

    def __init__(self, chrome_port=15264):
        self.chrome_port = chrome_port
        self.base_url = "https://pro.xiaohongshu.com"
        self.browser = None
        self.page = None

    def connect_to_chrome(self):
        """连接到已运行的 Chrome"""
        logger.info(f"🔌 尝试连接 Chrome (端口 {self.chrome_port})...")
        
        try:
            playwright = sync_playwright().start()
            self.browser = playwright.chromium.connect_over_cdp(
                f"http://127.0.0.1:{self.chrome_port}",
                timeout=30000
            )
            contexts = self.browser.contexts
            if not contexts:
                self.context = self.browser.new_context()
            else:
                self.context = contexts[0]
            
            self.page = self.context.new_page()
            logger.info("✅ Chrome 连接成功")
            return True
        except Exception as e:
            logger.error(f"❌ Chrome 连接失败：{e}")
            logger.error("请确保 Chrome 已启动，并且开启了远程调试端口")
            return False

    def check_login(self):
        """检查是否已登录"""
        logger.info("🔐 检查登录状态...")
        
        try:
            self.page.goto(f"{self.base_url}/enterprise/home", timeout=30000, wait_until="domcontentloaded")
            time.sleep(3)
            
            # 检查是否在登录页
            current_url = self.page.url
            if "login" in current_url.lower():
                logger.warning("⚠️ 未登录，需要扫码")
                return False
            
            logger.info("✅ 已登录")
            return True
        except Exception as e:
            logger.error(f"❌ 检查登录失败：{e}")
            return False

    def scrape_data(self, date=None):
        """抓取数据"""
        if date is None:
            date = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
        
        logger.info(f"📊 开始抓取 {date} 数据...")
        
        data = {
            'date': date,
            'gmv': 0,
            'orders': 0,
            'fans_total': 0,
            'fans_growth': 0,
            'note_views': 0,
            'error': None
        }
        
        try:
            # 打开数据中心
            logger.info("📈 打开数据中心...")
            self.page.goto(f"{self.base_url}/enterprise/data", timeout=30000, wait_until="domcontentloaded")
            time.sleep(5)  # 等待页面加载
            
            # 尝试抓取数据（使用通用的选择器）
            # 注意：实际选择器需要根据页面结构调整
            
            # 查找 GMV 数据
            try:
                gmv_el = self.page.query_selector('[data-e2e="gmv-value"], .gmv-value, [class*="gmv"]')
                if gmv_el:
                    gmv_text = gmv_el.inner_text()
                    data['gmv'] = self._parse_number(gmv_text)
                    logger.info(f"✅ GMV: ¥{data['gmv']:,.0f}")
            except Exception as e:
                logger.warning(f"⚠️ GMV 抓取失败：{e}")
            
            # 查找订单数
            try:
                orders_el = self.page.query_selector('[data-e2e="order-value"], .order-value, [class*="order"]')
                if orders_el:
                    orders_text = orders_el.inner_text()
                    data['orders'] = self._parse_number(orders_text)
                    logger.info(f"✅ 订单数：{data['orders']}")
            except Exception as e:
                logger.warning(f"⚠️ 订单数抓取失败：{e}")
            
            # 查找粉丝数据
            try:
                fans_el = self.page.query_selector('[data-e2e="fans-value"], .fans-value, [class*="fans"]')
                if fans_el:
                    fans_text = fans_el.inner_text()
                    data['fans_total'] = self._parse_number(fans_text)
                    logger.info(f"✅ 粉丝总数：{data['fans_total']:,.0f}")
            except Exception as e:
                logger.warning(f"⚠️ 粉丝数据抓取失败：{e}")
            
            # 截图保存（调试用）
            screenshot_path = Path('logs') / f'screenshot_{date}.png'
            self.page.screenshot(path=str(screenshot_path), full_page=True)
            logger.info(f"📸 截图已保存：{screenshot_path}")
            
        except Exception as e:
            logger.error(f"❌ 抓取失败：{e}")
            data['error'] = str(e)
        
        return data

    def _parse_number(self, text):
        """解析数字字符串"""
        import re
        if not text:
            return 0
        # 移除所有非数字字符（除了小数点和负号）
        cleaned = re.sub(r'[^\d.\-]', '', text)
        try:
            return float(cleaned) if cleaned else 0
        except:
            return 0

    def close(self):
        """关闭浏览器"""
        if self.browser:
            self.browser.close()
            logger.info("👋 浏览器已关闭")


def generate_report(data):
    """生成报告"""
    report = f"""
📊 小红书店铺日报 - 悉世药业
━━━━━━━━━━━━━━━━━━━━
日期：{data.get('date', 'N/A')}

💰 电商数据
  GMV: ¥{data.get('gmv', 0):,.0f}
  订单数：{int(data.get('orders', 0))}

👥 粉丝数据
  粉丝总数：{data.get('fans_total', 0):,.0f}
  净增长：{data.get('fans_growth', 0):+d}

📝 笔记数据
  总阅读：{data.get('note_views', 0):,}

━━━━━━━━━━━━━━━━━━━━
生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
数据来源：小红书专业版（浏览器抓取）
"""
    return report


def main():
    """主函数"""
    logger.info("=" * 60)
    logger.info("开始执行小红书数据浏览器抓取")
    logger.info("=" * 60)

    if not PLAYWRIGHT_AVAILABLE:
        logger.error("❌ Playwright 未安装")
        logger.error("请运行：pip install playwright")
        logger.error("然后运行：playwright install chromium")
        return

    scraper = XiaohongshuScraper(chrome_port=15264)

    # 连接 Chrome
    if not scraper.connect_to_chrome():
        logger.error("❌ 无法连接 Chrome")
        logger.error("请确保 Chrome 已启动（端口 15264）")
        return

    try:
        # 检查登录
        if not scraper.check_login():
            logger.error("❌ 未登录，请在浏览器中扫码登录")
            logger.error("登录后重新运行此程序")
            return

        # 抓取数据
        data = scraper.scrape_data()

        # 生成报告
        report = generate_report(data)

        # 保存报告
        data_dir = Path('data')
        data_dir.mkdir(exist_ok=True)
        report_path = data_dir / f"report_{data['date']}.txt"
        
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(report)

        logger.info(f"✅ 报告已保存到 {report_path}")
        print("\n" + report)

    finally:
        scraper.close()

    logger.info("✅ 数据抓取完成")
    logger.info("=" * 60)


if __name__ == "__main__":
    main()
