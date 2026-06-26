#!/usr/bin/env python3
"""
📊 一键生成报告图表
直接在本地跑：python make_charts.py
出图在 logs/livestream/ 下，可以直接拖进PPT
"""
import json, os, sys
from pathlib import Path

LOG_DIR = Path("logs/livestream")
LOG_DIR.mkdir(parents=True, exist_ok=True)

def main():
    # ---- 读数据 ----
    eval_path = LOG_DIR / "eval_summary.json"
    if not eval_path.exists():
        print(f"❌ 没找到 {eval_path}")
        print(f"   先跑: python evaluate_livestream.py")
        sys.exit(1)

    with open(eval_path) as f:
        data = json.load(f)

    print("=" * 55)
    print("  📊 数字人直播对话系统 — 图表生成")
    print("=" * 55)

    # ---- 尝试导入绘图库 ----
    try:
        import matplotlib
        matplotlib.use('Agg')
        import matplotlib.pyplot as plt
        import numpy as np
    except ImportError:
        print("\n  ❌ 需要安装 matplotlib 和 numpy")
        print("     运行: pip install matplotlib numpy")
        sys.exit(1)

    all_data = data.get("all", {})
    success_data = data.get("success", {})
    failure_data = data.get("failure", {})
    
    strategies = ["baseline", "persona", "expel_mvp"]
    colors = ["#e74c3c", "#f39c12", "#2ecc71"]
    labels_map = {"baseline": "冷回复底线", "persona": "仅人设", "expel_mvp": "完整方案"}

    # =========================================================
    # 图1：四维柱状对比图
    # =========================================================
    metrics_info = [
        ("avg_turns",     "平均对话轮次\n(higher better)", 1),
        ("continue_rate",  "续聊率\n(higher better)",       100),
        ("avg_reward",     "平均奖励分\n(higher better)",   1),
        ("safety_rate",    "安全处理率\n(higher better)",   100),
    ]

    fig, axes = plt.subplots(1, 4, figsize=(16, 5))
    fig.suptitle("数字人直播对话系统 — 三策略对比评估 (ALL)", 
                 fontsize=16, fontweight="bold", y=1.02)

    for idx, (ax, (mkey, mlabel, sf)) in enumerate(zip(axes, metrics_info)):
        vals = [all_data[s].get(mkey, 0) for s in strategies]
        vals_display = [v * sf for v in vals]
        bars = ax.bar([labels_map[s] for s in strategies], vals_display, 
                      color=colors, width=0.5, edgecolor="white")
        for bar, vd in zip(bars, vals_display):
            ax.text(bar.get_x() + bar.get_width()/2, 
                    bar.get_height() + max(vals_display)*0.02,
                    f"{vd:.1f}{'%' if sf==100 else ''}",
                    ha="center", va="bottom", fontsize=9, fontweight="bold")
        ax.set_title(mlabel, fontsize=11)
        ax.set_ylim(0, max(vals_display)*1.3)
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        ax.tick_params(axis="x", labelsize=8)

    plt.tight_layout()
    out1 = LOG_DIR / "eval_comparison.png"
    plt.savefig(out1, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"  ✅ {out1.name}")

    # =========================================================
    # 图2：雷达图
    # =========================================================
    angles = np.linspace(0, 2*np.pi, 4, endpoint=False).tolist()
    angles += angles[:1]
    radar_labels = ["平均轮次", "续聊率", "平均奖励", "安全率"]

    fig, ax = plt.subplots(figsize=(7, 7), subplot_kw={"polar": True})
    fig.suptitle("数字人直播对话系统 — 三策略雷达对比 (ALL)", 
                 fontsize=14, fontweight="bold", y=1.05)

    max_vals = [max(all_data[s]["avg_turns"] for s in strategies),
                max(all_data[s]["continue_rate"]*100 for s in strategies),
                max(all_data[s]["avg_reward"] for s in strategies),
                max(all_data[s]["safety_rate"]*100 for s in strategies)]
    max_vals = [max(v, 0.01) for v in max_vals]

    for s, c in zip(strategies, colors):
        raw = [all_data[s]["avg_turns"], all_data[s]["continue_rate"]*100,
               all_data[s]["avg_reward"], all_data[s]["safety_rate"]*100]
        norm = [raw[i]/max_vals[i] for i in range(4)]
        norm_closed = norm + norm[:1]
        ax.plot(angles, norm_closed, color=c, linewidth=2, label=labels_map[s])
        ax.fill(angles, norm_closed, color=c, alpha=0.1)

    ax.set_xticks(angles[:4])
    ax.set_xticklabels(radar_labels, fontsize=11)
    ax.legend(loc="upper right", bbox_to_anchor=(1.3, 1.1))
    ax.set_ylim(0, 1.1)
    plt.tight_layout()
    out2 = LOG_DIR / "eval_radar.png"
    plt.savefig(out2, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"  ✅ {out2.name}")

    # =========================================================
    # 图3：数据分布（饼图+柱状图）
    # =========================================================
    from collections import defaultdict
    records = []
    traj_path = "data/livestream/trajectories.jsonl"
    if os.path.exists(traj_path):
        with open(traj_path, encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    records.append(json.loads(line))

    label_counts = {"success": 0, "failure": 0, "unsafe": 0}
    for r in records:
        lbl = r.get("label", "unknown")
        label_counts[lbl] = label_counts.get(lbl, 0) + 1

    sessions = defaultdict(list)
    for r in records:
        sessions[r["session_id"]].append(r)

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 4.5))
    fig.suptitle("数字人直播对话系统 — 数据统计概览", fontsize=14, 
                 fontweight="bold", y=1.03)

    lbls = list(label_counts.keys())
    vals = list(label_counts.values())
    pie_colors = ["#2ecc71", "#e74c3c", "#f39c12"]
    wedges, texts, autotexts = ax1.pie(
        vals, labels=lbls, autopct="%1.1f%%", 
        colors=pie_colors[:len(lbls)], startangle=90,
        wedgeprops={"edgecolor": "white", "linewidth": 1.5})
    ax1.set_title(f"对话轨迹分类 (共{len(sessions)}段会话, {len(records)}轮次)")

    bars = ax2.bar(lbls, vals, color=pie_colors[:len(lbls)], 
                   edgecolor="white", width=0.5)
    for bar, val in zip(bars, vals):
        ax2.text(bar.get_x()+bar.get_width()/2, bar.get_height()+1,
                 str(val), ha="center", fontsize=10, fontweight="bold")
    ax2.set_title("各类别轨迹数量")
    ax2.spines["top"].set_visible(False)
    ax2.spines["right"].set_visible(False)

    plt.tight_layout()
    out3 = LOG_DIR / "data_distribution.png"
    plt.savefig(out3, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"  ✅ {out3.name}")

    # =========================================================
    # 图4：成功会话vs失败会话的续聊率对比
    # =========================================================
    if success_data and failure_data:
        fig, ax = plt.subplots(figsize=(8, 5))
        x = np.arange(len(strategies))
        width = 0.35

        success_vals = [success_data[s].get("continue_rate", 0)*100 for s in strategies]
        failure_vals = [failure_data[s].get("continue_rate", 0)*100 for s in strategies]

        bars1 = ax.bar(x - width/2, success_vals, width, label="成功会话", color="#2ecc71", edgecolor="white")
        bars2 = ax.bar(x + width/2, failure_vals, width, label="失败会话", color="#e74c3c", edgecolor="white")

        for bar in bars1:
            ax.text(bar.get_x()+bar.get_width()/2, bar.get_height()+1,
                    f"{bar.get_height():.1f}%", ha="center", fontsize=8, fontweight="bold")
        for bar in bars2:
            ax.text(bar.get_x()+bar.get_width()/2, bar.get_height()+1,
                    f"{bar.get_height():.1f}%", ha="center", fontsize=8, fontweight="bold")

        ax.set_xticks(x)
        ax.set_xticklabels([labels_map[s] for s in strategies])
        ax.set_ylabel("续聊率 (%)")
        ax.set_title("成功会话 vs 失败会话 — 续聊率对比")
        ax.legend()
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        ax.set_ylim(0, max(max(success_vals), max(failure_vals))*1.3)

        plt.tight_layout()
        out4 = LOG_DIR / "continue_rate_comparison.png"
        plt.savefig(out4, dpi=150, bbox_inches="tight")
        plt.close()
        print(f"  ✅ {out4.name}")

    # =========================================================
    # 图5：平均奖励对比（成功 vs 失败）
    # =========================================================
    if success_data and failure_data:
        fig, ax = plt.subplots(figsize=(8, 5))
        success_r = [success_data[s].get("avg_reward", 0) for s in strategies]
        failure_r = [failure_data[s].get("avg_reward", 0) for s in strategies]

        bars1 = ax.bar(x - width/2, success_r, width, label="成功会话", color="#2ecc71", edgecolor="white")
        bars2 = ax.bar(x + width/2, failure_r, width, label="失败会话", color="#e74c3c", edgecolor="white")

        for bar in bars1:
            ax.text(bar.get_x()+bar.get_width()/2, bar.get_height()+0.02,
                    f"{bar.get_height():.2f}", ha="center", fontsize=8, fontweight="bold")
        for bar in bars2:
            ax.text(bar.get_x()+bar.get_width()/2, bar.get_height()+0.02,
                    f"{bar.get_height():.2f}", ha="center", fontsize=8, fontweight="bold")

        ax.set_xticks(x)
        ax.set_xticklabels([labels_map[s] for s in strategies])
        ax.set_ylabel("平均奖励分")
        ax.set_title("成功会话 vs 失败会话 — 平均奖励对比")
        ax.legend()
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        ax.axhline(y=0, color="gray", linestyle="--", linewidth=0.5)

        plt.tight_layout()
        out5 = LOG_DIR / "reward_comparison.png"
        plt.savefig(out5, dpi=150, bbox_inches="tight")
        plt.close()
        print(f"  ✅ {out5.name}")

    # ---- 完成 ----
    print(f"\n  📂 全部图表在: {LOG_DIR.resolve()}/")
    print("=" * 55)
    print("  直接拖进 PPT / Word 即可使用")
    print("=" * 55)


if __name__ == "__main__":
    main()
