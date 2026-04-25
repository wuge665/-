import os
import sys
os.chdir(r"F:\程序项目\公众号自动流")
sys.path.insert(0, r"F:\程序项目\公众号自动流")

import requests
from src.editor import AIEditor

# 测试生成
editor = AIEditor()
test_article = {
    "title": "Test title",
    "source": "TechCrunch",
    "url": "https://test.com",
    "summary": "Test summary"
}

# 调用API生成
posts = editor.generate([test_article])
print("Generated posts count:", len(posts))

if posts:
    post = posts[0]
    print("Title:", post.get("title"))
    print("Content preview:", post.get("content", "")[:50])
    
    # 保存看正确性
    with open("output/debug_article.md", "w", encoding="utf-8") as f:
        f.write("Title: ")
        f.write(post.get("title", ""))
        f.write("\n\nContent:\n")
        f.write(post.get("content", ""))