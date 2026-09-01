# COMSOL MCP 安装脚本
param([string] = "C:\Program Files\COMSOL\COMSOL62\Multiphysics")

Write-Host "COMSOL MCP 安装脚本" -ForegroundColor Cyan

# 检查管理员权限
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")
if (-not $isAdmin) {
    Write-Host "请以管理员身份运行此脚本！" -ForegroundColor Red
    exit 1
}

# 安装 Python 依赖
Write-Host "安装 Python 依赖..." -ForegroundColor Yellow
python -m pip install mph jpype1

# 安装 COMSOL MCP
Write-Host "安装 COMSOL MCP..." -ForegroundColor Yellow
pip install -e comsol_mcp

Write-Host "安装完成！" -ForegroundColor Green
