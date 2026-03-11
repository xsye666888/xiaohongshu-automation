@echo off
chcp 65001 >nul
echo ========================================
echo 小红书数据浏览器抓取器
echo ========================================
echo.

cd /d "%~dp0"

echo 检查 Chrome 连接...
curl -s http://127.0.0.1:15264/json/version >nul 2>&1
if errorlevel 1 (
    echo [错误] 无法连接 Chrome (端口 15264)
    echo.
    echo 请先启动 Chrome：
    echo 1. 双击 chrome-stable.bat
    echo 2. 等待 Chrome 启动完成
    echo 3. 重新运行此脚本
    echo.
    pause
    exit /b 1
)

echo [1/2] Chrome 已连接
echo.
echo [2/2] 开始抓取数据...
echo.
python browser_scraper.py

echo.
echo ========================================
echo 运行完成！
echo ========================================
echo.
pause
