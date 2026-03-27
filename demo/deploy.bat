@echo off
chcp 65001 >nul
echo ========================================
echo   汇通智融 - 业务数据系统部署脚本
echo ========================================
echo.

REM 检查 Python 是否安装
python --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未检测到 Python，请先安装 Python 3.8+
    pause
    exit /b 1
)

echo [1/4] Python 已安装
echo.

REM 安装依赖
echo [2/4] 正在安装依赖...
pip install -r requirements.txt
if errorlevel 1 (
    echo [错误] 依赖安装失败
    pause
    exit /b 1
)
echo 依赖安装完成
echo.

REM 配置防火墙
echo [3/4] 正在配置 Windows 防火墙...
netsh advfirewall firewall show rule name="FastAPI 8000" >nul 2>&1
if errorlevel 1 (
    echo 添加防火墙规则...
    netsh advfirewall firewall add rule name="FastAPI 8000" dir=in action=allow protocol=TCP localport=8000
    if errorlevel 1 (
        echo [警告] 防火墙规则添加失败，请手动配置
    ) else (
        echo 防火墙规则已添加
    )
) else (
    echo 防火墙规则已存在
)
echo.

REM 启动服务
echo [4/4] 正在启动服务...
echo.
echo ========================================
echo   服务已启动！
echo   本地访问：http://localhost:8000
echo   局域网访问：http://10.10.20.200:8000
echo.
echo   默认账号：admin
echo   默认密码：admin123
echo.
echo   按 Ctrl+C 停止服务
echo ========================================
echo.

python main.py

pause
