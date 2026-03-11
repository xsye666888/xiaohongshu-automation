@echo off
chcp 65001 >nul
echo ========================================
echo 小红书自动化分析器 - 运行程序
echo ========================================
echo.
echo 开始执行数据分析...
echo.

python analyzer.py

echo.
echo ========================================
echo 执行完成！
echo ========================================
echo.
echo 报告已保存到：data\report_*.txt
echo 日志文件：logs\xiaohongshu_analyzer.log
echo.
pause
