@echo off
echo 启动 Chrome（远程调试端口 15264）...
echo.

start chrome.exe ^
    --remote-debugging-port=15264 ^
    --user-data-dir="%USERPROFILE%\.openclaw\chrome-profile" ^
    --no-sandbox ^
    --disable-gpu ^
    https://pro.xiaohongshu.com

echo.
echo Chrome 已启动！
echo.
echo 请在 Chrome 中：
echo 1. 扫码登录小红书专业版
echo 2. 登录后关闭窗口
echo 3. 运行 run.bat 抓取数据
echo.
pause
