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
        response = requests.post(api_url, headers=headers, json=data)
        response.raise_for_status()
        result = response.json()
        return result.get('choices', [{}])[0].get('message', {}).get('content', '')
    except Exception as e:
        print(f"Error calling GPT API: {str(e)}")
        return None


def detect_gender(
    name: str,
    *,
    system_prompt: Optional[str] = None,
    api_key: Optional[str] = None,
    api_url: Optional[str] = None
) -> Optional[str]:
    """根据提示词识别性别
    Args:
        name: 待识别的名字
        system_prompt: 系统提示词
        api_key: API密钥，如果为None则从环境变量获取
        api_url: API地址，如果为None则从环境变量获取
    Returns:
        'male' 或 'female' 或 'unknown' 或 'error'
    """
    system_prompt = system_prompt or """你是一个性别识别助手。请分析输入姓名中的性别。
    只需返回 'male' 或 'female'，如果无法判断则返回 'unknown'。不需要其他解释。"""

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": name}
    ]

    result = call_gpt(
        messages,
        temperature=0.1,
        api_key=api_key,
        api_url=api_url
    )
    if result:
        result = result.lower().strip()
        if result in ['male', 'female', 'unknown']:
            return result
    return 'error'


# 使用示例
if __name__ == '__main__':
    for text in ["李彩霞", "王大雷", "江铜"]:
        print(f'文字：{text} 检测到的性别: {detect_gender(text)}')
