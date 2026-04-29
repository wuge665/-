"""
资讯抓取模块
从多个来源抓取科技资讯
"""
import feedparser
import requests
import json
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from pathlib import Path
from loguru import logger
from typing import List, Dict


class NewsFetcher:
    """资讯抓取器"""
    
    def __init__(self):
        # 从 sources.json 加载配置
        self.sources_config = self._load_sources_config()
        self.RSS_SOURCES = self._build_rss_sources()
        
        # 如果配置文件加载失败，使用默认配置
        if not self.RSS_SOURCES:
            self.RSS_SOURCES = {
                "techcrunch": "https://techcrunch.com/feed/",
                "theverge": "https://www.theverge.com/rss/index.xml",
                "wired": "https://www.wired.com/feed/rss",
                "hackernews": "https://hnrss.org/frontpage",
                "36kr": "https://36kr.com/feed",
                "infoq": "https://feed.infoq.com/",
                "medium_aitools": "https://medium.com/feed/tag/artificial-intelligence-tools/",
                "medium_tutorials": "https://medium.com/feed/tag/tutorial/",
                "medium_ai": "https://medium.com/feed/tag/machine-learning/",
            }
        
        # 初始化请求会话
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        })
    
    def _load_sources_config(self) -> dict:
        """加载 sources.json 配置"""
        config_file = Path(__file__).parent.parent / "config" / "sources.json"
        if config_file.exists():
            with open(config_file, "r", encoding="utf-8") as f:
                return json.load(f)
        return {"sources": {}}
    
    def _build_rss_sources(self) -> dict:
        """从配置构建 RSS 源列表"""
        sources = {}
        for key, config in self.sources_config.get("sources", {}).items():
            if config.get("enabled", True) and config.get("type") == "rss":
                sources[key] = config["url"]
        return sources
    
    # 需要排除的域名（公众号来源）
    EXCLUDE_DOMAINS = [
        "mp.weixin.qq.com",
        "weixin.qq.com",
        "weixindubai.com",
    ]
    
    def fetch(self, sources: List[str] = None) -> List[Dict]:
        """抓取所有配置的资讯源"""
        articles = []
        
        if sources:
            target_sources = {k: v for k, v in self.RSS_SOURCES.items() if k in sources}
        else:
            target_sources = self.RSS_SOURCES
        
        for name, url in target_sources.items():
            try:
                logger.info(f"   正在抓取 {name}...")
                articles.extend(self._fetch_rss(name, url))
            except Exception as e:
                logger.error(f"   ❌ {name} 抓取失败: {str(e)}")
        
        # 按时间排序
        articles.sort(key=lambda x: x.get("published", ""), reverse=True)
        
        return articles
    
    def _fetch_rss(self, source_name: str, url: str) -> List[Dict]:
        """通过RSS抓取单个源"""
        try:
            feed = feedparser.parse(url)
            articles = []
            
            for entry in feed.entries[:20]:  # 每个源最多取20条
                # 检查是否排除域名
                if any(domain in entry.get("link", "") for domain in self.EXCLUDE_DOMAINS):
                    continue
                
                article = {
                    "source": source_name,
                    "title": entry.get("title", "").strip(),
                    "url": entry.get("link", ""),
                    "summary": self._clean_summary(entry.get("summary", "")),
                    "published": self._parse_date(entry.get("published", "")),
                    "author": entry.get("author", ""),
                }
                
                # 简单过滤：标题太短或包含特定关键词则跳过
                if len(article["title"]) < 10:
                    continue
                if any(kw in article["title"] for kw in ["广告", "招聘", "优惠券"]):
                    continue
                
                articles.append(article)
            
            logger.info(f"   ✅ {source_name}: 获取 {len(articles)} 篇文章")
            return articles
            
        except Exception as e:
            logger.warning(f"   ⚠️ {source_name} 解析失败: {e}")
            return []
    
    def _clean_summary(self, summary: str) -> str:
        """清理摘要文本"""
        if not summary:
            return ""
        # 移除HTML标签
        soup = BeautifulSoup(summary, "html.parser")
        text = soup.get_text()
        # 截断过长内容
        if len(text) > 300:
            text = text[:300] + "..."
        return text.strip()
    
    def _parse_date(self, date_str: str) -> str:
        """解析日期字符串"""
        try:
            if not date_str:
                return datetime.now().isoformat()
            # 尝试解析常见格式
            from email.utils import parsedate_to_datetime
            dt = parsedate_to_datetime(date_str)
            return dt.isoformat()
        except:
            return datetime.now().isoformat()


def fetch_with_playwright(source_name: str, config: Dict) -> List[Dict]:
    """使用浏览器抓取动态内容（备选方案）"""
    # 如果RSS无法满足需求，可扩展此方法
    pass
