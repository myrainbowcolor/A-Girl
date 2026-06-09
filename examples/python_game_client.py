"""A-Girl 游戏嵌入示例（Python 游戏脚本层）。

演示从游戏 Python 脚本层调用 A-Girl 后端 /api/chat、/api/tts、/api/stt，
并把返回的表情/动作线索映射到游戏内数字人（如伙伴系统 PartnerDojo）。

仅依赖标准库（urllib），便于直接嵌入游戏脚本环境运行。
游戏侧的渲染/音频接口用占位对象 `game` 表示，请替换为你引擎的实际 API。

直接运行可对着本地后端做一次冒烟演示：
    python examples/python_game_client.py
"""
from __future__ import annotations

import base64
import json
import urllib.request
from dataclasses import dataclass, field

BASE_URL = "http://127.0.0.1:8011"

# expression -> 游戏内 Live2D/3D 资源映射（按项目自定义）
EXPRESSION_MAP: dict[str, dict[str, str]] = {
    "微笑": {"exp": "exp_smile", "anim": "anim_nod"},
    "大笑": {"exp": "exp_laugh", "anim": "anim_cheer"},
    "难过": {"exp": "exp_sad", "anim": "anim_idle"},
    "担心": {"exp": "exp_worried", "anim": "anim_comfort"},
    "惊讶": {"exp": "exp_surprised", "anim": "anim_idle"},
    "平静": {"exp": "exp_neutral", "anim": "anim_idle"},
}


def _post_json(url: str, payload: dict) -> dict:
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        url, data=data, headers={"Content-Type": "application/json"}, method="POST"
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode("utf-8"))


@dataclass
class AGirlClient:
    """游戏脚本层使用的轻量客户端（单玩家 1:1）。"""

    player_id: str
    base_url: str = BASE_URL
    session_id: str = field(default="")

    def __post_init__(self) -> None:
        if not self.session_id:
            self.session_id = f"save-{self.player_id}"

    def chat(self, message: str) -> dict:
        return _post_json(
            f"{self.base_url}/api/chat",
            {"user_id": self.player_id, "message": message, "session_id": self.session_id},
        )

    def tts(self, text: str, voice: str | None = None) -> dict:
        return _post_json(f"{self.base_url}/api/tts", {"text": text, "voice": voice})

    def stt(self, audio_base64: str, fmt: str = "wav") -> str:
        return _post_json(
            f"{self.base_url}/api/stt", {"audio_base64": audio_base64, "format": fmt}
        )["text"]

    @staticmethod
    def map_avatar(data: dict) -> dict[str, str]:
        cue = data.get("avatar", {}) or {}
        return EXPRESSION_MAP.get(cue.get("expression"), EXPRESSION_MAP["平静"])


# ── 游戏侧驱动示例（game 为引擎占位接口，请替换为实际实现）──
def apply_to_avatar(game, client: AGirlClient, data: dict) -> None:
    cue = data.get("avatar", {}) or {}
    mapped = client.map_avatar(data)

    game.show_dialogue(data["reply"])
    game.avatar.set_expression(mapped["exp"], cue.get("intensity", 0.5))
    game.avatar.play_animation(mapped["anim"])
    game.partner.set_relation_stage(
        data["relationship"]["stage"], data["relationship"]["affinity"]
    )
    # 安全分支：触发安全话术时切到更克制的表现
    if data.get("is_crisis") or data.get("safety_category"):
        game.avatar.set_expression("exp_worried", 0.9)


def speak(game, client: AGirlClient, text: str) -> None:
    resp = client.tts(text)
    audio = base64.b64decode(resp["audio_base64"])  # wav 字节
    game.audio.play_wav(audio)
    game.avatar.lip_sync_for_ms(resp["duration_ms"])  # 用时长做简单口型开合


def _demo() -> None:
    """对着本地后端做一次冒烟演示（无需游戏引擎）。"""
    client = AGirlClient(player_id="player-001")
    for msg in ["你好呀，我养了一只叫橘子的猫", "你还记得我的猫叫什么吗"]:
        data = client.chat(msg)
        mapped = client.map_avatar(data)
        print(f"你: {msg}")
        print(f"NPC: {data['reply']}")
        print(f"  表情={data['avatar']['expression']} -> 游戏资源={mapped}")
        print(f"  关系阶段={data['relationship']['stage']} 亲密度={data['relationship']['affinity']}")
        print(f"  回忆={data['retrieved_memories']}\n")
    audio = client.tts("你好呀")
    print(f"TTS: format={audio['format']} duration_ms={audio['duration_ms']}")


if __name__ == "__main__":
    _demo()
