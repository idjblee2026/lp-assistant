@echo off
chcp 65001 > nul
cd /d D:\LP_Agent
git add .
git commit -m "Auto upload LP files"
git push origin main
echo.
echo ========================================
echo     작업이 성공적으로 끝났습니다!
echo     아무 키나 누르면 창이 닫힙니다.
echo ========================================
pause