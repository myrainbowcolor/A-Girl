from app.reply_guard import (
    guard_closed_user_reply,
    needs_mock_fallback,
    polish_reply,
    reply_is_filler_heavy,
    reply_is_generic_llm,
    reply_is_generic_mock,
    reply_similarity,
    scene_fallback_reply,
    user_is_closed,
)


def test_user_is_closed():
    assert user_is_closed("不想说")
    assert user_is_closed("..")
    assert user_is_closed("嗯")
    assert not user_is_closed("你好")
    assert not user_is_closed("嗨")
    assert not user_is_closed("今天加班好累")
    assert not user_is_closed("随便聊聊")
    assert not user_is_closed("还好")
    assert not user_is_closed("不知道")
    assert not user_is_closed("累")


def test_polish_fixes_generic_scene():
    bad = "嗯，我在听呢——后来呢，发生什么了？"
    out = polish_reply("后来呢", bad, history=[{"role": "user", "content": "去公园逛了逛"}])
    assert "后来呢，发生什么了" not in out
    assert "愿意多说" not in out


def test_polish_repeat_greeting():
    prior = "你好呀，我是小语，很高兴认识你～"
    hist = [{"role": "assistant", "content": prior}]
    out = polish_reply("你好", prior, prior_reply=prior, history=hist)
    assert out != prior
    assert "愿意多说" not in out


def test_guard_replaces_pushy_on_closed():
    out = guard_closed_user_reply("不想说", "嗯……你愿意多说一点吗？我听着。")
    assert "愿意多说" not in out
    assert "我陪着" in out or "不说也行" in out


def test_meta_pushback_fallback():
    out = scene_fallback_reply("为啥一定要跟你聊天?")
    assert out
    assert "必须" in out or "强迫" in out or "不用" in out
    assert "小确幸" not in out


def test_identity_fallback():
    out = scene_fallback_reply("你是机器人吗")
    assert out
    assert "AI" in out or "小语" in out


def test_needs_mock_fallback_bad_llm():
    bad = "哈哈，很高兴你和我有相似之处，或许我们可以聊聊小确幸。"
    assert needs_mock_fallback(bad, "你是机器人吗")


def test_needs_mock_fallback_self_talk():
    bad = "嗯，还好，最近工作挺顺利的。你最近忙吗？"
    assert needs_mock_fallback(bad, "..")


def test_reply_is_generic_mock():
    assert reply_is_generic_mock("嗯……你愿意多说一点吗？我听着。")
    assert not reply_is_generic_mock("养猫呀！粘人的小家伙最会撒娇了～")


def test_polish_keeps_good_llm():
    good = "听起来你今天加班到挺晚的，辛苦啦。先缓口气，是哪件事最耗你？"
    out = polish_reply("今天加班好累", good)
    assert out == good


def test_polish_fixes_bad_llm():
    bad = "哈哈，很高兴你和我有相似之处，或许我们可以聊聊小确幸。"
    out = polish_reply("你是机器人吗", bad)
    assert "相似之处" not in out
    assert "小确幸" not in out


def test_reply_is_filler_heavy():
    assert reply_is_filler_heavy("嗯……嗯……我理解了。你想聊什么？")
    assert reply_is_filler_heavy("嗯嗯，有什么新鲜事吗？")
    assert not reply_is_filler_heavy("叫我小语就好，很高兴认识你。")


def test_needs_mock_fallback_filler():
    bad = "嗯嗯，有什么新鲜事吗？"
    assert needs_mock_fallback(bad, "能别嗯嗯的回答吗")


def test_polish_filler_complaint():
    bad = "嗯嗯，有什么新鲜事吗？"
    out = polish_reply("能别嗯嗯的回答吗", bad)
    assert not out.startswith("嗯")
    assert "抱歉" in out or "对不起" in out


def test_polish_avoids_exact_repeat():
    prior = "嗯，我陪着。不急着说~"
    out = polish_reply("..", prior, prior_reply=prior)
    assert reply_similarity(out, prior) < 0.88


def test_polish_strips_pushy_fallback():
    out = polish_reply("工作上的事", "嗯嗯，我懂。然后呢？")
    assert not out.startswith("，")
    assert "我懂。然后呢" not in out


def test_ensure_reply_diversity():
    from app.reply_guard import ensure_reply_diversity

    hist = [
        {"role": "user", "content": "有点烦"},
        {"role": "assistant", "content": "我听到了。是最近这事一直压着你吗？"},
    ]
    out = ensure_reply_diversity(
        "我听到了。是最近这事一直压着你吗？",
        "嗯",
        hist,
        prior_reply=hist[-1]["content"],
    )
    assert out != hist[-1]["content"]
    assert "一直压着你" not in out or out.count("一直压着你") == 0


def test_no_repeat_across_vague_turns():
    import tempfile
    import time
    from app.config import Settings
    from app.db import Database
    from app.domain import Relationship
    from app.emotion import EmotionEngine
    from app.llm import MockLLMProvider
    from app.memory import HashEmbeddingProvider, MemoryStore
    from app.orchestrator import Orchestrator
    from app.reply_guard import reply_similarity

    with tempfile.NamedTemporaryFile(suffix=".db") as f:
        db = Database(f.name)
        settings = Settings(reflection_every_n_memories=999, dialogue_strategy="scene_first")
        mem = MemoryStore(db, HashEmbeddingProvider(dim=256), settings)
        orch = Orchestrator(db, mem, EmotionEngine(), MockLLMProvider(), settings)
        uid, sid = "u", "s"
        rel = Relationship(affinity=28.0)
        rel.recompute_stage()
        db.save_relationship(uid, rel, time.time())
        replies = []
        for t in ["工作上的事", "嗯", "就那样", "有点烦", "嗯嗯", "不知道"]:
            r = orch.chat(uid, sid, t).reply
            replies.append(r)
            for prev in replies[:-1]:
                assert reply_similarity(r, prev) < 0.88, (t, r, prev)
            assert "一直压着你" not in r or all(
                "一直压着你" not in p for p in replies[:-1]
            )
