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

article = {
    "title": "测试中文标题",
    "author": "小科",
    "digest": "这是测试摘要内容",
    "content": "<p>这是中文测试内容段落</p>",
    "content_source_url": "https://mp.weixin.qq.com",
    "need_open_comment": 0,
    "only_fans_can_comment": 0,
}

# 测试1: 用 data=json.encode
data1 = json.dumps({"articles": [article]}, ensure_ascii=False).encode("utf-8")
r1 = requests.post(f"https://api.weixin.qq.com/cgi-bin/draft/add?access_token={token}", 
    data=data1, headers={"Content-Type": "application/json; charset=utf-8"})
print("Test 1:", r1.json())