"""强制安装 matplotlib 后端并生成图表"""
import subprocess, sys, os

os.chdir(os.path.dirname(os.path.abspath(__file__)))

# 安装
subprocess.check_call([sys.executable, "-m", "pip", "install", "matplotlib", "numpy", "-q"])

# 测试 matplotlib
import matplotlib
matplotlib.use('Agg')  # 强制非交互后端
import matplotlib.pyplot as plt
import numpy as np
import json
from pathlib import Path

LOG_DIR = Path("logs/livestream")
LOG_DIR.mkdir(parents=True, exist_ok=True)

# 读取结果
with open(LOG_DIR / "eval_summary.json") as f:
    data = json.load(f)["all"]

strategies = ["baseline", "persona", "expel_mvp"]
colors = ["#e74c3c", "#f39c12", "#2ecc71"]

# 生成柱状图
metrics_info = [
    ("avg_turns", "平均对话轮次", 1),
    ("continue_rate", "续聊率(%)", 100),
    ("avg_reward", "平均奖励分", 1),
    ("safety_rate", "安全处理率(%)", 100),
]

fig, axes = plt.subplots(1, 4, figsize=(16, 5))
fig.suptitle("数字人直播对话系统 — 三策略对比评估", fontsize=16, fontweight="bold", y=1.02)

for idx, (ax, (mkey, mlabel, sf)) in enumerate(zip(axes, metrics_info)):
    vals = [data[s].get(mkey, 0) for s in strategies]
    vals_display = [v * sf for v in vals]
    bars = ax.bar(strategies, vals_display, color=colors, width=0.5, edgecolor="white")
    for bar, vd in zip(bars, vals_display):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + max(vals_display)*0.02,
                f"{vd:.1f}{'%' if sf==100 else ''}", ha='center', va='bottom',
                fontsize=9, fontweight='bold')
    ax.set_title(mlabel, fontsize=11)
    ax.set_ylim(0, max(vals_display) * 1.25)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

plt.tight_layout()
plt.savefig(str(LOG_DIR / "eval_comparison.png"), dpi=150, bbox_inches="tight")
print(f"✅ eval_comparison.png 生成 ({os.path.getsize(LOG_DIR / 'eval_comparison.png')/1024:.0f} KB)")
plt.close()

# 生成雷达图
angles = np.linspace(0, 2*np.pi, 4, endpoint=False).tolist()
angles += angles[:1]
labels = ["平均轮次", "续聊率", "平均奖励", "安全率"]

fig, ax = plt.subplots(figsize=(7, 7), subplot_kw={"polar": True})
for s, c in zip(strategies, colors):
    raw = [data[s].get("avg_turns", 0), data[s].get("continue_rate", 0)*100,
           data[s].get("avg_reward", 0), data[s].get("safety_rate", 0)*100]
    # 归一化到 0-1
    max_vals = [max(data[ss].get("avg_turns", 0) for ss in strategies),
                max(data[ss].get("continue_rate", 0)*100 for ss in strategies),
                max(data[ss].get("avg_reward", 0) for ss in strategies),
                max(data[ss].get("safety_rate", 0)*100 for ss in strategies)]
    max_vals = [max(v, 0.01) for v in max_vals]
    norm = [raw[i] / max_vals[i] for i in range(4)]
    norm_closed = norm + norm[:1]
    ax.plot(angles, norm_closed, color=c, linewidth=2, label=s)
    ax.fill(angles, norm_closed, color=c, alpha=0.1)

ax.set_xticks(angles[:-1])
ax.set_xticklabels(labels, fontsize=11)
ax.legend(loc="upper right", bbox_to_anchor=(1.3, 1.1))
ax.set_ylim(0, 1.1)
fig.suptitle("数字人直播对话系统 — 三策略雷达对比", fontsize=14, fontweight="bold", y=1.05)
plt.tight_layout()
plt.savefig(str(LOG_DIR / "eval_radar.png"), dpi=150, bbox_inches="tight")
print(f"✅ eval_radar.png 生成 ({os.path.getsize(LOG_DIR / 'eval_radar.png')/1024:.0f} KB)")
plt.close()

# 生成数据分布图
import json as j2
from collections import defaultdict
records = []
with open("data/livestream/trajectories.jsonl", encoding="utf-8") as f:
    for line in f:
        if line.strip():
            records.append(j2.loads(line))

labels_counts = {"success": 0, "failure": 0, "unsafe": 0}
for r in records:
    lbl = r.get("label", "unknown")
    labels_counts[lbl] = labels_counts.get(lbl, 0) + 1

sessions = defaultdict(list)
for r in records:
    sessions[r["session_id"]].append(r)

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 4.5))
fig.suptitle("数字人直播对话系统 — 数据统计概览", fontsize=14, fontweight="bold", y=1.03)

lbls = list(labels_counts.keys())
vals = list(labels_counts.values())
colors_pie = ["#2ecc71", "#e74c3c", "#f39c12"]
ax1.pie(vals, labels=lbls, autopct="%1.1f%%", colors=colors_pie[:len(lbls)],
        startangle=90, wedgeprops={"edgecolor": "white", "linewidth": 1.5})
ax1.set_title(f"对话轨迹分类 (共{len(sessions)}段会话, {len(records)}轮次)")

bars = ax2.bar(lbls, vals, color=colors_pie[:len(lbls)], edgecolor="white", width=0.5)
for bar, val in zip(bars, vals):
    ax2.text(bar.get_x()+bar.get_width()/2, bar.get_height()+1, str(val),
             ha="center", fontsize=10, fontweight="bold")
ax2.set_title("各类别轨迹数量")
ax2.spines["top"].set_visible(False)
ax2.spines["right"].set_visible(False)

plt.tight_layout()
plt.savefig(str(LOG_DIR / "data_distribution.png"), dpi=150, bbox_inches="tight")
print(f"✅ data_distribution.png 生成 ({os.path.getsize(LOG_DIR / 'data_distribution.png')/1024:.0f} KB)")
plt.close()

print("\n✅ 所有图表生成完毕!")
