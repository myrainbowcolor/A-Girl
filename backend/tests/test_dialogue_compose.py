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


def test_compose_pet_share_first_turn():
    """首轮养猫分享应返回亲昵接话，而非 open 兜底。"""
    out = compose_contextual_reply(
        "我养了一只叫橘子的猫，超粘人", [], relationship_stage="friend"
    )
    assert out
    assert any(w in out for w in ("猫", "粘人", "撒娇", "毛孩子"))
    assert "随便丢几个词" not in out
    assert "突然" not in out


def test_compose_pet_share_skips_memory_recall():
    """记忆追问不应误入养宠分享分支。"""
    out = compose_contextual_reply("你还记得我的猫叫什么吗", [])
    assert out is None or "养猫呀" not in out


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


def test_compose_minimal_fatigue_hao_lei():
    """极简「好累」应返回疲惫共情短句，而非问卷式 open 兜底。"""
    out = compose_contextual_reply("好累", [])
    assert out
    assert any(w in out for w in ("累", "辛苦", "歇", "心疼"))
    assert "不太好受" not in out
    assert "突然" not in out
    assert not out.startswith("嗯")


def test_compose_minimal_morning_zao():
    """单字「早」应返回自然早安寒暄，而非 open 兜底。"""
    out = compose_contextual_reply("早", [])
    assert out
    assert "早" in out
    assert out.count("？") + out.count("?") <= 1
    assert not out.startswith("嗯")


def test_compose_intimate_lean_on_by_stage():
    """亲密「想靠着你说说」无历史时，relationship_stage 应驱动亲昵接话。"""
    out = compose_contextual_reply(
        "今天过得好累，想靠着你说说", [], relationship_stage="close"
    )
    assert out
    assert any(w in out for w in ("靠", "陪", "抱抱"))
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


def test_compose_longing_miss_you_intimate_by_stage():
    """亲密想念首轮无历史时，relationship_stage 应驱动亲昵接话。"""
    out = compose_contextual_reply(
        "好久没聊了，有点想你", [], relationship_stage="close"
    )
    assert out
    assert "想你" in out or "好久" in out
    assert "心里暖暖的" not in out or "我也想你" in out


def test_compose_longing_miss_you_friend_by_stage():
    """朋友想念应通过 relationship_stage 返回依恋接话。"""
    out = compose_contextual_reply(
        "好久不见，有点想你", [], relationship_stage="friend"
    )
    assert out
    assert any(w in out for w in ("想", "好久", "聊", "暖暖"))
    assert out.count("？") <= 1


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


def test_compose_bored_smalltalk_first_turn():
    """无聊闲聊首轮 compose 路径应轻松续聊，非 open 兜底。"""
    out = compose_contextual_reply("好无聊啊", [])
    assert out
    assert any(w in out for w in ("无聊", "唠", "聊", "闲", "有意思"))
    assert "突然" not in out
    assert "一阵子" not in out
    assert not out.startswith("嗯")


def test_compose_bored_smalltalk_friend_stage():
    """朋友关系无聊首轮应亲昵轻松续聊。"""
    out = compose_contextual_reply(
        "好无聊啊", [], relationship_stage="friend"
    )
    assert out
    assert any(w in out for w in ("唠", "聊", "无聊", "摸鱼", "剧"))
    assert out.count("？") <= 1
    assert not out.startswith("嗯")


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


def test_compose_breakup_sad_first_turn():
    """分手首轮应接住悲伤，而非问卷式 open 兜底。"""
    out = compose_contextual_reply("我们分手了", [])
    assert out
    assert any(w in out for w in ("分手", "分开", "陪着", "硬撑"))
    assert "突然" not in out
    assert "一阵子" not in out


def test_compose_breakup_sad_cry_followup():
    """分手语境忍不住哭应接住悲伤，而非问卷式 open 兜底。"""
    hist = [
        {"role": "user", "content": "我们分手了"},
        {"role": "assistant", "content": "分手真的很难扛，我陪你待着。"},
    ]
    out = compose_contextual_reply("我还是忍不住想哭", hist)
    assert out
    assert any(w in out for w in ("哭", "分手", "陪着", "忍着"))
    assert "突然" not in out
    assert "一阵子" not in out


def test_compose_breakup_sad_hope_followup():
    """怀疑自己能否好起来应接住悲伤，而非问卷式 open 兜底。"""
    hist = [
        {"role": "user", "content": "我们分手了"},
        {"role": "assistant", "content": "分手真的很难扛，我陪你待着。"},
        {"role": "user", "content": "我还是忍不住想哭"},
        {"role": "assistant", "content": "想哭就哭出来吧，我陪着你。"},
    ]
    out = compose_contextual_reply("你觉得我还能好起来吗", hist)
    assert out
    assert any(w in out for w in ("好起来", "慢慢来", "陪着", "理解"))
    assert "突然" not in out
    assert "一阵子" not in out


def test_compose_sick_care():
    """生病求关心应表达关心与陪伴，而非问卷式 open 兜底。"""
    out = compose_contextual_reply("我感冒了，头好痛", [])
    assert out
    assert any(w in out for w in ("感冒", "头痛", "生病", "心疼", "辛苦", "休息", "陪"))
    assert "突然" not in out
    assert "一阵子" not in out


def test_compose_festival_lonely_first_turn():
    """节日一人过节应看见孤独感，而非问卷式 open 兜底。"""
    out = compose_contextual_reply("过年一个人，有点落寞", [])
    assert out
    assert any(w in out for w in ("落寞", "一个人", "过节", "想家", "空落", "陪"))
    assert "突然" not in out
    assert "一阵子" not in out
    assert not out.lstrip().startswith("嗯")


def test_compose_festival_lonely_reunion_followup():
    """看到别人团圆更难受应接住对比下的扎心感。"""
    hist = [
        {"role": "user", "content": "过年一个人，有点落寞"},
        {"role": "assistant", "content": "一个人过节确实会空落落的，我陪你待着。"},
    ]
    out = compose_contextual_reply("看到别人团圆就更难受", hist)
    assert out
    assert any(w in out for w in ("团圆", "难受", "扎心", "敏感", "陪"))
    assert "突然" not in out
    assert "一阵子" not in out
    assert not out.lstrip().startswith("嗯")


def test_compose_nostalgic_childhood_first_turn():
    """怀旧童年首轮应柔软共鸣，而非问卷式 open 兜底。"""
    out = compose_contextual_reply("突然想到小时候外婆做的汤圆，好怀念", [])
    assert out
    assert any(w in out for w in ("怀念", "小时候", "外婆", "汤圆", "旧时光", "暖"))
    assert "一阵子" not in out
    assert not out.lstrip().startswith("嗯")


def test_compose_nostalgic_childhood_calm_followup():
    """怀旧续聊难静下来应顺着回忆共鸣。"""
    hist = [
        {"role": "user", "content": "突然想到小时候外婆做的汤圆，好怀念"},
        {"role": "assistant", "content": "突然想到那些旧时光，心里会又暖又酸吧。外婆的汤圆是什么馅的？"},
    ]
    out = compose_contextual_reply("那时候日子简单，现在好难静下来", hist)
    assert out
    assert any(w in out for w in ("静下来", "简单", "节奏", "慢下来"))
    assert "突然" not in out
    assert "一阵子" not in out
    assert not out.lstrip().startswith("嗯")


def test_compose_parent_anxiety_first_turn():
    """家长自责首轮应理解操心与自责，而非问卷式 open 兜底。"""
    out = compose_contextual_reply("孩子这次考得不好，我是不是太严厉了", [])
    assert out
    assert any(w in out for w in ("严厉", "操心", "在乎", "心疼", "自责"))
    assert "突然" not in out
    assert "一阵子" not in out
    assert "别担心" not in out
    assert not out.lstrip().startswith("嗯")


def test_compose_parent_anxiety_fear_followup():
    """怕耽误孩子续聊应理解焦虑，而非问卷式 open 兜底。"""
    hist = [
        {"role": "user", "content": "孩子这次考得不好，我是不是太严厉了"},
        {"role": "assistant", "content": "当家长这么操心，我真的心疼你……你已经很在乎 ta 了。"},
    ]
    out = compose_contextual_reply("我很怕耽误他", hist)
    assert out
    assert any(w in out for w in ("耽误", "担心", "在乎", "焦虑"))
    assert "突然" not in out
    assert "一阵子" not in out
    assert not out.lstrip().startswith("嗯")


def test_compose_stranger_continue_chat():
    """陌生关系续聊 compose 路径应口语化，禁止嗯开头与欢迎随时客服腔。"""
    out = compose_contextual_reply("明天还想来找你聊聊", [])
    assert out
    assert not out.lstrip().startswith("嗯")
    assert "欢迎随时" not in out
    assert any(w in out for w in ("开心", "高兴", "真好", "陪"))
    assert "哪一块" not in out


def test_compose_friend_continue_chat():
    """朋友续聊 compose 路径应亲昵口语化，至多一个问句。"""
    hist = [
        {"role": "user", "content": "和你聊还挺开心的"},
        {"role": "assistant", "content": "和你聊我也很开心呀～"},
    ]
    out = compose_contextual_reply("明天还想来找你聊聊", hist)
    assert out
    assert any(w in out for w in ("随时", "开心", "陪"))
    assert out.count("？") <= 1


def test_compose_what_doing_after_bored_smalltalk():
    """无聊闲聊后问「你在干嘛」应口语自述并续聊摸鱼，非 open 兜底。"""
    hist = [
        {"role": "user", "content": "好无聊啊"},
        {"role": "assistant", "content": "闲下来也行呀。要不随便聊聊？"},
        {"role": "user", "content": "嗯"},
        {"role": "assistant", "content": "那咱就随便唠～"},
    ]
    out = compose_contextual_reply("你在干嘛", hist)
    assert out
    assert not out.lstrip().startswith("嗯")
    assert any(w in out for w in ("发呆", "茶", "沙发"))
    assert "摸鱼" in out
    assert "收到了" not in out


def test_compose_what_doing_plain():
    """普通探问 compose 应自述并轻问忙不忙。"""
    out = compose_contextual_reply("你在干嘛", [])
    assert out
    assert any(w in out for w in ("发呆", "茶", "沙发"))
    assert any(w in out for w in ("忙不忙", "忙什么"))
    assert out.count("？") <= 1


def test_compose_childcare_fatigue_after_good_news():
    """报喜后倾诉哄娃疲惫应接住育儿劳累，而非问卷式 open 兜底。"""
    hist = [
        {"role": "user", "content": "今天项目过了，超开心！"},
        {"role": "assistant", "content": "太棒了！替你开心～"},
    ]
    out = compose_contextual_reply(
        "但回家还要哄娃，心好累", hist, relationship_stage="close"
    )
    assert out
    assert not out.lstrip().startswith("嗯")
    assert any(w in out for w in ("顾娃", "哄娃", "带娃"))
    assert "突然这样的" not in out
    assert out.count("？") <= 1


def test_compose_childcare_fatigue_first_turn():
    """首轮带娃疲惫倾诉应共情陪伴，不落入问卷式兜底。"""
    out = compose_contextual_reply("一边上班一边带娃，心好累", [])
    assert out
    assert any(w in out for w in ("带娃", "顾娃", "辛苦", "耗"))
    assert "哪一块你现在最想提" not in out


def test_compose_happy_share_project_passed():
    """报喜分享首轮应同频共振，而非问卷式 open 兜底。"""
    out = compose_contextual_reply("今天项目过了，超开心！", [])
    assert out
    assert any(w in out for w in ("开心", "替你", "棒", "高兴"))
    assert "收到了" not in out
    assert out.count("？") <= 1


def test_compose_happy_share_city_followup():
    """城市期待续聊应同频共振，至多一个问句。"""
    hist = [
        {"role": "user", "content": "我拿到 dream offer 了！！"},
        {"role": "assistant", "content": "哇，听你这么说我也跟着开心起来了！快多跟我说说～"},
    ]
    out = compose_contextual_reply("终于可以去喜欢的城市了", hist, relationship_stage="friend")
    assert out
    assert any(w in out for w in ("城市", "期待", "开心", "替你"))
    assert out.count("？") <= 1


def test_compose_happy_share_close_mixed_day_first_turn():
    """close_mixed_day 首轮报喜 compose 路径应同频共振。"""
    out = compose_contextual_reply(
        "今天项目过了，超开心！", [], relationship_stage="close"
    )
    assert out
    assert any(w in out for w in ("开心", "替你", "棒", "高兴"))
    assert not out.lstrip().startswith("嗯")


def test_compose_burnout_close_mixed_day_third_turn():
    """close_mixed_day 第 3 轮倦怠极限 compose 路径应接住共情，非 open 兜底。"""
    hist = [
        {"role": "user", "content": "今天项目过了，超开心！"},
        {"role": "assistant", "content": "替你开心！项目过了真棒～"},
        {"role": "user", "content": "但回家还要哄娃，心好累"},
        {"role": "assistant", "content": "下班还要哄娃，真的太累了……你先缓口气，我陪着你。"},
    ]
    out = compose_contextual_reply(
        "有时候觉得自己快撑不住了", hist, relationship_stage="close"
    )
    assert out
    assert any(w in out for w in ("极限", "陪", "累", "撑"))
    assert "随便丢几个词" not in out
    assert not out.lstrip().startswith("嗯")
    assert out.count("？") <= 1


def test_compose_defensive_nobody_understands():
    """friend_defensive 首轮防御心态 compose 路径应接住委屈。"""
    out = compose_contextual_reply("你不懂的，没人懂", [], relationship_stage="friend")
    assert out
    assert any(w in out for w in ("懂", "委屈", "听"))
    assert "突然" not in out
    assert out.count("？") <= 1


def test_compose_defensive_withdraw_follow_up():
    """friend_defensive 续聊封闭撤回 compose 路径应尊重边界。"""
    hist = [
        {"role": "user", "content": "你不懂的，没人懂"},
        {"role": "assistant", "content": "我听见你的委屈了，我在认真听。"},
    ]
    out = compose_contextual_reply("算了，不想说了", hist, relationship_stage="friend")
    assert out
    assert any(w in out for w in ("陪着", "不说", "没关系", "都在"))
    assert out.count("？") <= 1


def test_compose_weather_smalltalk():
    """天气闲聊 compose 路径应轻松接话，非 open 兜底。"""
    out = compose_contextual_reply("今天天气不错", [])
    assert out
    assert any(w in out for w in ("天气", "晒", "走", "出门"))
    assert out.count("？") <= 1


def test_compose_movie_smalltalk():
    """电影闲聊 compose 路径应轻松接话。"""
    out = compose_contextual_reply("刚看完一部挺好的电影", [])
    assert out
    assert any(w in out for w in ("电影", "片子", "好看"))
    assert out.count("？") <= 1


def test_compose_thank_you_not_happy_share():
    """感谢句 compose 路径应回应感谢，而非误判为报喜。"""
    out = compose_contextual_reply("感觉你挺温柔的，谢谢", [], relationship_stage="friend")
    assert out
    assert any(w in out for w in ("客气", "高兴", "见外", "帮"))
    assert "开心起来了" not in out


def test_compose_goodnight_farewell():
    """晚安道别 compose 路径应温暖道别。"""
    out = compose_contextual_reply("晚安", [], relationship_stage="friend")
    assert out
    assert any(w in out for w in ("晚安", "好梦", "休息"))
    assert out.count("？") <= 1


def test_compose_emo_fatigue():
    """心累低落 compose 路径应共情陪伴，非问卷兜底，且不以嗯开头。"""
    from app.reply_guard import polish_reply

    out = compose_contextual_reply("心好累", [])
    assert out
    assert any(w in out for w in ("低落", "陪", "懂", "硬撑"))
    assert "突然" not in out
    assert not out.startswith("嗯")
    polished = polish_reply("心好累", out)
    assert not polished.startswith("嗯")


def test_compose_unhappy_no_um_prefix():
    """不开心 compose 路径不以嗯开头。"""
    out = compose_contextual_reply("我不开心了", [])
    assert out
    assert not out.startswith("嗯")


def test_compose_short_annoyance_no_um_prefix():
    """短句烦躁 compose 路径不以嗯开头。"""
    from app.reply_guard import polish_reply

    for text in ("好烦", "有点烦"):
        out = compose_contextual_reply(text, [])
        assert out
        assert any(w in out for w in ("堵", "烦", "缠人", "消化"))
        assert not out.startswith("嗯")
        polished = polish_reply(text, out)
        assert not polished.startswith("嗯")


def test_compose_friendly_greeting_nihao_ya():
    """初识「你好呀」compose 路径应口语自我介绍，非 open 兜底。"""
    out = compose_contextual_reply("你好呀", [], relationship_stage="stranger")
    assert out
    assert any(w in out for w in ("你好", "认识", "小语", "嗨"))
    assert out.count("？") <= 1
    assert not out.startswith("嗯")


def test_compose_friendly_greeting_first_visit():
    """初识「嗨，第一次来」compose 路径应自然接话，语气克制。"""
    out = compose_contextual_reply("嗨，第一次来", [], relationship_stage="stranger")
    assert out
    assert any(w in out for w in ("嗨", "认识", "小语", "你好"))
    assert "亲爱的" not in out
    assert out.count("？") <= 1
    assert not out.startswith("嗯")

