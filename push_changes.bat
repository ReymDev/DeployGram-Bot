@echo off
cd /d "d:\1. Super Projects\DeployGram"
git add agent/main.py ИНСТРУКЦИЯ_ЗАПУСКА.md БЫСТРЫЙ_СТАРТ.txt "✅_ГОТОВО.txt"
git commit -m "fix: auto chown project directories to 1000:1000 for container write access"
git push
pause
