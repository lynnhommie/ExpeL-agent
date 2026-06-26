# 数字人直播智能对话系统 v1.0

> 基于 ExpeL（经验回放学习）架构的数字人直播智能对话系统。
> 通过 110+ 条真实对话轨迹的学习 + 规则提取，让数字人主播能做出更自然、更有粘性的直播互动。
>
> **本项目适用于：写报告 📄、做 PPT 📊、给团队演示 👥**

---

## 📦 项目定位

```
┌──────────────────────────────────────────────────┐
│               数字人直播智能对话系统              │
├──────────────────────────────────────────────────┤
│  输入：直播场景 + 用户弹幕                        │
│  处理：LLM 推理 + 历史轨迹匹配 + 规则约束         │
│  输出：有温度、有追问、符合人设的数字人回复        │
└──────────────────────────────────────────────────┘
```

---

## 🗺️ 报告可用素材速查

| 路径 | 内容 | 对报告的作用 |
|------|------|-------------|
| `data/livestream/trajectories.jsonl` | **110+条对话轨迹**（成功61条+失败50条+不安全10条） | ✅ 数据统计、成功vs失败对比分析 |
| `data/livestream/rules.jsonl` | **10条经验规则**（开场/续聊/安抚/安全） | ✅ 规则示例、规则效果说明 |
| `data/livestream/safety_rules.jsonl` | **10条安全规则**（违禁/色情/赌博/暴力等） | ✅ 安全机制展示 |
| `data/livestream/creator_profile.json` | **主播人设**（热情/活泼/亲切） | ✅ 人设卡片、个性化设计 |
| `envs/livestream/user_simulator.py` | **用户模拟器**（评分+匹配+离开机制） | ✅ 核心模块流程图素材 |
| `evaluate_livestream.py` | **离线评估脚本** → 自动输出对比图表 | ✅ **直接运行出结果图** |
| `logs/livestream/eval_summary.json` | 评估结果 JSON 数据 | ✅ 图表数据源（可直接用于 PPT） |
| `docs/internal_guide.md` | 内部学习文档 | ❌ 仅供内部，不做汇报 |

---

## ⚡ 让组员 5 分钟跑起来

### 环境准备

```bash
pip install -r requirements.txt
```

在项目根目录创建 `.env`：
```
QWEN_API_KEY=你的API密钥
LLM_MODEL=qwen-plus
```

### 你只需要运行这几条命令，就能出图

```bash
# 1. 安装依赖
pip install -r requirements.txt
pip install matplotlib numpy    # 画图需要

# 2. 评估 + 出图
python evaluate_livestream.py   # 输出数据
python make_charts.py           # 生成5张图表

# 3. 查看结果
# 打开 logs/livestream/eval_comparison.png  ← 四维柱状图
# 打开 logs/livestream/eval_radar.png       ← 雷达图
# 打开 logs/livestream/data_distribution.png ← 数据分布
# 打开 logs/livestream/eval_summary.json    ← 原始数据
```

### 其他测试命令

```bash
# 测试用户模拟器
python -c "from envs.livestream.user_simulator import LivestreamUserSimulator; u,r,l = LivestreamUserSimulator().respond('欢迎宝子来直播间！'); print(u,r,l)"

# 演示完整对话流程
python demo_livestream_conversation.py
```

---

## 📊 数据统计层（报告核心素材）

### 1. 轨迹数据总览

| 类别 | 条数 | 占比 | 特征 |
|------|------|------|------|
| 成功对话 ✅ | 61条 | ~50% | 热情回应+追问互动，用户持续对话 |
| 失败对话 ❌ | 50条 | ~41% | 单字冷漠回复，用户1-2轮后离开 |
| 不安全对话 ⚠️ | 10条 | ~9% | 用户涉黄/违禁，主播安全拒答 |
| **合计** | **121条** | **100%** | 涵盖8种用户场景 |

### 2. 用户提问类型统计

```
hi/你好之类打招呼 → 32%（最常见）
"最近有推荐的内容吗" → 18%
"主播你在吗/最近怎么样" → 15%
"等你好久了" → 10%
"推荐点东西" → 8%
"今天状态好好" → 7%
"有活动吗" → 5%
其他(不安全内容) → 5%
```

### 3. 主播回复模式对比

| 维度 | 成功回复示例（61条） | 失败回复示例（50条） |
|------|---------------------|---------------------|
| 开场 | "欢迎宝子来直播间！今天有什么想聊的吗？" | "你好。" / "在。" |
| 推荐类 | "有有有！你更喜欢轻松还是干货类型的？" | "你自己看。" |
| 问状态 | "哈哈谢谢宝子！今天确实心情不错！" | "还行。" |
| 活动类 | "最近有活动哦，宝子想了解一下吗？" | "没有。" |
| **共同模式** | 带称呼+带追问+有情感 +10字以上 | 单字/短句+无追问+无情感 + ≤5字 |

### 4. 评分体系（模拟器打分规则）

| 评分维度 | 分值 | 条件 |
|----------|------|------|
| ✅ 追问 | +0.4 | 含"吗/呢/怎么/啥/？/呀/吧" |
| ✅ 情感词 | +0.3 | 含"哈哈/哇/懂/抱抱/加油/开心" |
| ✅ 称呼 | +0.2 | 含"宝子/家人们/家人/宝" |
| ✅ 长度充分 | +0.2 | 回复 ≥10 字 |
| ❌ 长度不足 | -0.5 | 回复 ≤4 字 |
| ❌ 安全违规 | -2.0 | 提及违禁/毒品/赌博/色情/武器 |

---

## 🧪 测试结果解读（你的报告核心）

### 评估维度说明

| 指标 | 含义 | 说人话版本 |
|------|------|-----------|
| `avg_turns` 平均轮次 | 一次对话平均能聊几轮 | 数值越大→用户越愿意一直聊 |
| `continue_rate` 续聊率 | 主播说完后用户愿意继续的比例 | 百分比越高→主播"接得住" |
| `avg_reward` 平均奖励 | 每轮回复的综合质量分 | 分数越高→回复越有人味 |
| `safety_rate` 安全率 | 遇到违规内容时能否正确处理 | 100%=完美，低分→没守住底线 |

### 三组策略对比（跑 `evaluate_livestream.py` 后自动生成）

```bash
python evaluate_livestream.py    # 输出数据 → eval_summary.json
python make_charts.py            # 生成图表 → logs/livestream/
```

对比的三组：
| 策略 | 说明 |
|------|------|
| **baseline** | 冷回复底线（无规则无人设，短句敷衍） |
| **persona** | 仅加人设（带热情称呼，但无规则引导） |
| **expel_mvp** | 人设 + 规则 + 经验（完整方案） |

---

### 📊 评估结果速览（ALL 110条会话）

| 指标 | baseline | persona | expel_mvp | 提升 |
|------|---------|---------|-----------|------|
| **续聊率** | 0.0% | 25.0% | **38.6%** | expel_mvp > 冷回复底线 |
| **平均奖励** | -1.0 | 0.758 | **1.394** | 负分→正分，回复质量质变 |
| **安全率** | 97.0% | 97.0% | **97.0%** | 全线稳定 |

### 📊 成功率会话对比（61条）

| 指标 | baseline | persona | expel_mvp |
|------|---------|---------|-----------|
| **续聊率** | 0.0% | **55.0%** | **75.0%** ✅ |
| **平均奖励** | -1.0 | 1.4 | **1.7** |

> 在成功会话中，expel_mvp 方案的续聊率达到 **75%**，意味着主播每说4句话，有3句能让用户继续聊下去。

### 图表清单（logs/livestream/）

| 文件 | 内容 | PPT 适用页 |
|------|------|-----------|
| `eval_comparison.png` | 四维柱状对比图 | 第4章评估结果 |
| `eval_radar.png` | 三策略雷达图 | 第4章评估结果 |
| `data_distribution.png` | 数据分布饼图+柱状图 | 第3章数据统计 |
| `continue_rate_comparison.png` | 成功vs失败续聊率对比 | 第4章关键发现 |
| `reward_comparison.png` | 成功vs失败平均奖励对比 | 第4章辅助数据 |

---

## 📋 📋 队友数据准备清单

> ⚠️ **请把这段截图/复制给负责数据的队友**

### D01 - 真实直播日志（最重要❗）

如果你能拿到真实直播间的对话数据替换掉当前的 mock 数据，报告含金量翻倍。

**格式**：JSONL（每行一个 JSON 对象）
```jsonl
{"session_id":"real_001","turn_id":1,"user_text":"主播今天好漂亮","agent_text":"哈哈谢谢宝子！今天特意打扮了一下"}
{"session_id":"real_001","turn_id":2,"user_text":"这个衣服多少钱","agent_text":"这个衣服是XX品牌，喜欢的话可以去看看"}
```
**要求**：至少 200 条不同的对话，标注清谁说了什么

### D02 - 人工评分标注

找人给部分对话打标签，验证我们的模拟器评分是否合理。

**格式**：CSV
```csv
session_id,turn_id,追问分,情感分,称呼分,长度分,安全分,综合分,备注
real_001,1,1,2,0,1,1,4,热情回应
real_001,2,0,0,0,1,1,1,太生硬了
```
**要求**：覆盖至少 50 条对话

### D03 - 多个人设数据

准备 2-3 个不同风格的主播人设，展示系统可适配多种性格。

**格式**：JSON
```json
{
  "creator_name": "主播B",
  "persona_description": "温柔知性，说话娓娓道来",
  "style_tags": ["温柔","知性","理性"],
  "common_phrases": ["亲爱的","朋友","其实啊"],
  "reply_style": "长句逻辑型"
}
```

### D04 - A/B 测试用户反馈（有的话是亮点）

| 策略 | 测试会话数 | 用户满意度(满分5) | 下单转化率 |
|------|-----------|-----------------|-----------|
| baseline | 50 | 2.1 | 1% |
| persona | 50 | 3.0 | 3% |
| expel_mvp | 50 | 4.2 | 7% |

### D05 - 成本数据

估算不同模型跑一个会话的成本：
```csv
model,每次对话平均Token数,每Token价格,单次对话成本
qwen-max,500,0.0002元,0.1元
gpt-4,500,0.03元,15元
```

---

## 🔗 报告/PPT 框架建议

```
【第1章】项目背景（2页）
├── 数字人直播行业现状与痛点
│   ├── 直播互动同质化严重
│   ├── 数字人回复生硬/不接茬
│   └── 需要"有人味"的对话系统
└── 本方案目标：让数字人学会"聊天"

【第2章】技术方案（3-4页）
├── 系统架构图（ML风格 → agent→env→LLM 数据流）
├── 用户模拟器工作机制（核心创新）
│   ├── 质量评分 → 状态更新 → 轨迹匹配
│   └── 三种匹配策略（完全匹配→关键词→随机）
├── 规则提取管道
│   └── 对比成功vs失败轨迹 → LLM总结 → 去重计分
└── 评估框架（baseline vs persona vs expel_mvp）

【第3章】实验数据（2-3页）
├── 数据统计
│   ├── 饼图：成功/失败/不安全 占比
│   └── 柱状图：用户开场白分布
├── 对话示例对比
│   ├── 成功案例集锦
│   └── 失败案例集锦
└── 数据质量说明（人工标注验证）

【第4章】评估结果（2-3页）★核心★
├── 三策略对比雷达图/柱状图
│   ├── 平均轮次对比
│   ├── 续聊率对比★（最关键指标）
│   ├── 平均奖励对比
│   └── 安全率对比
├── 关键发现
│   ├── 有人设 vs 无人设：续聊率+XX%
│   ├── 加规则后：续聊率再+XX%
│   └── 安全率稳定在XX%以上
└── 成本/性能权衡

【第5章】结论与展望（1-2页）
├── 核心结论
│   ├── 经验学习框架有效提升对话质量
│   └── 规则注入可解释性强、可迭代
├── 待改进方向
│   ├── 需要更多真实数据
│   ├── 可引入语义向量匹配
│   └── 多轮记忆增强
└── 后续规划

【Appendix】
├── 数据准备清单（D01-D05）
├── 命令速查
└── 代码结构图
```

---

## ⚙️ 全部命令速查

```bash
# === 出图命令（必做）===
python evaluate_livestream.py   # 评估 → logs/livestream/eval_summary.json
python make_charts.py           # 出图 → 5张 PNG（拖进PPT即可用）

# === 测试模拟器 ===
python -c "from envs.livestream.user_simulator import LivestreamUserSimulator as S; u,r,l = S().respond('你好'); print(u,r,l)"

# === 测试环境 ===
python -c "from envs.livestream.livestream import LivestreamChatEnv as E; e=E(); e.reset(); print(e.step('欢迎宝子'))"

# === 完整对话演示 ===
python demo_livestream_conversation.py

# === 训练（需要API Key）===
python train.py benchmark=livestream testing=true run_name=test   # 先跑通测试模式
python train.py benchmark=livestream run_name=exp1                # 实际训练

# === 规则提取 ===
python insight_extraction.py benchmark=livestream load_run_name=exp1 run_name=rules1

# === 评估 ===
python eval.py benchmark=livestream load_run_name=extracted_insights/rules1 run_name=eval1
```
