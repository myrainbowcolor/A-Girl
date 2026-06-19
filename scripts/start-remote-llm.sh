#!/usr/bin/env bash
# 默认启动 A-Girl + 真实 LLM（llama-cpp / 本机 GGUF）
# mock 仅用于 pytest/CI，不用于实际聊天
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"

pip install -q -r "$ROOT/backend/requirements.txt" -r "$ROOT/backend/requirements-llm.txt" huggingface-hub

# 优先 Ollama llama3 blob；不存在则下载 Qwen2.5-0.5B（中文友好）
_DEFAULT_GGUF="$HOME/.ollama/models/blobs/sha256-6a0746a1ec1aef3e7ec53868f220ff6e389f6f8ef87a01d77c96807de94ca2aa"
if [ -z "${LLAMA_GGUF_PATH:-}" ]; then
  if [ -f "$_DEFAULT_GGUF" ]; then
    export LLAMA_GGUF_PATH="$_DEFAULT_GGUF"
    LLM_MODEL_NAME="llama3"
  else
    echo ">> llama3 GGUF 未找到，下载 Qwen2.5-0.5B-Instruct（约 400MB）..."
    export LLAMA_GGUF_PATH="$(python3 - <<'PY'
from huggingface_hub import hf_hub_download
print(hf_hub_download(
    repo_id="Qwen/Qwen2.5-0.5B-Instruct-GGUF",
    filename="qwen2.5-0.5b-instruct-q4_k_m.gguf",
))
PY
)"
    LLM_MODEL_NAME="qwen2.5-0.5b-instruct"
  fi
else
  LLM_MODEL_NAME="${AGIRL_LLM_MODEL:-local-gguf}"
fi
export LLAMA_GGUF_PATH

SESSION_LLM="llama-cpp-server"
SESSION_APP="agirl-server"

tmux -f /exec-daemon/tmux.portal.conf kill-session -t "$SESSION_LLM" 2>/dev/null || true
tmux -f /exec-daemon/tmux.portal.conf new-session -d -s "$SESSION_LLM" -c "$ROOT" -- "${SHELL:-bash}" -l
tmux -f /exec-daemon/tmux.portal.conf send-keys -t "$SESSION_LLM:0.0" \
  "cd $ROOT && export LLAMA_GGUF_PATH='$LLAMA_GGUF_PATH' && python3 -m uvicorn examples.llama_cpp_server:app --host 127.0.0.1 --port 11435" C-m

cat > "$ROOT/backend/.env" <<EOF
AGIRL_LLM_PROVIDER=openai_compatible
AGIRL_LLM_BASE_URL=http://127.0.0.1:11435/v1
AGIRL_LLM_API_KEY=local
AGIRL_LLM_MODEL=${LLM_MODEL_NAME}
AGIRL_LLM_TIMEOUT_SECONDS=180
AGIRL_SENTIMENT_MODE=lexicon
AGIRL_USER_INSIGHT_USE_LLM=false
AGIRL_USER_INSIGHT_HISTORY_LIMIT=40
AGIRL_USER_INSIGHT_LLM_EVERY_N=2
AGIRL_RELATIONSHIP_SUMMARY_EVERY_N=6
AGIRL_CHAT_DEFER_HEAVY_POST=true
AGIRL_RECENT_MESSAGES_WINDOW=6
AGIRL_LLM_MOCK_FALLBACK=true
AGIRL_TTS_PROVIDER=edge
AGIRL_EDGE_TTS_VOICE=zh-CN-XiaoxiaoNeural
AGIRL_STT_PROVIDER=mock
EOF

echo ">> 等待 LLM 加载..."
for i in $(seq 1 30); do
  if curl -sf "http://127.0.0.1:11435/health" | grep -q '"exists":true'; then
    break
  fi
  sleep 2
done
curl -sf "http://127.0.0.1:11435/health" >/dev/null

pkill -f "uvicorn app.main:app.*8011" 2>/dev/null || true
tmux -f /exec-daemon/tmux.portal.conf kill-session -t "$SESSION_APP" 2>/dev/null || true
tmux -f /exec-daemon/tmux.portal.conf new-session -d -s "$SESSION_APP" -c "$ROOT/backend" -- "${SHELL:-bash}" -l
tmux -f /exec-daemon/tmux.portal.conf send-keys -t "$SESSION_APP:0.0" \
  "cd $ROOT/backend && python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8011" C-m

sleep 3
echo "=== LLM health ==="
curl -s "http://127.0.0.1:11435/health"
echo
echo "=== A-Girl health ==="
curl -s "http://127.0.0.1:8011/health"
echo
echo ">> 打开 http://127.0.0.1:8011/  （当前为真实 LLM，非 mock）"
