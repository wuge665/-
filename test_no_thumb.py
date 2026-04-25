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

# 测试：不含thumb_media_id
article = {
    "title": "Test Title",
    "author": "Test",
    "digest": "Test",
    "content": "<p>Test</p>",
    "content_source_url": "https://mp.weixin.qq.com",
}

data = json.dumps({"articles": [article]}, ensure_ascii=False).encode("utf-8")
r = requests.post(f"https://api.weixin.qq.com/cgi-bin/draft/add?access_token={token}", 
    data=data, headers={"Content-Type": "application/json; charset=utf-8"})
print("Result:", r.json())