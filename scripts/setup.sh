#!/bin/bash

# 美团AI Agent 安装脚本

echo "=== 美团AI Agent 安装脚本 ==="
echo "=== 作者: zjf ==="
echo ""

# 获取脚本所在目录的绝对路径
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
# 获取项目根目录
PROJECT_ROOT="$( cd "$SCRIPT_DIR/.." && pwd )"

# 检查Python是否安装
if ! command -v python3 &> /dev/null; then
    echo "错误: 未找到Python 3，请先安装Python 3"
    exit 1
fi

# 检查pip是否安装
if ! command -v pip3 &> /dev/null; then
    echo "错误: 未找到pip3，请先安装pip3"
    exit 1
fi

# 检查Node.js是否安装
if ! command -v node &> /dev/null; then
    echo "错误: 未找到Node.js，请先安装Node.js"
    exit 1
fi

# 检查npm是否安装
if ! command -v npm &> /dev/null; then
    echo "错误: 未找到npm，请先安装npm"
    exit 1
fi

# 创建虚拟环境
echo "正在创建Python虚拟环境..."
cd "$PROJECT_ROOT"

# 检查是否已存在虚拟环境
if [ -d "$PROJECT_ROOT/env" ]; then
    echo "发现已存在的虚拟环境，是否重新创建? (y/n)"
    read -r answer
    if [ "$answer" = "y" ] || [ "$answer" = "Y" ]; then
        echo "正在删除旧的虚拟环境..."
        rm -rf "$PROJECT_ROOT/env"
        python3 -m venv env
    fi
else
    python3 -m venv env
fi

# 激活虚拟环境
source env/bin/activate

# 升级pip
echo "正在升级pip..."
pip install --upgrade pip

# 创建requirements.txt文件（如果不存在）
if [ ! -f "$PROJECT_ROOT/requirements.txt" ]; then
    echo "创建requirements.txt文件..."
    cat > "$PROJECT_ROOT/requirements.txt" << EOF
# 后端依赖
flask==2.0.1
flask-cors==3.0.10
requests==2.28.2
python-dotenv==0.19.2

# AI Agent 依赖
openai==1.3.0
langchain==0.0.335
langchain-openai==0.0.2
pydantic==2.4.2
tiktoken==0.5.1
numpy==1.24.3
pandas==2.0.3
scikit-learn==1.3.0

# 数据处理和存储
pymongo==4.5.0
redis==4.6.0
sqlalchemy==2.0.21

# 前端依赖在package.json中定义
EOF
fi

# 安装后端依赖
echo "正在安装后端依赖..."
pip install -r "$PROJECT_ROOT/requirements.txt"

# 检查依赖安装是否成功
if [ $? -ne 0 ]; then
    echo "警告: 部分依赖安装失败，请检查错误信息"
else
    echo "后端依赖安装成功"
fi

# 检查前端目录
if [ ! -d "$PROJECT_ROOT/web" ]; then
    echo "错误: 未找到前端目录 (web)"
    exit 1
fi

# 检查前端package.json
if [ ! -f "$PROJECT_ROOT/web/package.json" ]; then
    echo "警告: 未找到前端package.json文件，跳过前端依赖安装"
else
    # 安装前端依赖
    echo "正在安装前端依赖..."
    cd "$PROJECT_ROOT/web"
    npm install
    
    # 检查依赖安装是否成功
    if [ $? -ne 0 ]; then
        echo "警告: 部分前端依赖安装失败，请检查错误信息"
    else
        echo "前端依赖安装成功"
    fi
fi

# 返回项目根目录
cd "$PROJECT_ROOT"

# 创建必要的目录
mkdir -p conversations
mkdir -p images
mkdir -p logs
mkdir -p data

# 为MCP准备目录
mkdir -p mcp
touch mcp/__init__.py

# 创建.env文件（如果不存在）
if [ ! -f "$PROJECT_ROOT/.env" ]; then
    echo "创建.env文件..."
    cat > "$PROJECT_ROOT/.env" << EOF
# API配置
API_PORT=5001

# 大模型配置
FRIDAY_TENANT_ID=
FRIDAY_APP_ID=
FRIDAY_API_KEY=

# 数据库配置
DB_HOST=localhost
DB_PORT=27017
DB_NAME=meituan_ai_agent

# 日志配置
LOG_LEVEL=INFO
EOF
    echo "请在.env文件中填写您的FRIDAY大模型平台配置"
fi

echo "=== 安装完成 ==="
echo "现在可以使用以下命令启动应用:"
echo "1. 一键启动: ./scripts/start_app.sh"
echo "2. 分别启动:"
echo "   - 后端: ./scripts/start_api_server.sh"
echo "   - 前端: ./scripts/start_frontend.sh"
echo ""
echo "首次启动时，系统会要求您输入FRIDAY大模型平台的租户ID和应用ID"
echo "如果您没有这些信息，请联系管理员或访问FRIDAY大模型平台获取"
echo ""
echo "MCP开发准备就绪，您可以在mcp目录中开发MCP相关功能"
echo ""
echo "祝您使用愉快！"