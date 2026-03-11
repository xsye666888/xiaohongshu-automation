# 小红书数据自动化抓取器

## 📋 功能

- ✅ 浏览器自动化抓取数据（无需 API）
- ✅ 复用已登录的 Chrome 会话
- ✅ 自动抓取 GMV、订单、粉丝数据
- ✅ 生成日报报告
- ✅ 飞书推送（可选）

## 🔧 安装

### 1. 安装依赖
```cmd
install.bat
```

### 2. 启动 Chrome
```cmd
chrome-stable.bat
```

### 3. 运行抓取
```cmd
run.bat
```

## 📁 文件说明

| 文件 | 说明 |
|------|------|
| `browser_scraper.py` | 主程序 |
| `config.json` | 配置文件 |
| `install.bat` | 安装脚本 |
| `run.bat` | 运行脚本 |
| `chrome-stable.bat` | 启动 Chrome |

## 🚀 使用说明

1. **首次运行**：先运行 `install.bat` 安装依赖
2. **启动 Chrome**：运行 `chrome-stable.bat`
3. **扫码登录**：在 Chrome 中打开小红书专业版并登录
4. **运行抓取**：运行 `run.bat` 抓取数据

## 📊 数据输出

- 报告保存在 `data/` 文件夹
- 日志保存在 `logs/` 文件夹
- 截图保存在 `logs/` 文件夹（调试用）

## ⚠️ 注意事项

1. Chrome 必须保持运行状态
2. 首次需要扫码登录
3. Cookie 会自动保存，下次无需重新登录
