import os
import sys
import requests
import json

os.chdir(r"F:\程序项目\公众号自动流")
sys.path.insert(0, r"F:\程序项目\公众号自动流")

from dotenv import load_dotenv
load_dotenv(r"F:\程序项目\公众号自动流\.env")

app_id = os.getenv("WECHAT_APP_ID")
app_secret = os.getenv("WECHAT_APP_SECRET")

token_url = f"https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid={app_id}&secret={app_secret}"
token = requests.get(token_url).json().get("access_token")

# 和之前一样的发送逻辑
article = {
    "title": "测试中文",
    "author": "小科", 
    "digest": "测试摘要",
    "content": "<p>这是一段中文测试内容</p>",
    "content_source_url": "https://mp.weixin.qq.com",
    "need_open_comment": 0,
    "only_fans_can_comment": 0,
}

data = {"articles": [article]}
json_data = json.dumps(data, ensure_ascii=False)
encoded = json_data.encode("utf-8")

# 保存发送的数据
with open("output/send_data.txt", "wb") as f:
    f.write(encoded)

url = f"https://api.weixin.qq.com/cgi-bin/draft/add?access_token={token}"
response = requests.post(url, data=encoded, headers={"Content-Type": "application/json; charset=utf-8"})
result = response.json()
print("Result:", result)