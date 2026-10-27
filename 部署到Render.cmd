@echo off
chcp 65001 >nul
title 薪火仁义 - 部署到 Render
cd /d "%~dp0"

set "PY="
python -c "import sys;print(1)" >nul 2>nul && set "PY=python"
if not defined PY py -3 -c "import sys;print(1)" >nul 2>nul && set "PY=py -3"
if not defined PY (
  for /f "delims=" %%P in ('dir /b /s "%USERPROFILE%\.dsh\dsh-runtimes\*\dependencies\python\python.exe" 2^>nul') do set "PY=%%P"
)
if not defined PY (
  echo   没找到 Python 3。装一个再跑： https://www.python.org/downloads/
  pause
  exit /b 1
)

echo.
echo   ================================================
echo    第 2 步：部署到 Render
echo   ================================================
echo.
echo   需要 Render API Key：
echo   https://dashboard.render.com/u/settings/api-keys  -^> Create API Key
echo.
set /p REPO="  粘贴 GitHub 仓库地址（https://github.com/xxx/yyy）: "
echo.
%PY% "tools\deploy_render.py" "%REPO%"
echo.
pause
