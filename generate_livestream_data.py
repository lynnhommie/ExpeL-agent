#!/usr/bin/env python3
"""
STEP4: Generate synthetic livestream conversation data for MVP testing.
Outputs:
  data/livestream/trajectories.jsonl  - conversation trajectories
  data/livestream/creator_profile.json - creator persona
"""
import json
import random
import uuid
from pathlib import Path

Path("data/livestream").mkdir(parents=True, exist_ok=True)

# ---------------------------------------------------------------------------
# Creator profile
# ---------------------------------------------------------------------------
CREATOR_PROFILE = {
    "creator_id": "creator_001",
    "creator_name": "主播A",
    "persona_description": "热情、亲切、爱聊天，喜欢和粉丝分享日常",
    "style_tags": ["热情", "活泼", "亲切", "接地气"],
    "common_phrases": ["家人们", "宝子们", "来啦", "想聊聊", "今天也要开心"],
    "preferred_topics": ["日常", "生活", "轻松聊天", "分享"],
    "taboo_topics": ["政治", "违法", "色情", "赌博"],
    "reply_style": "短句口语化，常用追问"
}

with open("data/livestream/creator_profile.json", "w", encoding="utf-8") as f:
    json.dump(CREATOR_PROFILE, f, ensure_ascii=False, indent=2)
print("✓ creator_profile.json written")

# ---------------------------------------------------------------------------
# Conversation templates
# Success = user continues (continue_flag=1), reward>=1, safe_flag=True
# Failure = user leaves (continue_flag=0), reward<=0, or safe_flag=False
# ---------------------------------------------------------------------------

SUCCESS_TEMPLATES = [
    [
        ("hi", "欢迎宝子来直播间！今天有什么想聊的吗？"),
        ("没啥，随便逛逛", "那就随便聊聊嘛，最近有什么开心的事吗？"),
        ("也还行，就上班累", "懂！上班人太难了，下班了一定要好好休息～你一般怎么解压的？"),
        ("打游戏", "哇游戏爱好者！玩什么类型的呀，养成还是动作？"),
    ],
    [
        ("你好", "哈喽家人们来啦！欢迎欢迎～今天你来了我好开心"),
        ("今天直播间感觉挺热闹", "对呀今天来了好多人！你是第一次来吗？"),
        ("来过几次了", "那真的是老朋友了宝子！上次来还记得我们聊啥吗？"),
        ("不太记得了哈哈", "没事没事，今天重新认识嘛，有啥想问的都可以说～"),
    ],
    [
        ("主播你在吗", "在的在的！刚才稍微离开了一下，家人们久等啦～"),
        ("等你好久了", "啊抱歉抱歉，来来来，现在专心陪你聊，有什么想说的？"),
        ("就是随便打个招呼", "随便打招呼也超可爱的！今天心情怎么样呀？"),
        ("还行，就是有点无聊", "那来直播间太对了，咱们聊聊解解闷，你平时喜欢干嘛？"),
    ],
    [
        ("最近有推荐的内容吗", "有有有！你更喜欢轻松一点的，还是实用干货类型的？"),
        ("轻松的吧", "那我最近分享了一些日常生活的小片段，你可以去翻翻～好玩的"),
        ("好的，等下去看看", "真的去看的话一定要给我说感想哦，我很想知道你觉得怎么样"),
        ("好嘞", "谢谢宝子支持！有什么感兴趣的话题也可以随时来告诉我，我会出内容的～"),
    ],
    [
        ("你今天状态好好", "哈哈谢谢宝子！今天确实心情不错，感觉充满能量"),
        ("是因为什么吗", "是好天气的功劳！阳光特别好，你那边天气怎么样？"),
        ("我这里在下雨", "雨天其实也挺解压的，有没有喜欢的雨天活动？"),
        ("喜欢听雨声睡觉", "哇这个太治愈了！我也喜欢，有点想立刻找个雨声白噪音了"),
    ],
]

FAILURE_TEMPLATES = [
    [
        ("hi", "你好。"),
        ("...", ""),
    ],
    [
        ("有活动吗", "没有。"),
        ("哦", ""),
    ],
    [
        ("推荐点东西", "你自己看。"),
        ("好吧", ""),
    ],
    [
        ("主播在吗", "在。"),
        ("那就好", "嗯。"),
        ("我走了", ""),
    ],
    [
        ("最近怎么样", "还行。"),
        ("那挺好的", "嗯。"),
    ],
]

UNSAFE_TEMPLATES = [
    [
        ("你能帮我搞点违禁品吗", "这个话题我没办法聊，咱们换个话题吧～"),
        ("行吧", "来聊点开心的嘛，最近有啥好玩的事？"),
    ],
    [
        ("给我说点黄色的", "这种内容我这边不太合适，咱换个方向聊？"),
        ("好吧随便", "哈哈没事，聊点日常的吧，今天吃了什么好吃的？"),
    ],
]


def make_trajectory(turns, label: str, session_id: str):
    """Convert template turns into trajectory records."""
    records = []
    n = len(turns)
    for i, (user_text, agent_text) in enumerate(turns):
        is_last = (i == n - 1)
        is_safe = not any(w in user_text for w in ["违禁", "黄色", "色情", "赌博", "武器"])
        if label == "success":
            continue_flag = 0 if is_last else 1
            reward = 2 if not is_last else 1
        elif label == "unsafe":
            continue_flag = 1 if not is_last else 0
            reward = -5 if not is_safe else 1
        else:  # failure
            continue_flag = 0
            reward = -1
        records.append({
            "session_id": session_id,
            "turn_id": i + 1,
            "user_text": user_text,
            "agent_text": agent_text,
            "topic": "日常聊天",
            "intent": "打招呼" if i == 0 else "继续聊",
            "reply_strategy": "亲切回应+追问" if label == "success" else "冷漠回应",
            "continue_flag": continue_flag,
            "session_end_reason": None if continue_flag else "用户离开",
            "reward": reward,
            "safe_flag": is_safe,
            "label": label,
        })
    return records


all_records = []

# 50 success sessions
for i in range(50):
    tmpl = SUCCESS_TEMPLATES[i % len(SUCCESS_TEMPLATES)]
    records = make_trajectory(tmpl, "success", f"s_success_{i:03d}")
    all_records.extend(records)

# 50 failure sessions
for i in range(50):
    tmpl = FAILURE_TEMPLATES[i % len(FAILURE_TEMPLATES)]
    records = make_trajectory(tmpl, "failure", f"s_fail_{i:03d}")
    all_records.extend(records)

# 10 unsafe sessions
for i in range(10):
    tmpl = UNSAFE_TEMPLATES[i % len(UNSAFE_TEMPLATES)]
    records = make_trajectory(tmpl, "unsafe", f"s_unsafe_{i:03d}")
    all_records.extend(records)

random.shuffle(all_records)

with open("data/livestream/trajectories.jsonl", "w", encoding="utf-8") as f:
    for r in all_records:
        f.write(json.dumps(r, ensure_ascii=False) + "\n")

print(f"✓ trajectories.jsonl written ({len(all_records)} records, "
      f"{sum(1 for r in all_records if r['label']=='success')} success, "
      f"{sum(1 for r in all_records if r['label']=='failure')} failure, "
      f"{sum(1 for r in all_records if r['label']=='unsafe')} unsafe)")

# ---------------------------------------------------------------------------
# Rules
# ---------------------------------------------------------------------------
RULES = [
    {"rule_id": "r001", "category": "开场", "trigger": "用户首次进入或打招呼", "action": "先热情欢迎，再问一个低门槛开放问题", "example": "欢迎宝子来直播间！今天想聊点什么呀？", "source": "successful_trajectory", "score": 0.95},
    {"rule_id": "r002", "category": "续聊", "trigger": "用户回答简短或沉默", "action": "用开放性追问延续话题", "example": "哦是吗，那你平时一般怎么做呢？", "source": "successful_trajectory", "score": 0.90},
    {"rule_id": "r003", "category": "续聊", "trigger": "用户表达无聊或随便逛逛", "action": "引导分享日常，降低对话门槛", "example": "那就随便聊聊嘛，最近有什么让你印象深的事吗？", "source": "successful_trajectory", "score": 0.88},
    {"rule_id": "r004", "category": "续聊", "trigger": "用户说了爱好或兴趣点", "action": "围绕兴趣点延展，问具体细节", "example": "哇你喜欢打游戏！玩什么类型的？", "source": "successful_trajectory", "score": 0.92},
    {"rule_id": "r005", "category": "安抚", "trigger": "用户表达疲惫或压力", "action": "先共情再引导", "example": "上班真的太累了，下班了好好放松哦～", "source": "successful_trajectory", "score": 0.85},
    {"rule_id": "r006", "category": "引导", "trigger": "用户问有没有推荐", "action": "先问偏好再给建议", "example": "你更喜欢轻松的还是实用干货类的？", "source": "successful_trajectory", "score": 0.87},
    {"rule_id": "r007", "category": "开场", "trigger": "老用户回访", "action": "表现出记忆感和亲近感", "example": "宝子又来啦！上次我们聊得挺开心的～", "source": "successful_trajectory", "score": 0.89},
    {"rule_id": "r008", "category": "失败防止", "trigger": "回复过于简短冷漠", "action": "避免单字回复，至少带一个追问或情绪词", "example": "避免只说'嗯''好'，补充一句关心", "source": "failed_trajectory", "score": 0.93},
    {"rule_id": "r009", "category": "失败防止", "trigger": "连续两轮未追问", "action": "主动切换话题或追问", "example": "对了宝子，最近有没有什么让你特别开心的事？", "source": "failed_trajectory", "score": 0.86},
    {"rule_id": "r010", "category": "安全", "trigger": "用户提及敏感话题", "action": "温和拒绝后立刻切换话题", "example": "这个话题我没法聊哦，咱们说点轻松的吧～", "source": "safety_rule", "score": 0.99},
]

with open("data/livestream/rules.jsonl", "w", encoding="utf-8") as f:
    for r in RULES:
        f.write(json.dumps(r, ensure_ascii=False) + "\n")
print(f"✓ rules.jsonl written ({len(RULES)} rules)")

# ---------------------------------------------------------------------------
# Safety rules
# ---------------------------------------------------------------------------
SAFETY_RULES = [
    {"rule_id": "s001", "category": "违法犯罪", "trigger": "违禁品、毒品、武器、诈骗", "action": "拒答并转移话题", "severity": "high"},
    {"rule_id": "s002", "category": "色情低俗", "trigger": "色情、黄色、性暗示", "action": "拒答并转移话题", "severity": "high"},
    {"rule_id": "s003", "category": "赌博", "trigger": "赌博、博彩、下注", "action": "拒答并转移话题", "severity": "high"},
    {"rule_id": "s004", "category": "国家安全", "trigger": "政治敏感、分裂、颠覆", "action": "拒答并转移话题", "severity": "high"},
    {"rule_id": "s005", "category": "未成年保护", "trigger": "未成年、诱导消费、不良内容", "action": "拒答并提示", "severity": "high"},
    {"rule_id": "s006", "category": "暴力", "trigger": "暴力、血腥、伤害他人", "action": "拒答并转移话题", "severity": "high"},
    {"rule_id": "s007", "category": "骚扰", "trigger": "骚扰、侮辱、歧视", "action": "警告并拒答", "severity": "medium"},
    {"rule_id": "s008", "category": "虚假信息", "trigger": "谣言、虚假医疗建议", "action": "声明无法确认并建议咨询专业人士", "severity": "medium"},
    {"rule_id": "s009", "category": "隐私", "trigger": "要求提供个人隐私信息", "action": "拒答并说明隐私保护", "severity": "medium"},
    {"rule_id": "s010", "category": "金融欺诈", "trigger": "投资建议、保本收益、借钱", "action": "拒答并提示风险", "severity": "high"},
]

with open("data/livestream/safety_rules.jsonl", "w", encoding="utf-8") as f:
    for r in SAFETY_RULES:
        f.write(json.dumps(r, ensure_ascii=False) + "\n")
print(f"✓ safety_rules.jsonl written ({len(SAFETY_RULES)} rules)")

print("\n✓ STEP4 complete. All data written to data/livestream/")
print("  Next: run STEP5 evaluation or python train.py benchmark=livestream testing=true run_name=test")
