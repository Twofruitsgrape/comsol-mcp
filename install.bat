@echo off
echo ========================================
echo   COMSOL MCP 安装脚本
echo ========================================

echo.
echo [1/3] 安装 Python 依赖...
pip install -r requirements.txt

echo.
echo [2/3] 配置 COMSOL 路径...
echo 请编辑 config\comsol_path.bat 设置你的 COMSOL 安装路径
echo.

echo [3/3] 安装完成!
echo.
echo ========================================
echo   使用方法
echo ========================================
echo.
echo 1. 启动 COMSOL:
echo    scripts\start_comsol.bat
echo.
echo 2. 运行示例:
echo    python examples\heat_transfer.py
echo    python examples\laminar_flow.py
echo    python examples\conjugate_heat.py
echo    python examples\transient_probe.py
echo.
echo 3. 在 AI Agent 中使用:
echo    说 "启动 COMSOL，我要做一个传热仿真"
echo.
echo ========================================
pause
