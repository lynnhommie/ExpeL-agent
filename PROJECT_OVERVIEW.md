# ExpeL MVP 直播 AI 分身项目 - 完整改造清单 & 快速理解指南

---

# 一、本项目是什么

## 核心定义
这是一个**基于 ExpeL 框架的直播 AI 分身文本陪伴系统 MVP**。

通俗说法：
> 用一个 AI Agent 来模拟直播主播，通过学习历史对话经验，让它越来越会聊天、越来越能留住用户。

## 为什么改造 ExpeL？

ExpeL 原本是用来做：
- 问答任务（HotpotQA）
- 游戏文本冒险（ALFWorld）
- 电商搜索购物（WebShop）
- 事实核查（FEVER）

这些都是"完成一个离散任务"的场景。

我们现在要改造它，让它适应：
- **直播文本对话场景**
- **不是"完成任务"，而是"保持对话"**
- **优化指标是"轮次""留存""用户继续率"，不是"任务成功率"**

## ExpeL 的核心价值是什么？

ExpeL 最核心的三步闭环：

```
经验收集 → 经验提炼 → 经验复用
```

也就是：

1. **收集轨迹**：记录历次对话
2. **提炼规则**：从成功对话中总结规律
3. **检索增强**：新对话时查历史，用过往经验来指导

这个流程对直播场景特别适合，因为：
- 每个主播都有独特的风格和话术
- 历史对话中总有一些"最有效的回复"
- 这些回复可以重复使用

---

# 二、改造清单（STEP1-3 完整内容）

## STEP 1：搭建直播对话环境

### 新增文件
- `envs/livestream/livestream.py`

### 改造内容
把原来的"任务环境"（返回成功/失败）改成"对话环境"（返回用户是否继续）。

#### 环境做什么
```
用户输入 → 环境接收 → 计算 reward（是否继续聊、是否安全等）
                  ↓
            返回观察 + 奖励 + 是否结束
```

#### 关键方法
- `reset()`：初始化一个新会话
- `step(user_input)`：处理一条用户消息
- `success_fn()`：判断是否成功（对话继续且无违规）
- `_score_reply()`：根据内容给 reward

#### 简单 Reward 规则
- 用户继续说话：`+1`
- 包含引导词（"想听""聊聊"）：`+1`
- 触发安全规则：`-5`

---

## STEP 2：配置直播 Prompt 和人设

### 新增文件
- `prompts/livestream.py`
- `prompts/livestream_utils.py`
- `data/livestream/creator_profile.json`
- `data/livestream/tasks.json`
- `configs/benchmark/livestream.yaml`

### 改造内容

#### A. 直播场景 Prompt（livestream.py）

**System Instruction**
```
你是直播 AI 主持人。
目标：
1. 保持对话自然友好
2. 体现主播个性
3. 鼓励用户继续对话
4. 避免不安全内容
```

**Human Instruction**
```
你在直播间陪聊。
目标：
1. 角色一致
2. 用户参与
3. 简短自然
4. 低门槛追问
5. 拒绝不安全内容
```

**Few-shot 示例**
```
User: hi
Assistant: 欢迎宝子来直播间，今天想聊点什么呀？

User: 你今天怎么这么晚
Assistant: 来啦来啦，今天稍微忙了一点，但我还是想快点来陪大家聊天～你今天过得怎么样？

User: 你推荐点什么
Assistant: 可以呀宝子，你更想看轻松一点的内容，还是更实用一点的分享？
```

#### B. 工具函数（livestream_utils.py）

6 个必要的工具函数：

1. **`LIVESTREAM_LLM_PARSER`**
   - 功能：解析模型输出
   - 输入：原始文本
   - 输出：ChatMessage + 消息类型 + 动作

2. **`LIVESTREAM_OBSERVATION_FORMATTER`**
   - 功能：格式化环境反馈
   - 例：`Observation: 用户继续停留，等待下一句回复`

3. **`LIVESTREAM_STEP_IDENTIFIER`**
   - 功能：识别步骤类型（action/observation）

4. **`LIVESTREAM_CYCLER`**
   - 功能：循环处理历史记录

5. **`LIVESTREAM_REFLECTION_PREFIX`**
   - 功能：格式化反思内容

6. **`LIVESTREAM_STEP_STRIPPER`**
   - 功能：清理步骤文本

#### C. 配置文件

**`configs/benchmark/livestream.yaml`**
```yaml
name: livestream
task_prefix: "User: "
task_file: data/livestream/tasks.json
max_steps: 8           # 最多对话轮次
num_fewshots: 3
ai_name: livestream host
```

**`data/livestream/tasks.json`**
```json
[
  {
    "task": "新用户刚进入直播间，先欢迎并引导聊天",
    "env_kwargs": {"creator_name": "主播A"},
    "env_name": "livestream"
  },
  ...
]
```

---

## STEP 3：接入主流程

### 改造文件

#### A. `envs/__init__.py`
添加 livestream 到环境注册：
```python
from .livestream.livestream import LivestreamChatEnv

INIT_TASKS_FN['livestream'] = lambda cfg: [...]
ENVS['livestream'] = LivestreamChatEnv
```

#### B. `prompts/__init__.py`
注册所有直播相关的 prompt：
```python
from . import livestream

FEWSHOTS['livestream'] = livestream.LIVESTREAM_FEWSHOTS
LLM_PARSER['livestream'] = livestream.LIVESTREAM_LLM_PARSER
OBSERVATION_FORMATTER['livestream'] = livestream.LIVESTREAM_OBSERVATION_FORMATTER
STEP_IDENTIFIER['livestream'] = livestream.LIVESTREAM_STEP_IDENTIFIER
...
```

#### C. `train.py`
改主程序的条件判断，让它自动选择直播配置：
```python
if cfg.benchmark.name == 'livestream':
    system_instruction = livestream.LIVESTREAM_SYSTEM_INSTRUCTION
    human_instruction = livestream.LIVESTREAM_HUMAN_INSTRUCTION
    fewshots = livestream.LIVESTREAM_FEWSHOTS
    ...
else:
    # 原有逻辑
```

---

# 三、改造涉及的所有文件列表

## 新增文件（9 个）

```
envs/livestream/
  └── livestream.py                    ✓ 直播环境实现

prompts/
  ├── livestream.py                    ✓ 直播 prompt 定义
  └── livestream_utils.py              ✓ 直播工具函数

configs/benchmark/
  └── livestream.yaml                  ✓ 直播 benchmark 配置

data/livestream/
  ├── tasks.json                       ✓ 演示任务集
  ├── README_livestream_data_spec.md   ✓ 数据收集规范

文档
  ├── STEP3_SUMMARY.md                 ✓ 步骤总结
  ├── test_livestream_setup.py         ✓ 验证脚本
```

## 修改文件（3 个）

```
envs/__init__.py                       ✓ 注册 livestream 环境
prompts/__init__.py                    ✓ 注册 livestream prompt
train.py                               ✓ 适配 livestream 逻辑
```

---

# 四、快速理解指南

如果你只有 10 分钟，按这个顺序理解：

## 第一步（2 分钟）：理解概念
- ExpeL 的三步：收集 → 提炼 → 复用
- 直播场景的目标：保持用户聊天（不是完成任务）
- 奖励信号：轮次、继续率、安全性

## 第二步（3 分钟）：看环境代码
打开 `envs/livestream/livestream.py`

关键看这 3 个方法：
```python
def reset(self)                    # 初始化
def step(self, action)             # 处理用户输入
def success_fn(self)               # 判断成功
```

这就是"直播对话环境"的全部逻辑。

## 第三步（3 分钟）：看 Prompt
打开 `prompts/livestream.py`

只需看：
- `LIVESTREAM_SYSTEM_INSTRUCTION` - agent 的角色定义
- `LIVESTREAM_FEWSHOTS` - 3 个例子
- `LIVESTREAM_SYSTEM_CRITIQUE_INSTRUCTIONS` - 怎么从对话中提规则

## 第四步（2 分钟）：看主流程
打开 `train.py`，找这句：
```python
if cfg.benchmark.name == 'livestream':
```

看看它是怎么根据 benchmark 选择不同的配置的。

---

# 五、项目现在的完整架构

```
┌─────────────────────────────────────────────────────────────────┐
│                          主入口 train.py                         │
│                    (支持 benchmark=livestream)                  │
└──────────────┬──────────────────────────────────────────────────┘
               │
        ┌──────┴──────┐
        ↓             ↓
  ┌──────────────┐  ┌─────────────────────┐
  │   Agent      │  │   Livestream Env    │
  │   (ExpelAgent│  │   (LivestreamChatEnv│
  │    ReactAgent│  │    + LiveEnv)       │
  │    etc)      │  │                     │
  └──────┬───────┘  └─────────┬───────────┘
         │                    │
         └────────┬───────────┘
                  ↓
         ┌─────────────────────┐
         │  Prompt System      │
         ├─────────────────────┤
         │ System Instruction  │
         │ Human Instruction   │
         │ Few-shots           │
         │ LLM Parser          │
         │ Observation Format  │
         │ Step Identifier     │
         └─────────────────────┘
                  ↓
         ┌─────────────────────┐
         │  Data Layer         │
         ├─────────────────────┤
         │ tasks.json          │
         │ creator_profile     │
         │ trajectories        │
         │ rules               │
         │ safety_rules        │
         └─────────────────────┘
```

---

# 六、数据流走向

### 一轮对话完整流程

```
1. Agent 准备 prompt
   ├─ System instruction（直播角色）
   ├─ Few-shots（示例对话）
   ├─ Task prompt（当前任务，如"新用户进入"）
   └─ History（之前的对话记录）

2. LLM 生成回复
   └─ "欢迎宝子来直播间，今天想聊什么呀？"

3. LLM Parser 解析
   └─ 提取出动作："欢迎宝子..."

4. Environment 处理
   ├─ 检查内容安全
   ├─ 计算 reward（+1 欢迎词，+1 追问等）
   └─ 返回观察："用户继续停留"

5. Observation Formatter 格式化
   └─ "Observation: 用户继续停留，等待下一句"

6. 轨迹记录
   └─ 保存到 logs/ 和内存

7. 重复 1-6，直到轮次达到上限或用户流失
```

---

# 七、核心改造的三个思路

## 思路 1：环境是对话模拟器，不是任务完成器

**原来的 ExpeL**
```
Task: "Find the answer to: Who is X?"
Environment: 执行 Search 动作 → 返回搜索结果
Success: 找到正确答案时 True
```

**现在的直播**
```
Task: "新用户进入，保持对话"
Environment: 执行 Reply 动作 → 用户是否继续说话
Success: 用户说了多轮 + 没违规 → True
```

## 思路 2：Reward 来自对话行为，不是任务完成度

**原来的 ExpeL**
```
Reward = 1 if 任务成功 else 0
```

**现在的直播**
```
Reward = +1(用户继续) + 1(包含互动词) - 5(违规) ...
```

## 思路 3：规则提炼的对象是"什么对话更能留人"

**原来的 ExpeL**
```
规则例：
- 当需要数学计算时，先查表再做运算
- 当概念不清时，先定义后应用
```

**现在的直播**
```
规则例：
- 用户首次进入时，先欢迎再问问题
- 用户沉默时，用开放问题，不要硬推
- 用户提价格时，先给结论再补卖点
```

---

# 八、为什么要这样改造？

### 问题 1：为什么不直接微调模型？
**原因**：
- 微调成本高
- 更新慢（每次要重训）
- 新策略不好快速迭代
- 难以人工审查和修正

**我们的方案优势**：
- 经验可复用（相似对话直接查历史）
- 规则可解释（能看到"为什么生效"）
- 快速迭代（改规则不用重训）
- 人工可干预（不信任的规则可删除）

### 问题 2：为什么要记录轨迹？
**原因**：
- 可以看到什么对话方式有效
- 可以统计成功率和失败原因
- 可以做 A/B 对比
- 可以自动生成新规则

### 问题 3：为什么要提炼规则？
**原因**：
- 模型不一定每次都最优
- 规则可以指导模型往正确方向走
- 规则是可解释的，可以人工审查
- 规则可以快速扩展到其他主播

---

# 九、现在能做什么

## 立即能运行的命令

```bash
# 测试模式（不需要真实 API）
python train.py benchmark=livestream testing=true run_name=test

# 正式模式（需要配置 LLM_MODEL 和 API_KEY）
python train.py benchmark=livestream run_name=my_experiment
```

## 立即能查看的结果

运行后会输出：
- 每轮对话的 prompt + 回复
- 每轮的 reward
- 会话的成功/失败
- 最后的统计数据

输出位置：`logs/livestream/expel/my_experiment_logs/`

---

# 十、下一步是什么？

## STEP 4：生成模拟数据
写脚本自动生成 100+ 条模拟对话，验证系统能否工作。

## STEP 5：做评估对比
比较：
- 无 prompt 版本（随机回复）
- 有人设 prompt 版本
- 有经验检索版本

看哪个版本对话轮次更长。

## STEP 6：提炼规则
从成功的对话中自动提取规则，用于指导后续对话。

## STEP 7：安全加固
加强违规内容检测和过滤。

---

# 十一、技术栈概览

```
输入层
  ↓
Agent (ExpelAgent)
  ├─ System Prompt
  ├─ Human Prompt
  ├─ Few-shots
  └─ History
  ↓
LLM (Qwen / GPT)
  ↓
输出层
  ├─ LLM Parser
  ├─ Safety Filter
  └─ Format Output
  ↓
Environment (LivestreamChatEnv)
  ├─ Reward 计算
  ├─ 安全检查
  └─ 状态转移
  ↓
数据层
  ├─ 轨迹记录
  ├─ 规则提炼
  └─ 经验检索
```

---

# 十二、如果你要改动代码，最常见的改法

## 改 Prompt
编辑 `prompts/livestream.py` 的 `LIVESTREAM_SYSTEM_INSTRUCTION` 或 `LIVESTREAM_FEWSHOTS`

## 改 Reward 规则
编辑 `envs/livestream/livestream.py` 的 `_score_reply()` 方法

## 改任务列表
编辑 `data/livestream/tasks.json`

## 改最大轮次
编辑 `configs/benchmark/livestream.yaml` 的 `max_steps`

## 改模型
在 `.env` 里设置 `LLM_MODEL=qwen-max` 或其他模型

---

# 十三、最重要的文件速查表

| 文件 | 作用 | 何时改 |
|------|------|--------|
| `envs/livestream/livestream.py` | 定义对话环境 | 改对话规则、安全策略 |
| `prompts/livestream.py` | 定义 prompt | 改 agent 的说话风格 |
| `configs/benchmark/livestream.yaml` | 配置参数 | 改超参数 |
| `data/livestream/tasks.json` | 定义任务 | 加新任务 |
| `train.py` | 主程序 | 改流程逻辑 |

---

# 十四、常见问题速答

### Q：为什么叫"ExpeL"？
A：Experience Learning，体验式学习。核心思想是通过积累经验来学习。

### Q：直播环境和其他环境有什么区别？
A：
- HotpotQA：找信息（有明确答案）
- WebShop：买商品（有明确目标）
- Livestream：**保持聊天**（目标是"继续对话"）

### Q：为什么要记录轨迹？
A：后面要从轨迹中学到规则，规则用来指导新对话。

### Q：Reward 是怎么算的？
A：简单规则：继续聊 +1，好词 +1，违规 -5。

### Q：能不能不用 ExpeL，直接用 LLM？
A：可以，但你就失去了"学习和改进"的能力。ExpeL 的价值就在于能从经验中自动提升。

---

# 十五：一页纸总结

## 项目是什么
**用 ExpeL 框架改造出一个直播 AI 分身，让它通过学习历史对话来改进表现。**

## 怎么改造的
- Step 1：改环境（从"完成任务"改成"保持对话"）
- Step 2：改 prompt（加入直播风格和人设）
- Step 3：改主程序（让系统支持 `benchmark=livestream`）

## 现在能做什么
- 直播 agent 能生成对话
- 环境能模拟用户反应
- 系统能记录轨迹和 reward
- 后续能从轨迹提炼规则

## 下一步
- 生成模拟数据或收集真实数据
- 提炼规则
- 评估效果提升

## 核心价值
不用微调模型，通过记录经验+提炼规则+检索增强，让 AI 越来越会聊天。

