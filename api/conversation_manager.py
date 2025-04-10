#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
对话历史管理器 - 用于保存和加载对话历史
"""

import os
import json
import time
import datetime
from pathlib import Path

class ConversationManager:
    """对话历史管理器"""

    def __init__(self, save_dir=None):
        """
        初始化对话历史管理器

        Args:
            save_dir: 保存对话历史的目录，默认为项目根目录下的conversations目录
        """
        if save_dir is None:
            # 使用项目根目录下的conversations目录
            self.save_dir = Path(__file__).parent.parent / 'conversations'
        else:
            self.save_dir = Path(save_dir)
        
        # 确保目录存在
        os.makedirs(self.save_dir, exist_ok=True)
        
        print(f"对话历史将保存在: {self.save_dir}")
    
    def save_conversation(self, messages, title=None):
        """
        保存对话历史

        Args:
            messages: 对话历史列表
            title: 对话标题，如果为None则使用时间戳

        Returns:
            保存的文件路径
        """
        # 生成时间戳
        timestamp = int(time.time())
        datetime_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # 如果没有提供标题，使用时间戳
        if not title:
            title = f"对话_{timestamp}"
        # 构建文件名
        filename = f"{timestamp}_{title.replace(' ', '_')}.json"
        filepath = self.save_dir / filename
        
        # 构建保存的数据
        data = {
            "timestamp": timestamp,
            "datetime": datetime_str,
            "title": title,
            "messages": messages
        }
        
        # 保存到文件
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        print(f"对话已保存到: {filepath}")
        return str(filepath)
    
    def load_conversation(self, filename):
        """
        加载对话历史
        Args:
            filename: 文件名或文件路径
        Returns:
            对话历史列表
        """
        # 如果提供的是文件名而不是完整路径，则构建完整路径
        if not os.path.isabs(filename):
            filepath = self.save_dir / filename
        else:
            filepath = Path(filename)
        
        # 检查文件是否存在
        if not filepath.exists():
            print(f"文件不存在: {filepath}")
            return None
        
        # 从文件加载数据
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # 返回对话历史
            return data.get("messages", [])
        except Exception as e:
            print(f"加载对话失败: {e}")
            return None
    
    def list_conversations(self):
        """
        列出所有保存的对话
        
        Returns:
            对话列表，每个对话包含时间戳、日期时间、标题和文件名
        """
        conversations = []
        
        # 遍历目录中的所有JSON文件
        for filepath in sorted(self.save_dir.glob("*.json"), reverse=True):
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # 提取对话信息
                conversation = {
                    "timestamp": data.get("timestamp", 0),
                    "datetime": data.get("datetime", ""),
                    "title": data.get("title", ""),
                    "filename": filepath.name
                }
                
                conversations.append(conversation)
            except Exception as e:
                print(f"读取对话文件失败: {filepath}, 错误: {e}")
        
        return conversations    
    def delete_conversation(self, filename):
        """
        删除对话历史
        
        Args:
            filename: 文件名或文件路径
            
        Returns:
            是否成功删除
        """
        # 如果提供的是文件名而不是完整路径，则构建完整路径
        if not os.path.isabs(filename):
            filepath = self.save_dir / filename
        else:
            filepath = Path(filename)
        
        # 检查文件是否存在
        if not filepath.exists():
            print(f"文件不存在: {filepath}")
            return False
        
        # 删除文件
        try:
            os.remove(filepath)
            print(f"对话已删除: {filepath}")
            return True
        except Exception as e:
            print(f"删除对话失败: {e}")
            return False
