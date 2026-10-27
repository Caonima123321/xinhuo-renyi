@echo off
chcp 65001 >nul
title 薪火仁义 - 联机演示（同一 Wi-Fi）
cd /d "%~dp0"

set "PY="
python -c "import sys;print(1)" >nul 2>nul && set "PY=python"
if not defined PY py -3 -c "import sys;print(1)" >nul 2>nul && set "PY=py -3"
if not defined PY (
  for /f "delims=" %%P in ('dir /b /s "%USERPROFILE%\.dsh\dsh-runtimes\*\dependencies\python\python.exe" 2^>nul') do set "PY=%%P"
)
if not defined PY (
  echo.
  echo   没找到 Python 3。
  echo   装一个再双击本文件： https://www.python.org/downloads/
  echo.
  pause
  exit /b 1
)

echo.
echo   薪火仁义 · 联机演示
echo   ---------------------------------------------
echo   手机连同一个 Wi-Fi 或热点，扫下面的码
echo   关掉本窗口 = 服务停止
echo.
start "" "http://127.0.0.1:8787/join"
%PY% "tools\server.py" 8787
pause
