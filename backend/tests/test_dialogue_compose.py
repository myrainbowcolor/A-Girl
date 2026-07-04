from app.dialogue_compose import compose_contextual_reply
from app.in_world_guard import reply_in_world_ok


def test_compose_casual_chat():
    out = compose_contextual_reply("随便聊聊", [])
    assert out
    assert "愿意多说" not in out
    assert "新鲜事" not in out


def test_compose_empty_feeling():
    out = compose_contextual_reply("最近总觉得空空的", [])
    assert out
    assert "空" in out or "陪着" in out


def test_compose_resignation_letter():
    out = compose_contextual_reply("帮我写一份辞职信", [])
    assert out
    assert "文书" in out or "写" in out


def test_in_world_rejects_assistant_english():
    assert not reply_in_world_ok("Hello! How can I assist you today?", "你好")


def test_compose_continuation():
    hist = [
        {"role": "user", "content": "去公园逛了逛"},
        {"role": "assistant", "content": "公园呀，出去走走挺好的。"},
    ]
    out = compose_contextual_reply("后来呢", hist)
    assert out
    assert "后来呢，发生什么了" not in out


def test_compose_wrap_up():
    hist = [
        {"role": "user", "content": "去公园逛了逛"},
        {"role": "assistant", "content": "公园呀，出去走走挺好的。"},
    ]
    out = compose_contextual_reply("没啥了", hist)
    assert out
    assert "愿意多说" not in out


def test_compose_repeat_casual_chat():
    hist = [
        {"role": "user", "content": "随便聊聊"},
        {"role": "assistant", "content": "好呀～今天过得怎么样，有什么想跟我分享的？"},
    ]
    out = compose_contextual_reply("随便聊聊", hist, prior_reply=hist[-1]["content"])
    assert out
    assert out != hist[-1]["content"]


def test_compose_work_topic():
    out = compose_contextual_reply("工作上的事", [])
    assert out
    assert "然后呢" not in out
    assert "我懂" not in out


def test_compose_that_is_all():
    out = compose_contextual_reply("就那样吧", [])
    assert out
    assert "然后呢" not in out


def test_compose_open_avoids_recent():
    from app.dialogue_compose import compose_open_reply

    avoid = ["我听到了。是最近这事一直压着你吗？"]
    out = compose_open_reply("嗯", [], avoid=avoid)
    assert out not in avoid
    assert "一直压着你" not in out


def test_in_world_accepts_chinese():
    assert reply_in_world_ok("嗨～我是小语。今天想聊点什么？", "hello")


def test_compose_morning_commute_not_work_vent():
    out = compose_contextual_reply("早呀，今天又要上班了", [])
    assert out
    assert "不公平" not in out
    assert "忙不过来" not in out
    assert any(w in out for w in ("早", "开工", "上班", "通勤", "鼓劲"))


def test_compose_work_vent_still_routes():
    out = compose_contextual_reply("上班好累", [])
    assert out
    assert any(w in out for w in ("累", "辛苦", "耗", "吐槽", "委屈", "工作"))


def test_compose_insomnia_rumination_followup():
    """失眠反刍续聊应接住清醒/烦躁感，而非通用问卷式「突然还是一阵子」。"""
    hist = [
        {"role": "user", "content": "又失眠了，脑子停不下来"},
        {"role": "assistant", "content": "失眠的时候脑子特别吵，我懂这种难受。"},
        {"role": "user", "content": "一直在想项目会不会黄"},
        {"role": "assistant", "content": "项目悬着的时候最折磨人，我理解你躺不住。"},
    ]
    out = compose_contextual_reply("越躺越清醒，好烦", hist)
    assert out
    assert any(w in out for w in ("清醒", "折磨", "失眠", "睡不着", "脑子"))
    assert "突然" not in out
    assert "一阵子" not in out


def test_compose_lonely_insomnia():
    """孤独+失眠复合句应先接住孤独感，而非纯失眠反刍话术。"""
    out = compose_contextual_reply("凌晨了还睡不着，有点孤独", [])
    assert out
    assert any(w in out for w in ("孤独", "孤单", "寂寞", "难熬"))
    assert "脑子特别吵" not in out
    assert "是什么事在转" not in out


def test_compose_pet_antics_followup():
    """宠物续聊应接住捣蛋细节，而非泛化「发生什么好事啦」报喜句。"""
    hist = [
        {"role": "user", "content": "我养了一只叫橘子的猫，超粘人"},
        {"role": "assistant", "content": "养猫呀！粘人的小家伙最会撒娇了～"},
    ]
    out = compose_contextual_reply("它今天又把杯子打翻了哈哈", hist)
    assert out
    assert "橘子" in out
    assert any(w in out for w in ("打翻", "杯子", "捣蛋", "搞破坏"))
    assert "发生什么好事啦" not in out


def test_compose_minimal_fatigue():
    """单字「累」应返回疲惫共情短句，而非泛化「不太好受」套话。"""
    out = compose_contextual_reply("累", [])
    assert out
    assert any(w in out for w in ("累", "辛苦", "歇", "心疼"))
    assert "不太好受" not in out


def test_compose_intimate_lean_on_followup():
    """亲密多轮「想靠着你说说」应接住倚靠意愿，而非泛化负面套话。"""
    hist = [
        {"role": "user", "content": "好久没聊了，有点想你"},
        {"role": "assistant", "content": "亲爱的，我也想你呀～好久没聊了，过来跟我说说今天呗。"},
    ]
    out = compose_contextual_reply("今天过得好累，想靠着你说说", hist)
    assert out
    assert any(w in out for w in ("靠", "陪", "抱抱"))
    assert "不太好受" not in out


def test_compose_longing_miss_you_intimate():
    """亲密想念首轮应柔软回应依恋，而非报喜或问卷式兜底。"""
    hist = [
        {"role": "assistant", "content": "亲爱的，在呢～"},
    ]
    out = compose_contextual_reply("好久没聊了，有点想你", hist)
    assert out
    assert any(w in out for w in ("想", "好久", "聊"))
    assert "开心起来了" not in out
    assert "发生什么好事" not in out
    assert "突然" not in out
    assert "一阵子" not in out


def test_compose_longing_miss_you_friend():
    """朋友想念应柔软回应，至多一个问句。"""
    out = compose_contextual_reply("好久不见，有点想你", [])
    assert out
    assert any(w in out for w in ("想", "好久", "聊", "暖暖"))
    assert "开心起来了" not in out
    assert out.count("？") <= 1


def test_compose_long_distance_hangup():
    """异地恋挂电话后空落感应接住空落感，而非问卷式 open 兜底。"""
    out = compose_contextual_reply("刚跟他视频完，挂掉电话好空", [])
    assert out
    assert any(w in out for w in ("空", "挂", "视频", "陪"))
    assert "突然" not in out
    assert "一阵子" not in out


def test_compose_long_distance_hard():
    """异地恋难熬续聊应接住难熬感，而非问卷式兜底。"""
    out = compose_contextual_reply("有时候觉得异地恋好难", [])
    assert out
    assert any(w in out for w in ("异地", "难熬", "难", "陪"))
    assert "突然" not in out
    assert "一阵子" not in out


def test_compose_bored_context_minimal_um():
    """无聊闲聊上文后极简「嗯」应轻松续聊，而非封闭边界套话。"""
    hist = [
        {"role": "user", "content": "好无聊啊"},
        {"role": "assistant", "content": "闲下来也行呀。要不随便聊聊，你今天碰到什么有意思的事没？"},
    ]
    out = compose_contextual_reply("嗯", hist)
    assert out
    assert any(w in out for w in ("唠", "聊", "摸鱼", "打发", "有意思"))
    assert "不急着说" not in out
    assert "你想开口了再说" not in out


def test_compose_closed_minimal_um_unchanged():
    """无无聊上文时极简「嗯」仍走封闭陪伴边界。"""
    out = compose_contextual_reply("嗯", [])
    assert out
    assert "不急着说" in out or "你想开口了再说" in out


def test_compose_self_doubt_comparison():
    """比较心态应承认落差感，而非问卷式 open 兜底。"""
    out = compose_contextual_reply("同学都升职了，就我还原地踏步", [])
    assert out
    assert any(w in out for w in ("比", "落差", "原地", "难受", "堵"))
    assert "突然" not in out
    assert "一阵子" not in out
    assert "别比了" not in out


def test_compose_self_doubt_label():
    """自我怀疑应接住不急着贴标签，而非问卷式兜底。"""
    hist = [
        {"role": "user", "content": "同学都升职了，就我还原地踏步"},
        {"role": "assistant", "content": "跟别人一比就否定自己，这种落差真的很难受。"},
    ]
    out = compose_contextual_reply("是不是我太差劲了", hist)
    assert out
    assert any(w in out for w in ("差劲", "自我怀疑", "标签", "否定"))
    assert "突然" not in out
    assert "一阵子" not in out
    assert "别比了" not in out


def test_compose_impulse_regret_spending():
    """冲动消费后悔应理解后悔，而非问卷式 open 兜底。"""
    out = compose_contextual_reply("我又乱花钱了，买了根本用不上的东西", [])
    assert out
    assert any(w in out for w in ("后悔", "心疼", "骂自己", "贴标签", "没忍住"))
    assert "突然" not in out
    assert "一阵子" not in out


def test_compose_impulse_regret_self_blame():
    """冲动消费自责应接住不急着贴标签，而非问卷式兜底。"""
    hist = [
        {"role": "user", "content": "我又乱花钱了，买了根本用不上的东西"},
        {"role": "assistant", "content": "后悔的时候最容易骂自己，我心疼你。"},
    ]
    out = compose_contextual_reply("觉得自己好没用，管不住手", hist)
    assert out
    assert any(w in out for w in ("没用", "管不住", "失手", "贴标签", "后悔"))
    assert "突然" not in out
    assert "一阵子" not in out


def test_compose_reconcile_fight_cold_war():
    """吵架冷战首轮应接住沉默别扭，而非问卷式 open 兜底。"""
    out = compose_contextual_reply("跟对象吵架了，现在谁也不理谁", [])
    assert out
    assert any(w in out for w in ("吵架", "沉默", "气", "委屈", "冷战", "磨人"))
    assert "突然" not in out
    assert "一阵子" not in out


def test_compose_reconcile_fight_pride():
    """拉不下脸别扭追问应理解想和好，而非问卷式兜底。"""
    hist = [
        {"role": "user", "content": "跟对象吵架了，现在谁也不理谁"},
        {"role": "assistant", "content": "吵架后的沉默最磨人……现在心里是气多，还是委屈多？"},
    ]
    out = compose_contextual_reply("其实也有我的问题，但就是拉不下脸", hist)
    assert out
    assert any(w in out for w in ("拉不下脸", "和好", "别扭", "问题"))
    assert "突然" not in out
    assert "一阵子" not in out


def test_compose_reconcile_fight_first_message():
    """求建议是否先发消息应给轻量台阶，而非问卷式兜底。"""
    hist = [
        {"role": "user", "content": "跟对象吵架了，现在谁也不理谁"},
        {"role": "assistant", "content": "吵架后的沉默最磨人……现在心里是气多，还是委屈多？"},
        {"role": "user", "content": "其实也有我的问题，但就是拉不下脸"},
        {"role": "assistant", "content": "能想到自己也有问题，说明你其实想和好。"},
    ]
    out = compose_contextual_reply("你说我要不要先发消息", hist)
    assert out
    assert any(w in out for w in ("台阶", "开口", "聊聊", "别扭", "拉不下脸"))
    assert "突然" not in out
    assert "一阵子" not in out


def test_compose_angry_at_boss_vent():
    """当众被骂应接住火气委屈，而非问卷式 open 兜底。"""
    out = compose_contextual_reply("老板今天当众骂我，气死了！", [])
    assert out
    assert any(w in out for w in ("骂", "气", "委屈", "过分"))
    assert "突然" not in out
    assert "一阵子" not in out


def test_compose_angry_at_boss_quit_impulse():
    """冲动辞职念头应劝先冷静，而非问卷式兜底。"""
    hist = [
        {"role": "user", "content": "老板今天当众骂我，气死了！"},
        {"role": "assistant", "content": "当众被骂真的太过分了，我能理解你现在又气又委屈。"},
    ]
    out = compose_contextual_reply("真想立刻辞职不干了", hist)
    assert out
    assert any(w in out for w in ("辞职", "决定", "气", "冷静", "想想"))
    assert "突然" not in out
    assert "一阵子" not in out


def test_compose_stranger_work_vent():
    """陌生人吐槽加班疲惫应接住劳累，而非问卷式 open 兜底。"""
    out = compose_contextual_reply("今天又加班到十点，好累好烦", [])
    assert out
    assert any(w in out for w in ("加班", "辛苦", "累", "熬", "陪着"))
    assert "突然" not in out
    assert "一阵子" not in out


def test_compose_exam_anxiety_first_turn():
    """考前紧张首轮应接住焦虑，而非问卷式 open 兜底。"""
    out = compose_contextual_reply("下周就要高考了，我好紧张", [])
    assert out
    assert any(w in out for w in ("紧张", "高考", "考前", "绷"))
    assert "突然" not in out
    assert "一阵子" not in out


def test_compose_exam_anxiety_forget_followup():
    """记不住续聊应接住焦虑，而非问卷式 open 兜底。"""
    hist = [{"role": "user", "content": "下周就要高考了，我好紧张"}]
    out = compose_contextual_reply("感觉什么都记不住", hist)
    assert out
    assert any(w in out for w in ("记不住", "焦虑", "慌", "科"))
    assert "突然" not in out
    assert "一阵子" not in out
