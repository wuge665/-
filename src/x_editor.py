"""
X platform content generator
"""
import os
from typing import List, Dict
from loguru import logger


class XEditor:
    """X platform editor"""

    DEFAULT_STYLE = """You are a normal person who browses tech news and shares interesting stuff on X.

Write a X post based on the news below:

1. Length: 100-200 characters
2. Style:
   - Like sharing with friends, not writing news
   - Can be funny, surprised, or skeptical
   - Real tone, with some emotion
   - First sentence must be eye-catching
3. Structure:
   - Start: One sentence about core point (data, contrast, or controversy)
   - Middle: 1-2 sentences about background or details
   - End: One personal feeling or leave suspense
4. Forbidden:
   - No official tone like "recently announced"
   - No "first/second/last"
   - No links in the text
   - No AI-like repetitive sentences
5. End: Can add an emoji for realism

Output just the post content, no title."""

    def __init__(self):
        self.use_api = bool(
            os.getenv("OPENROUTER_API_KEY") or
            os.getenv("ANTHROPIC_API_KEY") or
            os.getenv("OPENAI_API_KEY") or
            os.getenv("XAI_API_KEY") or
            os.getenv("ZHIPU_API_KEY")
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