@echo off
chcp 65001 >nul
echo ========================================
echo 小红书数据浏览器抓取器 - 安装
echo ========================================
echo.

python --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未检测到 Python
    echo 请先安装：https://www.python.org/downloads/
    echo 安装时勾选 "Add Python to PATH"
    pause
    exit /b 1
)

echo [1/3] Python 已安装
python --version

echo.
echo [2/3] 安装依赖...
pip install -r requirements.txt

echo.
echo [3/3] 安装 Playwright 浏览器...
playwright install chromium

echo.
if not exist "data" mkdir data
if not exist "logs" mkdir logs

echo ========================================
echo 安装完成！
echo ========================================
echo.
echo 下一步：
echo 1. 确保 Chrome 已启动（端口 15264）
echo 2. 双击 run.bat 运行
echo.
pause
