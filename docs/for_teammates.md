# 📢 给队友的一封信：关于这个项目，你们需要知道的一切

嗨，我是这个数字人直播对话系统的项目负责人。

如果你们要看这个项目写文档和做 PPT，**这篇东西就够了**。我把所有东西按"你们的需要"整理好了。

---

## 🎯 第一步：先跑一下看看效果（5分钟）

```bash
cd ExpeL-agent

# 1. 安装依赖
pip install -r requirements.txt
pip install matplotlib numpy

# 2. 直接跑离线评估（不需要API Key，纯算）
python evaluate_livestream.py

# 3. 出图（所有图表一键生成）
python make_charts.py

# 4. 看结果
# 终端会打印表格
# 数据在 logs/livestream/eval_summary.json
# 图表在 logs/livestream/*.png（共5张）
```

---

## 📊 图在哪里？怎么继续出图？

### 已有的图（不需要你画，代码自动生成）

| 图片 | 在哪 | 怎么得到 |
|------|------|---------|
| **三策略对比柱状图** | `logs/livestream/eval_comparison.png` | 运行 `python make_charts.py` |
| **三策略雷达图** | `logs/livestream/eval_radar.png` | 运行 `python make_charts.py` |
| **数据分布饼图+柱状图** | `logs/livestream/data_distribution.png` | 运行 `python make_charts.py` |
| **成功vs失败续聊率对比** | `logs/livestream/continue_rate_comparison.png` | 运行 `python make_charts.py` |
| **成功vs失败奖励对比** | `logs/livestream/reward_comparison.png` | 运行 `python make_charts.py` |
| **学习曲线图**（训练才会出） | `logs/livestream/expel/*_logs_stats.png` | 运行 `python train.py ...` |

### 如果 matplotlib 没装

```bash
pip install matplotlib numpy
```

装完后所有图自动就能生成了。

### 这些图怎么用

直接拖进 PPT/Word，或者截屏贴报告里。分辨率 150dpi，够清晰。

---

## 📂 项目架构——你们要写文档看这些文件

### 我全部分好类了

```
【报告/PPT素材 → 看 README.md】
├── 数据统计、评分体系、对比结果
├── 对话示例（成功vs失败）
├── PPT 框架建议（每页写什么）
└── 队友数据准备清单（D01-D05）
✅ 这是你们写文档的入口文件

【技术细节/代码流程图 → 看 docs/internal_guide.md】
├── 用户模拟器怎么工作（流程图）
├── 评分机制怎么打分（代码+权重）
├── 匹配策略三级降级
├── 调优参数表（改什么参数影响什么）
└── FAQ（常见报错怎么解决）
✅ 这是你们写"技术方案"章节的素材

【关键代码文件】
├── envs/livestream/user_simulator.py  ← 用户模拟器（核心新模块）
├── envs/livestream/livestream.py      ← 直播对话环境
├── evaluate_livestream.py             ← 离线评估（出数据+出图）
├── generate_report_charts.py          ← 报告图表生成
├── demo_livestream_conversation.py    ← 对话演示
├── generate_livestream_data.py        ← 数据增强生成
├── agent/expel.py                     ← 核心算法逻辑
└── prompts/livestream.py              ← 提示词模板

【数据文件】
├── data/livestream/trajectories.jsonl  ← 110+条对话轨迹 ★
├── data/livestream/rules.jsonl         ← 10条提取规则
├── data/livestream/safety_rules.jsonl  ← 10条安全规则
├── data/livestream/creator_profile.json← 主播人设
└── data/livestream/tasks.json          ← 训练任务
```

### 如果时间紧，按优先级看

```
1. README.md（必看）← 报告/PPT 素材全在这
2. docs/internal_guide.md（建议看）← 技术方案素材
3. data/livestream/trajectories.jsonl（扫一眼）← 感受数据长什么样
4. 跑一次 python evaluate_livestream.py（必做）← 出图
5. 跑一次 python demo_livestream_conversation.py（建议）← 看对话效果
```

---

## 📋 如果需要更多数据/更多图

### 情况1：想要更多的对话数据

```bash
# 运行数据增强脚本
python generate_livestream_data.py

# 它会生成新的轨迹，追加到 data/livestream/trajectories.jsonl
# 然后再跑评估就能看到新数据的结果
```

### 情况2：想要更漂亮的图

改 `generate_report_charts.py` 里的画图代码，或者直接跟我（项目负责人）说，我来加。

### 情况3：想要真实数据的对比

把真实直播日志按格式整理好（具体格式见 README.md 的 D01 部分），放到 `data/real_livestream/` 目录下，我改代码加载它。

### 情况4：想要不同人设的效果对比

准备多个人设 JSON（格式见 README.md 的 D03 部分），我改环境代码适配。

### 情况5：想知道某个技术细节

```bash
# 测试用户模拟器怎么工作的
python -c "from envs.livestream.user_simulator import LivestreamUserSimulator; u,r,l = LivestreamUserSimulator().respond('欢迎宝子来直播间'); print(f'用户回复: {u}  评分: {r}  离开: {l}')"

# 测试完整对话
python demo_livestream_conversation.py

# 查看所有可运行的脚本
ls *.py
```

---

## ⚠️ 常见踩坑提醒

### 报错 "openai_api_key" 或 "QWEN_API_KEY" 相关

```
原因：train.py 需要 API Key 调 LLM，但我们离线评估不需要
解决：只跑 python evaluate_livestream.py 和 python generate_report_charts.py
     这两个完全不需要 API Key
     
如果非要跑 train.py，在根目录创建 .env 文件：
  QWEN_API_KEY=你的密钥
  LLM_MODEL=qwen-plus
```

### 报错 "module not found"

```bash
pip install -r requirements.txt
# 如果还缺，单独装
pip install matplotlib numpy hydra-core
```

### 报错 matplotlib 相关

```bash
pip install matplotlib numpy pillow
```

### 不知道怎么改代码

先看 `docs/internal_guide.md` 的 "常见开发任务" 章节，有我写好的代码示例。如果还搞不定，问我或群里问。

---

## 📞 最后

如果你们写文档/PPT 需要我：
1. **跑特定的数据/图表** → 叫我来跑
2. **解释某个技术细节** → 直接问
3. **需要我配合补数据** → 把数据发我，我来合并
4. **文档写完了让我 review** → 叫我

祝报告顺利！🎉

---

_此文档在项目中：README.md（报告素材） + docs/internal_guide.md（技术细节）_
