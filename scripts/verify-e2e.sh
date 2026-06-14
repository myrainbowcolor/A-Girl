#!/usr/bin/env bash
# 端到端冒烟：health → consent → chat stream → edge TTS
set -euo pipefail
BASE="${1:-http://127.0.0.1:8011}"
USER_ID="e2e-$(date +%s)"

echo "==> health"
curl -sf "$BASE/health" | python3 -m json.tool

echo "==> consent"
curl -sf -X POST "$BASE/api/consent" -H 'Content-Type: application/json' \
  -d "{\"user_id\":\"$USER_ID\",\"age\":18}"

echo ""
echo "==> chat stream (may take ~30s)"
OUT=$(curl -sN --max-time 120 -X POST "$BASE/api/chat/stream" -H 'Content-Type: application/json' \
  -d "{\"user_id\":\"$USER_ID\",\"message\":\"你好呀\"}")
echo "$OUT" | head -8
echo "$OUT" | grep -q '"type": "token"' || { echo "FAIL: no tokens"; exit 1; }
echo "$OUT" | grep -q '"type": "done"' || { echo "FAIL: no done"; exit 1; }

echo "==> edge TTS"
curl -sf -X POST "$BASE/api/tts" -H 'Content-Type: application/json' \
  -d '{"text":"你好，我是小语"}' | python3 -c "
import sys,json
d=json.load(sys.stdin)
assert d.get('provider','').startswith('edge'), d
assert d.get('format')=='mp3', d
assert len(d.get('audio_base64',''))>100, 'empty audio'
print('TTS OK:', d['provider'], d['duration_ms'], 'ms')
"

echo "==> ALL PASSED"
