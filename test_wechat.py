import os
import sys
import json

os.chdir(r"F:\程序项目\公众号自动流")
sys.path.insert(0, r"F:\程序项目\公众号自动流")

# 模拟 main.py 加载 .env
from dotenv import load_dotenv
load_dotenv(r"F:\程序项目\公众号自动流\.env")

import requests

# 获取token
app_id = os.getenv("WECHAT_APP_ID")
app_secret = os.getenv("WECHAT_APP_SECRET")

token_url = f"https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid={app_id}&secret={app_secret}"
token_r = requests.get(token_url)
token = token_r.json().get("access_token")
print("Token:", token[:20] if token else "Failed")

# 准备测试内容
test_content = "你好世界！这是测试"

# 构建文章数据
article = {
    "title": "测试标题",
    "author": "小科",
    "digest": "测试摘要",
    "content": f"<p>{test_content}</p>",
    "content_source_url": "https://mp.weixin.qq.com",
    "thumb_media_id": "",
    "need_open_comment": 0,
    "only_fans_can_comment": 0,
}

data = {"articles": [article]}

# 发送请求
url = f"https://api.weixin.qq.com/cgi-bin/draft/add?access_token={token}&type=json"
response = requests.post(url, json=data, headers={"Content-Type": "application/json; charset=utf-8"})
result = response.json()
print("Result:", result)