import os
import sys
import requests
import json

os.chdir(r"F:\程序项目\公众号自动流")

from dotenv import load_dotenv
load_dotenv(r"F:\程序项目\公众号自动流\.env")

app_id = os.getenv("WECHAT_APP_ID")
app_secret = os.getenv("WECHAT_APP_SECRET")

token_url = f"https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid={app_id}&secret={app_secret}"
token = requests.get(token_url).json().get("access_token")

article = {
    "title": "测试中文",
    "author": "小科", 
    "digest": "测试摘要",
    "content": "<p>这是一段中文测试内容</p>",
    "content_source_url": "https://mp.weixin.qq.com",
    "need_open_comment": 0,
    "only_fans_can_comment": 0,
}

url = f"https://api.weixin.qq.com/cgi-bin/draft/add?access_token={token}"

# 用 data 参数而不是 json，强制转成字符串
response = requests.post(url, data=json.dumps({"articles": [article]}, ensure_ascii=False))
result = response.json()
print("Result:", result)

if result.get("media_id"):
    with open("output/wechat_test_ok.txt", "w", encoding="utf-8") as f:
        f.write("OK - " + str(result))