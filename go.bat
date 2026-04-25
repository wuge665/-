@echo off
cd /d F:\程序项目\公众号自动流
echo ============================================
echo 推送到GitHub
echo ============================================

git init
git add .
git commit -m "init" 2>nul

git branch -M main

set url=https://github.com/rwu665/公众号自动流.git

echo 仓库: %url%
echo.
echo 推送中...
git remote add origin %url% 2>nul
git push -u origin main

echo.
echo ============================================
echo 完成！已推送到GitHub
echo.
echo 下一步：去 GitHub 设置 Secrets
echo ============================================
pause