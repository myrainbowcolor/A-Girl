#!/usr/bin/env bash
# 清理 HuggingFace 缓存里已弃用 / 未使用的本地 Qwen GGUF 模型
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
# shellcheck source=lib/resolve-local-gguf.sh
source "$ROOT/scripts/lib/resolve-local-gguf.sh"

HF_HUB="${HF_HOME:-$HOME/.cache/huggingface}/hub"
DRY_RUN=0
REMOVE_OBSOLETE=1
REMOVE_UNUSED_TIERS=0

usage() {
  cat <<EOF
用法: $(basename "$0") [选项]

  默认：删除已弃用档位（0.5B、3B 等）

选项:
  --dry-run           只打印将删除的路径，不实际删除
  --obsolete-only     仅删已弃用 repo（默认）
  --unused-tiers      额外删除非当前 AGIRL_LOCAL_LLM_TIER 的 Qwen 档位
  --all-unused        同 --obsolete-only --unused-tiers
  -h, --help          显示帮助

环境变量:
  AGIRL_LOCAL_LLM_TIER   当前保留档位（默认 7b），配合 --unused-tiers
  LLAMA_GGUF_PATH        若指向某 GGUF，该文件所在 repo 不会被删

示例:
  bash scripts/clean-local-llm-models.sh
  AGIRL_LOCAL_LLM_TIER=7b bash scripts/clean-local-llm-models.sh --unused-tiers
EOF
}

while [ $# -gt 0 ]; do
  case "$1" in
    --dry-run) DRY_RUN=1 ;;
    --obsolete-only) REMOVE_UNUSED_TIERS=0 ;;
    --unused-tiers) REMOVE_UNUSED_TIERS=1 ;;
    --all-unused) REMOVE_OBSOLETE=1; REMOVE_UNUSED_TIERS=1 ;;
    -h|--help) usage; exit 0 ;;
    *) echo "未知参数: $1" >&2; usage >&2; exit 1 ;;
  esac
  shift
done

# 已弃用、不再出现在 resolve-local-gguf.sh 档位中的 repo
_OBSOLETE_REPOS=(
  "models--Qwen--Qwen2.5-0.5B-Instruct-GGUF"
  "models--Qwen--Qwen2.5-3B-Instruct-GGUF"
)

declare -A _TIER_REPO=(
  [1.5b]="models--Qwen--Qwen2.5-1.5B-Instruct-GGUF"
  [7b]="models--bartowski--Qwen2.5-7B-Instruct-GGUF"
)

_protected_repo=""
if [ -n "${LLAMA_GGUF_PATH:-}" ] && [ -f "${LLAMA_GGUF_PATH}" ]; then
  _protected_repo="$(python3 - <<PY
from pathlib import Path
p = Path("${LLAMA_GGUF_PATH}").resolve()
for parent in p.parents:
    name = parent.name
    if name.startswith("models--"):
        print(name)
        break
PY
)"
fi

_active_tier="${AGIRL_LOCAL_LLM_TIER:-7b}"
case "$_active_tier" in
  1.5b|1.5B) _active_tier="1.5b" ;;
  *) _active_tier="7b" ;;
esac

_to_remove=()

if [ "$REMOVE_OBSOLETE" -eq 1 ]; then
  for repo in "${_OBSOLETE_REPOS[@]}"; do
    _to_remove+=("$repo")
  done
fi

if [ "$REMOVE_UNUSED_TIERS" -eq 1 ]; then
  _keep="${_TIER_REPO[$_active_tier]}"
  for tier in 1.5b 7b; do
    repo="${_TIER_REPO[$tier]}"
    if [ "$repo" != "$_keep" ]; then
      _to_remove+=("$repo")
    fi
  done
fi

declare -A _seen=()
_unique=()
for repo in "${_to_remove[@]}"; do
  if [ -z "${_seen[$repo]+x}" ]; then
    _seen[$repo]=1
    _unique+=("$repo")
  fi
done

if [ ! -d "$HF_HUB" ]; then
  echo ">> HuggingFace 缓存目录不存在: $HF_HUB（无需清理）"
  exit 0
fi

removed=0
freed=0

for repo in "${_unique[@]}"; do
  if [ -n "$_protected_repo" ] && [ "$repo" = "$_protected_repo" ]; then
    echo ">> 跳过（当前 LLAMA_GGUF_PATH）: $repo"
    continue
  fi
  path="$HF_HUB/$repo"
  if [ ! -d "$path" ]; then
    continue
  fi
  size="$(du -sb "$path" 2>/dev/null | cut -f1 || echo 0)"
  if [ "$DRY_RUN" -eq 1 ]; then
    echo "[dry-run] 将删除: $path ($(numfmt --to=iec-i --suffix=B "$size" 2>/dev/null || echo "${size}B"))"
  else
    echo ">> 删除: $path ($(numfmt --to=iec-i --suffix=B "$size" 2>/dev/null || echo "${size}B"))"
    rm -rf "$path"
  fi
  removed=$((removed + 1))
  freed=$((freed + size))
done

if [ "$removed" -eq 0 ]; then
  echo ">> 未发现可清理的本地模型缓存（当前档位: ${_active_tier}）"
else
  echo ">> 完成：${removed} 个 repo，释放约 $(numfmt --to=iec-i --suffix=B "$freed" 2>/dev/null || echo "${freed}B")"
fi
