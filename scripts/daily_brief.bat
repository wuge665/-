# 科技简报定时任务脚本
# 用于Windows任务计划程序

@echo off
chcp 65001 >nul
echo ========================================
echo 科技简报自动生成系统
echo ========================================
echo [%date% %time%] 开始执行任务...
echo.

cd /d "%~dp0"

REM 检查Python环境
python --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未找到Python，请先安装Python 3.10+
    exit /b 1
)

REM 检查依赖
python -c "import feedparser" >nul 2>&1
if errorlevel 1 (
    echo [提示] 正在安装依赖...
    pip install -r requirements.txt -q
)

REM 执行主程序
python main.py --run

echo.
echo ========================================
echo [%date% %time%] 任务完成
echo ========================================
pause