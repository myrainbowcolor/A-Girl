#!/usr/bin/env bash
# 解析本机 GGUF 路径与模型名（供 start-*.sh 引用）
# 环境变量：
#   LLAMA_GGUF_PATH        已有时跳过下载
#   AGIRL_LOCAL_LLM_TIER    1.5b | 3b | 7b（start-local-game 默认）
resolve_local_gguf() {
  if [ -n "${LLAMA_GGUF_PATH:-}" ] && [ -f "${LLAMA_GGUF_PATH}" ]; then
    export LLAMA_GGUF_PATH
    LLM_MODEL_NAME="${AGIRL_LLM_MODEL:-local-gguf}"
    return 0
  fi

  local tier="${AGIRL_LOCAL_LLM_TIER:-3b}"
  local ollama_llama3="$HOME/.ollama/models/blobs/sha256-6a0746a1ec1aef3e7ec53868f220ff6e389f6f8ef87a01d77c96807de94ca2aa"
  if [ -f "$ollama_llama3" ] && [ "$tier" = "llama3" ]; then
    export LLAMA_GGUF_PATH="$ollama_llama3"
    LLM_MODEL_NAME="llama3"
    return 0
  fi

  case "$tier" in
    1.5b|1.5B)
      _repo="Qwen/Qwen2.5-1.5B-Instruct-GGUF"
      _file="qwen2.5-1.5b-instruct-q4_k_m.gguf"
      LLM_MODEL_NAME="qwen2.5-1.5b-instruct"
      _size="约 1GB"
      ;;
    7b|7B)
      _repo="bartowski/Qwen2.5-7B-Instruct-GGUF"
      _file="Qwen2.5-7B-Instruct-Q4_K_M.gguf"
      LLM_MODEL_NAME="qwen2.5-7b-instruct"
      _size="约 4.7GB"
      ;;
    3b|3B|*)
      _repo="Qwen/Qwen2.5-3B-Instruct-GGUF"
      _file="qwen2.5-3b-instruct-q4_k_m.gguf"
      LLM_MODEL_NAME="qwen2.5-3b-instruct"
      _size="约 2GB"
      tier="3b"
      ;;
  esac

  echo ">> 下载 Qwen2.5-${tier}-Instruct（${_size}，本地对话推荐）..."
  export LLAMA_GGUF_PATH="$(python3 - <<PY
from huggingface_hub import hf_hub_download
print(hf_hub_download(repo_id="${_repo}", filename="${_file}"))
PY
)"
}
