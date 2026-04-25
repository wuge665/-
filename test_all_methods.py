import os
import sys
import requests
import json

os.chdir(r"F:\程序项目\公众号自动流")
from dotenv import load_dotenv
load_dotenv(r"F:\程序项目\公众号自动流\.env")

app_id = os.getenv("WECHAT_APP_ID")
app_secret = os.getenv("WECHAT_APP_SECRET")

# 换一种方式获取token - 用测试接口验证
url = f"https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid={app_id}&secret={app_secret}"
r = requests.get(url)
print("Token URL:", url)
print("Response:", r.json())

if r.json().get("access_token"):
    token = r.json()["access_token"]
    
    # 用最简单的article测试
    article = {
        "title": "Test123",
        "author": "A", 
        "digest": "D",
        "content": "<p>Test</p>",
    }
    
    # 尝试不同的编码方式
    test_cases = [
        ("json param", {"articles": [article]}),
        ("data str", json.dumps({"articles": [article]})),
        ("data encoded", json.dumps({"articles": [article]}).encode('utf-8')),
    ]
    
    for name, data in test_cases:
        try:
            if isinstance(data, dict):
                resp = requests.post(f"https://api.weixin.qq.com/cgi-bin/draft/add?access_token={token}", json=data)
            else:
                resp = requests.post(f"https://api.weixin.qq.com/cgi-bin/draft/add?access_token={token}", data=data)
            print(f"{name}: {resp.json()}")
        except Exception as e:
            print(f"{name}: Error - {e}")