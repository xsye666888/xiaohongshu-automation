@echo off
chcp 65001 >nul
echo ========================================
echo 小红书自动化分析器 - 安装程序
echo ========================================
echo.

REM 检查 Python 是否安装
python --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未检测到 Python，请先安装 Python 3.8+
    echo 下载地址：https://www.python.org/downloads/
    pause
    exit /b 1
)

echo [1/3] 检查 Python 环境... OK
python --version

echo.
echo [2/3] 安装依赖包...
pip install requests -q
if errorlevel 1 (
    echo [警告] 依赖安装失败，请手动运行：pip install requests
)

echo.
echo [3/3] 创建数据目录...
if not exist "data" mkdir data
if not exist "logs" mkdir logs

echo.
echo ========================================
echo 安装完成！
echo ========================================
echo.
echo 下一步：
echo 1. 编辑 config.json 配置飞书 Webhook（可选）
echo 2. 双击 run.bat 运行程序
echo 3. 配置定时任务每天自动执行
echo.
pause
