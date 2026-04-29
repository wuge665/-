"""
X平台内容自动生成系统
每日抓取资讯 → AI生成短内容 → 保存到本地待审核
"""
import os
import sys
import argparse
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent / ".env")

from loguru import logger
sys.path.insert(0, str(Path(__file__).parent))

from src.fetcher import NewsFetcher
from src.filter import ContentFilter
from src.x_editor import XEditor


def setup_logger():
    """配置日志"""
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)

    logger.add(
        f"logs/x_brief_{datetime.now().strftime('%Y%m%d')}.log",
        rotation="00:00",
        retention="7 days",
        level="INFO"
    )


def parse_args():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(description="X平台内容生成系统")
    parser.add_argument("--count", type=int, default=10, help="生成内容数量")
    parser.add_argument("--sources", nargs="+", default=None, help="指定资讯源")
    return parser.parse_args()


def main():
    setup_logger()
    args = parse_args()

    logger.info("=" * 50)
    logger.info("🐦 X平台内容生成系统启动")
    logger.info(f"📅 运行时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info("=" * 50)

    # 1. 抓取资讯
    logger.info("📡 步骤1: 抓取科技资讯...")
    fetcher = NewsFetcher()
    articles = fetcher.fetch(sources=args.sources)
    logger.info(f"    抓取到 {len(articles)} 篇原始文章")

    if not articles:
        logger.warning("⚠️ 未抓取到任何文章")
        return

    # 2. 过滤与去重
    logger.info("🔍 步骤2: 过滤与去重...")
    content_filter = ContentFilter()
    filtered = content_filter.process(articles)
    logger.info(f"    保留 {len(filtered)} 篇优质内容")

    if not filtered:
        logger.warning("⚠️ 过滤后无内容")
        return

    # 3. AI生成X平台内容
    logger.info("✍️ 步骤3: AI生成X平台内容...")
    editor = XEditor()
    count = min(args.count, len(filtered))
    posts = editor.generate(filtered, count=count)
    logger.info(f"    生成 {len(posts)} 条待发布内容")

    if not posts:
        logger.warning("⚠️ 未生成任何内容")
        return

    # 4. 保存到本地
    logger.info("💾 步骤4: 保存到本地...")
    x_content_dir = Path("x平台内容")
    x_content_dir.mkdir(exist_ok=True)

    for i, post in enumerate(posts, 1):
        with open(x_content_dir / f"draft_{i}.md", "w", encoding="utf-8") as f:
            f.write(f"{post['content']}\n\n")
            f.write(f"---\n")
            f.write(f"来源: {post.get('source_name', '')}\n")
            f.write(f"链接: {post.get('source_url', '')}\n")

    logger.info(f"📁 内容已保存到 x平台内容/draft_*.md")
    logger.info("=" * 50)
    logger.info("⚠️ 任务完成！请审核后手动发布到X平台")
    logger.info("=" * 50)


if __name__ == "__main__":
    main()