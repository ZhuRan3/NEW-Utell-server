#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""生成 D3a Relay 语言/运行时选型学习文档所需的 PNG 图表
与 gen_figures.py 同约定:matplotlib + Hiragino Sans GB,输出到 assets/"""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Circle
import os

plt.rcParams["font.family"] = ["Hiragino Sans GB", "PingFang SC", "sans-serif"]
plt.rcParams["axes.unicode_minus"] = False

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets")
os.makedirs(OUT, exist_ok=True)

INK = "#1a1a2e"; BLUE = "#2563eb"; GREEN = "#059669"; AMBER = "#d97706"
RED = "#dc2626"; GREY = "#6b7280"; BG = "#ffffff"
C_GO = "#dbeafe"; C_RUST = "#fde8d8"; C_NODE = "#dcfce7"; C_WARN = "#fee2e2"; C_RELAY = "#fef3c7"

def box(ax, x, y, w, h, text, fc, ec=INK, fs=11, bold=False, tc=INK, lw=1.6):
    b = FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.02,rounding_size=0.03",
                       fc=fc, ec=ec, lw=lw, mutation_aspect=1)
    ax.add_patch(b)
    ax.text(x + w/2, y + h/2, text, ha="center", va="center", fontsize=fs,
            color=tc, fontweight="bold" if bold else "normal", linespacing=1.5)

def arrow(ax, x1, y1, x2, y2, text=None, color=INK, fs=9.5, lw=1.8,
          offset=(0, 0.014), ls="-"):
    a = FancyArrowPatch((x1, y1), (x2, y2), arrowstyle="-|>", color=color,
                        lw=lw, mutation_scale=16, linestyle=ls, shrinkA=2, shrinkB=2)
    ax.add_patch(a)
    if text:
        ax.text((x1+x2)/2 + offset[0], (y1+y2)/2 + offset[1], text, ha="center",
                va="center", fontsize=fs, color=color, fontweight="bold")

def new_fig(w, h, title):
    fig, ax = plt.subplots(figsize=(w, h), dpi=160)
    ax.set_xlim(0, 1); ax.set_ylim(0, 1); ax.axis("off")
    fig.patch.set_facecolor(BG)
    ax.text(0.5, 0.97, title, ha="center", va="top", fontsize=16, fontweight="bold", color=INK)
    return fig, ax

# ============ 图1:Relay 在链路中的位置 —— 我们到底在为谁选语言 ============
fig, ax = new_fig(11.5, 6.6, "图1 · Relay 的位置:一个「看不见内容」的接线总机")

box(ax, 0.03, 0.52, 0.20, 0.24, "手机 App\n(Utell 端点)", C_GO, fs=13, bold=True)
box(ax, 0.40, 0.48, 0.22, 0.32, "Relay\n(云主机 · 本题主角)", C_RELAY, fs=13, bold=True, ec=AMBER, lw=2.4)
box(ax, 0.77, 0.52, 0.20, 0.24, "Connector\n(家中树莓派等)", C_NODE, fs=13, bold=True)

arrow(ax, 0.235, 0.64, 0.395, 0.64, text=None, color=BLUE)
arrow(ax, 0.395, 0.59, 0.235, 0.59, text=None, color=BLUE)
ax.text(0.315, 0.685, "WSS 长连接(公网 443/TLS)", ha="center", fontsize=10, color=BLUE, fontweight="bold")
ax.text(0.315, 0.545, "只传「密文信封」", ha="center", fontsize=9.5, color=GREY)

arrow(ax, 0.625, 0.64, 0.765, 0.64, text=None, color=GREEN)
arrow(ax, 0.765, 0.59, 0.625, 0.59, text=None, color=GREEN)
ax.text(0.695, 0.685, "WSS 长连接", ha="center", fontsize=10, color=GREEN, fontweight="bold")
ax.text(0.695, 0.545, "同样只传密文", ha="center", fontsize=9.5, color=GREY)

# 端点 E2EE 标注
box(ax, 0.16, 0.83, 0.68, 0.09,
    "端到端加密(E2EE)在两个端点之间终止 —— Relay 没有钥匙,永远读不到正文",
    "#f1f5f9", ec=GREY, fs=10.5)

# Relay 职责清单
box(ax, 0.06, 0.08, 0.40, 0.30,
    "Relay 白天干什么:\n· 身份校验 / 二维码配对 / 公钥登记\n"
    "· 单主 Connector 约束与原子撤销\n· 密文信封路由 + ACK / 心跳\n"
    "· 限流、背压、消息大小上限\n· 只存最小脱敏元数据(SQLite)",
    "#fffbeb", ec=AMBER, fs=10)
box(ax, 0.54, 0.08, 0.40, 0.30,
    "Relay 永远不干什么:\n· 不解密业务正文(没有密钥)\n"
    "· 不建离线消息队列\n· 不持久化正文\n"
    "→ 选型不需要看密码库生态,\n   只比「连接并发 × 部署形态 × 迭代成本」",
    C_WARN, ec=RED, fs=10)

ax.text(0.5, 0.035, "D3a 要回答的问题:用哪门语言/运行时,把这个「接线总机」造出来?",
        ha="center", fontsize=12, fontweight="bold", color=AMBER)
fig.savefig(os.path.join(OUT, "d3a-fig1-relay-context.png"), bbox_inches="tight", facecolor=BG)
plt.close(fig)

# ============ 图2:三种并发模型结构对比 ============
fig, ax = new_fig(13.5, 7.2, "图2 · 三种「同时握住几万条连接」的方式")

col_w = 0.30
cols = [(0.02, C_GO, "A. Go:每连接一个 goroutine", BLUE),
        (0.35, C_RUST, "B. Rust tokio:编译期状态机", "#c2410c"),
        (0.68, C_NODE, "C. Node:单线程事件循环", GREEN)]

for x0, fc, title, tc in cols:
    ax.text(x0 + col_w/2, 0.885, title, ha="center", fontsize=12.5, fontweight="bold", color=tc)

# --- Go 栏 ---
x0 = 0.02
for i in range(3):
    box(ax, x0 + 0.005 + i*0.098, 0.72, 0.085, 0.09, f"连接{i+1}\n1个goroutine", C_GO, fs=8.5)
ax.text(x0 + col_w/2, 0.685, "· · · 一条连接 = 一个 goroutine,写法像同步代码 · · ·",
        ha="center", fontsize=8.5, color=GREY)
box(ax, x0 + 0.03, 0.47, 0.24, 0.13, "Go runtime 调度器(G-M-P)\n把 M 个 goroutine 轮流放上\n少数 OS 线程;网络等待\n交给 netpoller(epoll)", "#eff6ff", ec=BLUE, fs=9)
box(ax, x0 + 0.04, 0.30, 0.065, 0.08, "线程1", "#bfdbfe", fs=9)
box(ax, x0 + 0.115, 0.30, 0.065, 0.08, "线程2", "#bfdbfe", fs=9)
box(ax, x0 + 0.19, 0.30, 0.065, 0.08, "…≈CPU核数", "#bfdbfe", fs=8)
box(ax, x0 + 0.03, 0.13, 0.24, 0.09, "goroutine 初始栈仅 KB 级\n→ 10 万条连接也扛得住", C_GO, ec=BLUE, fs=9.5, bold=True)
arrow(ax, x0 + col_w/2, 0.71, x0 + col_w/2, 0.615, color=BLUE)
arrow(ax, x0 + col_w/2, 0.455, x0 + col_w/2, 0.395, color=BLUE)

# --- Rust 栏 ---
x0 = 0.35
for i in range(3):
    box(ax, x0 + 0.005 + i*0.098, 0.72, 0.085, 0.09, f"连接{i+1}\nasync task", C_RUST, fs=8.5)
ax.text(x0 + col_w/2, 0.685, "· · · async/await 被编译成状态机:记下「等到哪一步」 · · ·",
        ha="center", fontsize=8.5, color=GREY)
box(ax, x0 + 0.03, 0.47, 0.24, 0.13, "tokio 调度器轮询任务:\n谁的数据到了就推进谁一步\n没有 GC,没有隐藏分配\n内存曲线最平", "#fff7ed", ec="#c2410c", fs=9)
box(ax, x0 + 0.04, 0.30, 0.065, 0.08, "线程1", "#fed7aa", fs=9)
box(ax, x0 + 0.115, 0.30, 0.065, 0.08, "线程2", "#fed7aa", fs=9)
box(ax, x0 + 0.19, 0.30, 0.065, 0.08, "…≈CPU核数", "#fed7aa", fs=8)
box(ax, x0 + 0.03, 0.13, 0.24, 0.09, "资源占用最可预测\n但 async+借用检查迭代成本高", C_RUST, ec="#c2410c", fs=9.5, bold=True)
arrow(ax, x0 + col_w/2, 0.71, x0 + col_w/2, 0.615, color="#c2410c")
arrow(ax, x0 + col_w/2, 0.455, x0 + col_w/2, 0.395, color="#c2410c")

# --- Node 栏 ---
x0 = 0.68
for i in range(3):
    box(ax, x0 + 0.005 + i*0.098, 0.72, 0.085, 0.09, f"连接{i+1}\n登记回调", C_NODE, fs=8.5)
ax.text(x0 + col_w/2, 0.685, "· · · 没有「每连接一个执行体」,只有事件登记表 · · ·",
        ha="center", fontsize=8.5, color=GREY)
c = Circle((x0 + col_w/2, 0.525), 0.075, fc="#f0fdf4", ec=GREEN, lw=2.2)
ax.add_patch(c)
ax.text(x0 + col_w/2, 0.525, "事件循环\n(唯一线程)\n来一件办一件\n绝不等待", ha="center", va="center", fontsize=9)
box(ax, x0 + 0.04, 0.30, 0.22, 0.08, "libuv 事件队列(操作系统帮忙盯网络)", "#bbf7d0", fs=9)
box(ax, x0 + 0.03, 0.13, 0.24, 0.09, "转发型 I/O 极快\n但一次 CPU 密集操作堵住所有连接", C_WARN, ec=RED, fs=9.5, bold=True)
arrow(ax, x0 + col_w/2, 0.71, x0 + col_w/2, 0.615, color=GREEN)
arrow(ax, x0 + col_w/2, 0.445, x0 + col_w/2, 0.395, color=GREEN)

ax.text(0.5, 0.045, "共同点:都避免了「一条连接 = 一个 OS 线程」的昂贵方案;差别在写法心智负担与出事时的表现",
        ha="center", fontsize=10.5, color=GREY)
fig.savefig(os.path.join(OUT, "d3a-fig2-concurrency.png"), bbox_inches="tight", facecolor=BG)
plt.close(fig)

# ============ 图3:事件循环阻塞时间轴 vs Go 多核 ============
fig, ax = new_fig(12.5, 6.2, "图3 · 为什么 Node 怕「重活」,Go 不怕:同一时间,两个世界")

def timeline(ax, y0, label, segments, label_color=INK):
    ax.text(0.045, y0 + 0.035, label, ha="left", va="center", fontsize=11,
            fontweight="bold", color=label_color)
    ax.plot([0.16, 0.97], [y0, y0], color=GREY, lw=1)
    for (x1, x2, txt, fc, ec, tc) in segments:
        b = FancyBboxPatch((x1, y0 - 0.028), x2 - x1, 0.056,
                           boxstyle="round,pad=0.004,rounding_size=0.012",
                           fc=fc, ec=ec, lw=1.4)
        ax.add_patch(b)
        ax.text((x1+x2)/2, y0, txt, ha="center", va="center", fontsize=8.5, color=tc)

# Node 世界
ax.text(0.5, 0.86, "Node 的世界(单线程):一次大 JSON 解析,全店停摆 200ms",
        ha="center", fontsize=12, fontweight="bold", color=RED)
timeline(ax, 0.72, "事件循环", [
    (0.17, 0.30, "处理连接A的小消息", C_NODE, GREEN, INK),
    (0.30, 0.68, "连接B的大消息来了:JSON 解析占满唯一线程 200ms", "#fecaca", RED, RED),
    (0.68, 0.80, "继续处理A…", C_NODE, GREEN, INK),
])
timeline(ax, 0.60, "连接C", [
    (0.30, 0.68, "消息到了,只能排队干等(延迟飙升)", "#f1f5f9", GREY, GREY),
])
timeline(ax, 0.48, "连接D", [
    (0.30, 0.68, "心跳帧也发不出去 → 可能被误判掉线", "#f1f5f9", GREY, GREY),
])

# Go 世界
ax.text(0.5, 0.365, "Go 的世界(多核并行):B 的重活只占一个核,别人照常",
        ha="center", fontsize=12, fontweight="bold", color=BLUE)
timeline(ax, 0.245, "goroutine A\n(核1)", [
    (0.17, 0.42, "处理小消息", C_GO, BLUE, INK),
    (0.42, 0.68, "照常收发,不受 B 影响", C_GO, BLUE, INK),
])
timeline(ax, 0.135, "goroutine B\n(核2)", [
    (0.30, 0.68, "大消息 JSON 解析在核2 上慢慢算 200ms", "#bfdbfe", BLUE, INK),
], label_color=INK)
timeline(ax, 0.025, "goroutine C\n(核1)", [
    (0.17, 0.68, "调度器把它排进核1 的空档,正常服务", C_GO, BLUE, INK),
])

fig.savefig(os.path.join(OUT, "d3a-fig3-eventloop.png"), bbox_inches="tight", facecolor=BG)
plt.close(fig)

# ============ 图4:部署产物形态对比 ============
fig, ax = new_fig(13.0, 6.0, "图4 · 「扔到一台云主机上就跑」:三个候选的交付物长什么样?")

# Go
box(ax, 0.03, 0.76, 0.28, 0.10, "A. Go(CGO_ENABLED=0)", C_GO, ec=BLUE, fs=12, bold=True)
box(ax, 0.06, 0.47, 0.22, 0.20, "relay\n一个文件\n静态链接,零依赖\n含 TLS + SQLite", "#eff6ff", ec=BLUE, fs=10.5, bold=True)
arrow(ax, 0.17, 0.74, 0.17, 0.69, color=BLUE)
box(ax, 0.06, 0.16, 0.22, 0.16, "scp 上服务器\n直接 ./relay\n完事", "#f0fdf4", ec=GREEN, fs=10.5)
arrow(ax, 0.17, 0.45, 0.17, 0.345, color=GREEN)
ax.text(0.17, 0.09, "连 libc 都不依赖,scratch 镜像也能跑", ha="center", fontsize=9, color=GREY)

# Rust
box(ax, 0.37, 0.76, 0.28, 0.10, "B. Rust(musl 静态)", C_RUST, ec="#c2410c", fs=12, bold=True)
box(ax, 0.40, 0.47, 0.22, 0.20, "relay\n一个文件\nmusl 静态链接\nrusqlite bundled", "#fff7ed", ec="#c2410c", fs=10.5, bold=True)
arrow(ax, 0.51, 0.74, 0.51, 0.69, color="#c2410c")
box(ax, 0.40, 0.16, 0.22, 0.16, "scp 上服务器\n直接 ./relay\n完事", "#f0fdf4", ec=GREEN, fs=10.5)
arrow(ax, 0.51, 0.45, 0.51, 0.345, color=GREEN)
ax.text(0.51, 0.09, "同样单二进制,构建链条略重于 Go", ha="center", fontsize=9, color=GREY)

# Node
box(ax, 0.71, 0.76, 0.28, 0.10, "C. Node/TS", C_NODE, ec=GREEN, fs=12, bold=True)
box(ax, 0.735, 0.44, 0.235, 0.26,
    "服务器上必须先装好:\n① Node 运行时(版本要匹配)\n"
    "② node_modules/(体积庞大)\n③ better-sqlite3 的 .node\n   (C++ 编译产物,绑死 ABI)",
    "#fff7ed", ec=AMBER, fs=9.5)
arrow(ax, 0.85, 0.74, 0.85, 0.72, color=GREEN)
box(ax, 0.735, 0.16, 0.235, 0.14, "SEA 单文件打包?\n官方仍标注「实验性」,\nnative 模块塞不进去", C_WARN, ec=RED, fs=9.5)
arrow(ax, 0.85, 0.42, 0.85, 0.325, color=RED)
ax.text(0.85, 0.09, "Node 大版本一升级,.node 可能要重新编译", ha="center", fontsize=9, color=GREY)

ax.text(0.5, 0.02, "PRD 硬约束:「单台云主机可承载的轻量部署」—— 交付物越像一个文件,越符合",
        ha="center", fontsize=10.5, color=GREY)
fig.savefig(os.path.join(OUT, "d3a-fig4-deploy.png"), bbox_inches="tight", facecolor=BG)
plt.close(fig)

# ============ 图5:三候选对比热力表 ============
fig, ax = plt.subplots(figsize=(12.5, 7.4), dpi=160)
fig.patch.set_facecolor(BG)
ax.set_xlim(0, 1); ax.set_ylim(0, 1); ax.axis("off")
ax.text(0.5, 0.98, "图5 · D3a 候选矩阵", ha="center", va="top", fontsize=16, fontweight="bold", color=INK)
color_map = {2: "#bbf7d0", 1: "#fef9c3", 0: "#fecaca"}
edge_map = {2: GREEN, 1: AMBER, 0: RED}
# 图例放标题下方横条
for i, (g, txt) in enumerate([(2, "绿 = 占优"), (1, "黄 = 可用但有代价"), (0, "红 = 硬伤/空缺")]):
    c = Circle((0.24 + i*0.20, 0.935), 0.008, fc=color_map[g], ec=edge_map[g], lw=1.4)
    ax.add_patch(c)
    ax.text(0.255 + i*0.20, 0.935, txt, ha="left", va="center", fontsize=10, color=INK)

rows = [
    ("WSS 连接并发模型", 2, 2, 1,
     "goroutine 写法直白", "tokio 同样适配", "I/O 快但 CPU 堵全局"),
    ("单机部署产物", 2, 2, 0,
     "纯静态单二进制", "musl 单二进制", "要装运行时+依赖"),
    ("核心库稳定性", 2, 1, 2,
     "标准库TLS+活跃1.x库", "Web栈全0.x会改API", "ws/better-sqlite3成熟"),
    ("本机就绪(2026-08-23)", 0, 2, 2,
     "Go 未安装", "rustc 1.94.1 已装", "Node v24.14.0 已装"),
    ("单 Owner 迭代成本", 1, 0, 2,
     "低到中", "高(async+借用检查)", "最低,前后端同语言"),
    ("资源可预测性", 1, 2, 1,
     "GC 尾部延迟待实测", "无 GC,内存最平", "基线内存最高"),
]
col_titles = ["维度", "A. Go", "B. Rust", "C. Node/TS"]
xs = [0.03, 0.27, 0.50, 0.73]
ws = [0.22, 0.21, 0.21, 0.21]
y_top = 0.85; rh = 0.118

for x, w, t in zip(xs, ws, col_titles):
    box(ax, x, y_top, w, 0.07, t, "#f1f5f9", ec=GREY, fs=12, bold=True)
for i, (dim, ga, gb, gc, na, nb, nc) in enumerate(rows):
    y = y_top - (i+1) * rh
    box(ax, xs[0], y, ws[0], rh - 0.014, dim, "#f8fafc", ec=GREY, fs=10.5, bold=True)
    for x, w, g, note in [(xs[1], ws[1], ga, na), (xs[2], ws[2], gb, nb), (xs[3], ws[3], gc, nc)]:
        box(ax, x, y, w, rh - 0.014, note, color_map[g], ec=edge_map[g], fs=9)

ax.text(0.5, 0.085, "Go:6 项中 4 绿、无红项 → AI 推荐;Rust 胜在资源可预测性;Node 胜在开发速度",
        ha="center", fontsize=11, color=INK, fontweight="bold")
ax.text(0.5, 0.038, "注意:容量 / 背压 / 尾部延迟三项无官方基准,一律待 Spike 实测,本图不替它们打分",
        ha="center", fontsize=10, color=GREY)
fig.savefig(os.path.join(OUT, "d3a-fig5-matrix.png"), bbox_inches="tight", facecolor=BG)
plt.close(fig)

print("OK: d3a-fig1 ~ d3a-fig5 已生成到 assets/")
