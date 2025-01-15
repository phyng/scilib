# coding: utf-8

from __future__ import unicode_literals, absolute_import, print_function, division
from typing import Optional
from scilib.gpt.gpt_api import call_gpt


def gpt_trans(
    name: str,
    to_languege: str,
    *,
    system_prompt: Optional[str] = None,
    api_key: Optional[str] = None,
    api_url: Optional[str] = None
) -> Optional[str]:
    """根据提示词翻译
    Args:
        name: 待识别的名字
        system_prompt: 系统提示词
        api_key: API密钥，如果为None则从环境变量获取
        api_url: API地址，如果为None则从环境变量获取
    """
    system_prompt = system_prompt or """You are a professional, authentic machine translation engine"""

    messages = [
        {
            "role": "system",
            "content": system_prompt
        },
        {
            "role": "user",
            "content": f"""Translate input into {to_languege}, output translation ONLY. NO explanations. NO notes. Input: {name}"""  # noqa
        }
    ]

    result = call_gpt(
        messages,
        temperature=0.1,
        api_key=api_key,
        api_url=api_url
    )
    return result


# 使用示例
if __name__ == '__main__':
    for text in ["hello, world"]:
        print(f"{text} 翻译为: {gpt_trans(text, '中文')}")
