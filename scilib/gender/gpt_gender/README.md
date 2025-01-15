# gpt_gender

基于 GPT API 的中文姓名性别识别工具。支持使用 OpenAI 或 Deepseek 等兼容接口的服务。

## 功能特点

- 支持单个或批量姓名性别识别
- 灵活的配置方式（环境变量或参数传递）
- 可自定义系统提示词
- 返回结果规范化（male/female/unknown/error）

## 环境配置

需要设置以下环境变量：

```bash
export OPENAI_API_KEY='your-api-key'
export OPENAI_API_URL='https://api.deepseek.com/chat/completions'  # 可选，默认使用 deepseek 接口
```

## 使用方法

### 单个名字识别

```python
from scilib.gender.gpt_gender import detect_gender

# 基础用法
result = detect_gender("张三")

# 自定义配置
result = detect_gender(
    "张三",
    api_key="your-api-key",
    api_url="your-api-url",
    system_prompt="自定义提示词"
)
```

### 批量识别

```python
from scilib.gender.gpt_gender.public import batch_classify

# 基础用法
results = batch_classify(["李彩霞", "王大雷", "江铜"])

# 自定义配置
results = batch_classify(
    ["张三", "李四"],
    api_key="your-api-key",
    api_url="your-api-url",
    system_prompt="自定义提示词"
)
```

## 返回值说明

- `male`: 男性
- `female`: 女性
- `unknown`: 无法判断
- `error`: 调用出错

## 测试运行

执行以下命令可以运行测试用例：

```bash
python -m scilib.gender.gpt_gender.public
```

## 注意事项

1. 请确保已正确配置 API 密钥
2. API 调用可能会产生费用，请注意使用频率
3. 批量处理时建议控制并发数量
