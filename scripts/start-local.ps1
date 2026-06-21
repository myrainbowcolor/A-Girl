# Local launcher (same stack as Cloud Agent: llama-cpp + scene_first)
# Usage:
#   powershell -ExecutionPolicy Bypass -File scripts\start-local.ps1
#   powershell -ExecutionPolicy Bypass -File scripts\start-local.ps1 -Tier 1.5b -Background
#
# Optional if you already use Ollama: scripts\setup-ollama.ps1

param(
    [ValidateSet("1.5b", "7b")]
    [string]$Tier = "7b",
    [switch]$Background,
    [switch]$Game
)

$scriptPath = Join-Path $PSScriptRoot "start-remote-llm.ps1"
& $scriptPath -Tier $Tier -Background:$Background -Game:$Game
