# 修复 Cursor 端口转发：spawn code-tunnel.exe ENOENT
# 用法（管理员 PowerShell）：
#   Set-ExecutionPolicy -Scope Process Bypass -Force
#   & "E:\path\to\a-girl\scripts\fix-cursor-port-forward.ps1"
#
# 或直接复制本脚本全文到 PowerShell 运行。

$ErrorActionPreference = "Stop"

function Write-Step($msg) { Write-Host "`n==> $msg" -ForegroundColor Cyan }

function Find-CursorRoot {
    $candidates = @(
        "C:\Program Files\cursor",
        "$env:LOCALAPPDATA\Programs\cursor",
        "$env:LOCALAPPDATA\Programs\Cursor"
    )
    foreach ($p in $candidates) {
        if (Test-Path $p) { return $p }
    }
    return $null
}

function Test-TunnelReady($root) {
    $dest = Join-Path $root "bin\code-tunnel.exe"
    return (Test-Path $dest)
}

function Repair-FromCursorTunnel($root) {
    $srcCandidates = @(
        (Join-Path $root "resources\app\bin\cursor-tunnel.exe"),
        (Join-Path $root "resources\app\bin\code-tunnel.exe"),
        (Join-Path $root "cursor-tunnel.exe")
    )
    $src = $srcCandidates | Where-Object { Test-Path $_ } | Select-Object -First 1
    if (-not $src) { return $false }

    $binDir = Join-Path $root "bin"
    $dest = Join-Path $binDir "code-tunnel.exe"
    if (-not (Test-Path $binDir)) {
        New-Item -ItemType Directory -Path $binDir -Force | Out-Null
    }
    Copy-Item -Path $src -Destination $dest -Force
    Write-Host "已复制: $src -> $dest" -ForegroundColor Green
    return (Test-Path $dest)
}

Write-Step "1/4 查找 Cursor 安装目录"
$root = Find-CursorRoot
if (-not $root) {
    Write-Host "未找到 Cursor 安装目录。请先安装: https://cursor.com/download" -ForegroundColor Red
    exit 1
}
Write-Host "找到: $root"

Write-Step "2/4 检查 code-tunnel.exe"
if (Test-TunnelReady $root) {
    Write-Host "code-tunnel.exe 已存在，无需修复。" -ForegroundColor Green
    exit 0
}

Write-Host "code-tunnel.exe 缺失，尝试从 cursor-tunnel.exe 修复..." -ForegroundColor Yellow
if (Repair-FromCursorTunnel $root) {
    Write-Step "修复成功"
    exit 0
}

Write-Step "3/4 本地修复失败，尝试 winget 升级 Cursor"
if (Get-Command winget -ErrorAction SilentlyContinue) {
    try {
        winget upgrade -e --id Anysphere.Cursor --accept-package-agreements --accept-source-agreements
    } catch {
        Write-Host "winget upgrade 失败，尝试 install..." -ForegroundColor Yellow
        winget install -e --id Anysphere.Cursor --accept-package-agreements --accept-source-agreements
    }
    Start-Sleep -Seconds 3
    $root = Find-CursorRoot
    if ($root) { Repair-FromCursorTunnel $root | Out-Null }
}

Write-Step "4/4 验证并添加 Defender 排除项（可选）"
if ($root -and (Test-TunnelReady $root)) {
    try {
        Add-MpPreference -ExclusionPath $root -ErrorAction SilentlyContinue
    } catch { }
    Write-Host "`n成功! code-tunnel.exe 已就绪:" -ForegroundColor Green
    Write-Host (Join-Path $root "bin\code-tunnel.exe")
    Write-Host "`n下一步: 重启 Cursor -> Ctrl+J -> Ports -> Forward 8011" -ForegroundColor Cyan
    exit 0
}

Write-Host "`n仍无法修复。请手动重装 Cursor 后重试:" -ForegroundColor Red
Write-Host "  https://cursor.com/download"
Write-Host "`n诊断命令:"
Write-Host "  Get-ChildItem `"$root`" -Recurse -Filter *tunnel*.exe -ErrorAction SilentlyContinue | Select FullName"
exit 1
