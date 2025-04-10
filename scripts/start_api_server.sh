#!/bin/bash

# 美团AI Agent API服务器启动脚本

echo "=== 启动美团AI Agent API服务器 ==="
echo "=== 作者: zjf ==="
echo ""

# 获取脚本所在目录的绝对路径
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
# 获取项目根目录
PROJECT_ROOT="$( cd "$SCRIPT_DIR/.." && pwd )"

# 检查Python环境
if [ ! -d "$PROJECT_ROOT/env" ]; then
  echo "错误: 未找到虚拟环境 (env)"
  echo "请确保您已经创建了虚拟环境"
  exit 1
fi

# 检查API服务器文件
if [ ! -f "$PROJECT_ROOT/api/api_server.py" ]; then
  echo "错误: 未找到API服务器文件 (api/api_server.py)"
  exit 1
fi

# 定义端口
PORT=5001
echo "API服务器将使用端口: $PORT"

# 激活虚拟环境并启动API服务器
echo "正在启动API服务器..."
cd "$PROJECT_ROOT"
source env/bin/activate
python -m api.api_server --port $PORT

# 如果API服务器异常退出，显示错误信息
if [ $? -ne 0 ]; then
  echo "错误: API服务器启动失败"
  exit 1
fi

# 等待用户中断
echo "按 Ctrl+C 停止API服务器"
wait $API_PID