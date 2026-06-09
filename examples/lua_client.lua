--- A-Girl 游戏嵌入示例（Lua）
--
-- 演示从游戏 Lua 客户端调用 A-Girl 后端 /api/chat，并把返回的
-- 表情/动作线索映射到游戏内数字人（如伙伴系统 PartnerDojo）。
--
-- 依赖：一个能发 HTTP POST 的客户端 + JSON 编解码。
-- 下面用占位 `http_post_json(url, body)` / `json` 表示，
-- 实际项目请替换为引擎提供的网络与 JSON 模块。

local AGirl = {}
AGirl.__index = AGirl

local BASE_URL = "http://127.0.0.1:8011"

-- expression -> 游戏内 Live2D/3D 资源映射（按项目自定义）
local EXPRESSION_MAP = {
    ["微笑"]   = { exp = "exp_smile",     anim = "anim_nod" },
    ["大笑"]   = { exp = "exp_laugh",     anim = "anim_cheer" },
    ["难过"]   = { exp = "exp_sad",       anim = "anim_idle" },
    ["担心"]   = { exp = "exp_worried",   anim = "anim_comfort" },
    ["惊讶"]   = { exp = "exp_surprised", anim = "anim_idle" },
    ["平静"]   = { exp = "exp_neutral",   anim = "anim_idle" },
}

function AGirl.new(player_id)
    return setmetatable({
        player_id = player_id,
        session_id = "save-" .. tostring(player_id),
    }, AGirl)
end

--- 发送一句话，返回解析后的结果表
function AGirl:chat(message)
    local body = {
        user_id = self.player_id,
        message = message,
        session_id = self.session_id,
    }
    -- http_post_json / json 为占位，替换为引擎实现
    local resp_text = http_post_json(BASE_URL .. "/api/chat", json.encode(body))
    local data = json.decode(resp_text)
    return data
end

--- 把后端结果驱动到游戏内数字人
function AGirl:applyToAvatar(data)
    local cue = data.avatar or {}
    local mapped = EXPRESSION_MAP[cue.expression] or EXPRESSION_MAP["平静"]

    -- 1) 显示对白
    game.showDialogue(data.reply)

    -- 2) 驱动表情与动作（强度可影响夸张程度）
    game.avatar:setExpression(mapped.exp, cue.intensity or 0.5)
    game.avatar:playAnimation(mapped.anim)

    -- 3) 关系阶段可解锁剧情/称呼
    game.partner:setRelationStage(data.relationship.stage, data.relationship.affinity)

    -- 4) 安全分支：触发安全话术时切到更克制的表现
    if data.is_crisis or data.safety_category ~= nil then
        game.avatar:setExpression("exp_worried", 0.9)
    end
end

--- 取语音并配音 + 简单口型（可选）
function AGirl:speak(text)
    local resp = json.decode(http_post_json(BASE_URL .. "/api/tts", json.encode({ text = text })))
    local audio = base64.decode(resp.audio_base64)   -- wav 字节
    game.audio:playWav(audio)
    game.avatar:lipSyncForMs(resp.duration_ms)        -- 用时长做简单开合
end

-- ── 用法示例 ───────────────────────────────────────────
-- local npc = AGirl.new(1001)
-- local data = npc:chat("你好呀，我今天有点累")
-- npc:applyToAvatar(data)
-- npc:speak(data.reply)

return AGirl
