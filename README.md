# 科技简报自动生成系统

> 全自动公众号运营系统 | 每日9点自动运行 | 零手动操作

## 快速开始

### 1. 安装依赖
```powershell
pip install -r requirements.txt
```

### 2. 配置微信公众号
复制 `.env.example` 为 `.env`，填入您的凭证：
- `WECHAT_APP_ID`
- `WECHAT_APP_SECRET`

### 3. 配置AI编辑（可选）
- Claude API: `ANTHROPIC_API_KEY`
- 或 OpenAI: `OPENAI_API_KEY`

### 4. 测试运行
```powershell
python main.py --test
```

### 5. 定时自动运行
#### 方式A: Windows任务计划程序
```powershell
schtasks /create /tn "TechBriefDaily" /tr "python F:\程序项目\公众号自动流\main.py --run" /sc daily /st 09:00
```

#### 方式B: GitHub Actions
1. Fork此仓库
2. 在Settings > Secrets中添加环境变量
3. 每天北京时间9点自动运行

## 项目结构

```
公众号自动流/
├── main.py              # 主入口
├── src/
│   ├── fetcher.py       # 资讯抓取
│   ├── filter.py        # 内容过滤
│   ├── editor.py        # AI编辑
│   └── publisher.py     # 公众号发布
├── config/
│   └── sources.json     # 资讯源配置
├── scripts/
│   └── daily_brief.bat  # 定时脚本
├── AGENTS.md            # 风格规范
└── .env                 # 环境变量
```

## 功能特点

- 多源RSS聚合（自动排除公众号源）
- 智能内容去重与评分
- AI生成人工风格内容
- Markdown转微信富文本
- 草稿箱预览模式

## 定时任务设置说明

### Windows 定时任务
每天9点自动运行已配置好脚本 `scripts\daily_brief.bat`

### GitHub Actions（推荐）
免费托管，每天自动运行，可查看执行日志