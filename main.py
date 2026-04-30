"""
科技前沿资讯自动发布系统
每日抓取资讯 → AI生成内容 → 公众号自动发布
"""
import os
import sys
import argparse
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv

# 加载 .env 文件
load_dotenv(Path(__file__).parent / ".env")

from loguru import logger

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent))

from src.fetcher import NewsFetcher
from src.filter import ContentFilter
from src.editor import AIEditor
from src.publisher import WeChatPublisher


def setup_logger():
    """配置日志"""
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    logger.add(
        f"logs/brief_{datetime.now().strftime('%Y%m%d')}.log",
        rotation="00:00",
        retention="7 days",
        level="INFO"
    )


def parse_args():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(description="科技简报自动生成系统")
    parser.add_argument("--test", action="store_true", help="测试模式")
    parser.add_argument("--run", action="store_true", help="正式运行")
    parser.add_argument("--sources", nargs="+", default=None, help="指定资讯源")
    parser.add_argument("--count", type=int, default=int(os.getenv("ARTICLES_COUNT", "20")), help="生成文章数量")
    parser.add_argument("--retry", type=int, metavar="N", help="重新生成第N篇文章")
    parser.add_argument("--feedback", type=str, help="修改意见（配合--retry使用）")
    parser.add_argument("--save", action="store_true", help="保存生成内容到本地")
    parser.add_argument("--publish-local", action="store_true", help="发布本地已保存的内容")
    return parser.parse_args()


def get_sources_from_env() -> list:
    """从环境变量获取资讯源列表"""
    sources_str = os.getenv("NEWS_SOURCES", "")
    if sources_str:
        return [s.strip() for s in sources_str.split(",") if s.strip()]
    return None


def main():
    setup_logger()
    args = parse_args()
    
    # 如果没有命令行指定 sources，从环境变量读取
    if args.sources is None:
        args.sources = get_sources_from_env()
    
    logger.info("=" * 50)
    logger.info("🚀 科技简报自动生成系统启动")
    logger.info(f"📅 运行时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info("=" * 50)
    
    try:
        # 1. 抓取资讯
        logger.info("📡 步骤1: 抓取科技资讯...")
        fetcher = NewsFetcher()
        articles = fetcher.fetch(sources=args.sources)
        logger.info(f"   抓取到 {len(articles)} 篇原始文章")
        
        if not articles:
            logger.warning("⚠️ 未获取到任何文章，请检查网络和资讯源配置")
            return
        
        # 2. 过滤去重
        logger.info("🔍 步骤2: 过滤与去重...")
        filter_module = ContentFilter()
        filtered = filter_module.process(articles)
        logger.info(f"   保留 {len(filtered)} 篇优质内容")
        
        # 3. AI编辑生成
        logger.info("✍️ 步骤3: AI生成人工风格内容...")
        editor = AIEditor()
        articles_to_post = min(args.count, len(filtered))
        posts = editor.generate(filtered[:articles_to_post])
        logger.info(f"   生成 {len(posts)} 篇待发布内容")
        
        # 4. 保存到本地（默认行为）
        if os.getenv("GITHUB_ACTIONS"):
            output_dir = Path("output")
        else:
            output_dir = Path.home() / "Desktop" / "公众号草稿"
        output_dir.mkdir(exist_ok=True)
        for i, post in enumerate(posts, 1):
            with open(output_dir / f"draft_{i}.md", "w", encoding="utf-8") as f:
                f.write(f"# {post['title']}\n\n")
                f.write(post['content'])
                f.write(f"\n\n标签: {post.get('tags', '')}")
                f.write(f"\n\n来源: {post.get('source', '')}")
                f.write(f"\n链接: {post.get('url', '')}")
        logger.info(f"📁 内容已保存到 {output_dir}/draft_*.md")
        
        if args.save:
            logger.info("📁 内容已保存（额外保存模式）")
            return
        
        if args.retry and args.feedback:
            # 重写指定文章
            logger.info(f"🔄 重新生成第 {args.retry} 篇文章...")
            if args.retry <= len(posts):
                post = posts[args.retry - 1]
                new_post = editor.rewrite(post, args.feedback)
                posts[args.retry - 1] = new_post
                logger.info(f"✅ 已重新生成: {new_post['title']}")
        
        if args.publish_local:
            # 发布本地已保存的内容
            output_dir = Path("output")
            local_posts = []
            for f in sorted(output_dir.glob("article_*.md")):
                with open(f, "r", encoding="utf-8") as file:
                    content = file.read()
                    local_posts.append({
                        "title": content.split("\n")[0].replace("# ", ""),
                        "content": "\n".join(content.split("\n")[2:]),
                        "tags": ""
                    })
            posts = local_posts
            logger.info(f"📁 加载了 {len(posts)} 篇本地内容")
        
        # 5. 发布到公众号 - 检查是否启用自动发布
        auto_publish = os.getenv("AUTO_PUBLISH", "false").lower() == "true"
        
        if auto_publish:
            logger.info("📤 步骤4: 发布到微信公众号...")
            publisher = WeChatPublisher()
            
            for i, post in enumerate(posts, 1):
                logger.info(f"   发布第 {i}/{len(posts)} 篇: {post['title']}")
                as_draft = os.getenv("POST_AS_DRAFT", "true").lower() == "true"
                result = publisher.publish(post, as_draft=as_draft)
                if result.get("success"):
                    logger.info(f"   ✅ 成功 {post['title']}")
                else:
                    logger.error(f"   ❌ 失败: {result.get('error', '未知错误')}")
            logger.info("=" * 50)
            logger.info("✨ 任务完成！请登录公众号后台审核草稿")
            logger.info("=" * 50)
        else:
            logger.info("⏭️ 步骤4: 已跳过发布，内容保存在本地待审核")
            logger.info("=" * 50)
            logger.info("✨ 任务完成！请审核后手动复制到公众号")
            logger.info("=" * 50)
        
        # 无论发布成功与否都保存到本地
        if os.getenv("GITHUB_ACTIONS"):
            output_dir = Path("output")
        else:
            output_dir = Path.home() / "Desktop" / "公众号草稿"
        output_dir.mkdir(exist_ok=True)
        for i, post in enumerate(posts, 1):
            with open(output_dir / f"draft_{i}.md", "w", encoding="utf-8") as f:
                f.write(f"# {post['title']}\n\n")
                f.write(post['content'])
                f.write(f"\n\n标签: {post.get('tags', '')}")
                if post.get('image_suggestion'):
                    f.write(f"\n配图建议: {post['image_suggestion']}")
                f.write(f"\n\n来源: {post.get('source_name', '')}")
                f.write(f"\n链接: {post.get('source_url', '')}")
        logger.info(f"📁 草稿已保存到 {output_dir}/ 目录")
        
        if args.test:
            # 测试模式保存到本地
            output_dir = Path("output")
            output_dir.mkdir(exist_ok=True)
            for i, post in enumerate(posts, 1):
                with open(output_dir / f"article_{i}.md", "w", encoding="utf-8") as f:
                    f.write(f"# {post['title']}\n\n")
                    f.write(post['content'])
                    f.write(f"\n\n标签: {post.get('tags', '')}")
            logger.info(f"📁 测试内容已保存到 output/ 目录")
        
    except Exception as e:
        logger.error(f"❌ 系统异常: {str(e)}")
        raise


if __name__ == "__main__":
    main()