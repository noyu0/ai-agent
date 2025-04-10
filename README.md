# AI Agent - 基于FRIDAY大模型平台

这是一个基于美团FRIDAY大模型平台的AI Agent项目，提供Web界面，支持对话和图像生成功能。

## 项目结构

- `api/`: 后端API服务器和核心功能实现
  - `api_server.py`: 后端API服务器，基于Flask
  - `meituan_agent.py`: AI Agent核心实现，基于FRIDAY大模型平台
  - `conversation_manager.py`: 对话历史管理器
  - `config.py`: 配置管理
- `web/`: 前端React应用
- `scripts/`: 启动脚本和工具脚本
  - `start_api_server.sh`: 启动后端API服务器的脚本
  - `start_frontend.sh`: 启动前端应用的脚本
  - `start_app.sh`: 同时启动后端和前端的脚本
  - `setup.sh`: 安装脚本
- `docs/`: 文档
- `conversations/`: 保存的对话历史
- `config.json`: 配置文件，存储租户ID和应用ID

## 功能特点

- 基于美团FRIDAY大模型平台的AI对话功能
- 支持OpenAI兼容API接口
- 支持图像生成（DALL-E 3）
- 提供Web界面
- 支持对话历史管理
- 支持保存和加载对话历史
- 支持自定义角色和角色管理
- 支持多种大模型选择
- 支持联网搜索功能（对于支持联网的模型）

## 快速开始

### 环境准备

1. 克隆仓库：
\`\`\`bash
git clone https://github.com/yourusername/meituan-ai-agent.git
cd meituan-ai-agent
\`\`\`

2. 运行安装脚本：
\`\`\`bash
./scripts/setup.sh
\`\`\`

### 运行Web界面

使用一键启动脚本：
\`\`\`bash
./scripts/start_app.sh
\`\`\`

或者分别启动后端和前端：

1. 启动后端API服务器：
\`\`\`bash
./scripts/start_api_server.sh
\`\`\`

2. 启动前端React应用：
\`\`\`bash
./scripts/start_frontend.sh
\`\`\`

### 首次运行配置

首次运行时，系统会要求您输入FRIDAY大模型平台的租户ID和应用ID。这些信息将保存在`config.json`文件中，您可以随时修改。

如果您没有这些信息，请联系管理员或访问FRIDAY大模型平台获取。

## Web界面功能

- 简洁美观的聊天界面，类似微信风格
- 支持选择不同的大模型
- 支持联网搜索功能（对于支持联网的模型）
- 支持自定义角色和角色管理
- 支持图像生成，可调整尺寸、质量和风格
- 支持保存和加载对话历史

## 技术栈

- 前端：React、Ant Design
- 后端：Flask、Python
- API：FRIDAY大模型平台OpenAI兼容API

## 贡献指南

欢迎提交Issue和Pull Request！

## 许可证

MIT License