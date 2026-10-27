@echo off
chcp 65001 >nul
title 薪火仁义 - 部署到 GitHub
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
echo    第 1 步：推送到 GitHub
echo   ================================================
echo.
echo   需要一个 token（只勾选该仓库 Contents 读写即可）：
echo   网页打开  https://github.com/settings/tokens?type=beta
echo   Generate new token -^> Repository access: All 或选一个仓库
echo   Permissions -^> Repository permissions -^> Contents: Read and write
echo.
echo   提示：用「只勾一个仓库、7 天过期」的 token 最安全，用完删掉。
echo.
%PY% "tools\deploy_github.py"
echo.
pause
