#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""生成 C2 审计元数据保留决策学习文档所需的 PNG 图表"""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
import numpy as np, os

plt.rcParams["font.family"] = ["Hiragino Sans GB", "PingFang SC", "sans-serif"]
plt.rcParams["axes.unicode_minus"] = False

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets")
os.makedirs(OUT, exist_ok=True)

INK = "#1a1a2e"; BLUE = "#2563eb"; GREEN = "#059669"; AMBER = "#d97706"
RED = "#dc2626"; GREY = "#6b7280"; BG = "#ffffff"
C_PHONE = "#dbeafe"; C_RELAY = "#fef3c7"; C_CONN = "#d1fae5"; C_FORBID = "#fee2e2"

def box(ax, x, y, w, h, text, fc, ec=INK, fs=11, bold=False, tc=INK, style="round,pad=0.02,rounding_size=0.03"):
    b = FancyBboxPatch((x, y), w, h, boxstyle=style, fc=fc, ec=ec, lw=1.6, mutation_aspect=1)
    ax.add_patch(b)
    ax.text(x + w/2, y + h/2, text, ha="center", va="center", fontsize=fs,
            color=tc, fontweight="bold" if bold else "normal", linespacing=1.5)

def arrow(ax, x1, y1, x2, y2, text=None, color=INK, fs=9.5, style="-|>", lw=1.8,
          offset=(0, 0.012), ls="-"):
    a = FancyArrowPatch((x1, y1), (x2, y2), arrowstyle=style, color=color,
                        lw=lw, mutation_scale=16, linestyle=ls, shrinkA=2, shrinkB=2)
    ax.add_patch(a)
    if text:
        ax.text((x1+x2)/2 + offset[0], (y1+y2)/2 + offset[1], text, ha="center",
                va="center", fontsize=fs, color=color, fontweight="bold")

# ============ 图1：系统结构图 —— Relay 能看见什么 ============
fig, ax = plt.subplots(figsize=(11.5, 6.8), dpi=160)
ax.set_xlim(0, 1); ax.set_ylim(0, 1); ax.axis("off")
fig.patch.set_facecolor(BG)
ax.text(0.5, 0.965, "图1 · Utell 链路结构图：Relay 的「视野」", ha="center",
        fontsize=16, fontweight="bold", color=INK)
ax.text(0.5, 0.925, "端到端加密下，Relay 只是「戴着眼罩的邮递员」——只能看信封，不能看信",
        ha="center", fontsize=10.5, color=GREY)

box(ax, 0.03, 0.52, 0.20, 0.30, "手机端\n（NEW-Utell-phone）\n\n明文只在这里\n短暂存在", C_PHONE, fs=11.5, bold=True)
box(ax, 0.40, 0.52, 0.20, 0.30, "Relay 服务器\n（NEW-Utell-server）\n\n路由 + 限流\n+ 最小脱敏审计", C_RELAY, fs=11.5, bold=True)
box(ax, 0.77, 0.52, 0.20, 0.30, "电脑端 Connector\n+ Pi（权威数据库）\n\n解密、解析、\n持久保存业务数据", C_CONN, fs=11, bold=True)

arrow(ax, 0.23, 0.70, 0.40, 0.70, "E2EE 密文信封", offset=(0, 0.035))
arrow(ax, 0.60, 0.70, 0.77, 0.70, "E2EE 密文信封", offset=(0, 0.035))
arrow(ax, 0.77, 0.60, 0.60, 0.60, "ACK / 回执", color=GREY, offset=(0, -0.04))
arrow(ax, 0.40, 0.60, 0.23, 0.60, "卡片 Projection（密文）", color=GREY, offset=(0, -0.04))

# Relay 视野框
box(ax, 0.33, 0.06, 0.34, 0.38, "", "#fffbeb", ec=AMBER, style="round,pad=0.02,rounding_size=0.02")
ax.text(0.50, 0.405, "Relay 实际「落盘」的审计元数据（C2 讨论对象）", ha="center",
        fontsize=11, fontweight="bold", color=AMBER)
ax.text(0.50, 0.30,
        "✓ pairing 标识的不可逆哈希（不是配对ID本身）\n"
        "✓ 时间戳\n"
        "✓ 消息大小区间（如 1~4KB，不是精确字节数）\n"
        "✓ 投递结果（成功 / 不可投递）\n"
        "✓ 错误类别（限流 / 认证失败 / 路由失败…）",
        ha="center", va="center", fontsize=10.5, color=INK, linespacing=1.7)
ax.text(0.50, 0.115, "✗ 绝不保存：明文、可解密载荷、标题、摘要、Pi 输出、私钥",
        ha="center", fontsize=10, color=RED, fontweight="bold")
ax.plot([0.50, 0.50], [0.44, 0.52], color=AMBER, lw=1.5, ls="--")

# 排障用途标注
ax.annotate("审计元数据的用途：\n出了故障能回答\n「谁的链路、几点、\n多大、送没送到、\n为什么失败」", xy=(0.67, 0.25), xytext=(0.80, 0.22),
            fontsize=9.5, color=GREY, ha="center",
            arrowprops=dict(arrowstyle="->", color=GREY))

plt.tight_layout()
fig.savefig(os.path.join(OUT, "fig1-architecture.png"), bbox_inches="tight", facecolor=BG)
plt.close(fig)

# ============ 图2：审计元数据生命周期流程图 ============
fig, ax = plt.subplots(figsize=(11.5, 6.2), dpi=160)
ax.set_xlim(0, 1); ax.set_ylim(0, 1); ax.axis("off")
fig.patch.set_facecolor(BG)
ax.text(0.5, 0.96, "图2 · 一条脱敏审计元数据的生命周期（以「接受 30 天」为例）", ha="center",
        fontsize=15.5, fontweight="bold", color=INK)

steps = [
    (0.02, "① 产生", "手机发出\nE2EE 密文信封\n抵达 Relay", C_PHONE),
    (0.185, "② 脱敏提取", "Relay 只看信封：\npairing→哈希\n大小→区间\n结果→枚举", C_RELAY),
    (0.35, "③ 落盘", "写入审计存储\n（与业务正文\n物理隔离）", "#ede9fe"),
    (0.515, "④ 服役期", "0 ~ 30 天\n仅用于排障、\n安全事件调查", C_CONN),
    (0.68, "⑤ 到期", "定时任务扫描\nretention > 30d\n的记录", "#fef9c3"),
    (0.845, "⑥ 自动删除", "物理删除\n不可恢复\n（可选留删除凭证）", C_FORBID),
]
for x, title, body, color in steps:
    box(ax, x, 0.42, 0.145, 0.34, "", color, fs=10)
    ax.text(x + 0.0725, 0.715, title, ha="center", fontsize=11.5, fontweight="bold", color=INK)
    ax.text(x + 0.0725, 0.565, body, ha="center", va="center", fontsize=9.5, color=INK, linespacing=1.6)
for i in range(len(steps) - 1):
    arrow(ax, steps[i][0] + 0.145, 0.59, steps[i+1][0], 0.59)

# 时间轴
ax.plot([0.06, 0.94], [0.30, 0.30], color=GREY, lw=1.2)
for frac, label in [(0.10, "第 0 天"), (0.44, "第 30 天：到期线"), (0.80, "之后：已删除")]:
    ax.plot([frac, frac], [0.285, 0.315], color=GREY, lw=1.2)
    ax.text(frac, 0.245, label, ha="center", fontsize=9.5, color=GREY)
ax.add_patch(mpatches.Rectangle((0.06, 0.175), 0.355, 0.045, fc="#d1fae5", ec="none"))
ax.text(0.237, 0.1975, "可查窗口（排障有效）", ha="center", va="center", fontsize=9.5, color=GREEN, fontweight="bold")
ax.add_patch(mpatches.Rectangle((0.415, 0.175), 0.525, 0.045, fc="#f3f4f6", ec="none"))
ax.text(0.677, 0.1975, "隐私敞口已关闭（连法院传票也调不出）", ha="center", va="center", fontsize=9.5, color=GREY)

ax.text(0.5, 0.08, "关键性质：删除是系统自动执行的默认动作，不依赖人的自觉 —— 「到期自动删除」要写成发布门禁测试",
        ha="center", fontsize=10, color=AMBER, fontweight="bold")

plt.tight_layout()
fig.savefig(os.path.join(OUT, "fig2-lifecycle.png"), bbox_inches="tight", facecolor=BG)
plt.close(fig)

# ============ 图3：四方案对比图（隐私 vs 排障 二维象限） ============
fig, ax = plt.subplots(figsize=(10.5, 7), dpi=160)
fig.patch.set_facecolor(BG)
ax.set_xlim(0, 10); ax.set_ylim(0, 10)
ax.set_xlabel("排障 / 取证能力 →", fontsize=12.5, color=INK, fontweight="bold")
ax.set_ylabel("隐私友好度 →", fontsize=12.5, color=INK, fontweight="bold")
ax.set_title("图3 · C2 四个选项的「隐私 × 排障」权衡地图", fontsize=15.5,
             fontweight="bold", color=INK, pad=16)
ax.set_xticks([]); ax.set_yticks([])
for s in ax.spines.values():
    s.set_color(GREY)
ax.axhline(5, color="#e5e7eb", lw=1); ax.axvline(5, color="#e5e7eb", lw=1)

opts = [
    ("选项3\n不保留审计", 0.8, 9.0, RED, "隐私最强\n但链路出问题=盲人摸象"),
    ("选项2a\n7 天", 3.4, 7.4, GREEN, "隐私更优\n只能查「最近一周」的故障"),
    ("选项1\n30 天（PRD 推荐）", 6.2, 5.6, BLUE, "平衡点\n覆盖「用户隔几周才反馈」场景"),
    ("选项2b\n90 天", 8.6, 2.6, AMBER, "排障最强\n元数据敞口最长\n合规论证负担最大"),
]
for name, x, y, c, note in opts:
    ax.scatter([x], [y], s=2600, c=c, alpha=0.18, edgecolors=c, linewidths=2.5)
    ax.scatter([x], [y], s=120, c=c, edgecolors=c)
    ax.text(x, y, name, ha="center", va="center", fontsize=10.5, fontweight="bold", color=c)
    ax.text(x, y - 1.15, note, ha="center", va="top", fontsize=8.8, color=GREY, linespacing=1.5)

ax.text(2.5, 0.55, "⚠ 注意：四选项共享同一份「脱敏字段清单」——\n它们之间的差别只在「留多久」，不在「留什么」",
        fontsize=9.5, color=INK, style="italic",
        bbox=dict(boxstyle="round,pad=0.5", fc="#f8fafc", ec=GREY, lw=0.8))

plt.tight_layout()
fig.savefig(os.path.join(OUT, "fig3-tradeoff.png"), bbox_inches="tight", facecolor=BG)
plt.close(fig)

# ============ 图4：保留期限业界参照标尺 ============
fig, ax = plt.subplots(figsize=(11.5, 5.6), dpi=160)
fig.patch.set_facecolor(BG)
ax.set_xlim(0, 370); ax.set_ylim(-0.5, 8.5)
ax.set_xlabel("保留时长（天，对数感知的示意标尺 →）", fontsize=11, color=INK)
ax.set_title("图4 · 保留期限的业界参照系：30 天处在什么位置？", fontsize=15,
             fontweight="bold", color=INK, pad=14)
ax.set_yticks([])
for s in ["top", "right", "left"]:
    ax.spines[s].set_visible(False)

refs = [
    ("Signal 服务器可被\n传票调出的数据", 1, BLUE, "几乎为零：仅注册时间+最后活跃日期（精确到天）"),
    ("调试日志（业界惯例）", 7, GREEN, "GDPR 实务指南建议 7–14 天"),
    ("C2 选项1：30 天", 30, BLUE, "应用/API 访问日志惯例 30–60 天"),
    ("C2 选项2b：90 天", 90, AMBER, "错误日志惯例 30–90 天上沿"),
    ("中国《网络安全法》§21\n网络日志下限", 180, RED, "不少于 6 个月（法定下限）"),
    ("安全审计日志（惯例）", 365, GREY, "SOC2/ISO27001 常见 1 年"),
    ("美国联邦 OMB M-21-31", 365, GREY, "12 个月热存 + 18 个月冷存"),
]
y = 0.3
for name, days, color, note in refs:
    ax.barh(y, days, height=0.62, color=color, alpha=0.75 if color == BLUE else 0.45,
            edgecolor=color, lw=1.2)
    ax.text(days + 5, y, note, va="center", fontsize=8.8, color=GREY)
    ax.text(-6, y, name, va="center", ha="right", fontsize=9.5, color=INK, fontweight="bold")
    y += 1.15
ax.axvline(30, color=BLUE, ls="--", lw=1.4, alpha=0.7)
ax.text(30, 8.35, "30 天", ha="center", fontsize=10, color=BLUE, fontweight="bold")
ax.set_xticks([0, 7, 30, 90, 180, 365])
ax.set_xticklabels(["0", "7", "30", "90", "180", "365"], fontsize=9.5)

plt.tight_layout()
fig.savefig(os.path.join(OUT, "fig4-benchmark.png"), bbox_inches="tight", facecolor=BG)
plt.close(fig)

print("done:", os.listdir(OUT))
