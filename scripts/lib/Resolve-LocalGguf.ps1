# Resolve/download local GGUF (Windows port of scripts/lib/resolve-local-gguf.sh)

function Resolve-LocalGguf {
    param(
        [ValidateSet("1.5b", "7b", "llama3")]
        [string]$Tier = $(if ($env:AGIRL_LOCAL_LLM_TIER) { $env:AGIRL_LOCAL_LLM_TIER } else { "7b" })
    )

    if ($env:LLAMA_GGUF_PATH -and (Test-Path -LiteralPath $env:LLAMA_GGUF_PATH)) {
        $script:LlmModelName = if ($env:AGIRL_LLM_MODEL) { $env:AGIRL_LLM_MODEL } else { "local-gguf" }
        return $env:LLAMA_GGUF_PATH
    }

    $ollamaLlama3 = Join-Path $env:USERPROFILE ".ollama\models\blobs\sha256-6a0746a1ec1aef3e7ec53868f220ff6e389f6f8ef87a01d77c96807de94ca2aa"
    if ($Tier -eq "llama3" -and (Test-Path -LiteralPath $ollamaLlama3)) {
        $env:LLAMA_GGUF_PATH = $ollamaLlama3
        $script:LlmModelName = "llama3"
        return $env:LLAMA_GGUF_PATH
    }

    switch ($Tier.ToLower()) {
        "1.5b" {
            $repo = "Qwen/Qwen2.5-1.5B-Instruct-GGUF"
            $file = "qwen2.5-1.5b-instruct-q4_k_m.gguf"
            $script:LlmModelName = "qwen2.5-1.5b-instruct"
            $sizeHint = "~1GB"
        }
        default {
            $repo = "bartowski/Qwen2.5-7B-Instruct-GGUF"
            $file = "Qwen2.5-7B-Instruct-Q4_K_M.gguf"
            $script:LlmModelName = "qwen2.5-7b-instruct"
            $sizeHint = "~4.7GB"
            $Tier = "7b"
        }
    }

    Write-Host ("Downloading Qwen2.5-" + $Tier + " (" + $sizeHint + "), first run may take a while...") -ForegroundColor Cyan
    $py = @"
import os
endpoint = os.environ.get('HF_ENDPOINT', '')
if endpoint:
    print('HF endpoint:', endpoint)
from huggingface_hub import hf_hub_download
path = hf_hub_download(repo_id='$repo', filename='$file')
print(path)
"@
    $path = $null
    foreach ($endpoint in @($env:HF_ENDPOINT, "https://hf-mirror.com", "")) {
        if ($endpoint) { $env:HF_ENDPOINT = $endpoint } else { Remove-Item Env:HF_ENDPOINT -ErrorAction SilentlyContinue }
        try {
            $lines = & python -c $py 2>&1
            $candidate = ($lines | Select-Object -Last 1).ToString().Trim()
            if ($candidate -and (Test-Path -LiteralPath $candidate)) {
                $path = $candidate
                break
            }
        } catch {
            Write-Host ("Download attempt failed" + $(if ($endpoint) { " via $endpoint" } else { "" })) -ForegroundColor Yellow
        }
    }
    if (-not $path) {
        throw @"
GGUF download failed (network timeout?).
Options:
  1) Set mirror: `$env:HF_ENDPOINT='https://hf-mirror.com' then re-run
  2) Manual download from HuggingFace, then: `$env:LLAMA_GGUF_PATH='C:\path\to\model.gguf'
  3) Preview without LLM: use mock in backend\.env (scene_first still works for many replies)
"@
    }
    $env:LLAMA_GGUF_PATH = $path
    return $path
}
