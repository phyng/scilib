# coding: utf-8

from __future__ import unicode_literals, absolute_import, print_function, division
from typing import List, Optional

from .gpt_gender import detect_gender


def batch_classify(
    names: List[str],
    *,
    api_key: Optional[str] = None,
    api_url: Optional[str] = None,
    system_prompt: Optional[str] = None
) -> List[str]:
    """批量识别名字性别
    Args:
        names: 待识别的名字列表
        api_key: API密钥，如果为None则从环境变量获取
        api_url: API地址，如果为None则从环境变量获取
        system_prompt: 系统提示词
    Returns:
        列表，每个元素为 'male' 或 'female' 或 'unknown' 或 'error'
    """
    results = []
    for name in names:
        if not name:
            results.append('error')
            continue

        result = detect_gender(
            name,
            system_prompt=system_prompt,
            api_key=api_key,
            api_url=api_url
        )
        results.append(result)

    return results


def test():
    # 测试用例
    test_names = ["李彩霞", "王大雷", "江铜", "", "张三丰"]
    results = batch_classify(test_names)
    for name, gender in zip(test_names, results):
        print(f"{name}: {gender}")


if __name__ == '__main__':
    test()
