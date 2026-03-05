import matplotlib
matplotlib.use("Agg")

import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.patches import Rectangle
from matplotlib import font_manager

from datetime import datetime
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
font_path = BASE_DIR / "font" / "LXGWWenKai-Regular.ttf"
font_prop = font_manager.FontProperties(fname=str(font_path))

# 查询宿主机历史数据，并渲染成图片
def draw_server_chart(rows, output_path: Path):

    if not rows:
        raise ValueError("没有数据")

    timestamps = []
    cpu_values = []
    mem_values = []
    disk_values = []
    load_values = []

    for ts, cpu, mem, disk, load in rows:
        timestamps.append(datetime.fromtimestamp(ts))
        cpu_values.append(cpu)
        mem_values.append(mem)
        disk_values.append(disk)

        if load == -1:
            load_values.append(None)
        else:
            load_values.append(load)

    # 降低采样点数，提高性能（点数过多时触发）
    if len(timestamps) > 600:
        timestamps = timestamps[::2]
        cpu_values = cpu_values[::2]
        mem_values = mem_values[::2]
        disk_values = disk_values[::2]
        load_values = load_values[::2]

    fig, ax = plt.subplots(figsize=(12, 5))

    ax.xaxis.set_major_formatter(mdates.DateFormatter('%y-%m-%d %H:%M'))

    # 折线（颜色类似监控面板）
    ax.plot(timestamps, cpu_values, label="CPU %", linewidth=2)
    ax.fill_between(timestamps, cpu_values, alpha=0.2)
    ax.plot(timestamps, mem_values, label="Memory %", linewidth=2)
    ax.plot(timestamps, disk_values, label="Disk %", linewidth=2)
    ax.plot(timestamps, load_values, label="Load 1m", linewidth=2)

    # 标题
    ax.set_title("Server Status History", fontsize=14)

    # 坐标轴
    ax.set_xlabel("Time")
    ax.set_ylabel("Usage(%)")

    # 百分比数据限制
    ax.set_ylim(0, 100)

    # 网格
    ax.grid(True, linestyle="--", alpha=0.4)

    # 图例
    ax.legend(loc="upper left")

    # 时间轴优化
    fig.autofmt_xdate()

    plt.tight_layout()
    plt.savefig(output_path, dpi=130)
    plt.close()

    return output_path

# 查询宿主机实时状态与信息，并渲染成图片
def draw_server_stat_card(metrics, host_info, save_path):
    """整合了宿主机信息与宿主机状态，简化模块结构"""
    fig, ax = plt.subplots(figsize=(7, 4))

    # 浅色背景
    fig.patch.set_facecolor("#ffffff")
    ax.set_facecolor("#2b2b2b")

    ax.axis("off")

    text_color = "#000000"

    # ===== 外框 =====
    ax.add_patch(
        Rectangle(
            (0.01, 0.02),
            0.98,
            0.96,
            fill=False,
            edgecolor="#555",
            linewidth=1
        )
    )

    # ===== 标题 =====
    ax.text(
        0.03,
        0.90,
        "Server Monitor",
        fontsize=16,
        weight="bold",
        color=text_color,
        fontproperties=font_prop
    )

    ax.plot([0.02, 0.98], [0.87, 0.87], color="#555", linewidth=1)

    # ===== 主机信息 =====
    host_text = (
        f"Host : {host_info.hostname}\n"
        f"OS   : {host_info.os_name} {host_info.os_version}\n"
        f"Arch : {host_info.architecture}"
    )

    ax.text(
        0.03,
        0.70,
        host_text,
        fontsize=11,
        family="monospace",
        color=text_color,
        fontproperties=font_prop
    )

    ax.plot([0.02, 0.98], [0.66, 0.66], color="#555", linewidth=1)

    # ===== 指标 =====
    labels = ["CPU", "MEM", "DISK"]
    values = [
        metrics.cpu_usage,
        metrics.memory_usage,
        metrics.disk_usage
    ]

    colors = ["#5794F2", "#FF9830", "#73BF69"]

    bar_y = [0.50, 0.40, 0.30]

    for label, value, color, y in zip(labels, values, colors, bar_y):

        # 标签
        ax.text(
            0.03,
            y,
            label,
            fontsize=12,
            family="monospace",
            color=text_color,
            va="center",
            fontproperties=font_prop
        )

        # 进度条背景
        ax.add_patch(
            Rectangle(
                (0.15, y - 0.015),
                0.60,
                0.03,
                color="#444"
            )
        )

        # 进度条
        ax.add_patch(
            Rectangle(
                (0.15, y - 0.015),
                value / 100 * 0.60,
                0.03,
                color=color
            )
        )

        # 百分比
        ax.text(
            0.78,
            y,
            f"{value:.1f}%",
            fontsize=11,
            family="monospace",
            color=text_color,
            va="center",
            fontproperties=font_prop
        )

    # ===== Load =====
    ax.text(
        0.03,
        0.13,
        f"LOAD:   {metrics.load_1m}\n*Windows 环境下无法测量系统平均负载，显示 None 系正常现象",
        fontsize=12,
        family="monospace",
        color=text_color,
        fontproperties=font_prop
    )

    plt.tight_layout()
    plt.savefig(save_path, dpi=150, facecolor=fig.get_facecolor())
    plt.close()