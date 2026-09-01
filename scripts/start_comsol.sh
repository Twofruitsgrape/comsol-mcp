#!/bin/bash

echo "========================================"
echo "  启动 COMSOL 实时显示模式"
echo "========================================"

# 读取配置
source "$(dirname "$0")/../config/comsol_path.sh"

echo ""
echo "[1/2] 启动 COMSOL Server..."
"$COMSOL_PATH/bin/comsolmphserver" -port 2036 -multi on -graphics &
SERVER_PID=$!

echo "等待服务器启动 (10秒)..."
sleep 10

echo ""
echo "[2/2] 启动 COMSOL Desktop..."
"$COMSOL_PATH/bin/comsolmphclient" -host 127.0.0.1 -port 2036 &
DESKTOP_PID=$!

echo ""
echo "========================================"
echo "  启动完成！"
echo "========================================"
echo ""
echo "COMSOL Server: localhost:2036 (PID: $SERVER_PID)"
echo "COMSOL Desktop: 已打开 (PID: $DESKTOP_PID)"
echo ""
echo "现在可以使用 Python 连接 COMSOL 了"
echo "所有操作都会在 Desktop 中实时显示！"
echo ""
echo "按 Ctrl+C 停止所有进程"

# 等待子进程
wait
