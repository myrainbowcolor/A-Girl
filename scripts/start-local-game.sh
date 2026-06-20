#!/usr/bin/env bash
# 游戏 NPC 推荐启动：scene_first + 本机 llama-cpp（无云 LLM）
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"

export AGIRL_DIALOGUE_STRATEGY=scene_first
export AGIRL_DEPLOYMENT_MODE="${AGIRL_DEPLOYMENT_MODE:-embedded}"
export AGIRL_GAME_WORLD_BRIEF="${AGIRL_GAME_WORLD_BRIEF:-你是游戏世界里的陪伴角色小语。只聊当前世界、冒险与玩家心情；不要提现实公司、公文写作、联网查资料。}"

pip install -q -r "$ROOT/backend/requirements.txt" -r "$ROOT/backend/requirements-llm.txt" huggingface-hub

_DEFAULT_GGUF="$HOME/.ollama/models/blobs/sha256-6a0746a1ec1aef3e7ec53868f220ff6e389f6f8ef87a01d77c96807de94ca2aa"
if [ -z "${LLAMA_GGUF_PATH:-}" ]; then
  if [ -f "$_DEFAULT_GGUF" ]; then
    export LLAMA_GGUF_PATH="$_DEFAULT_GGUF"
    LLM_MODEL_NAME="llama3"
  else
    echo ">> 下载 Qwen2.5-1.5B-Instruct（约 1GB，本地 scene_first 推荐）..."
    export LLAMA_GGUF_PATH="$(python3 - <<'PY'
from huggingface_hub import hf_hub_download
print(hf_hub_download(
    repo_id="Qwen/Qwen2.5-1.5B-Instruct-GGUF",
    filename="qwen2.5-1.5b-instruct-q4_k_m.gguf",
))
PY
)"
    LLM_MODEL_NAME="qwen2.5-1.5b-instruct"
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
AGIRL_DIALOGUE_STRATEGY=scene_first
AGIRL_LLM_MOCK_FALLBACK=true
AGIRL_DEPLOYMENT_MODE=${AGIRL_DEPLOYMENT_MODE}
AGIRL_GAME_WORLD_BRIEF=${AGIRL_GAME_WORLD_BRIEF}
AGIRL_SENTIMENT_MODE=lexicon
AGIRL_USER_INSIGHT_USE_LLM=false
AGIRL_CHAT_DEFER_HEAVY_POST=true
AGIRL_RECENT_MESSAGES_WINDOW=6
AGIRL_TTS_PROVIDER=edge
AGIRL_EDGE_TTS_VOICE=zh-CN-XiaoxiaoNeural
AGIRL_STT_PROVIDER=mock
EOF

echo ">> 等待本地 LLM 加载..."
for i in $(seq 1 45); do
  if curl -sf "http://127.0.0.1:11435/health" | grep -q '"exists":true'; then
    break
  fi
  sleep 2
done

pkill -f "uvicorn app.main:app.*8011" 2>/dev/null || true
tmux -f /exec-daemon/tmux.portal.conf kill-session -t "$SESSION_APP" 2>/dev/null || true
tmux -f /exec-daemon/tmux.portal.conf new-session -d -s "$SESSION_APP" -c "$ROOT/backend" -- "${SHELL:-bash}" -l
tmux -f /exec-daemon/tmux.portal.conf send-keys -t "$SESSION_APP:0.0" \
  "cd $ROOT/backend && python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8011" C-m

sleep 3
echo "=== 策略: scene_first（场景优先，无云 LLM）==="
curl -s "http://127.0.0.1:8011/health"
echo
echo ">> http://127.0.0.1:8011/  |  修改世界观: AGIRL_GAME_WORLD_BRIEF"
