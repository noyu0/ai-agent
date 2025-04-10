#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
MCP客户端实现 - 模型上下文协议(Model Context Protocol)
允许大语言模型与外部服务交互，获取实时数据和执行操作
"""

import os
import json
import logging
import asyncio
import aiohttp
import sseclient
from typing import Dict, List, Any, Optional, Callable

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("mcp_client")

class MCPClient:
    """MCP客户端 - 用于与MCP服务器交互"""

    def __init__(self, config_path: str = None):
        """
        初始化MCP客户端
        
        Args:
            config_path: 配置文件路径，默认为项目根目录下的config.json
        """
        self.config_path = config_path or os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config.json')
        self.mcp_servers = {}
        self.load_config()
        
        # 记录活跃的连接
        self.active_connections = {}
        
        logger.info(f"MCP客户端初始化完成，已加载 {len(self.mcp_servers)} 个MCP服务器配置")
    
    def load_config(self):
        """从配置文件加载MCP服务器配置"""
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    
                # 获取MCP服务器配置
                self.mcp_servers = config.get('mcpServers', {})
                
                if self.mcp_servers:
                    logger.info(f"已加载MCP服务器配置: {list(self.mcp_servers.keys())}")
                else:
                    logger.warning("配置文件中未找到MCP服务器配置")
            else:
                logger.warning(f"配置文件不存在: {self.config_path}")
        except Exception as e:
            logger.error(f"加载MCP配置失败: {str(e)}")
    
    def get_available_servers(self) -> List[str]:
        """获取可用的MCP服务器列表"""
        return list(self.mcp_servers.keys())
    
    def is_server_available(self, server_id: str) -> bool:
        """检查指定的MCP服务器是否可用"""
        return server_id in self.mcp_servers
    
    async def connect_to_server(self, server_id: str, message_callback: Callable[[Dict], None]) -> bool:
        """
        连接到指定的MCP服务器
        
        Args:
            server_id: MCP服务器ID
            message_callback: 接收消息的回调函数
            
        Returns:
            连接是否成功
        """
        if not self.is_server_available(server_id):
            logger.error(f"MCP服务器不存在: {server_id}")
            return False
        
        server_config = self.mcp_servers[server_id]
        server_url = server_config.get('url')
        
        if not server_url:
            logger.error(f"MCP服务器URL未配置: {server_id}")
            return False
        
        # 如果已经有活跃连接，先关闭
        if server_id in self.active_connections:
            await self.disconnect_from_server(server_id)
        
        try:
            # 创建异步任务处理SSE连接
            task = asyncio.create_task(self._handle_sse_connection(server_id, server_url, message_callback))
            self.active_connections[server_id] = task
            logger.info(f"已连接到MCP服务器: {server_id}")
            return True
        except Exception as e:
            logger.error(f"连接MCP服务器失败: {server_id}, 错误: {str(e)}")
            return False
    
    async def disconnect_from_server(self, server_id: str) -> bool:
        """
        断开与指定MCP服务器的连接
        
        Args:
            server_id: MCP服务器ID
            
        Returns:
            断开连接是否成功
        """
        if server_id in self.active_connections:
            task = self.active_connections[server_id]
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass
            del self.active_connections[server_id]
            logger.info(f"已断开与MCP服务器的连接: {server_id}")
            return True
        return False
    
    async def disconnect_all(self):
        """断开所有MCP服务器连接"""
        for server_id in list(self.active_connections.keys()):
            await self.disconnect_from_server(server_id)
        logger.info("已断开所有MCP服务器连接")
    
    async def _handle_sse_connection(self, server_id: str, server_url: str, message_callback: Callable[[Dict], None]):
        """
        处理SSE连接
        
        Args:
            server_id: MCP服务器ID
            server_url: MCP服务器URL
            message_callback: 接收消息的回调函数
        """
        try:
            async with aiohttp.ClientSession() as session:
                headers = {
                    'Accept': 'text/event-stream',
                    'Cache-Control': 'no-cache',
                    'Connection': 'keep-alive'
                }
                async with session.get(server_url, headers=headers) as response:
                    if response.status != 200:
                        logger.error(f"连接MCP服务器失败: {server_id}, 状态码: {response.status}")
                        return
                    
                    # 直接处理响应流
                    buffer = b''
                    async for chunk in response.content.iter_any():
                        buffer += chunk
                        
                        # 检查是否有完整的事件（以两个换行符结束）
                        while b'\n\n' in buffer:
                            event_data, buffer = buffer.split(b'\n\n', 1)
                            
                            # 解析事件数据
                            event_lines = event_data.split(b'\n')
                            event_dict = {}
                            
                            for line in event_lines:
                                if not line:
                                    continue
                                    
                                line_str = line.decode('utf-8')
                                if ':' in line_str:
                                    field, value = line_str.split(':', 1)
                                    # 去除开头的空格
                                    if value.startswith(' '):
                                        value = value[1:]
                                    event_dict[field] = value
                            
                            # 如果有data字段，尝试解析为JSON
                            if 'data' in event_dict:
                                try:
                                    data = json.loads(event_dict['data'])
                                    # 调用回调函数处理消息
                                    message_callback({
                                        "server_id": server_id,
                                        "data": data
                                    })
                                except json.JSONDecodeError:
                                    logger.error(f"解析MCP消息失败: {event_dict['data']}")
        except asyncio.CancelledError:
            logger.info(f"MCP连接已取消: {server_id}")
            raise
        except Exception as e:
            logger.error(f"MCP连接异常: {server_id}, 错误: {str(e)}")
    
    def update_config(self, new_mcp_servers: Dict[str, Dict[str, str]]) -> bool:
        """
        更新MCP服务器配置
        
        Args:
            new_mcp_servers: 新的MCP服务器配置
            
        Returns:
            更新是否成功
        """
        try:
            # 读取当前配置
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
            else:
                config = {}
            
            # 更新MCP服务器配置
            config['mcpServers'] = new_mcp_servers
            
            # 保存配置
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
            
            # 更新内存中的配置
            self.mcp_servers = new_mcp_servers
            
            logger.info(f"MCP服务器配置已更新: {list(new_mcp_servers.keys())}")
            return True
        except Exception as e:
            logger.error(f"更新MCP配置失败: {str(e)}")
            return False
    
    def add_server(self, server_id: str, server_config: Dict[str, str]) -> bool:
        """
        添加MCP服务器配置
        
        Args:
            server_id: MCP服务器ID
            server_config: MCP服务器配置
            
        Returns:
            添加是否成功
        """
        try:
            # 读取当前配置
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
            else:
                config = {}
            
            # 确保mcpServers字段存在
            if 'mcpServers' not in config:
                config['mcpServers'] = {}
            
            # 添加新服务器
            config['mcpServers'][server_id] = server_config
            
            # 保存配置
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
            
            # 更新内存中的配置
            self.mcp_servers = config['mcpServers']
            
            logger.info(f"已添加MCP服务器: {server_id}")
            return True
        except Exception as e:
            logger.error(f"添加MCP服务器失败: {str(e)}")
            return False
    
    def remove_server(self, server_id: str) -> bool:
        """
        移除MCP服务器配置
        
        Args:
            server_id: MCP服务器ID
            
        Returns:
            移除是否成功
        """
        if server_id not in self.mcp_servers:
            logger.warning(f"MCP服务器不存在: {server_id}")
            return False
        
        try:
            # 读取当前配置
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
            else:
                return False
            
            # 确保mcpServers字段存在
            if 'mcpServers' not in config:
                return False
            
            # 移除服务器
            if server_id in config['mcpServers']:
                del config['mcpServers'][server_id]
                
                # 保存配置
                with open(self.config_path, 'w', encoding='utf-8') as f:
                    json.dump(config, f, indent=2, ensure_ascii=False)
                
                # 更新内存中的配置
                self.mcp_servers = config['mcpServers']
                
                logger.info(f"已移除MCP服务器: {server_id}")
                return True
            
            return False
        except Exception as e:
            logger.error(f"移除MCP服务器失败: {str(e)}")
            return False