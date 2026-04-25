@echo off
cd /d F:\程序项目\公众号自动流
echo ============================================
echo 推送到GitHub
echo ============================================

git init
git add .
git commit -m "init" 2>nul || echo 代码已最新

git branch -M main

echo.
echo 请粘贴仓库URL后回车:
set /p url=

if "%url%"=="" (
    echo 错误：请输入仓库URL
    pause
    exit /b 1
)

git remote add origin %url%
git push -u origin main

echo.
echo ============================================
echo 完成！
echo.
echo 去 GitHub 设置 Secrets:
echo https://github.com/你的用户名/公众号自动流/settings/secrets/actions
echo.
echo 添加:
echo   ZHIPU_API_KEY = adb9179c9f5c44409662a1d6f0d9cc5f.UtyktlKq4o6tZCz0
echo   WECHAT_APP_ID = wxcd38d76117a7d7e1
echo   WECHAT_APP_SECRET = c74d56e949bbe17d48ce46f9df8dcb89
echo ============================================
pause