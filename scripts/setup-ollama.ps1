# 一键配置 A-Girl 使用本机 Ollama（Llama 3 等）
# 用法（PowerShell）：
#   cd E:\new_git_work\A-Girl
#   powershell -ExecutionPolicy Bypass -File scripts\setup-ollama.ps1

$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
$Backend = Join-Path $Root "backend"
$EnvFile = Join-Path $Backend ".env"

Write-Host "`n==> 1/4 检查 Ollama" -ForegroundColor Cyan
if (-not (Get-Command ollama -ErrorAction SilentlyContinue)) {
    Write-Host "未找到 ollama 命令。请先安装: https://ollama.com" -ForegroundColor Red
    exit 1
}

try {
    $null = Invoke-RestMethod -Uri "http://127.0.0.1:11434/api/tags" -TimeoutSec 3
} catch {
    Write-Host "Ollama 未运行。请启动 Ollama 应用或执行: ollama serve" -ForegroundColor Red
    exit 1
}

Write-Host "`n==> 2/4 检测已安装的 Llama 模型" -ForegroundColor Cyan
$list = ollama list 2>&1 | Out-String
Write-Host $list

$model = $null
foreach ($line in ($list -split "`n")) {
    if ($line -match "^(llama3[^\s]*)\s") { $model = $Matches[1]; break }
    if ($line -match "^(llama3\.2[^\s]*)\s") { $model = $Matches[1]; break }
}
if (-not $model) {
    foreach ($line in ($list -split "`n")) {
        if ($line -match "^([a-zA-Z0-9._:-]+)\s") {
            $candidate = $Matches[1]
            if ($candidate -ne "NAME") { $model = $candidate; break }
        }
    }
}
if (-not $model) {
    Write-Host "未找到本地模型。请先执行: ollama pull llama3" -ForegroundColor Red
    exit 1
}
Write-Host "将使用模型: $model" -ForegroundColor Green

Write-Host "`n==> 3/4 写入 backend\.env" -ForegroundColor Cyan
$content = @"
AGIRL_LLM_PROVIDER=openai_compatible
AGIRL_LLM_BASE_URL=http://127.0.0.1:11434/v1
AGIRL_LLM_API_KEY=ollama
AGIRL_LLM_MODEL=$model
AGIRL_TTS_PROVIDER=mock
AGIRL_STT_PROVIDER=mock
"@
Set-Content -Path $EnvFile -Value $content -Encoding UTF8
Write-Host "已写入: $EnvFile"

Write-Host "`n==> 4/4 探测 Ollama Chat API" -ForegroundColor Cyan
$body = @{
    model = $model
    messages = @(@{ role = "user"; content = "只说一个字：好" })
    stream = $false
} | ConvertTo-Json -Depth 5
try {
    $resp = Invoke-RestMethod -Uri "http://127.0.0.1:11434/v1/chat/completions" `
        -Method Post -ContentType "application/json" -Body $body -TimeoutSec 120
    $reply = $resp.choices[0].message.content
    Write-Host "Ollama 回复测试: $reply" -ForegroundColor Green
} catch {
    Write-Host "Ollama API 调用失败: $_" -ForegroundColor Red
    exit 1
}

Write-Host @"

完成! 接下来在本机启动 A-Girl:

  cd $Backend
  pip install -r requirements.txt
  python -m uvicorn app.main:app --host 127.0.0.1 --port 8011

验证:
  curl http://127.0.0.1:8011/health
  (应看到 llm 为 openai_compatible:$model)

浏览器: http://127.0.0.1:8011/

"@ -ForegroundColor Cyan
