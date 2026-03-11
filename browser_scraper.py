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
            'note_likes': 0,
            'note_collections': 0,
            'note_comments': 0,
            'note_shares': 0,
            'note_clicks': 0,
            'note_cart_adds': 0,
            'error': None
        }
        
        try:
            # 打开商品笔记页面
            logger.info("📈 打开商品笔记数据页面...")
            self.page.goto(f"{self.base_url}/app-datacenter/goods-note", timeout=30000, wait_until="domcontentloaded")
            time.sleep(5)
            
            # 使用文本定位查找数据卡片
            logger.info(" 抓取笔记互动数据...")
            
            # 阅读次数
            try:
                el = self.page.locator('text=阅读次数').locator('..').locator('..').first
                text = el.inner_text(timeout=5000)
                data['note_views'] = self._parse_number(text)
                logger.info(f"✅ 阅读次数：{data['note_views']}")
            except Exception as e:
                logger.warning(f"⚠️ 阅读次数抓取失败：{e}")
            
            # 点赞次数
            try:
                el = self.page.locator('text=点赞次数').locator('..').locator('..').first
                text = el.inner_text(timeout=5000)
                data['note_likes'] = self._parse_number(text)
                logger.info(f"✅ 点赞次数：{data['note_likes']}")
            except Exception as e:
                logger.warning(f"⚠️ 点赞次数抓取失败：{e}")
            
            # 收藏次数
            try:
                el = self.page.locator('text=收藏次数').locator('..').locator('..').first
                text = el.inner_text(timeout=5000)
                data['note_collections'] = self._parse_number(text)
                logger.info(f"✅ 收藏次数：{data['note_collections']}")
            except Exception as e:
                logger.warning(f"⚠️ 收藏次数抓取失败：{e}")
            
            # 评论次数
            try:
                el = self.page.locator('text=评论次数').locator('..').locator('..').first
                text = el.inner_text(timeout=5000)
                data['note_comments'] = self._parse_number(text)
                logger.info(f"✅ 评论次数：{data['note_comments']}")
            except Exception as e:
                logger.warning(f"⚠️ 评论次数抓取失败：{e}")
            
            # 分享次数
            try:
                el = self.page.locator('text=分享次数').locator('..').locator('..').first
                text = el.inner_text(timeout=5000)
                data['note_shares'] = self._parse_number(text)
                logger.info(f"✅ 分享次数：{data['note_shares']}")
            except Exception as e:
                logger.warning(f"⚠️ 分享次数抓取失败：{e}")
            
            # 笔记商品点击次数
            try:
                el = self.page.locator('text=笔记商品点击次数').locator('..').locator('..').first
                text = el.inner_text(timeout=5000)
                data['note_clicks'] = self._parse_number(text)
                logger.info(f"✅ 笔记商品点击次数：{data['note_clicks']}")
            except Exception as e:
                logger.warning(f"⚠️ 笔记商品点击次数抓取失败：{e}")
            
            # 笔记加购件数
            try:
                el = self.page.locator('text=笔记加购件数').locator('..').locator('..').first
                text = el.inner_text(timeout=5000)
                data['note_cart_adds'] = self._parse_number(text)
                logger.info(f"✅ 笔记加购件数：{data['note_cart_adds']}")
            except Exception as e:
                logger.warning(f"⚠️ 笔记加购件数抓取失败：{e}")
            
            # 截图保存
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

📝 笔记互动数据
  阅读次数：{int(data.get('note_views', 0)):,}
  点赞次数：{int(data.get('note_likes', 0)):,}
  收藏次数：{int(data.get('note_collections', 0)):,}
  评论次数：{int(data.get('note_comments', 0)):,}
  分享次数：{int(data.get('note_shares', 0)):,}

🛒 转化数据
  笔记商品点击：{int(data.get('note_clicks', 0)):,}
  笔记加购件数：{int(data.get('note_cart_adds', 0)):,}

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
