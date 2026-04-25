@echo off
cd /d F:\程序项目\公众号自动流

echo 检查是否安装了Git...
where git >nul 2>&1
if errorlevel 1 (
    echo 需要先安装Git！
    echo 去 https://git-scm.com 下载安装
    pause
    exit /b 1
)

echo 初始化Git仓库...
git init

echo 添加所有文件...
git add .

echo 提交代码...
git commit -m "init: 公众号自动流系统"

echo 设置主分支...
git branch -M main

echo 请输入你的GitHub用户名然后回车:
set /p username=

echo 请输入你的仓库名(默认公众号自动流):
set /p reponame=

if "%reponame%"=="" set reponame=公众号自动流

echo 添加远程仓库...
git remote add origin https://github.com/%username%/%reponame%.git

echo 推送到GitHub...
git push -u origin main

echo.
echo 完成！现在需要：
echo 1. 去 GitHub 仓库 Settings 添加 Secrets
echo 2. 添加: ZHIPU_API_KEY, WECHAT_APP_ID, WECHAT_APP_SECRET
echo.
pause