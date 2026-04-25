import os
import sys
import requests
import json

os.chdir(r"F:\程序项目\公众号自动流")
from dotenv import load_dotenv
load_dotenv(r"F:\程序项目\公众号自动流\.env")

app_id = os.getenv("WECHAT_APP_ID")
app_secret = os.getenv("WECHAT_APP_SECRET")

token = requests.get(f"https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid={app_id}&secret={app_secret}").json()["access_token"]

# 最小参数测试
article = {
    "title": "Hello",
    "author": "Test",
    "digest": "Test",  
    "content": "<p>Hello</p>",
}

# 用data参数而不是json参数
json_str = json.dumps({"articles": [article]}, ensure_ascii=False)

r = requests.post(
    f"https://api.weixin.qq.com/cgi-bin/draft/add?access_token={token}",
    data=json_str,
    headers={"Content-Type": "application/json"}
)
print("Result:", r.json())