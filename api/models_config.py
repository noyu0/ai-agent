#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
模型配置文件 - 存储支持的模型列表
"""

# 支持的模型列表
SUPPORTED_MODELS = {
    # 自研模型
    "LongCat-8B-128K-Chat": {
        "category": "自研",
        "context_length": 128 * 1024,
        "price_input": 0.2,
        "price_output": 0.2,
        "description": "美团自研大模型，支持超长上下文",
        "recommended": True
    },
    "LongCat-Lite-8K-Chat": {
        "category": "自研",
        "context_length": 8 * 1024,
        "price_input": 0.3,
        "price_output": 0.3,
        "description": "美团自研轻量级模型"
    },
    "LongCat-Medium-32K-Chat": {
        "category": "自研",
        "context_length": 32 * 1024,
        "price_input": 0.5,
        "price_output": 1.0,
        "description": "美团自研中型模型"
    },
    "LongCat-Large-32K-Chat": {
        "category": "自研",
        "context_length": 32 * 1024,
        "price_input": 1.0,
        "price_output": 2.0,
        "description": "美团自研大型模型"
    },
    "LongCat-70B": {
        "category": "自研",
        "context_length": 32 * 1024,
        "price_input": 2.0,
        "price_output": 4.0,
        "description": "美团自研70B参数大模型"
    },

    # OpenAI模型
    "gpt-4o": {
        "category": "OpenAI多模态",
        "context_length": 128 * 1024,
        "price_input": 15.0,
        "price_output": 60.0,
        "description": "OpenAI最新模型，支持联网",
        "recommended": True
    },
    "gpt-4o-mini": {
        "category": "OpenAI多模态",
        "context_length": 128 * 1024,
        "price_input": 1.08,
        "price_output": 4.2,
        "description": "OpenAI最新多模态模型的轻量版",
        "recommended": True
    },
    "gpt-4o-2024-08-06": {
        "category": "OpenAI多模态",
        "context_length": 128 * 1024,
        "price_input": 18,
        "price_output": 72,
        "description": "OpenAI最新多模态模型"
    },
    "gpt-4": {
        "category": "OpenAI",
        "context_length": 8 * 1024,
        "price_input": 30.0,
        "price_output": 60.0,
        "description": "强大的通用模型，支持联网"
    },
    "gpt-4-turbo-2024-04-09": {
        "category": "OpenAI多模态",
        "context_length": 128 * 1024,
        "price_input": 72,
        "price_output": 216,
        "description": "OpenAI GPT-4 Turbo模型"
    },
    "gpt-3.5-turbo": {
        "category": "OpenAI",
        "context_length": 16 * 1024,
        "price_input": 5.0,
        "price_output": 10.0,
        "description": "性能均衡的模型，支持联网"
    },
    "gpt-3.5-turbo-1106": {
        "category": "OpenAI",
        "context_length": 16 * 1024,
        "price_input": 7.2,
        "price_output": 14.4,
        "description": "OpenAI GPT-3.5 Turbo模型"
    },
    "gpt-3.5-turbo-0613": {
        "category": "OpenAI",
        "context_length": 4 * 1024,
        "price_input": 10.8,
        "price_output": 14.4,
        "description": "OpenAI GPT-3.5 Turbo模型"
    },

    # Google模型
    "gemini-2.0-flash": {
        "category": "Google",
        "context_length": 128 * 1024,
        "price_input": 0.35,
        "price_output": 1.05,
        "description": "Google高性能模型，支持联网",
        "recommended": True
    },
    "gemini-1.5-pro": {
        "category": "Google",
        "context_length": 1024 * 1024,
        "price_input": 0.7,
        "price_output": 2.1,
        "description": "Google专业版模型，支持联网"
    },

    # Minimax模型
    "abab6.5s-chat": {
        "category": "Minimax",
        "context_length": 240 * 1024,
        "price_input": 1.0,
        "price_output": 1.0,
        "description": "Minimax最新大模型，支持超长上下文",
        "recommended": True
    },
    "abab6.5t-chat": {
        "category": "Minimax",
        "context_length": 8 * 1024,
        "price_input": 0.8,
        "price_output": 0.8,
        "description": "Minimax大模型"
    },
    "abab6.5g-chat": {
        "category": "Minimax",
        "context_length": 8 * 1024,
        "price_input": 0.8,
        "price_output": 0.8,
        "description": "Minimax大模型"
    },

    # DeepSeek模型
    "deepseek-chat": {
        "category": "DeepSeek",
        "context_length": 64 * 1024,
        "price_input": 2.0,
        "price_output": 8.0,
        "description": "DeepSeek大模型，擅长代码和推理",
        "recommended": True
    },
    "deepseek-reasoner": {
        "category": "DeepSeek",
        "context_length": 64 * 1024,
        "price_input": 4.0,
        "price_output": 16.0,
        "description": "DeepSeek推理增强模型"
    },
    "deepseek-v3-friday": {
        "category": "DeepSeek",
        "context_length": 32 * 1024,
        "price_input": 2.0,
        "price_output": 8.0,
        "description": "DeepSeek V3模型，Friday部署版"
    },
    "deepseek-r1-friday": {
        "category": "DeepSeek",
        "context_length": 32 * 1024,
        "price_input": 4.0,
        "price_output": 16.0,
        "description": "DeepSeek R1模型，Friday部署版"
    },
    "Doubao-deepseek-v3": {
        "category": "DeepSeek",
        "context_length": 32 * 1024,
        "price_input": 2.0,
        "price_output": 8.0,
        "description": "豆包DeepSeek V3模型"
    },
    "Doubao-deepseek-r1": {
        "category": "DeepSeek",
        "context_length": 32 * 1024,
        "price_input": 4.0,
        "price_output": 16.0,
        "description": "豆包DeepSeek R1模型"
    }
}

# 默认模型
DEFAULT_MODEL = "Doubao-deepseek-r1"

# 获取按类别分组的模型列表
def get_models_by_category():
    """
    获取按类别分组的模型列表
    
    Returns:
        Dict: 按类别分组的模型列表
    """
    models_by_category = {}
    for model_id, model_info in SUPPORTED_MODELS.items():
        category = model_info["category"]
        if category not in models_by_category:
            models_by_category[category] = []
        
        # 添加模型ID到模型信息中
        model_data = model_info.copy()
        model_data["id"] = model_id
        
        models_by_category[category].append(model_data)
    
    return models_by_category

# 检查模型是否支持
def is_model_supported(model_id):
    """
    检查模型是否支持
    
    Args:
        model_id: 模型ID
        
    Returns:
        bool: 如果模型支持则返回True，否则返回False
    """
    return model_id in SUPPORTED_MODELS

# 获取模型信息
def get_model_info(model_id):
    """
    获取模型信息
    
    Args:
        model_id: 模型ID
        
    Returns:
        Dict: 模型信息，如果模型不存在则返回空字典
    """
    return SUPPORTED_MODELS.get(model_id, {})