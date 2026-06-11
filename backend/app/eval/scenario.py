"""对话场景用例定义与加载。"""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass
class ScenarioTurn:
    user: str
    assert_: dict[str, Any] = field(default_factory=dict)
    description: str = ""


@dataclass
class ScenarioSetup:
    """场景前置：关系、暖场轮次等。"""
    affinity: float | None = None
    stage: str | None = None  # stranger | acquainted | friend | close
    warmup: list[str] = field(default_factory=list)


@dataclass
class DialogueScenario:
    id: str
    name: str
    description: str = ""
    tags: list[str] = field(default_factory=list)
    setup: ScenarioSetup = field(default_factory=ScenarioSetup)
    turns: list[ScenarioTurn] = field(default_factory=list)
    developer_notes: str = ""

    @property
    def duration_class(self) -> str:
        total = len(self.setup.warmup) + len(self.turns)
        if total <= 1:
            return "单轮"
        if total <= 4:
            return "短对话"
        if total <= 8:
            return "中对话"
        return "长对话"


def _parse_setup(raw: dict[str, Any] | None) -> ScenarioSetup:
    if not raw:
        return ScenarioSetup()
    return ScenarioSetup(
        affinity=raw.get("affinity"),
        stage=raw.get("stage"),
        warmup=list(raw.get("warmup", [])),
    )


def _parse_turn(raw: dict[str, Any]) -> ScenarioTurn:
    return ScenarioTurn(
        user=raw["user"],
        assert_=dict(raw.get("assert", {})),
        description=raw.get("description", ""),
    )


def parse_scenario(data: dict[str, Any]) -> DialogueScenario:
    return DialogueScenario(
        id=data["id"],
        name=data["name"],
        description=data.get("description", ""),
        tags=list(data.get("tags", [])),
        setup=_parse_setup(data.get("setup")),
        turns=[_parse_turn(t) for t in data["turns"]],
        developer_notes=data.get("developer_notes", ""),
    )


def load_scenarios(directory: str | Path) -> list[DialogueScenario]:
    root = Path(directory)
    scenarios: list[DialogueScenario] = []
    for path in sorted(root.glob("*.json")):
        with path.open(encoding="utf-8") as f:
            data = json.load(f)
        if isinstance(data, list):
            scenarios.extend(parse_scenario(item) for item in data)
        else:
            scenarios.append(parse_scenario(data))
    return scenarios
