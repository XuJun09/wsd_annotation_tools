@echo off
setlocal
chcp 65001

:: 检查是否安装了Python 3.11
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo 未检测到Python 3.11，请先安装Python 3.11。
    pause
    exit /b 1
)

:: 创建虚拟环境
python -m venv .venv

:: 激活虚拟环境
call .venv\Scripts\activate

:: 安装gradio和pandas
pip install gradio pandas

echo 安装完成。
pause