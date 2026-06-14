#!/usr/bin/env bash
# 在 Cloud Agent 上启动远程 Llama3 LLM + A-Girl
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"

pip install -q -r "$ROOT/backend/requirements.txt" -r "$ROOT/backend/requirements-llm.txt"

# Llama3 GGUF（ollama pull llama3 后的 blob 路径）
export LLAMA_GGUF_PATH="${LLAMA_GGUF_PATH:-$HOME/.ollama/models/blobs/sha256-6a0746a1ec1aef3e7ec53868f220ff6e389f6f8ef87a01d77c96807de94ca2aa}"

SESSION_LLM="llama-cpp-server"
SESSION_APP="agirl-server"

tmux -f /exec-daemon/tmux.portal.conf has-session -t "=$SESSION_LLM" 2>/dev/null || \
  tmux -f /exec-daemon/tmux.portal.conf new-session -d -s "$SESSION_LLM" -c "$ROOT" -- "${SHELL:-bash}" -l
tmux -f /exec-daemon/tmux.portal.conf send-keys -t "$SESSION_LLM:0.0" \
  "cd $ROOT && python3 -m uvicorn examples.llama_cpp_server:app --host 127.0.0.1 --port 11435" C-m

cat > "$ROOT/backend/.env" <<EOF
AGIRL_LLM_PROVIDER=openai_compatible
AGIRL_LLM_BASE_URL=http://127.0.0.1:11435/v1
AGIRL_LLM_API_KEY=local
AGIRL_LLM_MODEL=llama3
AGIRL_TTS_PROVIDER=edge
AGIRL_EDGE_TTS_VOICE=zh-CN-XiaoxiaoNeural
AGIRL_STT_PROVIDER=mock
EOF

sleep 3
curl -sf "http://127.0.0.1:11435/health" >/dev/null

pkill -f "uvicorn app.main:app.*8011" 2>/dev/null || true
tmux -f /exec-daemon/tmux.portal.conf has-session -t "=$SESSION_APP" 2>/dev/null || \
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
