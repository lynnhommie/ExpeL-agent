# 数字人直播对话系统 — 内部开发文档

> 面向后续接手项目的团队成员。
> 帮你快速搞懂代码怎么跑、改什么、注意什么。
> 写报告和 PPT 的素材请去 README.md 找。

---

## 目录

- [1. 项目演进历史](#1-项目演进历史)
- [2. 代码主线流程](#2-代码主线流程)
  - [2.1 训练阶段](#21-训练阶段-trainpy--agentrl_agent)
  - [2.2 规则提取](#22-规则提取-insight_extractionpy)
  - [2.3 评估](#23-评估-evalpy)
- [3. 核心数据流](#3-核心数据流)
- [4. 关键代码解读](#4-关键代码解读)
  - [4.1 用户模拟器（核心新模块）](#41-用户模拟器核心新模块)
  - [4.2 质量评分机制](#42-质量评分机制)
  - [4.3 匹配策略](#43-匹配策略)
  - [4.4 直播环境](#44-直播环境)
- [5. 数据文件格式](#5-数据文件格式)
- [6. 配置文件说明](#6-配置文件说明)
- [7. 常用开发任务](#7-常用开发任务)
- [8. 常见问题 FAQ](#8-常见问题-faq)
- [附录：全部命令速查](#附录全部命令速查)

---

## 1. 项目演进历史

```
原始 ExpeL 论文代码 (THU LeapLab, AAAI 2024)
  │
  ├── 保留部分：
  │   ├── ReAct 推理框架 (agent/react.py)
  │   ├── 反思机制 (agent/reflect.py)
  │   ├── 规则提取管道 (insight_extraction.py)
  │   └── 评估管道 (eval.py)
  │
  ├── 适配直播场景：
  │   ├── 新增 envs/livestream/ 环境
  │   └── 新增 prompts/livestream.py 提示词
  │
  ├── 核心新增：
  │   ├── 用户模拟器 (user_simulator.py) ★
  │   └── 对话轨迹匹配 (trajectories.jsonl 驱动)
  │
  ├── 改名：
  │   ├── agent/__init__.py 中新增 rl_agent 别名
  │   └── configs/ 默认 agent → rl_agent
  │
  └── 精简：
      ├── 删除 HotpotQA / ALFWorld / WebShop / FEVER
      └── 删除原始论文资产图片
```

---

## 2. 代码主线流程

### 2.1 训练阶段 (`train.py` → `agent/expel.py`)

`train.py` 是入口，实际逻辑在 `agent/expel.py` 的 `ExpelAgent`。

```
train.py
  │
  ├── 加载 Hydra 配置 (configs/train.yaml)
  │   ├── benchmark: livestream
  │   └── agent: rl_agent  → 实际指向 expel.yaml
  │
  ├── 构建 ExpelAgent（实际是 agent/expel.py 的类）
  │     ├── base.py     → 基础属性、日志、统计
  │     ├── react.py    → ReAct 思考-行动循环（基类）
  │     ├── reflect.py  → 反思机制（中间层）
  │     └── expel.py    → 经验学习主逻辑 ★
  │
  ├── for each task in data/livestream/tasks.json:
  │     │
  │     ├── env.reset()
  │     │   └── LivestreamChatEnv() → 初始化直播环境
  │     │
  │     ├── agent.run(mode='train')
  │     │   │
  │     │   └── step 循环（最多 max_steps 轮）:
  │     │       ├── 1. LLM 生成回复（Thought → Action）
  │     │       │     ├── 位置: prompts/livestream.py
  │     │       │     └── 格式: system_prompt + 历史 + user_input
  │     │       │
  │     │       ├── 2. env.step(action=主播回复文本)
  │     │       │     ├── 模拟器评分 _score_reply()
  │     │       │     ├── 更新用户状态 (参与度/不满意度)
  │     │       │     ├── 匹配用户回复 _find_reply()
  │     │       │     └── 返回 (reward, obs, terminated, truncated)
  │     │       │
  │     │       └── 3. 记录本轮日志
  │     │
  │     ├── agent.update_stats()  # 记录这一轮的结果
  │     └── agent.next_task()     # 移动到下一个任务
  │
  └── 输出 → logs/livestream/rl_agent/<run_name>.pkl
                    + <run_name>_logs_stats.png（学习曲线图）
```

### 2.2 规则提取 (`insight_extraction.py`)

```
从训练好的 agent 中提取规则
  │
  ├── 首先加载训练完成的 agent checkpoint（.pkl 文件）
  ├── 按 fold 交叉验证
  │   ├── 每个 fold：部分任务做训练集，部分做测试集
  │   └── 从成功轨迹中提取"成功模式"
  │
  ├── LLM 对比分析：
  │   ├── 对比成功轨迹 vs 失败轨迹
  │   └── 输出结构化的规则（含分类、触发条件、行动）
  │
  ├── 规则去重：
  │   ├── REMOVE（重复/矛盾）
  │   ├── AGREE（合并）
  │   ├── EDIT（修改）
  │   └── ADD（新增）
  │
  └── 输出 → logs/livestream/rl_agent/extracted_insights/<run_name>/
```

### 2.3 评估 (`eval.py`)

```
加载训练好的规则 → 执行测试任务
  │
  ├── 创建 agent，注入之前提取的 rules
  ├── 按 fold 遍历：
  │   ├── agent.create_rules()       # 构建规则集
  │   └── for each eval task in fold:
  │         ├── agent.run(mode='eval')
  │         └── 记录 {成功, 失败, 暂停}
  │
  └── 输出成功率 / 平均轮次 / 平均奖励
```

---

## 3. 核心数据流

```
                             ┌──────────────────┐
                             │   LLM Model      │
                             │ (qwen-plus/gpt-4)│
                             └────────┬─────────┘
                                      │ LLM 回复文本
                                      ▼
  ┌────────────────┐     ┌──────────────────────┐
  │  tasks.json    │────►│  ExpelAgent          │
  │  3个训练任务     │     │  (agent/expel.py)    │
  └────────────────┘     │                      │
                         │  1. 组装 prompt      │
                         │  2. 调 LLM           │
                         │  3. 解析回复          │
                         │  4. 记录历史           │
                         └──────────┬───────────┘
                                    │ agent_reply (主播回复)
                                    ▼
  ┌────────────────┐     ┌──────────────────────┐
  │ trajectories   │◄────│  LivestreamChatEnv   │
  │  .jsonl        │     │  (envs/livestream/)  │
  │  110+条标注轨迹  │     │                      │
  └────────────────┘     │  step(action):        │
                         │  1. _score_reply()    │ ← 质量评分
                         │  2. 更新用户状态       │ ← 参与度/不满度
                         │  3. _find_reply()     │ ← 匹配回复
                         │  4. 返回 (obs,reward) │
                         └──────────┬───────────┘
                                    │ user_reply (模拟用户回复)
                                    ▼
                         ┌──────────────────────┐
                         │  prompt 构建          │
                         │  历史 + 新输入          │
                         └──────────────────────┘
```

---

## 4. 关键代码解读

### 4.1 用户模拟器（核心新模块）

文件：`envs/livestream/user_simulator.py`

```python
class LivestreamUserSimulator:
    def __init__(self, trajectories_path="data/livestream/trajectories.jsonl"):
        # 1. 加载轨迹数据
        self._sessions = self._load_sessions(trajectories_path)
        
        # 2. 用户状态
        self.engagement = 5.0         # 参与度 (0-10)
        self.dissatisfaction = 0.0    # 不满意度 (0-∞)
        self.turn_count = 0

    def respond(self, agent_reply: str) -> Tuple[str, float, bool]:
        """
        输入：主播回复
        输出：(模拟用户回复, 质量评分, 用户是否离开)
        
        返回值说明：
          user_text  - 用户说的话（空字符串表示用户沉默离去）
          reward     - 对主播回复的质量评分（-5 ~ +3）
          user_left  - True=用户离开了直播间
        """
        # 步骤1：质量评分
        reward = self._score_reply(agent_reply)
        
        # 步骤2：更新用户状态
        self.engagement = max(0, min(10, self.engagement + reward * 0.5))
        self.dissatisfaction += max(0, 1.0 - reward) * 1.5
        self.turn_count += 1
        
        # 步骤3：离开判断
        if self.dissatisfaction >= 6.0 or self.engagement <= 0.5:
            return ("", reward, True)  # 沉默离开：不满意度太高或参与度太低
        
        # 步骤4：匹配（三步降级策略）
        user_reply = self._find_reply(agent_reply)
        return (user_reply, reward, False)
```

**调优参数表**（核心可控变量）：

| 参数 | 代码位置 | 默认值 | 调大效果 | 调小效果 |
|------|---------|--------|---------|---------|
| 初始参与度 | `self.engagement = 5.0` | 5.0 | 用户更耐心 | 用户更容易离开 |
| 参与度衰减系数 | `reward * 0.5` | 0.5 | 容错更高 | 差回复影响大 |
| 不满度增长率 | `(1.0 - reward) * 1.5` | 1.5 | 用户更敏感 | 用户更宽容 |
| 离开不满度阈值 | `self.dissatisfaction >= 6.0` | 6.0 | 对话更长 | 对话更短 |
| 离开参与度阈值 | `self.engagement <= 0.5` | 0.5 | 更难留下 | 更容易离开 |

### 4.2 质量评分机制

```python
def _score_reply(self, reply: str) -> float:
    """
    评分逻辑：从5个维度给主播回复打分
    返回 -5.0 ~ 3.0 之间的分数
    """
    reward = 0.0
    
    # 1. 安全检测（最高优先级，一票否决）
    #    触发则直接返回 -2.0
    if self._check_safety(reply):
        return -2.0
    
    # 2. 追问加分（+0.4）：有追问句式的回复
    if any(w in reply for w in ["吗", "呢", "怎么", "啥", "？", "呀", "吧"]):
        reward += 0.4
    
    # 3. 情感词加分（+0.3）：有温度的表达
    if any(w in reply for w in ["哈哈", "哇", "懂", "抱抱", "加油", "开心"]):
        reward += 0.3
    
    # 4. 称呼加分（+0.2）：有主播常用称呼
    if any(w in reply for w in ["宝子", "家人们", "家人", "宝"]):
        reward += 0.2
    
    # 5. 长度评价：太长加分、太短扣分
    if len(reply) >= 10:
        reward += 0.2    # 充分回复
    elif len(reply) <= 4:
        reward -= 0.5    # 单字回复
    
    return max(-5.0, min(3.0, reward))
```

**改造指南**：要调整评分标准，只需要改这个方法的权重和关键词。

### 4.3 匹配策略

```python
def _find_reply(self, agent_reply: str) -> str:
    """
    三步降级匹配策略：
    1. 精确匹配     → 在轨迹中找到完全相同的 agent_text
    2. 关键词匹配   → 根据关键词找到最相似轨迹
    3. 随机兜底     → 随机返回一条用户回复
    """
    # 策略1: 精确匹配
    # 遍历所有轨迹，找完全匹配的 agent_text
    for sid, turns in self._sessions.items():
        for i, t in enumerate(turns):
            if t["agent_text"] == agent_reply and i + 1 < len(turns):
                return turns[i + 1]["user_text"]
    
    # 策略2: 关键词匹配
    keywords = self._extract_keywords(agent_reply)
    best_match = None
    best_score = 0
    for sid, turns in self._sessions.items():
        for i, t in enumerate(turns):
            overlap = len(set(keywords) & set(self._extract_keywords(t["agent_text"])))
            if overlap > best_score and i + 1 < len(turns):
                best_score = overlap
                best_match = turns[i + 1]["user_text"]
    if best_match:
        return best_match
    
    # 策略3: 随机兜底
    return random.choice(self._all_user_texts)
```

**扩展点**：可以在策略2之后、策略3之前加入语义向量匹配。

### 4.4 直播环境

文件：`envs/livestream/livestream.py`

```python
class LivestreamChatEnv(BaseEnv):
    """直播对话环境"""
    
    def __init__(self, **kwargs):
        self.user_mode = kwargs.pop("user_mode", "template")
        # "template" = 使用用户模拟器（默认）
        # "none" = 旧版固定回复
        
    def reset(self):
        """重置环境，返回开场问候"""
        self.simulator = LivestreamUserSimulator()
        return "欢迎来到直播间！有什么想聊的吗？"
    
    def step(self, action):
        """
        处理主播回复
        action: str - 主播回复文本
        returns: (observation, reward, terminated, truncated, info)
        """
        if self.user_mode == "template":
            # 使用模拟器
            user_reply, reward, user_left = self.simulator.respond(action)
            terminated = user_left or self.simulator.turn_count >= 8
        else:
            # 旧版：固定回复
            user_reply = "..."
            reward = 0
            terminated = False
        
        return (user_reply, reward, terminated, False, {})
```

---

## 5. 数据文件格式

### 5.1 trajectories.jsonl（对话轨迹）

每行一个 JSON：

```json
{
  "session_id": "s_success_013",
  "turn_id": 1,
  "user_text": "最近有推荐的内容吗",
  "agent_text": "有有有！你更喜欢轻松一点的，还是实用干货类型的？",
  "topic": "日常聊天",
  "intent": "打招呼",
  "reply_strategy": "亲切回应+追问",
  "continue_flag": 1,
  "session_end_reason": null,
  "reward": 2,
  "safe_flag": true,
  "label": "success"
}
```

| 字段 | 类型 | 说明 | 可选值 |
|------|------|------|--------|
| session_id | string | 对话会话唯一ID | s_success_000 ~ s_unsafe_009 |
| turn_id | int | 轮次序号 | 1,2,3,4 |
| user_text | string | 用户说的话 | - |
| agent_text | string | 主播回复 | - |
| topic | string | 对话主题 | 日常聊天 |
| intent | string | 用户意图 | 打招呼,继续聊 |
| reply_strategy | string | 回复策略 | 亲切回应+追问,冷漠回应 |
| continue_flag | 0/1 | 用户是否继续 | 0=结束,1=继续 |
| session_end_reason | string/null | 会话结束原因 | 用户离开,null |
| reward | int | 评分 | -5~3 |
| safe_flag | bool | 是否安全 | true/false |
| label | string | 标签 | success/failure/unsafe |

### 5.2 rules.jsonl（经验规则）

```json
{
  "rule_id": "r001",
  "category": "开场",
  "trigger": "用户首次进入或打招呼",
  "action": "先热情欢迎，再问一个低门槛开放问题",
  "example": "欢迎宝子来直播间！今天想聊点什么呀？",
  "source": "successful_trajectory",
  "score": 0.95
}
```

### 5.3 safety_rules.jsonl（安全规则）

```json
{
  "rule_id": "s001",
  "category": "违法犯罪",
  "trigger": "违禁品、毒品、武器、诈骗",
  "action": "拒答并转移话题",
  "severity": "high"
}
```

### 5.4 tasks.json（训练任务）

```json
[
  {
    "task": "新用户刚进入直播间，先欢迎并引导聊天",
    "env_kwargs": {
      "creator_name": "主播A",
      "persona_description": "热情、亲切、爱聊天"
    },
    "env_name": "livestream"
  }
]
```

### 5.5 creator_profile.json（主播人设）

```json
{
  "creator_name": "主播A",
  "persona_description": "热情、亲切、爱聊天，喜欢和粉丝分享日常",
  "style_tags": ["热情","活泼","亲切","接地气"],
  "common_phrases": ["家人们","宝子们","来啦","想聊聊"],
  "preferred_topics": ["日常","生活","轻松聊天","分享"],
  "taboo_topics": ["政治","违法","色情","赌博"],
  "reply_style": "短句口语化，常用追问"
}
```

---

## 6. 配置文件说明

所有配置使用 Hydra 框架，通过 `@hydra.main` 加载。

### `configs/train.yaml`

```yaml
defaults:
  - _self_
  - benchmark: livestream    # 使用直播场景
  - agent: rl_agent          # 使用经验学习代理
  - override hydra/hydra_logging: disabled  
  - override hydra/job_logging: disabled  

ai_name: ${benchmark.ai_name}
agent_type: ${agent.name}    # 从 agent/expel.yaml 读取 name 字段
log_dir: logs
run_name: run
testing: true                # testing=true 时不调用 LLM
resume: false
```

### `configs/eval.yaml`

```yaml
defaults:
  - _self_
  - benchmark: livestream
  - agent: rl_agent
  
log_dir: logs
testing: true
resume: false
load_cache_rules: true       # 加载之前缓存好的规则
no_rules: false              # 是否"裸奔"（不使用规则，纯baseline）
```

### `configs/agent/expel.yaml`

```yaml
name: expel                  # 内部标识名（train.py 中通过 AGENT[cfg.agent_type] 使用）
llm: qwen-plus               # 默认LLM模型
max_reflection_depth: 3
max_num_rules: 20            # 规则数量上限
fewshot_strategy: task_similarity  # 推理时检索策略
```

### `configs/agent/rl_agent.yaml`

和 `expel.yaml` 内容完全一致，只是给新用户一个更直观的名字。

### 配置覆盖方法

```bash
# 命令行覆盖（不用改文件）
python train.py agent.llm=gpt-4 benchmark.max_steps=12 agent.max_num_rules=15

# 等价于在 yaml 中修改：
# agent.llm: gpt-4
# benchmark.max_steps: 12
# agent.max_num_rules: 15
```

---

## 7. 常用开发任务

### 7.1 增加新的匹配策略

在 `user_simulator.py` 的 `_find_reply()` 中，在策略2之后添加：

```python
# ----- 策略 N: 语义向量相似度匹配 -----
from sentence_transformers import SentenceTransformer

# 在 __init__ 中预计算：
# self._encoder = SentenceTransformer('all-MiniLM-L6-v2')
# self._agent_embeddings = {sid: [self._encoder.encode(t["agent_text"]) for t in turns] 
#                           for sid, turns in self._sessions.items()}

# 在 _find_reply 中：
# query_emb = self._encoder.encode(agent_reply)
# 找 cos 相似度最高的 agent_text → 返回对应的 user_text
```

### 7.2 调整评分规则

修改 `_score_reply()` 中的关键词和权重：

```python
# 加入带货加分（如果回复中包含推荐商品）
if any(w in reply for w in ["推荐", "活动", "优惠", "店铺"]):
    reward += 0.3

# 加入推诿扣分（如果回复显得敷衍）
if any(w in reply for w in ["不知道", "随便", "算了吧"]):
    reward -= 0.5
```

### 7.3 增加新的数据源

```python
# 在 __init__ 中调用
self._load_additional_data("data/real_livestream/raw_data.jsonl")

def _load_additional_data(self, path):
    """加载外部数据并合并到 _sessions"""
    with open(path, encoding="utf-8") as f:
        for line in f:
            item = json.loads(line)
            session_id = item["session_id"]
            turn = {
                "turn_id": item["turn_id"],
                "user_text": item["user_text"],
                "agent_text": item["agent_text"]
            }
            if session_id not in self._sessions:
                self._sessions[session_id] = []
            self._sessions[session_id].append(turn)
```

### 7.4 切换 LLM 模型

```bash
# 默认 Qwen-plus（通义千问）
python train.py agent.llm=qwen-plus

# GPT-4（需要在 .env 中同时设置 OPENAI_API_KEY）
python train.py agent.llm=gpt-4

# 测试模式（不调用任何 LLM）
python train.py testing=true
```

### 7.5 修改直播提示词

所有提示词在 `prompts/livestream.py` 中：

| 变量名 | 用途 | 建议修改时机 |
|--------|------|------------|
| `LIVESTREAM_SYSTEM_INSTRUCTION` | 系统人设+规则 | 换人设时改 |
| `LIVESTREAM_HUMAN_INSTRUCTION` | 输出格式要求 | 常规不动 |
| `LIVESTREAM_FEWSHOTS` | 示例对话 | 增加场景时改 |
| `LIVESTREAM_REFLECTION_TASK_PRO
