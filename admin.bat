@echo off
title Art of Life CMS Server
echo ===================================================
echo   Art of Life - 로컬 관리자 CMS 서버 구동 중...
echo ===================================================
echo.
echo 브라우저 창이 자동으로 열리지 않으면 아래 주소로 접속하세요:
echo http://localhost:8000
echo.
echo 서버를 종료하려면 이 터미널 창을 닫거나 Ctrl + C를 누르세요.
echo ---------------------------------------------------
echo.
python admin.py
pause
