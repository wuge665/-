import os, sys, requests, json

os.chdir(r"F:\程序项目\公众号自动流")
from dotenv import load_dotenv
load_dotenv(r"F:\程序项目\公众号自动流\.env")

app_id = os.getenv("WECHAT_APP_ID")
app_secret = os.getenv("WECHAT_APP_SECRET")

# 1. 获取token
token_resp = requests.get(
    f"https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid={app_id}&secret={app_secret}"
)
token_data = token_resp.json()
print("Token response:", token_data)

if "access_token" not in token_data:
    print("获取token失败!")
    sys.exit(1)

token = token_data["access_token"]

# 2. 先尝试上传一张图片作为永久素材
print("\n--- 测试上传封面图片 ---")
# 用一个简单1x1像素的白色图片
img_data = bytes([
    0x89, 0x50, 0x4E, 0x47, 0x0D, 0x0A, 0x1A, 0x0A, 0x00, 0x00, 0x00, 0x0D,
    0x49, 0x48, 0x44, 0x52, 0x00, 0x00, 0x00, 0x01, 0x00, 0x00, 0x00, 0x01,
    0x08, 0x06, 0x00, 0x00, 0x00, 0x1F, 0x15, 0xC4, 0x89, 0x00, 0x00, 0x00,
    0x0A, 0x49, 0x44, 0x41, 0x54, 0x78, 0x9C, 0x63, 0x00, 0x01, 0x00, 0x00,
    0x05, 0x00, 0x01, 0x0D, 0x0A, 0x2D, 0xB4, 0x00, 0x00, 0x00, 0x00, 0x49,
    0x45, 0x4E, 0x44, 0xAE, 0x42, 0x60, 0x82
])

files = {"media": ("cover.png", img_data, "image/png")}
upload_resp = requests.post(
    f"https://api.weixin.qq.com/cgi-bin/material/add_material?access_token={token}&type=image",
    files=files
)
upload_result = upload_resp.json()
print("Upload result:", upload_result)

media_id = upload_result.get("media_id")
print(f"获取到的media_id: {media_id}")

if media_id:
    # 3. 用这个media_id创建草稿
    print("\n--- 测试创建草稿 ---")
    article = {
        "title": "Test Chinese Title",
        "author": "Test",
        "digest": "Test digest",
        "content": "<p>Test content 中文测试</p>",
        "content_source_url": "https://mp.weixin.qq.com",
        "thumb_media_id": media_id,
        "need_open_comment": 0,
        "only_fans_can_comment": 0,
    }
    
    json_data = json.dumps({"articles": [article]}, ensure_ascii=False)
    draft_resp = requests.post(
        f"https://api.weixin.qq.com/cgi-bin/draft/add?access_token={token}",
        data=json_data.encode("utf-8"),
        headers={"Content-Type": "application/json; charset=utf-8"}
    )
    draft_result = draft_resp.json()
    print("Draft result:", draft_result)
else:
    print("上传失败，无法获取media_id")