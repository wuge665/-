import os, sys, requests, json

os.chdir(r"F:\程序项目\公众号自动流")
from dotenv import load_dotenv
load_dotenv(r"F:\程序项目\公众号自动流\.env")

app_id = os.getenv("WECHAT_APP_ID")
app_secret = os.getenv("WECHAT_APP_SECRET")

token = requests.get(f"https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid={app_id}&secret={app_secret}").json()["access_token"]

# 先上传图片获取media_id
img_data = bytes([0x89,0x50,0x4E,0x47,0x0D,0x0A,0x1A,0x0A,0x00,0x00,0x00,0x0D,0x49,0x48,0x44,0x52,0x00,0x00,0x00,0x01,0x00,0x00,0x00,0x01,0x08,0x06,0x00,0x00,0x00,0x1F,0x15,0xC4,0x89,0x00,0x00,0x00,0x0A,0x49,0x44,0x41,0x54,0x78,0x9C,0x63,0x00,0x01,0x00,0x00,0x05,0x00,0x01,0x0D,0x0A,0x2D,0xB4,0x00,0x00,0x00,0x00,0x49,0x45,0x4E,0x44,0xAE,0x42,0x60,0x82])
files = {"media": ("cover.png", img_data, "image/png")}
upload = requests.post(f"https://api.weixin.qq.com/cgi-bin/material/add_material?access_token={token}&type=image", files=files).json()
media_id = upload.get("media_id")
print("Media ID:", media_id)

# 用这个media_id创建草稿
article = {
    "title": "测试中文标题",
    "author": "小科", 
    "digest": "测试摘要",
    "content": "<p>这是一段中文测试内容</p>",
    "content_source_url": "https://mp.weixin.qq.com",
    "thumb_media_id": media_id,
    "need_open_comment": 0,
    "only_fans_can_comment": 0,
}

json_data = json.dumps({"articles": [article]}, ensure_ascii=False).encode("utf-8")
draft = requests.post(f"https://api.weixin.qq.com/cgi-bin/draft/add?access_token={token}", data=json_data, headers={"Content-Type": "application/json; charset=utf-8"}).json()
print("Draft:", draft)