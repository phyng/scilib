# GPT Translate

可以通过环境变量或参数传递的方式配置 GPT 翻译工具。

```bash
# 使用硅基流动的接口
env OPENAI_API_URL=https://api.siliconflow.cn/v1/chat/completions \
  OPENAI_MODEL=Qwen/Qwen2.5-7B-Instruct \
  OPENAI_API_KEY=sk-xxx \
  python -m scilib.gpt.gpt_trans
```
