@echo off
cd /d F:\程序项目\公众号自动流
echo 初始化...
git init
echo 添加文件...
git add .
echo 提交...
git commit -m "init"
git branch -M main
echo 推送...
git remote add origin https://github.com/rwu665/公众号自动流.git
git push -u origin main
echo 完成!
pause