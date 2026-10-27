# 薪火仁义 · 公网演示启动器
# 作用：起本地服务 → 开 ssh 反向隧道拿到公网地址 → 自动打开扫码页
$ErrorActionPreference = "Continue"
$Root = Split-Path -Parent $PSScriptRoot
$Port = 8787

function Find-Python {
    foreach ($c in @("python", "py")) {
        try {
            $out = & $c -c "import sys;print(sys.version_info[0])" 2>$null
            if ("$out".Trim() -eq "3") { return $c }
        } catch {}
    }
    $hits = Get-ChildItem "$env:USERPROFILE\.dsh\dsh-runtimes" -Recurse -Filter python.exe -ErrorAction SilentlyContinue |
            Where-Object { $_.FullName -like "*dependencies\python\python.exe" } | Select-Object -First 1
    if ($hits) { return $hits.FullName }
    return $null
}

$py = Find-Python
if (-not $py) {
    Write-Host "没找到 Python 3。" -ForegroundColor Red
    Write-Host "装一个（https://www.python.org/downloads/，勾选 Add to PATH）再双击本文件。"
    Read-Host "按回车退出"
    exit 1
}

# 1) 起服务（端口占用就跳过，说明已经在跑）
$busy = $false
try {
    $r = Invoke-WebRequest "http://127.0.0.1:$Port/api/state" -TimeoutSec 2 -UseBasicParsing
    if ($r.StatusCode -eq 200) { $busy = $true }
} catch {}
if (-not $busy) {
    Start-Process -FilePath $py -ArgumentList "$Root\tools\server.py", "$Port" -WorkingDirectory $Root -WindowStyle Minimized
    Start-Sleep -Seconds 2
}

# 2) 开隧道
Write-Host ""
Write-Host "正在建立公网隧道（约 5 秒）…" -ForegroundColor Yellow
$log = Join-Path $env:TEMP "xinhuo-tunnel.log"
if (Test-Path $log) { Remove-Item $log -Force }
$ssh = "C:\Windows\System32\OpenSSH\ssh.exe"
if (-not (Test-Path $ssh)) { $ssh = "ssh" }
$proc = Start-Process -FilePath $ssh `
    -ArgumentList @("-T","-o","StrictHostKeyChecking=no","-o","ServerAliveInterval=30","-R","80:127.0.0.1:$Port","nokey@localhost.run") `
    -RedirectStandardOutput $log -RedirectStandardError "$log.err" -WindowStyle Hidden -PassThru

$url = $null
for ($i = 0; $i -lt 40; $i++) {
    Start-Sleep -Milliseconds 500
    if (Test-Path $log) {
        $txt = Get-Content $log -Raw -ErrorAction SilentlyContinue
        $m = [regex]::Match("$txt", "https://[a-z0-9\-]+\.lhr\.life")
        if ($m.Success) { $url = $m.Value; break }
    }
    if ($proc.HasExited) { break }
}

Write-Host ""
if ($url) {
    Write-Host "公网地址（任何网络都能打开，评委手机直接扫）：" -ForegroundColor Green
    Write-Host "  $url" -ForegroundColor Green
    Write-Host ""
    $join = "http://127.0.0.1:$Port/join?u=$url"
    if (-not $env:XH_NO_OPEN) { Start-Process $join }
    Write-Host "已打开扫码页：$join" -ForegroundColor Gray
} else {
    Write-Host "隧道没起来（可能被网络策略拦了）。" -ForegroundColor Red
    Write-Host "备选：用同一 Wi-Fi 直接访问 http://<本机IP>:$Port/ ，见「启动联机演示.cmd」。"
    if (-not $env:XH_NO_OPEN) { Start-Process "http://127.0.0.1:$Port/join" }
}

Write-Host ""
Write-Host "演示期间请保持本窗口不要关；关掉窗口 = 公网地址失效。" -ForegroundColor Yellow
Write-Host "结束后按 Ctrl+C 停止隧道。" -ForegroundColor Yellow
Write-Host ""
try {
    while (-not $proc.HasExited) { Start-Sleep -Seconds 2 }
} finally {
    if (-not $proc.HasExited) { $proc.Kill() }
}

