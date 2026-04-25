"""
微信公众号发布模块
将文章发布到微信公众号
"""
import os
import requests
from typing import Dict
from pathlib import Path
from loguru import logger


class WeChatPublisher:
    """微信公众号发布器"""
    
    def __init__(self):
        self.app_id = os.getenv("WECHAT_APP_ID")
        self.app_secret = os.getenv("WECHAT_APP_SECRET")
        self.access_token = None
        
        if not self.app_id or not self.app_secret:
            logger.warning("⚠️ 未配置微信公众号凭证 (.env文件)")
    
    def publish(self, post: Dict, as_draft: bool = True) -> Dict:
        """发布文章"""
        if not self.app_id:
            logger.warning("⚠️ 无凭证，使用模拟模式")
            return self._mock_publish(post, as_draft)
        
        try:
            # 获取access_token
            token = self._get_access_token()
            if not token:
                return {"success": False, "error": "获取access_token失败"}
            
            if as_draft:
                return self._publish_draft(token, post)
            else:
                return self._publish_article(token, post)
                
        except Exception as e:
            logger.error(f"发布失败: {e}")
            return {"success": False, "error": str(e)}
    
    def _get_access_token(self) -> str:
        """获取access_token"""
        url = "https://api.weixin.qq.com/cgi-bin/token"
        params = {
            "grant_type": "client_credential",
            "appid": self.app_id,
            "secret": self.app_secret
        }
        
        try:
            response = requests.get(url, params=params, timeout=10)
            data = response.json()
            
            if "access_token" in data:
                return data["access_token"]
            else:
                logger.error(f"获取token失败: {data}")
                return None
        except Exception as e:
            logger.error(f"获取token异常: {e}")
            return None
    
    def _clean_text(self, text: str, max_len: int = 64) -> str:
        """清理文本并限制长度 - 移除emoji和特殊字符"""
        if not text:
            return ""
        # 移除emoji字符
        import re
        emoji_pattern = re.compile(
            "["
            "\U0001F600-\U0001F64F"  # emoticons
            "\U0001F300-\U0001F5FF"  # symbols & pictographs
            "\U0001F680-\U0001F6FF"  # transport & map symbols
            "\U0001F1E0-\U0001F1FF"  # flags
            "\U00002702-\U000027B0"
            "\U000024C2-\U0001F251"
            "]+", flags=re.UNICODE
        )
        text = emoji_pattern.sub('', text)
        # 限制长度
        text = text.strip()[:max_len]
        return text
    
    def _publish_draft(self, token: str, post: Dict) -> Dict:
        """发布到草稿箱"""
        # 不使用封面图片，避免40007错误
        thumb_media_id = ""
        
        url = f"https://api.weixin.qq.com/cgi-bin/draft/add?access_token={token}"
        
        # 构建文章内容
        content_html = self._markdown_to_wechat(post.get("content", "") or "")
        
        # 清理和限制标题、摘要 - 移除emoji但保留中文
        import re
        title_raw = post.get("title", "") or "科技简报"
        # 移除emoji
        emoji_pattern = re.compile("["
            "\U0001F600-\U0001F64F"
            "\U0001F300-\U0001F5FF"
            "\U0001F680-\U0001F6FF"
            "\U0001F1E0-\U0001F1FF"
            "\U00002702-\U000027B0"
            "\U000024C2-\U0001F251"
            "]+", flags=re.UNICODE)
        title = emoji_pattern.sub('', title_raw)[:30]
        digest = post.get("content", "")[:54]
        
        articles = [{
            "title": (title or "科技简报")[:30],
            "author": "小科",
            "digest": (digest or "科技简报每日资讯")[:54],
            "content": content_html,
            "content_source_url": post.get("source_url", "") or "https://mp.weixin.qq.com",
            "thumb_media_id": thumb_media_id,
            "need_open_comment": 0,
            "only_fans_can_comment": 0,
        }]
        
        data = {"articles": articles}
        
        try:
            import json
            
            json_data = json.dumps(data, ensure_ascii=False)
            response = requests.post(
                url, 
                data=json_data.encode("utf-8"),
                timeout=30,
                headers={"Content-Type": "application/json; charset=utf-8"}
            )
            result = response.json()
            
            if result.get("errcode") == 0 or result.get("media_id"):
                logger.info(f"   ✅ 草稿发布成功, media_id: {result.get('media_id')}")
                return {"success": True, "draft_id": result.get("media_id")}
            elif result.get("errcode") == 40007:
                # 无效的media_id，尝试不使用封面上传
                articles[0]["thumb_media_id"] = ""
                response2 = requests.post(url, json={"articles": articles}, timeout=30)
                result2 = response2.json()
                if result2.get("errcode") == 0:
                    logger.info(f"   ✅ 草稿发布成功(无封面)")
                    return {"success": True, "draft_id": result2.get("media_id")}
                logger.error(f"   ❌ 重试也失败: {result2}")
                return {"success": False, "error": result2.get("errmsg", "未知错误")}
            else:
                logger.error(f"   ❌ 发布失败: {result}")
                return {"success": False, "error": result.get("errmsg", "未知错误")}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _get_or_upload_thumb(self, token: str) -> str:
        """获取或上传封面图片"""
        # 检查是否已有缓存的封面media_id
        cache_file = Path("output/thumb_cache.txt")
        if cache_file.exists():
            cached_id = cache_file.read_text().strip()
            if cached_id:
                return cached_id
        
        # 上传新封面
        media_id = self._upload_thumb_simple(token)
        if media_id:
            cache_file.write_text(media_id)
        return media_id
    
    def _upload_thumb_simple(self, token: str) -> str:
        """简单上传封面图片"""
        # 使用微信图床上传图片（这里用公共图片）
        img_urls = [
            "https://mmbiz.qlogo.cn/mmbiz_png/libY2libqNb4pictG9zC21p1y3iaO2nicia0mibibibibibibibibibibibibibibibibibibibibibibibibibibibibibibibibibibibibibibibibibg/0",
            "https://picsum.photos/400/300",
        ]
        
        for img_url in img_urls:
            try:
                resp = requests.get(img_url, timeout=10, headers={
                    "User-Agent": "Mozilla/5.0"
                })
                if resp.status_code == 200 and len(resp.content) > 1000:
                    # 上传图片素材
                    upload_url = f"https://api.weixin.qq.com/cgi-bin/material/add_material?access_token={token}&type=image"
                    files = {"media": ("cover.jpg", resp.content, "image/jpeg")}
                    r = requests.post(upload_url, files=files, timeout=30)
                    result = r.json()
                    if result.get("media_id"):
                        logger.info(f"   ✅ 封面上传成功")
                        return result["media_id"]
            except Exception as e:
                logger.warning(f"   上传封面失败: {e}")
                continue
        
        return ""
    
    def _upload_thumb(self, token: str) -> str:
        """上传封面图片，返回media_id"""
        # 使用一个默认的封面图片URL
        thumb_url = "https://mmbiz.qpic.cn/mmbiz_jpg/LibY2libqNb4pictG9zC21p1y3iaO2nicia0m7eYb6icq0ibf0icTgiaGk4f8lF2sB3mib8M4iaDBpBicn5ia3s3icB1ib8bVg/0"
        
        try:
            # 先下载图片
            img_response = requests.get(thumb_url, timeout=10)
            if img_response.status_code != 200:
                logger.warning("   下载封面图片失败，使用默认")
                return ""
            
            # 上传为永久素材
            upload_url = f"https://api.weixin.qq.com/cgi-bin/material/add_material?access_token={token}&type=image"
            
            files = {"media": ("thumb.jpg", img_response.content, "image/jpeg")}
            response = requests.post(upload_url, files=files, timeout=30)
            result = response.json()
            
            if result.get("media_id"):
                logger.info(f"   ✅ 封面上传成功")
                return result["media_id"]
            else:
                logger.warning(f"   封面上传失败: {result}")
                return ""
        except Exception as e:
            logger.warning(f"   封面上传异常: {e}")
            return ""
    
    def _publish_article(self, token: str, post: Dict) -> Dict:
        """直接发布文章（需已上传封面）"""
        # 实现直接发布的逻辑
        return self._publish_draft(token, post)
    
    def _markdown_to_wechat(self, content: str) -> str:
        """将Markdown转换为微信HTML格式"""
        import re
        
        # 粗体
        content = content.replace("**", "<strong>").replace("**", "</strong>")
        
        # 链接
        content = re.sub(r'\[([^\]]+)\]\(([^\)]+)\)', r'<a href="\2">\1</a>', content)
        
        # 段落 - 按换行分段
        paragraphs = content.split("\n")
        result = []
        for p in paragraphs:
            p = p.strip()
            if p:
                result.append(f"<p>{p}</p>")
        
        return "\n".join(result)
    
    def _mock_publish(self, post: Dict, as_draft: bool) -> Dict:
        """模拟发布（无凭证时）"""
        logger.info(f"   [模拟] 发布到{'草稿箱' if as_draft else '正式发布'}")
        logger.info(f"   标题: {post.get('title', '')}")
        
        # 保存到本地文件模拟
        import json
        from pathlib import Path
        
        output_dir = Path("output/drafts")
        output_dir.mkdir(parents=True, exist_ok=True)
        
        filename = f"draft_{len(list(output_dir.glob('*.json'))) + 1}.json"
        with open(output_dir / filename, "w", encoding="utf-8") as f:
            json.dump(post, f, ensure_ascii=False, indent=2)
        
        logger.info(f"   📁 已保存到 {output_dir / filename}")
        
        return {"success": True, "mock": True, "file": str(output_dir / filename)}