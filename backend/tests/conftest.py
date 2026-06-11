import sys
import tempfile
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.config import Settings
from app.db import Database
from app.emotion import EmotionEngine
from app.eval.scenario import load_scenarios
from app.llm import MockLLMProvider
from app.memory import HashEmbeddingProvider, MemoryStore
from app.orchestrator import Orchestrator

SCENARIO_DIR = Path(__file__).resolve().parent / "fixtures" / "dialogue_scenarios"
REPORT_DIR = Path(__file__).resolve().parent / "reports"


@pytest.fixture
def orch():
    with tempfile.NamedTemporaryFile(suffix=".db") as f:
        s = Settings(db_path=f.name, reflection_every_n_memories=3)
        db = Database(f.name)
        mem = MemoryStore(db, HashEmbeddingProvider(dim=256), s)
        o = Orchestrator(db, mem, EmotionEngine(), MockLLMProvider(), s)
        yield o, db, mem
        db.close()


@pytest.fixture
def dialogue_scenarios():
    return load_scenarios(SCENARIO_DIR)


@pytest.fixture
def scenario_runner(orch):
    from app.eval.runner import DialogueScenarioRunner

    o, _, _ = orch
    return DialogueScenarioRunner(o)
