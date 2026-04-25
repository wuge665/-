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

# 测试1: 纯英文
article_en = {
    "title": "Test English Title",
    "author": "Test",
    "digest": "Test digest",
    "content": "<p>Test content</p>",
    "content_source_url": "https://mp.weixin.qq.com",
    "need_open_comment": 0,
    "only_fans_can_comment": 0,
}
data_en = json.dumps({"articles": [article_en]}, ensure_ascii=False).encode("utf-8")
r_en = requests.post(f"https://api.weixin.qq.com/cgi-bin/draft/add?access_token={token}", 
    data=data_en, headers={"Content-Type": "application/json; charset=utf-8"})
print("English:", r_en.json())