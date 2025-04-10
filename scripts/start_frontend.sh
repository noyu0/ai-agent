#!/bin/bash

# 美团AI Agent 前端应用启动脚本
# 美团AI Agent Web前端启动脚本

echo "=== 启动美团AI Agent 前端应用 ==="
echo "=== 启动美团AI Agent Web前端 ==="
echo "=== 作者: zjf ==="
echo ""

# 获取脚本所在目录的绝对路径
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
# 获取项目根目录
PROJECT_ROOT="$( cd "$SCRIPT_DIR/.." && pwd )"

# 检查前端目录
if [ ! -d "meituan-ai-web" ]; then
  echo "错误: 未找到前端应用目录 (meituan-ai-web)"
if [ ! -d "../web" ]; then
if [ ! -d "$PROJECT_ROOT/web" ]; then
  echo "错误: 未找到前端应用目录 (web)"
  exit 1
fi

# 检查API端口文件
if [ -f "api_port.txt" ]; then
  PORT=$(cat api_port.txt)
if [ -f "$PROJECT_ROOT/api_port.txt" ]; then
  PORT=$(cat "$PROJECT_ROOT/api_port.txt")
  echo "检测到API服务器端口: $PORT"

  # 确保前端public目录存在
  if [ ! -d "meituan-ai-web/public" ]; then
    mkdir -p meituan-ai-web/public
  if [ ! -d "$PROJECT_ROOT/web/public" ]; then
    mkdir -p "$PROJECT_ROOT/web/public"
  fi

  # 复制端口文件到前端应用的public目录
  echo "复制端口信息到前端应用..."
  cp api_port.txt meituan-ai-web/public/
  cp "$PROJECT_ROOT/api_port.txt" "$PROJECT_ROOT/web/public/"
  echo "端口信息已复制到前端应用"
else
  echo "警告: 未找到API端口文件 (api_port.txt)"
  echo "前端应用可能无法连接到API服务器"
  echo "请确保先运行 start_api_server.sh 脚本"
fi

# 进入前端目录
cd meituan-ai-web
cd "$PROJECT_ROOT/web"

# 检查依赖
if [ ! -d "node_modules" ]; then
# 检查node_modules是否存在
if [ ! -d "../web/node_modules" ]; then
if [ ! -d "node_modules" ]; then
  echo "正在安装前端依赖..."
  cd ../web
  npm install
  if [ $? -ne 0 ]; then
    echo "错误: 安装前端依赖失败"
    exit 1
  fi
  cd ../scripts
fi

# 启动前端应用
echo "正在启动前端应用..."
cd ../web
npm start

# 注意：这个脚本不会在后台运行，而是直接在前台运行前端应用
# 要停止应用，按 Ctrl+C
# 如果前端应用异常退出，显示错误信息
if [ $? -ne 0 ]; then
  echo "错误: 前端应用启动失败"
  exit 1
fi