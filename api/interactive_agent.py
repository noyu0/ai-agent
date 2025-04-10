#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
美团AI Agent交互式命令行界面 - 基于FRIDAY大模型平台
"""

import os
import json
import sys
from typing import List, Dict

# 导入我们的AI Agent类
from meituan_agent import MeituanAIAgent
from conversation_manager import ConversationManager
from config import TENANT_ID, APP_ID

def clear_screen():
    """清屏"""
    os.system('cls' if os.name == 'nt' else 'clear')

def print_header():
    """打印头部信息"""
    clear_screen()
    print("=" * 50)
    print("美团AI Agent交互式命令行 - 基于FRIDAY大模型平台")
    print("=" * 50)
    print("输入 'exit' 或 'quit' 退出程序")
    print("输入 'clear' 清除对话历史")
    print("输入 'save' 保存当前对话")
    print("输入 'list' 列出保存的对话")
    print("输入 'load:文件名' 加载保存的对话")
    print("输入 'image:你的描述' 生成图像")
    print("=" * 50)

def main():
    """主函数"""
    # 从配置文件读取租户ID和应用ID
    import config
    
    # 创建AI Agent实例
    agent = MeituanAIAgent()
    
    # 创建对话管理器
    conversation_manager = ConversationManager()
    
    # 初始化对话历史
    messages: List[Dict[str, str]] = [
        {"role": "system", "content": "你是美团AI助手，基于FRIDAY大模型平台，请提供专业、准确、有帮助的回答。"}
    ]
    
    print_header()
    
    while True:
        # 获取用户输入
        user_input = input("\n您: ")
        
        # 检查特殊命令
        if user_input.lower() in ['exit', 'quit']:
            print("\n感谢使用美团AI Agent，再见！")
            break
        
        elif user_input.lower() == 'clear':
            messages = [
                {"role": "system", "content": "你是美团AI助手，基于FRIDAY大模型平台，请提供专业、准确、有帮助的回答。"}
            ]
            print_header()
            print("\n对话历史已清除")
            continue
        
        elif user_input.lower() == 'save':
            # 保存当前对话
            title = input("\n请输入对话标题 (直接回车使用默认标题): ")
            filepath = conversation_manager.save_conversation(messages, title if title else None)
            print(f"\n对话已保存到: {filepath}")
            continue
        
        elif user_input.lower() == 'list':
            # 列出保存的对话
            conversations = conversation_manager.list_conversations()
            
            if not conversations:
                print("\n没有找到保存的对话")
                continue
            
            print("\n保存的对话列表:")
            for i, conv in enumerate(conversations):
                print(f"{i+1}. {conv['title']} - {conv['date']} ({conv['message_count']}条消息)")
            continue
        
        elif user_input.lower().startswith('load:'):
            # 加载保存的对话
            filename = user_input[5:].strip()
            
            try:
                loaded_messages = conversation_manager.load_conversation(filename)
                if loaded_messages:
                    messages = loaded_messages
                    print(f"\n已加载对话: {filename}")
                    
                    # 打印最后一条消息
                    if len(messages) > 1:
                        last_message = messages[-1]
                        role = last_message.get("role", "")
                        content = last_message.get("content", "")
                        print(f"\n最后一条消息 ({role}): {content[:100]}...")
                else:
                    print("\n对话加载失败或为空")
            except Exception as e:
                print(f"\n加载对话失败: {e}")
            continue
        
        # 检查是否是图像生成请求
        elif user_input.lower().startswith('image:'):
            image_prompt = user_input[6:].strip()
            print(f"\n正在生成图像: '{image_prompt}'...")
            
            try:
                response = agent.generate_image(image_prompt)
                print("\n图像生成结果:")
                
                # 检查是否成功
                if "data" in response and len(response["data"]) > 0:
                    image_url = response["data"][0].get("url")
                    if image_url:
                        print(f"\n生成的图像URL: {image_url}")
                    else:
                        print(f"\n图像URL不可用")
                else:
                    print(json.dumps(response, ensure_ascii=False, indent=2))
            except Exception as e:
                print(f"\n图像生成失败: {e}")
            
            continue
        
        # 添加用户消息到历史
        messages.append({"role": "user", "content": user_input})
        
        # 发送请求到AI
        print("\n美团AI正在思考...")
        try:
            response = agent.chat(messages)
            
            if "error" in response:
                print(f"\n请求失败: {response['error']}")
                continue
                
            # 提取AI回复
            if "choices" in response and len(response["choices"]) > 0:
                ai_message = response["choices"][0]["message"]["content"]
                print(f"\nAI: {ai_message}")
                
                # 将AI回复添加到历史
                messages.append({"role": "assistant", "content": ai_message})
            else:
                print("\n无法解析AI回复")
                print(json.dumps(response, ensure_ascii=False, indent=2))
                
        except Exception as e:
            print(f"\n请求处理失败: {e}")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n程序被用户中断，退出...")
        sys.exit(0)