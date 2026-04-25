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

# 尝试用正确文档格式 - 包括全部必填参数
article = {
    "title": "Test Title",
    "author": "Author",
    "digest": "Digest text",
    "content": "<p>Content here</p>",
    "content_source_url": "https://mp.weixin.qq.com",
    "thumb_media_id": "",  # 设为空字符串
    "show_cover_pic": 0,
    "need_open_comment": 0,
    "only_fans_can_comment": 0,
    "article_type": "news",
}

data = json.dumps({"articles": [article]}, ensure_ascii=False)

resp = requests.post(
    f"https://api.weixin.qq.com/cgi-bin/draft/add?access_token={token}",
    data=data.encode("utf-8"),
    headers={"Content-Type": "application/json"}
)
print("Result:", resp.json())

# 保存发送的实际数据
with open("output/last_request.json", "w", encoding="utf-8") as f:
    f.write(data)
print("Saved to output/last_request.json")