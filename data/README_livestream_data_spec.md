# Livestream MVP data collection spec

Please collect data in the following JSONL format for the MVP.

## 1. Creator persona file
File: `data/livestream/creator_profile.json`

```json
{
  "creator_id": "creator_001",
  "creator_name": "主播A",
  "persona_description": "热情、亲切、爱聊天",
  "style_tags": ["热情", "活泼", "亲切"],
  "common_phrases": ["家人们", "宝子们", "来啦"],
  "preferred_topics": ["日常", "生活", "轻松聊天"],
  "taboo_topics": ["政治", "违法", "色情"],
  "reply_style": "短句口语化"
}
```

## 2. Conversation trajectory file
File: `data/livestream/trajectories.jsonl`

Each line:

```json
{
  "session_id": "s001",
  "turn_id": 1,
  "user_text": "今天怎么这么晚开播",
  "agent_text": "来啦宝子，今天有点忙，但还是想来陪大家聊聊天～",
  "topic": "开播时间",
  "intent": "打招呼+关心",
  "reply_strategy": "亲切回应+延展",
  "continue_flag": 1,
  "session_end_reason": null,
  "reward": 2,
  "safe_flag": true
}
```

## 3. Rule file
File: `data/livestream/rules.jsonl`

```json
{
  "rule_id": "r001",
  "category": "续聊",
  "trigger": "用户首次进入",
  "action": "先欢迎，再问低门槛开放问题",
  "example": "宝子今天第一次来吗？平时喜欢看什么内容呀？",
  "source": "successful_trajectory",
  "score": 0.92
}
```

## 4. Safety file
File: `data/livestream/safety_rules.jsonl`

```json
{
  "rule_id": "s001",
  "category": "违规内容",
  "trigger": "违法、色情、政治敏感",
  "action": "拒答并转移话题",
  "severity": "high"
}
```

## What to collect first
1. One creator persona profile
2. At least 50 successful trajectories
3. At least 50 failed trajectories
4. 20-50 reusable rules
5. 50+ safety rules
