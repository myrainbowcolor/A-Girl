# Windows launcher matching Cloud Agent scripts/start-remote-llm.sh
# GGUF download -> llama-cpp :11435 -> A-Girl :8011 (no Ollama required)
#
# Usage:
#   powershell -ExecutionPolicy Bypass -File scripts\start-remote-llm.ps1
#   powershell -ExecutionPolicy Bypass -File scripts\start-remote-llm.ps1 -Tier 1.5b -Background
#   powershell -ExecutionPolicy Bypass -File scripts\start-local-game.ps1

param(
    [ValidateSet("1.5b", "7b")]
    [string]$Tier = $(if ($env:AGIRL_LOCAL_LLM_TIER) { $env:AGIRL_LOCAL_LLM_TIER } else { "7b" }),
    [switch]$Game,
    [switch]$Background,
    [int]$AppPort = 8011
)

$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
$Backend = Join-Path $Root "backend"
$Lib = Join-Path $Root "scripts\lib\Resolve-LocalGguf.ps1"

function Write-Step([string]$msg) { Write-Host ""; Write-Host "==> $msg" -ForegroundColor Cyan }

function Stop-PythonOnPort {
    param([int]$Port, [string]$Pattern = "")
    $pids = @()
    $lines = netstat -ano | Select-String (":$Port\s")
    foreach ($line in $lines) {
        if ($line -match "\sLISTENING\s+(\d+)\s*$") {
            $pids += [int]$Matches[1]
        }
    }
    foreach ($procId in ($pids | Select-Object -Unique)) {
        Write-Host ("Stopping PID " + $procId + " on port " + $Port) -ForegroundColor Yellow
        Stop-Process -Id $procId -Force -ErrorAction SilentlyContinue
    }
    if ($Pattern) {
        Get-CimInstance Win32_Process -Filter "Name = 'python.exe'" -ErrorAction SilentlyContinue |
            Where-Object { $_.CommandLine -and $_.CommandLine -match $Pattern -and $_.CommandLine -match ("--port\s+" + $Port) } |
            ForEach-Object {
                Write-Host ("Stopping PID " + $_.ProcessId) -ForegroundColor Yellow
                Stop-Process -Id $_.ProcessId -Force -ErrorAction SilentlyContinue
            }
    }
}

function Wait-HttpOk {
    param([string]$Url, [int]$MaxAttempts = 60, [string]$Match = "")
    for ($i = 1; $i -le $MaxAttempts; $i++) {
        try {
            $resp = Invoke-WebRequest -Uri $Url -UseBasicParsing -TimeoutSec 5
            if (-not $Match -or $resp.Content -match $Match) { return $true }
        } catch { }
        Start-Sleep -Seconds 2
    }
    return $false
}

function Start-BackgroundPython {
    param([string]$WorkingDir, [string[]]$PythonArgs, [string]$LogName)
    $logDir = Join-Path $Root ".local"
    if (-not (Test-Path $logDir)) { New-Item -ItemType Directory -Path $logDir -Force | Out-Null }
    $log = Join-Path $logDir ($LogName + ".log")
    $errLog = Join-Path $logDir ($LogName + ".err.log")
    return Start-Process -FilePath "python" -ArgumentList $PythonArgs `
        -WorkingDirectory $WorkingDir -PassThru -WindowStyle Hidden `
        -RedirectStandardOutput $log -RedirectStandardError $errLog
}

function Test-PortListening {
    param([int]$Port)
    return [bool](netstat -ano | Select-String (":$Port\s") | Select-String "LISTENING")
}

function Resolve-AppPort {
    param([int]$Preferred)
    if (-not (Test-PortListening -Port $Preferred)) { return $Preferred }
    foreach ($fallback in @(8020, 8030, 8040)) {
        if (-not (Test-PortListening -Port $fallback)) { return $fallback }
    }
    throw ("No free port near " + $Preferred)
}

Write-Step "1/5 Install Python dependencies"
Set-Location $Backend
python -m pip install -q --upgrade pip
python -m pip install -q -r requirements.txt huggingface-hub
python -m pip install -q llama-cpp-python `
    --extra-index-url https://abetlen.github.io/llama-cpp-python/whl/cpu `
    --only-binary=llama-cpp-python

Write-Step "2/5 Resolve GGUF model"
. $Lib
$ggufPath = Resolve-LocalGguf -Tier $Tier
Write-Host ("Model: " + $LlmModelName) -ForegroundColor Green
Write-Host ("Path:  " + $ggufPath) -ForegroundColor Gray

Write-Step "3/5 Start llama-cpp on 127.0.0.1:11435"
Stop-PythonOnPort -Port 11435 -Pattern "llama_cpp_server"
$llmProc = Start-BackgroundPython -WorkingDir $Root -LogName "llama-cpp" -PythonArgs @(
    "-m", "uvicorn", "examples.llama_cpp_server:app", "--host", "127.0.0.1", "--port", "11435"
)
Write-Host ("llama-cpp PID: " + $llmProc.Id + " | log: .local\llama-cpp.log")

if (-not (Wait-HttpOk -Url "http://127.0.0.1:11435/health" -Match '"exists"\s*:\s*true')) {
    throw "llama-cpp not ready. See .local\llama-cpp.log"
}

Write-Step "4/5 Write backend\.env"
$deploymentMode = "standalone"
$gameWorldBrief = ""
if ($Game) {
    $deploymentMode = if ($env:AGIRL_DEPLOYMENT_MODE) { $env:AGIRL_DEPLOYMENT_MODE } else { "embedded" }
    if ($env:AGIRL_GAME_WORLD_BRIEF) {
        $gameWorldBrief = $env:AGIRL_GAME_WORLD_BRIEF
    } else {
        $gameWorldBrief = "game-world-npc-brief"
    }
}

$envLines = @(
    "AGIRL_LLM_PROVIDER=openai_compatible"
    "AGIRL_LLM_BASE_URL=http://127.0.0.1:11435/v1"
    "AGIRL_LLM_API_KEY=local"
    ("AGIRL_LLM_MODEL=" + $LlmModelName)
    "AGIRL_LLM_TIMEOUT_SECONDS=240"
    "AGIRL_DIALOGUE_STRATEGY=scene_first"
    "AGIRL_SCENE_FALLBACK=true"
    "AGIRL_SENTIMENT_MODE=lexicon"
    "AGIRL_USER_INSIGHT_USE_LLM=false"
    "AGIRL_USER_INSIGHT_HISTORY_LIMIT=40"
    "AGIRL_USER_INSIGHT_LLM_EVERY_N=2"
    "AGIRL_RELATIONSHIP_SUMMARY_EVERY_N=6"
    "AGIRL_CHAT_DEFER_HEAVY_POST=true"
    "AGIRL_RECENT_MESSAGES_WINDOW=6"
    "AGIRL_TTS_PROVIDER=edge"
    "AGIRL_EDGE_TTS_VOICE=zh-CN-XiaoxiaoNeural"
    "AGIRL_STT_PROVIDER=mock"
    ("AGIRL_DEPLOYMENT_MODE=" + $deploymentMode)
)

if ($Game) {
    if ($gameWorldBrief -eq "game-world-npc-brief") {
        $envLines += 'AGIRL_GAME_WORLD_BRIEF=game NPC brief: in-world only, no real-world facts'
    } else {
        $envLines += ("AGIRL_GAME_WORLD_BRIEF=" + $gameWorldBrief)
    }
}

$envFile = Join-Path $Backend ".env"
$utf8NoBom = New-Object System.Text.UTF8Encoding $false
[System.IO.File]::WriteAllLines($envFile, $envLines, $utf8NoBom)
Write-Host ("Wrote " + $envFile) -ForegroundColor Green

$AppPort = Resolve-AppPort -Preferred $AppPort
if ($AppPort -ne 8011) {
    Write-Host ("Port 8011 busy (often Cursor port forward) -> using " + $AppPort) -ForegroundColor Yellow
}

Write-Step ("5/5 Start A-Girl on http://127.0.0.1:" + $AppPort)
Stop-PythonOnPort -Port $AppPort -Pattern "app\.main:app"

if ($Background) {
    $appProc = Start-BackgroundPython -WorkingDir $Backend -LogName "agirl" -PythonArgs @(
        "-m", "uvicorn", "app.main:app", "--host", "127.0.0.1", "--port", "$AppPort"
    )
    if (-not (Wait-HttpOk -Url ("http://127.0.0.1:" + $AppPort + "/health") -MaxAttempts 30)) {
        throw "A-Girl not ready. See .local\agirl.log"
    }
    Write-Host ""
    Write-Host "=== Running (background) ===" -ForegroundColor Green
    Write-Host ("LLM : http://127.0.0.1:11435/health  PID " + $llmProc.Id)
    Write-Host ("App : http://127.0.0.1:" + $AppPort + "/         PID " + $appProc.Id)
    Write-Host ("Tier: " + $Tier + " | strategy: scene_first | model: " + $LlmModelName)
} else {
    Write-Host ("Open http://127.0.0.1:" + $AppPort + "/  (Ctrl+C stops A-Girl only)") -ForegroundColor Green
    python -m uvicorn app.main:app --host 127.0.0.1 --port $AppPort
}
