#!/usr/bin/env bash
# 默认启动 A-Girl + 本机 llama-cpp（无云 LLM）
# 默认模型 Qwen2.5-3B；更小/更大：AGIRL_LOCAL_LLM_TIER=1.5b|3b|7b
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
# shellcheck source=lib/resolve-local-gguf.sh
source "$ROOT/scripts/lib/resolve-local-gguf.sh"

pip install -q -r "$ROOT/backend/requirements.txt" -r "$ROOT/backend/requirements-llm.txt" huggingface-hub

resolve_local_gguf
export LLAMA_GGUF_PATH
bash "$ROOT/scripts/clean-local-llm-models.sh" --obsolete-only 2>/dev/null || true

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
AGIRL_DIALOGUE_STRATEGY=scene_first
AGIRL_SCENE_FALLBACK=true
AGIRL_SENTIMENT_MODE=lexicon
AGIRL_USER_INSIGHT_USE_LLM=false
AGIRL_USER_INSIGHT_HISTORY_LIMIT=40
AGIRL_USER_INSIGHT_LLM_EVERY_N=2
AGIRL_RELATIONSHIP_SUMMARY_EVERY_N=6
AGIRL_CHAT_DEFER_HEAVY_POST=true
AGIRL_RECENT_MESSAGES_WINDOW=6
AGIRL_TTS_PROVIDER=edge
AGIRL_EDGE_TTS_VOICE=zh-CN-XiaoxiaoNeural
AGIRL_STT_PROVIDER=mock
EOF

echo ">> 等待 LLM 加载（${LLM_MODEL_NAME}）..."
for i in $(seq 1 60); do
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
echo ">> 模型: ${LLM_MODEL_NAME} | 策略: scene_first | http://127.0.0.1:8011/"
