@echo off
chcp 65001 >nul
title 薪火仁义 - 公网演示（跨网络）
cd /d "%~dp0"
powershell -NoProfile -ExecutionPolicy Bypass -File "tools\start-public.ps1"
pause
