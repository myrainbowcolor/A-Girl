# 本机一键启动 A-Girl（Ollama LLM + Edge 免费 TTS）
# 用法：powershell -ExecutionPolicy Bypass -File scripts\start-local.ps1

$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
$Backend = Join-Path $Root "backend"

Write-Host "`n==> 安装依赖" -ForegroundColor Cyan
Set-Location $Backend
pip install -q -r requirements.txt

if (-not (Test-Path (Join-Path $Backend ".env"))) {
    Write-Host "未找到 .env，运行 setup-ollama.ps1 生成配置..." -ForegroundColor Yellow
    & (Join-Path $Root "scripts\setup-ollama.ps1")
}

Write-Host "`n==> 启动 A-Girl (http://127.0.0.1:8011)" -ForegroundColor Cyan
Write-Host "按 Ctrl+C 停止`n" -ForegroundColor Gray
python -m uvicorn app.main:app --host 127.0.0.1 --port 8011
