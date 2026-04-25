@echo off
cd /d F:\程序项目\公众号自动流

echo ========================================
echo   公众号自动流 - 推送到GitHub
echo ========================================
echo.

echo 初始化...
git init 2>nul
echo 添加文件...
git add .
echo 提交...
git commit -m "init" 2>nul || echo 已最新

git branch -M main

echo.
echo 请在浏览器登录GitHub
echo 然后创建仓库: https://github.com/new
echo 仓库名设为: gzh-auto-flow
echo 不要勾选任何选项，直接创建
echo.
pause

echo.
echo 创建仓库后，在此输入仓库URL:
echo 例如: https://github.com/你的用户名/gzh-auto-flow.git
set /p giturl=

if "%giturl%"=="" (
    echo 错误：需要输入仓库URL
    pause
    exit /b 1
)

echo 添加远程...
git remote add origin %giturl%

echo 推送...
git push -u origin main

echo.
echo ========================================
echo 完成！
echo.
echo 下一步：去 GitHub 仓库设置 Secrets
echo 1. 打开: https://github.com/你的用户名/gzh-auto-flow/settings/secrets/actions
echo 2. 添加以下 Secrets:
echo    - ZHIPU_API_KEY   = adb9179c9f5c44409662a1d6f0d9cc5f.UtyktlKq4o6tZCz0
echo    - WECHAT_APP_ID   = wxcd38d76117a7d7e1
echo    - WECHAT_APP_SECRET = c74d56e949bbe17d48ce46f9df8dcb89
echo.
echo 完成后每天会自动生成内容！
echo ========================================
pause