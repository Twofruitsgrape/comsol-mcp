@echo off
echo ========================================
echo   启动 COMSOL 实时显示模式
echo ========================================

REM 读取配置
call "%~dp0..\config\comsol_path.bat"

echo.
echo [1/2] 启动 COMSOL Server...
start "COMSOL Server" "%COMSOL_PATH%\bin\win64\comsolmphserver.exe" -port 2036 -multi on -graphics

echo 等待服务器启动 (10秒)...
timeout /t 10 /nobreak > nul

echo.
echo [2/2] 启动 COMSOL Desktop...
start "COMSOL Desktop" "%COMSOL_PATH%\bin\win64\comsolmphclient.exe" -host 127.0.0.1 -port 2036

echo.
echo ========================================
echo   启动完成！
echo ========================================
echo.
echo COMSOL Server: localhost:2036
echo COMSOL Desktop: 已打开
echo.
echo 现在可以使用 Python 连接 COMSOL 了
echo 所有操作都会在 Desktop 中实时显示！
echo.
echo 按任意键退出此窗口...
pause > nul
