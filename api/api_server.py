#!/usr/bin/env python
# -*- coding: utf-

"""
服务器 - 基于FRIDAY大模型平台
提供RESTful API接口，供前端Web界面调用
"""

import os
import json
import socket
import getpass
import sys
from flask import Flask, request, jsonify
from flask_cors import CORS
from api.meituan_agent import MeituanAIAgent
from api.conversation_manager import ConversationManager
from api.models_config import SUPPORTED_MODELS, DEFAULT_MODEL, get_models_by_category, is_model_supported, get_model_info
from api import config
from mcp import MCPManager

# 初始化Flask应用
app = Flask(__name__)
# 允许跨域请求，方便本地开发
CORS(app)

# 检查配置
if not config.is_configured():
    print("\n=== 首次运行配置 ===")
    print("配置文件不存在或未正确配置")
    print("请确保config.json文件包含正确的租户ID和应用ID")
    print("您可以通过以下方式配置：")
    print("1. 手动编辑config.json文件")
    print("2. 设置环境变量FRIDAY_TENANT_ID和FRIDAY_APP_ID")
    print("3. 运行setup.sh脚本进行配置")
    
    # 从环境变量读取
    tenant_id = os.environ.get("FRIDAY_TENANT_ID", "")
    app_id = os.environ.get("FRIDAY_APP_ID", "")
    
    if not tenant_id or not app_id:
        print("\n错误: 未提供租户ID或应用ID")
        print("您需要提供有效的租户ID和应用ID才能使用FRIDAY大模型平台")
        print("如果您没有租户ID和应用ID，请联系管理员获取")
        sys.exit(1)
    
    config.configure(tenant_id, app_id)
    print("配置已保存到config.json文件")

# 创建AI Agent实例
agent = MeituanAIAgent()

# 创建对话管理器
conversation_manager = ConversationManager()

# 创建MCP管理器
mcp_manager = MCPManager()
mcp_manager.start()

# 预定义角色列表
predefined_roles = {
    "assistant": "你是美团AI助手，基于FRIDAY大模型平台，请提供专业、准确、有帮助的回答。",
    "programmer": "你是一位经验丰富的程序员，擅长解决各种编程问题，并能提供清晰的代码示例和解释。",
    "creative": "你是一位创意顾问，擅长提供创新的想法和解决方案，思维开放且富有想象力。"
}

# 加载自定义角色
try:
    role_file = os.path.join(os.path.dirname(__file__), '..', 'custom_roles.json')
    if os.path.exists(role_file):
        with open(role_file, 'r', encoding='utf-8') as f:
            saved_roles = json.load(f)
            # 更新预定义角色列表，但不覆盖内置角色
            for role_name, role_prompt in saved_roles.items():
                if role_name not in predefined_roles or role_name not in ["assistant", "programmer", "creative"]:
                    predefined_roles[role_name] = role_prompt
except Exception as e:
    print(f"加载自定义角色失败: {e}")

# 存储当前会话的消息历史
current_messages = [
    {"role": "system", "content": predefined_roles["assistant"]}
]

# 当前角色
current_role = "assistant"

@app.route('/api/role', methods=['GET'])
def get_role():
    """获取当前角色和所有预定义角色"""
    global current_role

    return jsonify({
        "current_role": current_role,
        "predefined_roles": {k: v.split('，')[0] for k, v in predefined_roles.items()}  # 只返回角色描述的第一部分作为简短描述
    })

@app.route('/api/role', methods=['POST'])
def set_role():
    """设置AI角色"""
    global current_messages, current_role

    data = request.json
    if data is None:
        data = {}  # 如果没有JSON数据，使用空字典

    role_type = data.get('type', 'assistant')  # 默认为助手角色
    custom_prompt = data.get('custom_prompt', '')

    # 如果是预定义角色
    if role_type in predefined_roles and not custom_prompt:
        system_content = predefined_roles[role_type]
        current_role = role_type
    # 如果是自定义角色
    elif custom_prompt:
        system_content = custom_prompt
        current_role = "custom"
    # 默认回退到助手角色
    else:
        system_content = predefined_roles["assistant"]
        current_role = "assistant"

    # 更新系统消息
    if current_messages and current_messages[0]["role"] == "system":
        current_messages[0]["content"] = system_content
    else:
        current_messages = [{"role": "system", "content": system_content}] + current_messages

    return jsonify({
        "success": True, 
        "role": current_role,
        "system_content": system_content
    })

@app.route('/api/chat', methods=['POST'])
def chat():
    """处理聊天请求"""
    global current_messages

    # 获取请求数据
    data = request.json
    user_message = data.get('message', '')
    model = data.get('model', DEFAULT_MODEL)
    web_search = data.get('web_search', False)

    # 验证模型是否支持
    if not is_model_supported(model):
        print(f"错误: 不支持的模型: {model}")
        print(f"支持的模型列表: {list(SUPPORTED_MODELS.keys())}")
        return jsonify({"error": f"不支持的模型: {model}"}), 400

    if not user_message:
        return jsonify({"error": "消息不能为空"}), 400

    # 添加用户消息到历史
    current_messages.append({"role": "user", "content": user_message})

    # 记录请求信息
    print(f"处理聊天请求: 模型={model}, 消息长度={len(user_message)}")
    
    # 获取模型信息
    model_info = get_model_info(model)
    print(f"模型信息: {json.dumps(model_info, ensure_ascii=False)}")

    try:
        # 发送请求到AI
        print(f"开始请求模型 {model}...")
        response = agent.chat(current_messages, model=model)
        print(f"模型 {model} 请求完成")

        if "choices" in response and len(response["choices"]) > 0:
            ai_message = response["choices"][0]["message"]["content"]
            print(f"AI回复长度: {len(ai_message)}")

            current_messages.append({"role": "assistant", "content": ai_message})

            return jsonify({
                "message": ai_message,
                "history": current_messages,
                "model": model,
                "model_info": model_info
            })
        else:
            print(f"错误: 无法解析AI回复: {json.dumps(response, ensure_ascii=False)}")
            return jsonify({
                "error": "无法解析AI回复", 
                "response": response,
                "model": model
            }), 500

    except Exception as e:
        import traceback
        error_traceback = traceback.format_exc()
        print(f"错误: 请求处理失败: {str(e)}")
        print(f"错误详情: {error_traceback}")
        
        # 返回更详细的错误信息
        return jsonify({
            "error": f"请求处理失败: {str(e)}",
            "model": model,
            "traceback": error_traceback.split("\n")[-5:] if error_traceback else None
        }), 500

# 添加MCP相关的API接口
@app.route('/api/mcp/servers', methods=['GET'])
def get_mcp_servers():
    """获取可用的MCP服务器列表"""
    servers = mcp_manager.get_available_servers()
    status = mcp_manager.get_connection_status()
    
    result = []
    for server_id in servers:
        result.append({
            "id": server_id,
            "status": status.get(server_id, "disconnected")
        })
    
    return jsonify({
        "servers": result
    })

@app.route('/api/mcp/servers/<server_id>/connect', methods=['POST'])
def connect_mcp_server(server_id):
    """连接到指定的MCP服务器"""
    if not mcp_manager.is_server_available(server_id):
        return jsonify({
            "success": False,
            "error": f"MCP服务器不存在: {server_id}"
        }), 404
    
    success = mcp_manager.connect_to_server(server_id)
    
    return jsonify({
        "success": success,
        "status": mcp_manager.get_connection_status(server_id).get(server_id, "unknown")
    })

@app.route('/api/mcp/servers/<server_id>/disconnect', methods=['POST'])
def disconnect_mcp_server(server_id):
    """断开与指定MCP服务器的连接"""
    success = mcp_manager.disconnect_from_server(server_id)
    
    return jsonify({
        "success": success,
        "status": mcp_manager.get_connection_status(server_id).get(server_id, "unknown")
    })

@app.route('/api/mcp/servers', methods=['POST'])
def add_mcp_server():
    """添加MCP服务器配置"""
    data = request.json
    if not data:
        return jsonify({
            "success": False,
            "error": "请求数据不能为空"
        }), 400
    
    server_id = data.get('id')
    server_config = data.get('config')
    
    if not server_id or not server_config:
        return jsonify({
            "success": False,
            "error": "服务器ID和配置不能为空"
        }), 400
    
    success = mcp_manager.add_server(server_id, server_config)
    
    return jsonify({
        "success": success
    })

@app.route('/api/mcp/servers/<server_id>', methods=['DELETE'])
def remove_mcp_server(server_id):
    """移除MCP服务器配置"""
    success = mcp_manager.remove_server(server_id)
    
    return jsonify({
        "success": success
    })

@app.route('/api/image', methods=['POST'])
def generate_image():
    """处理图像生成请求"""
    # 获取请求数据
    data = request.json
    prompt = data.get('prompt', '')
    size = data.get('size', '1024x1024')
    model = data.get('model', 'dall-e-3')
    quality = data.get('quality', 'standard')
    style = data.get('style', 'vivid')
    n = data.get('n', 1)

    if not prompt:
        return jsonify({"error": "图像描述不能为空"}), 400

    try:
        # 发送图像生成请求
        response = agent.generate_image(
            prompt=prompt,
            model=model,
            size=size,
            quality=quality,
            style=style,
            n=n
        )

        # 检查是否成功
        if "data" in response and len(response["data"]) > 0:
            image_data = response["data"][0]
            image_url = image_data.get("url")
            revised_prompt = image_data.get("revised_prompt")

            result = {"url": image_url}
            if revised_prompt:
                result["revised_prompt"] = revised_prompt

            return jsonify(result)

        # 如果没有成功，返回错误信息
        return jsonify({"error": "图像生成失败", "response": response}), 500

    except Exception as e:
        return jsonify({"error": f"图像生成请求处理失败: {str(e)}"}), 500

@app.route('/api/conversations', methods=['GET'])
def list_conversations():
    """获取保存的对话列表"""
    try:
        conversations = conversation_manager.list_conversations()
        return jsonify(conversations)
    except Exception as e:
        return jsonify({"error": f"获取对话列表失败: {str(e)}"}), 500

@app.route('/api/conversations', methods=['POST'])
def save_conversation():
    """保存当前对话"""
    global current_messages

    # 获取请求数据
    data = request.json
    title = data.get('title', None)

    try:
        filepath = conversation_manager.save_conversation(current_messages, title)
        return jsonify({"success": True, "filepath": filepath})
    except Exception as e:
        return jsonify({"error": f"保存对话失败: {str(e)}"}), 500

@app.route('/api/conversations/<path:filename>', methods=['GET'])
def load_conversation(filename):
    """加载保存的对话"""
    global current_messages, current_role

    try:
        loaded_messages = conversation_manager.load_conversation(filename)
        if loaded_messages:
            current_messages = loaded_messages
            
            # 更新当前角色
            if loaded_messages and loaded_messages[0]["role"] == "system":
                system_content = loaded_messages[0]["content"]
                # 尝试根据系统消息内容匹配角色
                matched_role = None
                for role_name, role_prompt in predefined_roles.items():
                    if system_content == role_prompt:
                        matched_role = role_name
                        break
                
                # 如果找到匹配的角色，更新当前角色
                if matched_role:
                    current_role = matched_role
                else:
                    # 如果没有匹配的角色，设置为自定义角色
                    current_role = "custom"
            
            return jsonify({
                "success": True, 
                "messages": current_messages,
                "current_role": current_role
            })
        else:
            return jsonify({"error": "对话加载失败或为空"}), 404
    except Exception as e:
        return jsonify({"error": f"加载对话失败: {str(e)}"}), 500

@app.route('/api/conversations/<path:filename>', methods=['DELETE'])
def delete_conversation(filename):
    """删除保存的对话"""
    try:
        success = conversation_manager.delete_conversation(filename)
        if success:
            return jsonify({"success": True, "message": f"对话 '{filename}' 已删除"})
        else:
            return jsonify({"error": f"对话 '{filename}' 删除失败"}), 404
    except Exception as e:
        return jsonify({"error": f"删除对话失败: {str(e)}"}), 500

@app.route('/api/conversations/clear', methods=['POST'])
def clear_conversation():
    """清除当前对话历史"""
    global current_messages, current_role

    # 完全清除对话历史，只保留系统消息
    current_messages = [
        {"role": "system", "content": predefined_roles[current_role]}
    ]

    return jsonify({"success": True, "messages": current_messages})

@app.route('/api/role/save', methods=['POST'])
def save_custom_role():
    """保存自定义角色到预定义角色列表"""
    global predefined_roles

    data = request.json
    role_name = data.get('name', '')
    role_prompt = data.get('prompt', '')

    if not role_name or not role_prompt:
        return jsonify({"error": "角色名称和提示词不能为空"}), 400

    # 检查角色名称是否已存在
    if role_name in predefined_roles:
        return jsonify({"error": f"角色名称 '{role_name}' 已存在"}), 400

    # 添加到预定义角色列表
    predefined_roles[role_name] = role_prompt
    # 保存到文件中，确保重启后仍然可用
    try:
        role_file = os.path.join(os.path.dirname(__file__), '..', 'custom_roles.json')
        with open(role_file, 'w', encoding='utf-8') as f:
            json.dump(predefined_roles, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"保存角色文件失败: {e}")

    return jsonify({
        "success": True,
        "message": f"角色 '{role_name}' 已保存",
        "predefined_roles": {k: v.split('，')[0] for k, v in predefined_roles.items()}
    })

@app.route('/api/role/delete', methods=['POST'])
def delete_custom_role():
    """删除预设角色"""
    global predefined_roles

    data = request.json
    role_name = data.get('name', '')

    if not role_name:
        return jsonify({"error": "角色名称不能为空"}), 400

    # 检查角色是否存在
    if role_name not in predefined_roles:
        return jsonify({"error": f"角色 '{role_name}' 不存在"}), 404

    # 检查是否是内置角色（不允许删除内置角色）
    if role_name in ["assistant", "programmer", "creative"]:
        return jsonify({"error": f"不能删除内置角色 '{role_name}'"}), 403

    # 从预定义角色列表中删除
    del predefined_roles[role_name]

    # 保存到文件中，确保重启后仍然可用
    try:
        role_file = os.path.join(os.path.dirname(__file__), '..', 'custom_roles.json')
        with open(role_file, 'w', encoding='utf-8') as f:
            json.dump(predefined_roles, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"保存角色文件失败: {e}")

    return jsonify({
        "success": True,
        "message": f"角色 '{role_name}' 已删除",
        "predefined_roles": {k: v.split('，')[0] for k, v in predefined_roles.items()}
    })

@app.route('/api/models', methods=['GET'])
def get_models():
    """获取支持的模型列表"""
    # 按类别分组模型
    models_by_category = get_models_by_category()

    return jsonify({
        "models": SUPPORTED_MODELS,
        "models_by_category": models_by_category,
        "default_model": DEFAULT_MODEL
    })

def is_port_available(port):
    """
    检查端口是否可用

    Args:
        port: 要检查的端口号

    Returns:
        如果端口可用则返回True，否则返回False
    """
    try:
        # 尝试绑定端口
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(('127.0.0.1', port))
            return True
    except socket.error:
        return False

if __name__ == '__main__':
    import argparse
    import sys
    import psutil

    # 解析命令行参数
    parser = argparse.ArgumentParser(description='美团AI Agent API服务器')
    parser.add_argument('--port', type=int, default=5001, help='服务器端口号')
    args = parser.parse_args()

    port = args.port
    print(f"准备启动API服务器，端口: {port}")

    # 检查端口是否被占用
    def check_port_in_use(port):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            return s.connect_ex(('localhost', port)) == 0

    if check_port_in_use(port):
        print(f"端口 {port} 已被占用")
        
        # 查找占用端口的进程
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                for conns in proc.connections(kind='inet'):
                    if conns.laddr.port == port:
                        print(f"占用端口的进程: PID={proc.info['pid']}, 名称={proc.info['name']}")
                        user_input = input(f"是否终止该进程? (y/n): ")
                        if user_input.lower() == 'y':
                            try:
                                proc.terminate()
                                print(f"进程 {proc.info['pid']} 已终止")
                                # 等待进程终止
                                proc.wait(timeout=3)
                                print("端口已释放，继续启动服务器")
                            except psutil.NoSuchProcess:
                                print("进程已不存在")
                            except psutil.AccessDenied:
                                print("没有权限终止该进程，请手动终止")
                                sys.exit(1)
                            except Exception as e:
                                print(f"终止进程时出错: {e}")
                                sys.exit(1)
                        else:
                            print("用户取消，退出程序")
                            sys.exit(1)
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass
    
    print(f"API服务器正在启动，端口: {port}")

    # 启动服务器
    app.run(debug=False, port=port)
