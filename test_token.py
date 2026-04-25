import os
import sys
import requests
import json

os.chdir(r"F:\程序项目\公众号自动流")
from dotenv import load_dotenv
load_dotenv(r"F:\程序项目\公众号自动流\.env")

app_id = os.getenv("WECHAT_APP_ID")
app_secret = os.getenv("WECHAT_APP_SECRET")

# 先检查token
token_resp = requests.get(f"https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid={app_id}&secret={app_secret}")
print("Token response:", token_resp.json())

token = token_resp.json().get("access_token")
if not token:
    print("Failed to get token")
    sys.exit(1)

# 测试最简单的调用
article = {
    "title": "Hello",
    "author": "Test", 
    "digest": "Test",
    "content": "<p>Test</p>",
    "need_open_comment": 0,
    "only_fans_can_comment": 0,
}

# 尝试用 json= 参数
r = requests.post(
    f"https://api.weixin.qq.com/cgi-bin/draft/add?access_token={token}",
    json={"articles": [article]},
    headers={"Content-Type": "application/json"}
)
print("Result with json=:", r.json())