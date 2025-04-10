#!/bin/bash

# 美团AI Agent Web界面启动脚本

echo "=== 启动美团AI Agent Web界面 ==="
echo "=== 作者: zjf ==="
echo ""

# 定义项目根目录
PROJECT_ROOT="/Users/zhengjinfeng05/ai_projects/meituan-ai-agent"
cd $PROJECT_ROOT

# 输出调试信息
echo "当前工作目录: $(pwd)"
echo "检查目录是否存在:"
echo "env目录: $([ -d "$PROJECT_ROOT/env" ] && echo "存在" || echo "不存在")"
echo "web目录: $([ -d "$PROJECT_ROOT/web" ] && echo "存在" || echo "不存在")"
echo "api目录: $([ -d "$PROJECT_ROOT/api" ] && echo "存在" || echo "不存在")"
echo ""

# 定义项目相关的进程标识
API_PROCESS_SIGNATURE="api.api_server"
FRONTEND_PROCESS_SIGNATURE="react-scripts/scripts/start.js"
# 定义变量
API_PORT=5001
DEBUG_API_PORT=5002  # 调试模式API端口
PROJECT_DIR=$PROJECT_ROOT
DEV_MODE=false  # 默认不启用开发模式

# 解析命令行参数
while [[ $# -gt 0 ]]; do
  case $1 in
    --dev)
      DEV_MODE=true
      shift
      ;;
    *)
      shift
      ;;
  esac
done

# 如果是开发模式，输出提示
if [ "$DEV_MODE" = true ]; then
  echo "=== 开发模式已启用 ==="
  echo "主API服务器将在端口 $API_PORT 运行"
  echo "调试API服务器将在端口 $DEBUG_API_PORT 运行"
  echo ""
fi

# 定义全局变量，用于跟踪是否正在关闭
SHUTTING_DOWN=false

# 检查进程是否属于当前项目
is_project_process() {
  local pid=$1
  local process_info=$(ps -p $pid -o command= 2>/dev/null)

  # 检查进程命令是否包含项目特征
  if [[ "$process_info" == *"$API_PROCESS_SIGNATURE"* ]] ||
     [[ "$process_info" == *"$FRONTEND_PROCESS_SIGNATURE"* ]] ||
     [[ "$process_info" == *"$PROJECT_DIR"* ]]; then
    return 0  # 是项目进程
  else
    return 1  # 不是项目进程
  fi
}

# 智能端口检查和清理
check_and_clean_port() {
  local port=$1
  local force=$2
  local max_attempts=3  # 最大尝试次数，防止死循环
  local attempt=1


  echo "检查端口 $port..."
  local pid=$(lsof -t -i:$port 2>/dev/null)


  while [ ! -z "$pid" ] && [ $attempt -le $max_attempts ]; do
    if is_project_process $pid || [ "$force" = "true" ]; then
      echo "端口 $port 被本项目进程 $pid 占用，正在释放... (尝试 $attempt/$max_attempts)"
      kill -15 $pid 2>/dev/null  # 先尝试正常终止
      sleep 2


      # 如果进程仍然存在，尝试强制终止
      if ps -p $pid > /dev/null 2>&1; then
        echo "进程 $pid 仍在运行，尝试强制终止..."
        kill -9 $pid 2>/dev/null
        sleep 1
      fi


      # 再次检查端口是否已释放
      pid=$(lsof -t -i:$port 2>/dev/null)
      attempt=$((attempt + 1))
    else
      if [ "$force" = "true" ]; then
        echo "警告: 端口 $port 被非项目进程 $pid 占用，尝试强制释放..."
        kill -9 $pid 2>/dev/null
        sleep 1
        pid=$(lsof -t -i:$port 2>/dev/null)
        attempt=$((attempt + 1))
      else
        echo "警告: 端口 $port 被非项目进程 $pid 占用"
        read -p "是否强制释放该端口? (y/n): " force_release
        if [[ $force_release == "y" || $force_release == "Y" ]]; then
          kill -9 $pid 2>/dev/null
          sleep 1
          pid=$(lsof -t -i:$port 2>/dev/null)
          attempt=$((attempt + 1))
        else
          echo "端口 $port 仍被占用，请选择其他端口或手动释放"
          return 1
        fi
      fi
    fi
  done


  if [ ! -z "$pid" ] && [ $attempt -gt $max_attempts ]; then
    echo "错误: 无法释放端口 $port，已达到最大尝试次数"
    return 1
  fi


  return 0
}

# 清理函数
cleanup() {
  # 防止重复执行清理
  if [ "$SHUTTING_DOWN" = true ]; then
    return
  fi


  SHUTTING_DOWN=true
  echo "正在停止应用..."


  # 停止监控进程
  if [ ! -z "$MONITOR_PID" ]; then
    echo "停止文件监控进程..."
    kill $MONITOR_PID 2>/dev/null || true
  fi


  # 杀死已知的前端和后端进程

  # 停止API服务器
  if [ ! -z "$API_PID" ]; then
    echo "停止API服务器进程..."
    kill $API_PID 2>/dev/null || true
    # 等待进程终止
    for i in {1..5}; do
      if ! ps -p $API_PID > /dev/null 2>&1; then
        break
      fi
      sleep 1
    done
    # 如果进程仍然存在，强制终止
    sleep 2
    if ps -p $API_PID > /dev/null 2>&1; then
      echo "API服务器进程未响应，强制终止..."
      kill -9 $API_PID 2>/dev/null || true
    fi
  fi

  # 如果存在调试API服务器，也停止它
  if [ ! -z "$DEBUG_API_PID" ]; then
    echo "停止调试API服务器进程..."
    kill $DEBUG_API_PID 2>/dev/null || true
    # 等待进程终止
    for i in {1..5}; do
      if ! ps -p $DEBUG_API_PID > /dev/null 2>&1; then
        break
      fi
      sleep 1
    done
    # 如果进程仍然存在，强制终止
    sleep 2
    if ps -p $DEBUG_API_PID > /dev/null 2>&1; then
      echo "调试API服务器进程未响应，强制终止..."
      kill -9 $DEBUG_API_PID 2>/dev/null || true
    fi
  fi

  # 停止前端应用
  if [ ! -z "$FRONTEND_PID" ]; then
    echo "停止前端应用进程..."
    kill $FRONTEND_PID 2>/dev/null || true
    # 等待进程终止
        for i in {1..5}; do
      if ! ps -p $FRONTEND_PID > /dev/null 2>&1; then
            break
          fi
          sleep 1
        done
        # 如果进程仍然存在，强制终止
    sleep 2
    if ps -p $FRONTEND_PID > /dev/null 2>&1; then
      echo "前端应用进程未响应，强制终止..."
      kill -9 $FRONTEND_PID 2>/dev/null || true
        fi
      fi


  # 查找并终止所有相关进程，但不要陷入死循环
  echo "查找并终止所有相关进程..."
  pkill -f "$API_PROCESS_SIGNATURE" 2>/dev/null || true
  pkill -f "$FRONTEND_PROCESS_SIGNATURE" 2>/dev/null || true

  # 查找并终止所有可能的Python进程
  pids=$(ps aux | grep "python" | grep -v "grep" | awk '{print $2}')
  for pid in $pids; do
    if is_project_process $pid; then
      echo "终止项目Python进程: $pid"
      kill -15 $pid 2>/dev/null || true
      sleep 1
      if ps -p $pid > /dev/null 2>&1; then
        kill -9 $pid 2>/dev/null || true
      fi
    fi
  done

  # 确保端口被释放，但限制尝试次数
  for port in 3000 5001 5002; do
    check_and_clean_port $port true
  done


  echo "应用已停止，所有端口已释放"

  echo "应用已停止"
  exit 0
}

# 监控文件变化的函数
monitor_file_changes() {
  local last_api_modified=$(stat -f "%m" api/api_server.py 2>/dev/null || echo 0)

  while [ "$SHUTTING_DOWN" = false ]; do
    sleep 5


    # 如果正在关闭，则退出循环
    if [ "$SHUTTING_DOWN" = true ]; then
      break
  fi


    # 检查API服务器文件是否被修改
    local current_api_modified=$(stat -f "%m" api/api_server.py 2>/dev/null || echo 0)
    if [ $current_api_modified -gt $last_api_modified ]; then
      echo "检测到API服务器文件变化，正在重启后端..."


      # 停止旧的API进程
      if [ ! -z "$API_PID" ]; then
        kill $API_PID 2>/dev/null || true
        # 等待进程终止
        for i in {1..5}; do
if ! ps -p $API_PID > /dev/null 2>&1; then
            break
fi
          sleep 1
        done
        # 如果进程仍然存在，强制终止
        if ps -p $API_PID > /dev/null 2>&1; then
          kill -9 $API_PID 2>/dev/null || true
fi
fi


      # 启动新的API进程
      source env/bin/activate
      PYTHONPATH=$(pwd) FLASK_DEBUG=0 python -m api.api_server --port $API_PORT &
      API_PID=$!
      echo "后端API服务器已重启，新PID: $API_PID"


      # 更新最后修改时间
      last_api_modified=$current_api_modified
    fi


    # 检查API进程是否仍在运行
    if [ ! -z "$API_PID" ] && ! ps -p $API_PID > /dev/null 2>&1; then
      # 如果不是正在关闭状态，才重启API
      if [ "$SHUTTING_DOWN" = false ]; then
        echo "检测到API服务器已停止，正在重启..."
        source env/bin/activate
        PYTHONPATH=$(pwd) FLASK_DEBUG=0 python -m api.api_server --port $API_PORT &
        API_PID=$!
        echo "后端API服务器已重启，新PID: $API_PID"
      fi
    fi

    # 如果是开发模式，检查调试API进程是否仍在运行
    if [ "$DEV_MODE" = true ] && [ ! -z "$DEBUG_API_PID" ] && ! ps -p $DEBUG_API_PID > /dev/null 2>&1; then
      # 如果不是正在关闭状态，才重启调试API
if [ "$SHUTTING_DOWN" = false ]; then
        echo "检测到调试API服务器已停止，正在重启..."
        source env/bin/activate
        PYTHONPATH=$(pwd) FLASK_DEBUG=1 python -m api.api_server --port $DEBUG_API_PORT &
        DEBUG_API_PID=$!
        echo "调试API服务器已重启，新PID: $DEBUG_API_PID"
      fi
    fi
  done


  echo "文件监控已停止"
}

# 注册清理函数
trap cleanup INT TERM EXIT

# 在启动前先清理可能的端口占用
echo "检查并清理可能的端口占用..."
for port in 3000 $API_PORT; do
  check_and_clean_port $port false || exit 1
done

# 如果是开发模式，也检查调试端口
if [ "$DEV_MODE" = true ]; then
  check_and_clean_port $DEBUG_API_PORT false || exit 1
fi

# 检查Python环境
if [ ! -d "$PROJECT_ROOT/env" ]; then
  echo "错误: 未找到虚拟环境 ($PROJECT_ROOT/env)"
  echo "请确保您已经创建了虚拟环境"
  exit 1
fi

# 检查前端目录
if [ ! -d "$PROJECT_ROOT/web" ]; then
  echo "错误: 未找到前端应用目录 ($PROJECT_ROOT/web)"
  exit 1
fi

if [ ! -d "$PROJECT_ROOT/api" ]; then
  echo "错误: 未找到后端API目录 ($PROJECT_ROOT/api)"
  exit 1
fi

if lsof -Pi :$API_PORT -sTCP:LISTEN -t >/dev/null ; then
  echo "警告: 端口 $API_PORT 已被占用"

  # 获取占用端口的进程ID
  PID=$(lsof -Pi :$API_PORT -sTCP:LISTEN -t)
  PROCESS_NAME=$(ps -p $PID -o comm=)

  echo "占用进程: PID=$PID, 名称=$PROCESS_NAME"

  # 检查是否是Python进程，可能是之前的API服务器
  if [[ "$PROCESS_NAME" == *"python"* ]]; then
    echo "检测到可能是之前的API服务器进程"
    read -p "是否终止该进程? (y/n): " KILL_PROCESS
    if [ "$KILL_PROCESS" = "y" ]; then
      echo "正在终止进程 $PID..."
      kill -9 $PID
      sleep 1
      if ! lsof -Pi :$API_PORT -sTCP:LISTEN -t >/dev/null ; then
        echo "端口 $API_PORT 已释放"
      else
        echo "错误: 无法释放端口 $API_PORT"
        exit 1
      fi
    else
      echo "用户取消，退出程序"
      exit 1
    fi
  else
    echo "错误: 端口 $API_PORT 被非项目进程占用，请手动释放该端口"
    exit 1
  fi
fi

# 保存端口号到文件
echo $API_PORT > $PROJECT_ROOT/api_port.txt
echo "API服务器将使用端口: $API_PORT"

# 如果前端目录存在，复制端口号到前端public目录
if [ -d "$PROJECT_ROOT/web/public" ]; then
  echo $API_PORT > $PROJECT_ROOT/web/public/api_port.txt
  echo "端口号已复制到前端public目录"
fi

echo "正在启动后端API服务器..."
source $PROJECT_ROOT/env/bin/activate
cd $PROJECT_ROOT
PYTHONPATH=$PROJECT_ROOT FLASK_DEBUG=0 python -m api.api_server --port $API_PORT &
API_PID=$!
echo "API服务器运行在: http://localhost:$API_PORT"

# 如果是开发模式，启动调试版本的API服务器
if [ "$DEV_MODE" = true ]; then
  echo "正在启动调试版本的API服务器..."
  PYTHONPATH=$PROJECT_ROOT FLASK_DEBUG=1 python -m api.api_server --port $DEBUG_API_PORT &
  DEBUG_API_PID=$!
  echo "调试API服务器运行在: http://localhost:$DEBUG_API_PORT"
fi

# 等待API服务器启动
echo "等待API服务器启动..."
sleep 3

# 检查API服务器是否成功启动
if ! ps -p $API_PID > /dev/null 2>&1; then
  echo "错误: API服务器启动失败"
  cleanup
  exit 1
fi

# 检查前端依赖
echo "检查前端依赖..."
cd $PROJECT_ROOT/web
if [ ! -d "node_modules" ]; then
  echo "正在安装前端依赖..."
  npm install
fi

# 启动前端应用
echo "启动前端应用..."
npm start &
FRONTEND_PID=$!
echo "前端应用已启动，PID: $FRONTEND_PID"
echo "前端应用运行在: http://localhost:3000"
echo ""

# 返回项目根目录
cd ..

# 启动文件监控
echo "启动文件变化监控..."
monitor_file_changes &
MONITOR_PID=$!

# 等待前端应用结束或用户中断
wait $FRONTEND_PID

# 如果前端应用自行结束，也执行清理
if [ "$SHUTTING_DOWN" = false ]; then
  echo "前端应用已停止，正在清理..."
  cleanup
fi