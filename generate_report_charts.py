#!/usr/bin/env python3
"""
📊 数字人直播对话系统 — 报告图表生成脚本

运行方式：
  python generate_report_charts.py

输出（在 logs/livestream/ 下）：
  eval_comparison.png  — 三策略对比柱状图（可直接放到PPT）
  eval_radar.png       — 三策略雷达图
  data_distribution.png— 数据分布概览（饼图+柱状图）
"""
import json
from pathlib import Path

DATA_DIR = Path("data/livestream")
LOG_DIR = Path("logs/livestream")
LOG_DIR.mkdir(parents=True, exist_ok=True)


def load_jsonl(path):
    with open(path, encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


def load_trajectories():
    """加载轨迹数据并做基础统计"""
    records = load_jsonl(DATA_DIR / "trajectories.jsonl")
    labels = {"success": 0, "failure": 0, "unsafe": 0}
    turn_counts = {"success": [], "failure": [], "unsafe": []}
    for r in records:
        lbl = r.get("label", "unknown")
        labels[lbl] = labels.get(lbl, 0) + 1
        turn_counts[lbl].append(turn_counts[lbl][-1] + 1 if turn_counts[lbl] else 1)
    # 按 session 统计
    from collections import defaultdict
    sessions = defaultdict(list)
    for r in records:
        sessions[r["session_id"]].append(r)
    session_turns = {s: len(t) for s, t in sessions.items()}
    avg_turns = sum(session_turns.values()) / max(len(session_turns), 1)
    return {
        "records": records,
        "label_counts": labels,
        "avg_turns": round(avg_turns, 2),
        "session_count": len(sessions),
        "total_turns": len(records),
    }


def load_eval_results():
    """加载评估结果"""
    path = LOG_DIR / "eval_summary.json"
    if path.exists():
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    return None


def plot_data_distribution(traj_stats, output_path):
    """饼图：数据分布；柱状图：session 轮次"""
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except ImportError:
        print("  [跳过] 请安装 matplotlib: pip install matplotlib")
        return False

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 4.5))
    fig.suptitle("数字人直播对话系统 — 数据统计概览", fontsize=14, fontweight="bold", y=1.03)

    # --- 饼图 ---
    labels_counts = traj_stats["label_counts"]
    lbls = list(labels_counts.keys())
    vals = list(labels_counts.values())
    colors_pie = ["#2ecc71", "#e74c3c", "#f39c12"]
    wedges, texts, autotexts = ax1.pie(
        vals, labels=lbls, autopct="%1.1f%%",
        colors=colors_pie[:len(lbls)], startangle=90,
        wedgeprops={"edgecolor": "white", "linewidth": 1.5}
    )
    ax1.set_title(f"对话轨迹分类 (共{traj_stats['session_count']}段会话, {traj_stats['total_turns']}轮次)")

    # --- 柱状图 ---
    bar_names = lbls
    bar_vals = vals
    bars = ax2.bar(bar_names, bar_vals, color=colors_pie[:len(bar_names)],
                   edgecolor="white", width=0.5)
    for bar, val in zip(bars, bar_vals):
        ax2.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 1,
                 str(val), ha="center", fontsize=10, fontweight="bold")
    ax2.set_title("各类别轨迹数量")
    ax2.spines["top"].set_visible(False)
    ax2.spines["right"].set_visible(False)

    plt.tight_layout()
    plt.savefig(str(output_path), dpi=150, bbox_inches="tight")
    plt.close()
    print(f"  📊 {output_path}")
    return True


def plot_comparison_bar(eval_data, output_path):
    """柱状图：三策略四维对比"""
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        import numpy as np
    except ImportError:
        print("  [跳过] 请安装 matplotlib: pip install matplotlib")
        return False

    data = eval_data.get("all", {})
    if not data:
        print("  [跳过] eval_summary.json 中没有 'all' 分组数据")
        return False

    strategies = ["baseline", "persona", "expel_mvp"]
    colors = ["#e74c3c", "#f39c12", "#2ecc71"]
    metrics_info = [
        ("avg_turns", "平均对话轮次\n(higher better)", 1),
        ("continue_rate", "续聊率\n(higher better)", 100),
        ("avg_reward", "平均奖励分\n(higher better)", 1),
        ("safety_rate", "安全处理率\n(higher better)", 100),
    ]

    fig, axes = plt.subplots(1, 4, figsize=(16, 5))
    fig.suptitle("数字人直播对话系统 — 三策略对比评估", fontsize=16, fontweight="bold", y=1.02)

    for idx, (ax, (mkey, mlabel, sf)) in enumerate(zip(axes, metrics_info)):
        vals = [data[s].get(mkey, 0) for s in strategies]
        vals_display = [v * sf for v in vals]

        bars = ax.bar(strategies, vals_display, color=colors, width=0.5, edgecolor="white")
        for bar, val_disp, val_raw in zip(bars, vals_display, vals):
            label = f"{val_disp:.1f}{'%' if sf == 100 else ''}"
            ax.text(bar.get_x() + bar.get_width() / 2,
                    bar.get_height() + max(vals_display) * 0.02,
                    label, ha="center", va="bottom", fontsize=9, fontweight="bold")

        ax.set_title(mlabel, fontsize=11)
        ax.set_ylim(0, max(vals_display) * 1.25)
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        # 基线显示
        if mkey in ["continue_rate", "safety_rate"]:
            ax.axhline(y=0, color="gray", linestyle="--", linewidth=0.5)

    plt.tight_layout()
    plt.savefig(str(output_path), dpi=150, bbox_inches="tight")
    plt.close()
    print(f"  📊 {output_path}")
    return True


def plot_radar(eval_data, output_path):
    """雷达图：三策略对比"""
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        import numpy as np
    except ImportError:
        print("  [跳过] 请安装 matplotlib: pip install matplotlib")
        return False

    data = eval_data.get("all", {})
    if not data:
        return False

    strategies = ["baseline", "persona", "expel_mvp"]
    colors = ["#e74c3c", "#f39c12", "#2ecc71"]
    metrics = ["avg_turns", "continue_rate", "avg_reward", "safety_rate"]
    labels = ["平均轮次", "续聊率", "平均奖励", "安全率"]

    # 归一化
    values = []
    for s in strategies:
        row = []
        for m in metrics:
            v = data[s].get(m, 0)
            if m in ["continue_rate", "safety_rate"]:
                row.append(v * 100)  # 转为百分比
            else:
                row.append(v)
        values.append(row)

    # 找最大值做归一化
    max_vals = [max(vals[i] for vals in values) for i in range(len(metrics))]
    max_vals = [max(mv, 0.01) for mv in max_vals]  # 避免除零

    norm_values = []
    for vals in values:
        norm_values.append([vals[i] / max_vals[i] for i in range(len(metrics))])

    angles = np.linspace(0, 2 * np.pi, len(metrics), endpoint=False).tolist()
    angles += angles[:1]  # 闭合

    fig, ax = plt.subplots(figsize=(7, 7), subplot_kw={"polar": True})
    fig.suptitle("数字人直播对话系统 — 三策略雷达对比", fontsize=14, fontweight="bold", y=1.05)

    for idx, (s, vals, nv) in enumerate(zip(strategies, values, norm_values)):
        nv_closed = nv + nv[:1]
        ax.plot(angles, nv_closed, color=colors[idx], linewidth=2, label=s)
        ax.fill(angles, nv_closed, color=colors[idx], alpha=0.1)

    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(labels, fontsize=11)
    ax.legend(loc="upper right", bbox_to_anchor=(1.3, 1.1))
    ax.set_ylim(0, 1.1)

    plt.tight_layout()
    plt.savefig(str(output_path), dpi=150, bbox_inches="tight")
    plt.close()
    print(f"  📊 {output_path}")
    return True


def print_text_table(eval_data):
    """打印文本表格"""
    data = eval_data.get("all", {})
    if not data:
        return
    strategies = ["baseline", "persona", "expel_mvp"]
    print("=" * 65)
    print("  🎯 三策略对比结果 (ALL sessions)")
    print("=" * 65)
    print(f"{'策略':<15} {'平均轮次':>10} {'续聊率':>10} {'平均奖励':>10} {'安全率':>10}")
    print("-" * 60)
    for s in strategies:
        d = data.get(s, {})
        cr = d.get("continue_rate", 0) * 100
        sr = d.get("safety_rate", 0) * 100
        print(f"{s:<15} {d.get('avg_turns', 0):>10.2f} {cr:>9.1f}% "
              f"{d.get('avg_reward', 0):>10.3f} {sr:>9.1f}%")
    print("-" * 60)
    b = data.get("baseline", {})
    e = data.get("expel_mvp", {})
    b_cr = b.get("continue_rate", 0) * 100
    e_cr = e.get("continue_rate", 0) * 100
    b_ar = b.get("avg_reward", 0)
    e_ar = e.get("avg_reward", 0)
    print(f"\n  📌 关键发现:")
    print(f"     ▸ 续聊率提升: baseline={b_cr:.1f}% → expel_mvp={e_cr:.1f}%")
    print(f"     ▸ 奖励分提升: baseline={b_ar:.2f} → expel_mvp={e_ar:.2f}")
    print(f"     ▸ 安全率稳定在 {b.get('safety_rate',0)*100:.0f}% 以上")
    print("=" * 65)


def main():
    print("=" * 65)
    print("  📊 数字人直播对话系统 — 报告图表生成")
    print("=" * 65)

    # 1. 加载评估结果
    eval_data = load_eval_results()
    if not eval_data:
        print("  ❌ 未找到 logs/livestream/eval_summary.json")
        print("     请先运行: python evaluate_livestream.py")
        return

    print_text_table(eval_data)

    # 2. 加载轨迹数据
    traj_stats = load_trajectories()
    print(f"\n  📂 数据概况: {traj_stats['session_count']}段会话, "
          f"{traj_stats['total_turns']}轮对话, 平均{traj_stats['avg_turns']}轮/会话")

    # 3. 生成图表
    print("\n  📊 正在生成图表...")
    ok1 = plot_data_distribution(traj_stats, LOG_DIR / "data_distribution.png")
    ok2 = plot_comparison_bar(eval_data, LOG_DIR / "eval_comparison.png")
    ok3 = plot_radar(eval_data, LOG_DIR / "eval_radar.png")

    print(f"\n  ✅ 完成! 图表保存在: {LOG_DIR}/")
    for f in ["eval_comparison.png", "eval_radar.png", "data_distribution.png"]:
        p = LOG_DIR / f
        if p.exists():
            print(f"     ✅ {f} ({p.stat().st_size / 1024:.0f} KB)")
        else:
            print(f"     ❌ {f} (未生成)")
    print("=" * 65)


if __name__ == "__main__":
    main()
