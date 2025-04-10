"""
配置文件，用于存储FRIDAY大模型平台的租户ID、应用ID和API URL等隐私信息
"""

import os
import json
from pathlib import Path

# 配置文件路径
CONFIG_FILE = Path(__file__).parent.parent / 'config.json'

# 默认配置
DEFAULT_CONFIG = {
    "tenant_id": "",
    "app_id": "",
    "api_urls": {
        "base_url": "https://your-api-base-url",
        "openai_api_base": "https://your-openai-api-base-url"
    },
    "timeout": 120,
    "is_configured": False,
    "mcpServers": {}
}

def load_config():
    """
    加载配置文件
    
    Returns:
        dict: 配置信息
    """
    if not CONFIG_FILE.exists():
        save_config(DEFAULT_CONFIG)
        return DEFAULT_CONFIG
    
    try:
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        # 确保配置文件包含所有必要的字段
        for key, value in DEFAULT_CONFIG.items():
            if key not in config:
                config[key] = value
                
        return config
    except Exception as e:
        print(f"加载配置文件失败: {e}")
        return DEFAULT_CONFIG

def save_config(config):
    """
    保存配置文件
    
    Args:
        config (dict): 配置信息
    """
    try:
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(config, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"保存配置文件失败: {e}")

def is_configured():
    """
    检查是否已配置
    
    Returns:
        bool: 是否已配置
    """
    config = load_config()
    return config.get("is_configured", False)

def get_tenant_id():
    """
    获取租户ID
    
    Returns:
        str: 租户ID
    """
    config = load_config()
    return config.get("tenant_id", "")

def get_app_id():
    """
    获取应用ID
    
    Returns:
        str: 应用ID
    """
    config = load_config()
    return config.get("app_id", "")

def get_api_urls():
    """
    获取API URL配置
    
    Returns:
        dict: API URL配置
    """
    config = load_config()
    return config.get("api_urls", DEFAULT_CONFIG["api_urls"])

def get_timeout():
    """
    获取请求超时时间
    
    Returns:
        int: 超时时间（秒）
    """
    config = load_config()
    return config.get("timeout", DEFAULT_CONFIG["timeout"])

def get_mcp_servers():
    """
    获取MCP服务器配置
    
    Returns:
        dict: MCP服务器配置
    """
    config = load_config()
    return config.get("mcpServers", {})

def configure(tenant_id, app_id, api_urls=None, timeout=None):
    """
    配置租户ID、应用ID和API URL
    
    Args:
        tenant_id (str): 租户ID
        app_id (str): 应用ID
        api_urls (dict, optional): API URL配置
        timeout (int, optional): 请求超时时间
    """
    config = load_config()
    config["tenant_id"] = tenant_id
    config["app_id"] = app_id
    
    if api_urls:
        config["api_urls"] = api_urls
    
    if timeout:
        config["timeout"] = timeout
    
    config["is_configured"] = True
    save_config(config)
def update_mcp_servers(mcp_servers):
    """
    更新MCP服务器配置
    
    Args:
        mcp_servers (dict): MCP服务器配置
    """
    config = load_config()
    config["mcpServers"] = mcp_servers
    save_config(config)
