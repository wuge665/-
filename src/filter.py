"""
内容过滤与去重模块
对抓取的资讯进行过滤、评分、排序
"""
import hashlib
from datetime import datetime, timedelta
from typing import List, Dict
from loguru import logger


class ContentFilter:
    """内容过滤器"""
    
    # 高权重关键词（行业热点）
    HIGH_WEIGHT_KEYWORDS = [
        "大模型", "LLM", "GPT", "AI", "AGI",
        "ChatGPT", "Gemini", "Claude", "Sora",
        "自动驾驶", "机器人", "量子计算",
        "OpenAI", "Google", "Anthropic", "Meta",
    ]
    
    # 低质量关键词（需过滤）
    LOW_QUALITY_KEYWORDS = [
        "广告", "招聘", "优惠券", "促销", "限时",
        "免费领取", "扫码关注", "抽奖",
    ]
    
    def __init__(self):
        # 简单内存缓存，实际项目可用Redis
        self.seen_hashes = set()
    
    def process(self, articles: List[Dict]) -> List[Dict]:
        """处理文章列表：去重 → 过滤 → 评分 → 排序"""
        if not articles:
            return []
        
        logger.info(f"   原始文章: {len(articles)} 篇")
        
        # 1. 去重
        articles = self._deduplicate(articles)
        logger.info(f"   去重后: {len(articles)} 篇")
        
        # 2. 过滤低质量内容
        articles = self._filter_low_quality(articles)
        logger.info(f"   过滤低质量后: {len(articles)} 篇")
        
        # 3. 评分排序
        articles = self._score_and_rank(articles)
        
        return articles
    
    def _deduplicate(self, articles: List[Dict]) -> List[Dict]:
        """标题+摘要指纹去重"""
        seen = set()
        unique = []
        
        for article in articles:
            # 生成指纹
            fingerprint = self._generate_fingerprint(article)
            
            if fingerprint not in seen and fingerprint not in self.seen_hashes:
                seen.add(fingerprint)
                unique.append(article)
        
        # 更新缓存（保留最近7天的）
        self.seen_hashes.update(seen)
        
        return unique
    
    def _generate_fingerprint(self, article: Dict) -> str:
        """生成文章指纹"""
        title = article.get("title", "")
        summary = article.get("summary", "")[:100]
        content = (title + summary).lower()
        return hashlib.md5(content.encode()).hexdigest()
    
    def _filter_low_quality(self, articles: List[Dict]) -> List[Dict]:
        """过滤低质量内容"""
        filtered = []
        
        for article in articles:
            title = article.get("title", "")
            
            # 检查是否包含低质量关键词
            if any(kw in title for kw in self.LOW_QUALITY_KEYWORDS):
                continue
            
            # 检查标题长度
            if len(title) < 15 or len(title) > 80:
                continue
            
            # 检查是否有摘要/内容
            if not article.get("summary") and not article.get("content"):
                continue
            
            filtered.append(article)
        
        return filtered
    
    def _score_and_rank(self, articles: List[Dict]) -> List[Dict]:
        """评分并排序"""
        scored = []
        
        for article in articles:
            score = 0
            title = article.get("title", "")
            
            # 高权重关键词加分
            for kw in self.HIGH_WEIGHT_KEYWORDS:
                if kw.lower() in title.lower():
                    score += 10
            
            # 来源权重
            high_quality_sources = ["techcrunch", "hackernews", "theverge", "36kr"]
            if article.get("source") in high_quality_sources:
                score += 5
            
            # 时效性（越新越好）
            try:
                published = article.get("published", "")
                if published:
                    dt = datetime.fromisoformat(published.replace("Z", "+00:00"))
                    hours_old = (datetime.now() - dt).total_seconds() / 3600
                    if hours_old < 24:
                        score += max(0, 5 - hours_old / 6)
            except:
                pass
            
            # 摘要长度（内容丰富度）
            summary_len = len(article.get("summary", ""))
            if summary_len > 100:
                score += 3
            elif summary_len > 50:
                score += 1
            
            article["score"] = score
            scored.append(article)
        
        # 按分数降序排序
        scored.sort(key=lambda x: x.get("score", 0), reverse=True)
        
        return scored