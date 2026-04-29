"""
优化本地公众号文章为更标准的 Markdown 格式
"""
import re
from pathlib import Path

def convert_markdown():
    output_dir = Path("output")
    
    for md_file in output_dir.glob("draft_*.md"):
        with open(md_file, "r", encoding="utf-8") as f:
            content = f.read()
        
        # 移除多余的分隔线 ##
        content = re.sub(r'\n##\s*\n', '\n', content)
        
        # 确保标题格式正确
        content = re.sub(r'^#\s+', '# ', content, flags=re.MULTILINE)
        
        # 移除 "来源:" 和 "链接:" 前的空行
        content = re.sub(r'\n\n来源:', '\n来源:', content)
        content = re.sub(r'\n\n链接:', '\n链接:', content)
        
        # 确保标签前有空行
        content = re.sub(r'(?<!\\n)(标签:)', r'\n\1', content)
        
        with open(md_file, "w", encoding="utf-8") as f:
            f.write(content.strip() + "\n")
        
        print(f"✅ 已优化: {md_file.name}")

if __name__ == "__main__":
    convert_markdown()
