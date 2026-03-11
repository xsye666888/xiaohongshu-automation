@echo off
echo ========================================
echo 小红书自动化 - 配置定时任务
echo ========================================
echo.
echo 这将创建每天 9:00 自动运行的任务
echo.
pause

REM 获取当前目录
set SCRIPT_DIR=%~dp0

REM 创建定时任务
schtasks /create /tn "小红书数据自动化" /tr "python \"%SCRIPT_DIR%analyzer.py\"" /sc daily /st 09:00 /ru SYSTEM

if errorlevel 1 (
    echo.
    echo [错误] 创建定时任务失败，需要管理员权限
    echo.
    echo 请右键点击此文件，选择"以管理员身份运行"
    echo.
    pause
) else (
    echo.
    echo ========================================
    echo 定时任务创建成功！
    echo ========================================
    echo.
    echo 任务名称：小红书数据自动化
    echo 执行时间：每天 09:00
    echo.
    echo 查看任务：控制面板 → 管理工具 → 任务计划程序
    echo.
    pause
)
