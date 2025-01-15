# coding: utf-8

from __future__ import unicode_literals, absolute_import, print_function, division

import os
import requests
from typing import Dict, List, Optional


def call_gpt(
    messages: List[Dict[str, str]],
    model: str = "deepseek-chat",
    temperature: float = 0.7,
    api_key: Optional[str] = None,
    api_url: Optional[str] = None
) -> Optional[str]:
    """通用GPT调用函数
    Args:
        messages: 消息列表
        model: 模型名称
        temperature: 温度参数
        api_key: API密钥，如果为None则从环境变量获取
        api_url: API地址，如果为None则从环境变量获取
    """
    # 获取配置，优先使用传入参数，其次使用环境变量
    api_key = api_key or os.getenv('OPENAI_API_KEY', '')
    api_url = api_url or os.getenv('OPENAI_API_URL', 'https://api.deepseek.com/chat/completions')

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }

    data = {
        "model": model,
        "messages": messages,
        "stream": False,
        "temperature": temperature
    }

    try:
        response = requests.post(api_url, headers=headers, json=data, timeout=20)
        response.raise_for_status()
        result = response.json()
        return result.get('choices', [{}])[0].get('message', {}).get('content', '')
    except Exception as e:
        print(f"Error calling GPT API: {str(e)}")
        return None
