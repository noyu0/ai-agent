# API文档

## FRIDAY大模型平台API

FRIDAY大模型平台提供了OpenAI兼容的API接口，可以使用与OpenAI相同的调用方式。

### 配置信息

- 租户ID: 在config.json中配置
- 应用ID: 在config.json中配置
- API基础地址: 在config.json中配置
- OpenAI兼容API: 在config.json中配置

### 聊天接口

\`\`\`
POST {openai_api_base}/chat/completions
\`\`\`

请求头：
\`\`\`
Content-Type: application/json
Authorization: Bearer {app_id}
\`\`\`

请求体：
\`\`\`json
{
  "model": "gpt-3.5-turbo",
  "messages": [
    {"role": "system", "content": "你是美团AI助手"},
    {"role": "user", "content": "你好"}
  ],
  "temperature": 0.7
}
\`\`\`

### 图像生成接口

\`\`\`
POST {openai_api_base}/images/generations
\`\`\`

请求头：
\`\`\`
Content-Type: application/json
Authorization: Bearer {app_id}
\`\`\`

请求体：
\`\`\`json
{
  "model": "dall-e-3",
  "prompt": "一只可爱的猫",
  "size": "1024x1024",
  "quality": "standard",
  "style": "vivid",
  "n": 1
}
\`\`\`

参数说明：
- `model`: 使用的模型，目前只支持"dall-e-3"
- `prompt`: 图像描述
- `size`: 图像尺寸，支持"1024x1024"、"1792x1024"或"1024x1792"
- `quality`: 图像质量，支持"standard"或"hd"
- `style`: 图像风格，支持"vivid"(生动)或"natural"(自然)
- `n`: 生成图像的数量，目前只支持1

## 后端API服务器

后端API服务器提供了以下接口：

### 聊天接口

\`\`\`
POST /api/chat
\`\`\`

请求体：
\`\`\`json
{
  "message": "你好",
  "model": "LongCat-Plus",
  "web_search": false
}
\`\`\`

参数说明：
- `message`: 用户消息
- `model`: 使用的模型
- `web_search`: 是否启用联网搜索

### 图像生成接口

\`\`\`
POST /api/image
\`\`\`

请求体：
\`\`\`json
{
  "model": "dall-e-3",
  "prompt": "一只可爱的猫",
  "size": "1024x1024",
  "quality": "standard",
  "style": "vivid",
  "n": 1
}
\`\`\`

### 角色管理接口

#### 获取角色列表

\`\`\`
GET /api/role
\`\`\`

#### 设置角色

\`\`\`
POST /api/role
\`\`\`

请求体：
\`\`\`json
{
  "type": "assistant",
  "custom_prompt": ""
}
\`\`\`

或者：
\`\`\`json
{
  "type": "custom",
  "custom_prompt": "你是一位专业的旅游顾问，擅长推荐旅游路线和景点..."
}
\`\`\`

#### 保存自定义角色

\`\`\`
POST /api/role/save
\`\`\`

请求体：
\`\`\`json
{
  "name": "旅游顾问",
  "prompt": "你是一位专业的旅游顾问，擅长推荐旅游路线和景点..."
}
\`\`\`

#### 删除自定义角色

\`\`\`
POST /api/role/delete
\`\`\`

请求体：
\`\`\`json
{
  "name": "旅游顾问"
}
\`\`\`

### 对话管理接口

#### 清除对话

\`\`\`
POST /api/conversations/clear
\`\`\`

#### 保存对话

\`\`\`
POST /api/conversations
\`\`\`

请求体：
\`\`\`json
{
  "title": "对话标题"
}
\`\`\`

#### 获取对话列表

\`\`\`
GET /api/conversations
\`\`\`

#### 加载对话

\`\`\`
GET /api/conversations/{filename}
\`\`\`

## 客户端API

### MeituanAIAgent类

\`\`\`python
agent = MeituanAIAgent(tenant_id, app_id)
\`\`\`

#### 对话功能

\`\`\`python
response = agent.chat(messages, temperature=0.7, model="gpt-3.5-turbo")
\`\`\`

参数:
- `messages`: 对话历史列表，格式为 `[{"role": "user", "content": "你好"}]`
- `temperature`: 温度参数，控制随机性，默认0.7
- `model`: 使用的模型，默认为"gpt-3.5-turbo"

#### 图像生成

\`\`\`python
response = agent.generate_image(prompt, size="1024x1024", model="dall-e-3", quality="standard", style="vivid", n=1)
\`\`\`

参数:
- `prompt`: 图像描述
- `size`: 图像尺寸，支持"1024x1024"、"1792x1024"或"1024x1792"
- `model`: 使用的模型，目前只支持"dall-e-3"
- `quality`: 图像质量，支持"standard"或"hd"
- `style`: 图像风格，支持"vivid"(生动)或"natural"(自然)
- `n`: 生成图像的数量，目前只支持1

### ConversationManager类

\`\`\`python
manager = ConversationManager(save_dir="conversations")
\`\`\`

#### 保存对话

\`\`\`python
filepath = manager.save_conversation(messages, title=None)
\`\`\`

#### 加载对话

\`\`\`python
messages = manager.load_conversation(filepath)
\`\`\`

#### 列出对话

\`\`\`python
conversations = manager.list_conversations()
\`\`\`