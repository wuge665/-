"""
AI编辑模块
将资讯转化为人工风格的文章
"""
import os
import json
from typing import List, Dict
from loguru import logger


class AIEditor:
    """AI编辑器"""
    
    # 默认风格提示词
    DEFAULT_STYLE = """你是一位真实测评过各种AI工具和科技产品的编辑"小科"，分享的内容都是自己真正用过的、实测过的。

⚠️ 核心原则（最重要）：
- 保留原文90%以上内容，只改语病和不通顺的地方
- 不要删减数据、案例、细节，原文有的全部保留
- 不要重新创作，只做轻微润色，让它读起来更通顺

✅ 必须做到：
- 原文数据、参数、对比、案例：一个都不能少
- 只改：不通顺的句子、明显的语病、啰嗦的表达
- 像人类编辑：看完文章，用自己的话简单复述（但保留所有原文信息）
- 自然流畅：不写小标题，用段落自然过渡

📸 图片规则（必须执行）：
- 在正文合适位置插入1-3张图片，用Markdown格式：![描述](图片URL)
- 图片必须真实有效，来自：原文配图、官方产品图、公司Logo、新闻截图
- 每张图片下方标注：(图片来源：XXX)
- 禁止使用占位符、无效URL、或随便编的链接

📝 输出要求：
【标题】不超过25字，带数字/反差/悬念，像新闻标题那样吸引人
【正文】600-1000字，保留原文90%内容，只做轻微润色
- 开头：直接说体验/发现，不要铺垫
- 中间：保留原文所有细节和数据
- 结尾：真实感受或建议
【标签】#AI #大模型 #工具测评 选2-3个
【配图说明】列出所有图片URL和来源

⚠️ 再次提醒：不要创作新content！不要删减原文！不要"首先/其次"！"""
    
    def __init__(self, style_prompt: str = None):
        # 尝试加载AGENTS.md
        agents_file = os.path.join(os.path.dirname(__file__), "..", "AGENTS.md")
        if os.path.exists(agents_file):
            with open(agents_file, "r", encoding="utf-8") as f:
                self.style_prompt = f.read()
        else:
            self.style_prompt = style_prompt or self.DEFAULT_STYLE
        
        # API配置 - 支持 OpenRouter, Claude, OpenAI, Grok, 智谱
        self.use_api = bool(
            os.getenv("OPENROUTER_API_KEY") or 
            os.getenv("ANTHROPIC_API_KEY") or 
            os.getenv("OPENAI_API_KEY") or
            os.getenv("XAI_API_KEY") or
            os.getenv("ZHIPU_API_KEY")
        )
    
    def generate(self, articles: List[Dict]) -> List[Dict]:
        """为每篇文章生成人工风格的帖子"""
        posts = []
        
        if not self.use_api:
            logger.warning("⚠️ 未配置AI API，使用模拟模式")
        
        for i, article in enumerate(articles, 1):
            logger.info(f"   正在处理第 {i} 篇: {article.get('title', '')[:30]}...")
            
            try:
                post = self._generate_post(article)
                posts.append(post)
            except Exception as e:
                logger.error(f"   ❌ 第 {i} 篇生成失败: {e}")
        
        return posts
    
    def _generate_post(self, article: Dict) -> Dict:
        """生成单篇文章"""
        if self.use_api:
            return self._generate_with_ai(article)
        else:
            return self._generate_mock(article)
    
    def _generate_with_ai(self, article: Dict) -> Dict:
        """使用AI生成内容"""
        # 构建提示词
        prompt = f"""{self.style_prompt}

请根据以下资讯，生成一篇公众号文章：

标题: {article.get('title', '')}
来源: {article.get('source', '')}
链接: {article.get('url', '')}
摘要: {article.get('summary', '')}

请严格按照格式输出：
【标题】
【正文】
【标签】
【配图建议】"""
        
        # 根据 AI_PROVIDER 配置选择
        provider = os.getenv("AI_PROVIDER", "zhipu").lower()
        
        if provider == "claude":
            api_key = os.getenv("ANTHROPIC_API_KEY")
            if api_key:
                return self._call_claude(prompt, article)
        
        elif provider == "openai":
            api_key = os.getenv("OPENAI_API_KEY")
            if api_key:
                return self._call_openai(prompt, article)
        
        elif provider == "grok":
            api_key = os.getenv("XAI_API_KEY")
            if api_key:
                return self._call_grok(prompt, article)
        
        elif provider == "openrouter":
            api_key = os.getenv("OPENROUTER_API_KEY")
            if api_key:
                return self._call_openrouter(prompt, article)
        
        elif provider == "zhipu":
            api_key = os.getenv("ZHIPU_API_KEY")
            if api_key:
                return self._call_zhipu(prompt, article)
        
        # 回退：按优先级尝试任一可用API
        for name, key_env, func in [
            ("智谱", "ZHIPU_API_KEY", self._call_zhipu),
            ("Grok", "XAI_API_KEY", self._call_grok),
            ("Claude", "ANTHROPIC_API_KEY", self._call_claude),
            ("OpenAI", "OPENAI_API_KEY", self._call_openai),
            ("OpenRouter", "OPENROUTER_API_KEY", self._call_openrouter),
        ]:
            api_key = os.getenv(key_env)
            if api_key:
                try:
                    return func(prompt, article)
                except Exception as e:
                    logger.warning(f"{name}调用失败，尝试下一个: {e}")
                    continue
        
        return self._generate_mock(article)
    
    def _call_claude(self, prompt: str, article: Dict) -> Dict:
        """调用Claude API"""
        import anthropic
        client = anthropic.Anthropic()
        
        response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=2000,
            messages=[{"role": "user", "content": prompt}]
        )
        
        return self._parse_ai_response(response.content[0].text, article)
    
    def _call_openai(self, prompt: str, article: Dict) -> Dict:
        """调用OpenAI API"""
        from openai import OpenAI
        client = OpenAI()
        
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=2000
        )
        
        return self._parse_ai_response(response.choices[0].message.content, article)
    
    def _call_openrouter(self, prompt: str, article: Dict) -> Dict:
        """调用OpenRouter API"""
        import httpx
        
        api_key = os.getenv("OPENROUTER_API_KEY")
        model = os.getenv("OPENROUTER_MODEL", "openai/gpt-4.1-nano:free")
        
        client = httpx.Client(timeout=60.0)
        response = client.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            },
            json={
                "model": model,
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": 2000
            }
        )
        response.raise_for_status()
        result = response.json()
        
        return self._parse_ai_response(result["choices"][0]["message"]["content"], article)
    
    def _call_grok(self, prompt: str, article: Dict) -> Dict:
        """调用Grok (xAI) API"""
        import httpx
        
        api_key = os.getenv("XAI_API_KEY")
        model = os.getenv("XAI_MODEL", "grok-4-mini")
        
        client = httpx.Client(timeout=60.0)
        response = client.post(
            "https://api.x.ai/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            },
            json={
                "model": model,
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": 2000
            }
        )
        response.raise_for_status()
        result = response.json()
        
        return self._parse_ai_response(result["choices"][0]["message"]["content"], article)
    
    def _call_zhipu(self, prompt: str, article: Dict) -> Dict:
        """调用智谱AI API"""
        import httpx
        import os
        
        api_key = os.getenv("ZHIPU_API_KEY")
        model = os.getenv("ZHIPU_MODEL", "glm-4-flash")
        
        client = httpx.Client(timeout=60.0)
        response = client.post(
            "https://open.bigmodel.cn/api/paas/v4/chat/completions",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            },
            json={
                "model": model,
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": 2000
            }
        )
        response.raise_for_status()
        result = response.json()
        content = result["choices"][0]["message"]["content"]
        if isinstance(content, bytes):
            content = content.decode("utf-8", errors="replace")
        
        return self._parse_ai_response(content, article)
    
    def _parse_ai_response(self, text: str, article: Dict) -> Dict:
        """解析AI响应"""
        # 简单解析：按【标题】【正文】【标签】分割
        parts = text.split("【")
        
        post = {
            "title": article.get("title", ""),
            "content": "",
            "tags": "#科技 #行业观察",
            "source_url": article.get("url", ""),
            "source_name": article.get("source", ""),
        }
        
        for part in parts:
            if "标题】" in part:
                post["title"] = part.split("】")[1].split("【")[0].strip()
            elif "正文】" in part:
                post["content"] = part.split("】")[1].split("【标签】")[0].strip()
            elif "标签】" in part:
                post["tags"] = part.split("】")[1].strip()
        
        # 如果解析失败，使用原始内容
        if not post["content"]:
            post["content"] = text
        
        return post
    
    def _generate_mock(self, article: Dict) -> Dict:
        """模拟生成（无API时使用）"""
        return {
            "title": article.get("title", ""),
            "content": f"""{article.get('summary', '')}

来源: {article.get('source', '')}
链接: {article.get('url', '')}

---
注：当前为测试模式，请配置AI API以生成完整内容""",
            "tags": "#科技 #行业观察",
            "source_url": article.get("url", ""),
            "source_name": article.get("source", ""),
        }