#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
MCP管理器 - 用于在API服务器中集成MCP功能
"""

import os
import json
import logging
import asyncio
from typing import Dict, List, Any, Optional, Callable
from .mcp_client import MCPClient

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("mcp_manager")

class MCPManager:
    """MCP管理器 - 用于在API服务器中集成MCP功能"""
    
    _instance = None
    
    def __new__(cls, *args, **kwargs):
        """单例模式"""
        if cls._instance is None:
            cls._instance = super(MCPManager, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self, config_path: str = None):
        """
        初始化MCP管理器
        
        Args:
            config_path: 配置文件路径，默认为项目根目录下的config.json
        """
        # 避免重复初始化
        if self._initialized:
            return
        
        self.config_path = config_path or os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config.json')
        self.mcp_client = MCPClient(self.config_path)
        
        # 存储MCP消息处理器
        self.message_handlers = {}
        
        # 存储MCP连接状态
        self.connection_status = {}
        
        # 创建事件循环
        self.loop = asyncio.new_event_loop()
        
        # 标记为已初始化
        self._initialized = True
        
        logger.info("MCP管理器初始化完成")
    
    def start(self):
        """启动MCP管理器"""
        # 在新线程中运行事件循环
        import threading
        self.thread = threading.Thread(target=self._run_event_loop, daemon=True)
        self.thread.start()
        logger.info("MCP管理器已启动")
    
    def _run_event_loop(self):
        """在新线程中运行事件循环"""
        asyncio.set_event_loop(self.loop)
        self.loop.run_forever()
    
    def stop(self):
        """停止MCP管理器"""
        # 断开所有连接
        asyncio.run_coroutine_threadsafe(self.mcp_client.disconnect_all(), self.loop)
        
        # 停止事件循环
        self.loop.call_soon_threadsafe(self.loop.stop)
        
        # 等待线程结束
        if hasattr(self, 'thread'):
            self.thread.join(timeout=5)
        
        logger.info("MCP管理器已停止")
    
    def register_message_handler(self, server_id: str, handler: Callable[[Dict], None]):
        """
        注册MCP消息处理器
        
        Args:
            server_id: MCP服务器ID
            handler: 消息处理函数
        """
        self.message_handlers[server_id] = handler
        logger.info(f"已注册MCP消息处理器: {server_id}")
    
    def unregister_message_handler(self, server_id: str):
        """
        注销MCP消息处理器
        
        Args:
            server_id: MCP服务器ID
        """
        if server_id in self.message_handlers:
            del self.message_handlers[server_id]
            logger.info(f"已注销MCP消息处理器: {server_id}")
    
    def _handle_mcp_message(self, message: Dict):
        """
        处理MCP消息
        
        Args:
            message: MCP消息
        """
        server_id = message.get("server_id")
        data = message.get("data")
        
        if server_id and server_id in self.message_handlers:
            try:
                # 调用注册的处理器
                self.message_handlers[server_id](data)
            except Exception as e:
                logger.error(f"处理MCP消息失败: {server_id}, 错误: {str(e)}")
    
    def connect_to_server(self, server_id: str) -> bool:
        """
        连接到指定的MCP服务器
        
        Args:
            server_id: MCP服务器ID
            
        Returns:
            是否成功发起连接请求
        """
        if not self.mcp_client.is_server_available(server_id):
            logger.error(f"MCP服务器不存在: {server_id}")
            return False
        
        # 更新连接状态
        self.connection_status[server_id] = "connecting"
        
        # 在事件循环中执行连接操作
        future = asyncio.run_coroutine_threadsafe(
            self.mcp_client.connect_to_server(server_id, self._handle_mcp_message),
            self.loop
        )
        
        try:
            # 等待连接结果
            result = future.result(timeout=5)
            
            # 更新连接状态
            self.connection_status[server_id] = "connected" if result else "failed"
            
            return result
        except Exception as e:
            logger.error(f"连接MCP服务器失败: {server_id}, 错误: {str(e)}")
            self.connection_status[server_id] = "failed"
            return False
    
    def disconnect_from_server(self, server_id: str) -> bool:
        """
        断开与指定MCP服务器的连接
        
        Args:
            server_id: MCP服务器ID
            
        Returns:
            是否成功发起断开连接请求
        """
        if server_id not in self.connection_status or self.connection_status[server_id] != "connected":
            logger.warning(f"MCP服务器未连接: {server_id}")
            return False
        
        # 更新连接状态
        self.connection_status[server_id] = "disconnecting"
        
        # 在事件循环中执行断开连接操作
        future = asyncio.run_coroutine_threadsafe(
            self.mcp_client.disconnect_from_server(server_id),
            self.loop
        )
        
        try:
            # 等待断开连接结果
            result = future.result(timeout=5)
            
            # 更新连接状态
            if result:
                self.connection_status[server_id] = "disconnected"
            else:
                self.connection_status[server_id] = "connected"
            
            return result
        except Exception as e:
            logger.error(f"断开MCP服务器连接失败: {server_id}, 错误: {str(e)}")
            self.connection_status[server_id] = "unknown"
            return False
    
    def get_connection_status(self, server_id: str = None) -> Dict[str, str]:
        """
        获取MCP服务器连接状态
        
        Args:
            server_id: MCP服务器ID，如果为None则返回所有服务器的状态
            
        Returns:
            连接状态字典
        """
        if server_id:
            return {server_id: self.connection_status.get(server_id, "disconnected")}
        else:
            return self.connection_status
    
    def get_available_servers(self) -> List[str]:
        """获取可用的MCP服务器列表"""
        return self.mcp_client.get_available_servers()
    
    def is_server_available(self, server_id: str) -> bool:
        """
        检查指定的MCP服务器是否可用
        
        Args:
            server_id: MCP服务器ID
            
        Returns:
            服务器是否可用
        """
        return self.mcp_client.is_server_available(server_id)
    
    def add_server(self, server_id: str, server_config: Dict[str, str]) -> bool:
        """
        添加MCP服务器配置
        
        Args:
            server_id: MCP服务器ID
            server_config: MCP服务器配置
            
        Returns:
            添加是否成功
        """
        return self.mcp_client.add_server(server_id, server_config)
    
    def remove_server(self, server_id: str) -> bool:
        """
        移除MCP服务器配置
        
        Args:
            server_id: MCP服务器ID
            
        Returns:
            移除是否成功
        """
        # 如果服务器已连接，先断开连接
        if server_id in self.connection_status and self.connection_status[server_id] == "connected":
            self.disconnect_from_server(server_id)
        
        return self.mcp_client.remove_server(server_id)
    
    def update_config(self, new_mcp_servers: Dict[str, Dict[str, str]]) -> bool:
        """
        更新MCP服务器配置
        
        Args:
            new_mcp_servers: 新的MCP服务器配置
            
        Returns:
            更新是否成功
        """
        # 断开所有连接
        for server_id in list(self.connection_status.keys()):
            if self.connection_status[server_id] == "connected":
                self.disconnect_from_server(server_id)
        
        return self.mcp_client.update_config(new_mcp_servers)