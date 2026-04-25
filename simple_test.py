import os, sys, requests, json

os.chdir(r"F:\程序项目\公众号自动流")
from dotenv import load_dotenv
load_dotenv(r"F:\程序项目\公众号自动流\.env")

app_id = os.getenv("WECHAT_APP_ID")
app_secret = os.getenv("WECHAT_APP_SECRET")

token = requests.get(f"https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid={app_id}&secret={app_secret}").json()["access_token"]

# 尝试用最简单的参数创建草稿，不传thumb_media_id
article = {
    "title": "Test",
    "author": "A", 
    "digest": "D",
    "content": "<p>C</p>",
}

json_data = json.dumps({"articles": [article]}, ensure_ascii=False).encode("utf-8")
draft = requests.post(f"https://api.weixin.qq.com/cgi-bin/draft/add?access_token={token}", data=json_data).json()

with open("output/simple_test.txt", "w", encoding="utf-8") as f:
    f.write(str(draft))
print("Result:", draft)