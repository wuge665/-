"""
X platform content generator
"""
import os
from typing import List, Dict
from loguru import logger


class XEditor:
    """X platform editor"""

    DEFAULT_STYLE = """你是一个关注科技资讯的普通人，在X平台上分享有趣的内容。

根据下面的新闻生成一条X帖子：

1. 长度：100-200字
2. 风格：
   - 像跟朋友聊天，自然、真实
   - 不要用"哇塞/震惊/天啊"等夸张开头
   - 不要每句话都惊叹号，保持平静的分享语气
   - 可以有个人观点，但不要刻意煽情
3. 结构：
   - 开头：平淡说出核心信息（数据、反差）
   - 中间：补充1-2句背景或细节
   - 结尾：一句真实感受或想法
4. 禁止：
   - 禁止"哇塞/震惊/太牛了/绝了"等夸张词
   - 不要"首先/其次/最后"
   - 不要车轱辘话和AI味
   - 不要每句都加emoji，最多1个
5. 语气：平实、自然，像随手发的真实动态

只输出帖子内容，不要标题。"""

    def __init__(self):
        # 尝试加载AGENTS.md
        agents_file = os.path.join(os.path.dirname(__file__), "..", "AGENTS.md")
        if os.path.exists(agents_file):
            with open(agents_file, "r", encoding="utf-8") as f:
                self.style_prompt = f.read()
        else:
            self.style_prompt = self.DEFAULT_STYLE
        
        self.use_api = bool(
            os.getenv("ZHIPU_API_KEY") or
            os.getenv("XAI_API_KEY") or
            os.getenv("OPENROUTER_API_KEY") or
            os.getenv("ANTHROPIC_API_KEY") or
            os.getenv("OPENAI_API_KEY")
        )

    def generate(self, articles: List[Dict], count: int = 5) -> List[Dict]:
        posts = []

        if not self.use_api:
            logger.warning("No AI API configured, using mock mode")

        for i, article in enumerate(articles[:count], 1):
            logger.info(f"Processing {i}: {article.get('title', '')[:30]}...")
            try:
                post = self._generate_post(article)
                posts.append(post)
            except Exception as e:
                logger.error(f"Failed to generate post {i}: {e}")

        return posts

    def _generate_post(self, article: Dict) -> Dict:
        if self.use_api:
            return self._generate_with_ai(article)
        else:
            return self._generate_mock(article)

    def _generate_with_ai(self, article: Dict) -> Dict:
        prompt = f"""{self.DEFAULT_STYLE}

News title: {article.get('title', '')}
Source: {article.get('source', '')}
Summary: {article.get('summary', '')}

Output just the post content."""

        for name, key_env, func in [
            ("Zhipu", "ZHIPU_API_KEY", self._call_zhipu),
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
                    logger.warning(f"{name} failed: {e}")
                    continue

        return self._generate_mock(article)

    def _call_zhipu(self, prompt: str, article: Dict) -> Dict:
        import httpx
        api_key = os.getenv("ZHIPU_API_KEY")
        client = httpx.Client(timeout=60.0)
        response = client.post(
            "https://open.bigmodel.cn/api/paas/v4/chat/completions",
            headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
            json={"model": "glm-4-flash", "messages": [{"role": "user", "content": prompt}], "max_tokens": 300}
        )
        response.raise_for_status()
        result = response.json()
        content = result["choices"][0]["message"]["content"]
        if isinstance(content, bytes):
            content = content.decode("utf-8", errors="replace")
        return self._parse_ai_response(content, article)

    def _call_grok(self, prompt: str, article: Dict) -> Dict:
        import httpx
        api_key = os.getenv("XAI_API_KEY")
        client = httpx.Client(timeout=60.0)
        response = client.post(
            "https://api.x.ai/v1/chat/completions",
            headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
            json={"model": "grok-4-mini", "messages": [{"role": "user", "content": prompt}], "max_tokens": 300}
        )
        response.raise_for_status()
        result = response.json()
        return self._parse_ai_response(result["choices"][0]["message"]["content"], article)

    def _call_claude(self, prompt: str, article: Dict) -> Dict:
        import anthropic
        client = anthropic.Anthropic()
        response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=300,
            messages=[{"role": "user", "content": prompt}]
        )
        return self._parse_ai_response(response.content[0].text, article)

    def _call_openai(self, prompt: str, article: Dict) -> Dict:
        from openai import OpenAI
        client = OpenAI()
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=300
        )
        return self._parse_ai_response(response.choices[0].message.content, article)

    def _call_openrouter(self, prompt: str, article: Dict) -> Dict:
        import httpx
        api_key = os.getenv("OPENROUTER_API_KEY")
        client = httpx.Client(timeout=60.0)
        response = client.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
            json={"model": "openai/gpt-4.1-nano:free", "messages": [{"role": "user", "content": prompt}], "max_tokens": 300}
        )
        response.raise_for_status()
        result = response.json()
        return self._parse_ai_response(result["choices"][0]["message"]["content"], article)

    def _parse_ai_response(self, text: str, article: Dict) -> Dict:
        content = text.strip()
        return {
            "content": content,
            "title": article.get("title", ""),
            "source_url": article.get("url", ""),
            "source_name": article.get("source", ""),
        }

    def _generate_mock(self, article: Dict) -> Dict:
        return {
            "content": f"[{article.get('title', '')}] {article.get('summary', '')}",
            "title": article.get("title", ""),
            "source_url": article.get("url", ""),
            "source_name": article.get("source", ""),
        }