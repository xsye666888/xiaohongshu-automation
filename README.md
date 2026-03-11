# 小红书 API 自动化分析器

## 🚀 真正的自动化方案

**核心：使用小红书官方 API，无需浏览器！**

---

## 📋 配置步骤（只需 1 次）

### 1️⃣ 获取授权码

1. 访问小红书开放平台：https://open.xiaohongshu.com
2. 登录你的账号
3. 进入「应用管理」→ 选择你的应用
4. 点击「获取授权码」
5. 复制授权码

### 2️⃣ 编辑 config.json

```json
{
  "app_key": "40c04b9ceb4d40ab86ac",
  "app_secret": "805fc28716bf9bed9d2e1830f310054a",
  "authorization_code": "这里粘贴授权码",
  "feishu_webhook": "https://open.feishu.cn/open-apis/bot/v2/hook/xxx"
}
```

### 3️⃣ 安装依赖

```bash
pip install -r requirements.txt
```

### 4️⃣ 运行测试

```bash
python analyzer.py
```

### 5️⃣ 配置定时任务（每天 9:00）

```bash
crontab -e
# 添加：
0 9 * * * cd /path/to/xiaohongshu_api_automation && python analyzer.py
```

---

## ✅ 之后每天自动：

```
09:00 自动执行脚本
   ↓
调用小红书 API 抓取昨天数据
   ↓
AI 分析生成优化建议
   ↓
飞书推送日报
```

**你什么都不用做！**

---

## 📊 日报内容

```
📊 小红书店铺日报 - 悉世药业
━━━━━━━━━━━━━━━━━━━
日期：2026-03-11

💰 电商数据
  GMV: ¥1,256
  订单数：42
  转化率：13.3%

📝 笔记数据
  总阅读：8,542
  互动率：7.2%

👥 粉丝数据
  粉丝总数：3,456
  净增长：+38

💡 AI 优化建议
  1. GMV 表现优秀！
  2. 转化率正常
  3. 最佳发布时间：19:00-21:00
```

---

**版本：** v1.0 (API 版)  
**日期：** 2026-03-11
