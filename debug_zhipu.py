import os
import sys
import requests
import json

os.chdir(r"F:\程序项目\公众号自动流")

# 设置输出编码
sys.stdout.reconfigure(encoding='utf-8')

# 测试调用智谱
api_key = os.getenv("ZHIPU_API_KEY") or "adb9179c9f5c44409662a1d6f0d9cc5f.UtyktlKq4o6tZCz0"

r = requests.post(
    "https://open.bigmodel.cn/api/paas/v4/chat/completions",
    headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json; charset=utf-8"},
    json={"model": "glm-4-flash", "messages": [{"role": "user", "content": "用中文说你好世界"}], "max_tokens": 50}
)

result = r.json()
content = result["choices"][0]["message"]["content"]

# 写文件用UTF-8
with open("debug_output.txt", "w", encoding="utf-8") as f:
    f.write("API Response:\n")
    f.write(f"Type: {type(content)}\n")
    f.write(f"Content: {content}\n")

print("Done - check debug_output.txt")