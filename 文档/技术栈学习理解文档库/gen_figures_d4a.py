#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""生成 D4a Noise 首发 Pattern 选型学习文档所需的 PNG 图表
与 gen_figures.py / gen_figures_d3a.py / gen_figures_d3b.py 同约定:
matplotlib + Hiragino Sans GB,输出到 assets/"""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
import os

plt.rcParams["font.family"] = ["Hiragino Sans GB", "PingFang SC", "sans-serif"]
plt.rcParams["axes.unicode_minus"] = False

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets")
os.makedirs(OUT, exist_ok=True)

INK = "#1a1a2e"; BLUE = "#2563eb"; GREEN = "#059669"; AMBER = "#d97706"
RED = "#dc2626"; GREY = "#6b7280"; BG = "#ffffff"; PURPLE = "#7c3aed"
C_XX = "#dcfce7"; C_IK = "#dbeafe"; C_RELAY = "#fef3c7"; C_NEUTRAL = "#f1f5f9"
C_WARN = "#fee2e2"; C_PHONE = "#ede9fe"; C_CONN = "#e0f2fe"

def box(ax, x, y, w, h, text, fc, ec=INK, fs=11, bold=False, tc=INK, lw=1.6):
    b = FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.02,rounding_size=0.03",
                       fc=fc, ec=ec, lw=lw, mutation_aspect=1)
    ax.add_patch(b)
    ax.text(x + w/2, y + h/2, text, ha="center", va="center", fontsize=fs,
            color=tc, fontweight="bold" if bold else "normal", linespacing=1.5)

def arrow(ax, x1, y1, x2, y2, text=None, color=INK, fs=9.5, lw=1.8,
          offset=(0, 0.02), ls="-"):
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
    ax.text(0.5, 0.975, title, ha="center", va="top", fontsize=16, fontweight="bold", color=INK)
    return fig, ax

# ============ 图1:Noise 站在哪 —— E2EE 那一层 ============
fig, ax = new_fig(11.5, 6.6, "图1 · Noise 在 NEW-Utell 链路中的位置:手机与电脑之间的「加密管道」")

box(ax, 0.03, 0.52, 0.20, 0.30, "手机 App\n\n持有:\n手机静态密钥对\n(长期身份证)", C_PHONE, ec=PURPLE, fs=11, bold=True)
box(ax, 0.77, 0.52, 0.20, 0.30, "Connector\n(家中电脑/树莓派)\n\n持有:\nConnector 静态密钥对", C_CONN, ec=BLUE, fs=11, bold=True)
box(ax, 0.33, 0.55, 0.34, 0.24, "Relay(蒙眼接线总机)\n\n只转发密文信封\n不看、也不能看内容\n负责:配对登记 / 公钥登记 / 路由 / ACK", C_RELAY, ec=AMBER, fs=10.5, bold=True, lw=2)

arrow(ax, 0.23, 0.67, 0.33, 0.67, color=GREY)
arrow(ax, 0.67, 0.67, 0.77, 0.67, color=GREY)

# E2EE 管道
box(ax, 0.23, 0.30, 0.54, 0.13,
    "←←←  Noise 端到端加密管道(E2EE):密钥只在两端手里,Relay 全程只见乱码  →→→",
    C_XX, ec=GREEN, fs=11, bold=True, lw=2.2)
arrow(ax, 0.13, 0.52, 0.13, 0.43, color=GREEN, ls="--")
arrow(ax, 0.87, 0.52, 0.87, 0.43, color=GREEN, ls="--")

box(ax, 0.03, 0.06, 0.44, 0.17,
    "建管道之前的「介绍人」环节:\nConnector 亮出二维码(含一次性 token,5 分钟有效)\n→ 手机扫码 → 核对公钥指纹 → 用户确认",
    C_NEUTRAL, ec=GREY, fs=10)
box(ax, 0.53, 0.06, 0.44, 0.17,
    "D4a 要回答的问题:\n这条 Noise 管道第一次怎么打通?\n首发握手 Pattern 选 XX 还是 IK?",
    C_WARN, ec=RED, fs=10.5, bold=True)
fig.savefig(os.path.join(OUT, "d4a-fig1-position.png"), bbox_inches="tight", facecolor=BG)
plt.close(fig)

# ============ 图2:协议名拆解 + 握手符号语言 ============
fig, ax = new_fig(11.5, 7.6, "图2 · 读懂名字:Noise_XX_25519_ChaChaPoly_SHA256 四段式 + 六种握手符号")

# 协议名拆解
box(ax, 0.06, 0.78, 0.88, 0.10, "Noise _ XX _ 25519 _ ChaChaPoly _ SHA256", C_NEUTRAL, ec=INK, fs=17, bold=True)
labels = [
    (0.10, "框架名\nNoise 协议框架", GREY),
    (0.30, "握手 Pattern\nXX = 本文主角之一\n决定消息怎么来往", GREEN),
    (0.50, "DH 曲线 25519\n算「共享秘密」的\n椭圆曲线数学", BLUE),
    (0.68, "AEAD 加密\nChaCha20-Poly1305\n加密+防篡改一体", PURPLE),
    (0.87, "哈希 SHA-256\n把 DH 结果「揉」成\n密钥的搅拌机", AMBER),
]
for x, t, c in labels:
    ax.text(x, 0.71, t, ha="center", va="top", fontsize=9.5, color=c, fontweight="bold", linespacing=1.4)
    ax.plot([x, x], [0.775, 0.755], color=c, lw=1.5)

# 符号语言
ax.text(0.5, 0.60, "握手 Pattern 用 6 种符号写成「对话脚本」,每个符号是一个动作:", ha="center",
        fontsize=12, fontweight="bold", color=INK)
syms = [
    (0.07, 0.44, "e", "发临时公钥", "「本次见面专用的一次性面具」\n每轮握手都换新,保卫前向 secrecy", BLUE),
    (0.40, 0.44, "s", "发静态公钥", "「出示身份证」\n长期身份,配对后就是设备身份", PURPLE),
    (0.73, 0.44, "ee", "临时×临时 DH", "两张一次性面具互相一碰\n算出只有本次会话有的秘密", GREEN),
    (0.07, 0.24, "es", "临时×静态 DH", "我的面具 × 你的身份证\n(发起方临时 × 响应方静态)", AMBER),
    (0.40, 0.24, "se", "静态×临时 DH", "我的身份证 × 你的面具\n(发起方静态 × 响应方临时)", AMBER),
    (0.73, 0.24, "ss", "静态×静态 DH", "两张身份证互碰\n证明「我们俩都到场了」", RED),
]
for x, y, sym, name, desc, c in syms:
    box(ax, x, y, 0.07, 0.09, sym, C_NEUTRAL, ec=c, fs=15, bold=True, tc=c, lw=2.2)
    ax.text(x + 0.095, y + 0.068, name, ha="left", fontsize=10.5, fontweight="bold", color=c)
    ax.text(x + 0.095, y + 0.030, desc, ha="left", va="center", fontsize=8.8, color=GREY, linespacing=1.35)

box(ax, 0.06, 0.04, 0.88, 0.13,
    "共同规则:每算出一个 DH 秘密,立刻用 SHA-256(HKDF)「揉」进滚动密钥链;\n"
    "此后发出去的静态公钥和负载,都用当时的链上密钥以 ChaCha20-Poly1305 加密 —— 所以越往后的消息藏得越好。",
    C_XX, ec=GREEN, fs=10.5)
fig.savefig(os.path.join(OUT, "d4a-fig2-name-symbols.png"), bbox_inches="tight", facecolor=BG)
plt.close(fig)

# ============ 图3:XX 握手三条消息 ============
fig, ax = new_fig(11.5, 8.2, "图3 · XX 三条消息:陌生人三轮对话,互相验明正身(1.5 个往返)")

box(ax, 0.05, 0.80, 0.20, 0.12, "手机\n发起方 initiator", C_PHONE, ec=PURPLE, fs=11.5, bold=True)
box(ax, 0.75, 0.80, 0.20, 0.12, "Connector\n响应方 responder", C_CONN, ec=BLUE, fs=11.5, bold=True)
ax.plot([0.15, 0.15], [0.14, 0.80], color=GREY, lw=1.2, ls=":")
ax.plot([0.85, 0.85], [0.14, 0.80], color=GREY, lw=1.2, ls=":")

arrow(ax, 0.16, 0.735, 0.84, 0.735, text="→ e(一张一次性面具,明文)", color=BLUE, fs=10.5, offset=(0, 0.024))
ax.text(0.50, 0.685, "第 1 句:「你好,我是路人甲」—— 只递面具,不亮身份,谁都能这么说", ha="center", fontsize=9.5, color=GREY)

arrow(ax, 0.84, 0.615, 0.16, 0.615, text="← e, ee, s, es(面具 + 加密身份证)", color=GREEN, fs=10.5, offset=(0, 0.024))
ax.text(0.50, 0.565, "第 2 句:「我也是路人,先碰面具(ee);这是我的身份证,用刚才的秘密加密了,再和你的面具交叉验证(es)」",
        ha="center", fontsize=9.5, color=GREY)
ax.text(0.50, 0.528, "→ 手机此刻已算出会话密钥,并看到了 Connector 的静态公钥(身份证)—— 正好拿去和扫码页指纹核对",
        ha="center", fontsize=9.5, color=GREEN, fontweight="bold")

arrow(ax, 0.16, 0.445, 0.84, 0.445, text="→ s, se(我的加密身份证 + 交叉验证)", color=PURPLE, fs=10.5, offset=(0, 0.024))
ax.text(0.50, 0.395, "第 3 句:「轮到我亮身份证了,用你的面具加密(se)」—— 双向身份确认完成", ha="center", fontsize=9.5, color=GREY)

box(ax, 0.16, 0.28, 0.68, 0.075,
    "握手完成 → 进入 transport 模式:双向对称加密管道,业务密文开始流动", C_XX, ec=GREEN, fs=11, bold=True, lw=2)

box(ax, 0.04, 0.05, 0.44, 0.16,
    "特点:事先谁也不用认识谁\n双方身份都在握手中「现场交换」\n代价:3 条消息 = 1.5 个往返", C_NEUTRAL, ec=GREY, fs=10)
box(ax, 0.54, 0.05, 0.42, 0.16,
    "身份隐藏:发起方 8 级(强)\n身份证第 3 条才发、已加密\n响应方 1 级(弱,明文可查)", C_RELAY, ec=AMBER, fs=10)
fig.savefig(os.path.join(OUT, "d4a-fig3-xx.png"), bbox_inches="tight", facecolor=BG)
plt.close(fig)

# ============ 图4:IK 握手两条消息 ============
fig, ax = new_fig(11.5, 8.0, "图4 · IK 两条消息:老熟人一句暗号就开聊(1 个往返,支持 0-RTT)")

box(ax, 0.30, 0.82, 0.40, 0.09,
    "前提(硬门槛):手机在握手之前,就必须已经可靠持有 Connector 的静态公钥 s",
    C_WARN, ec=RED, fs=11, bold=True, lw=2)
ax.text(0.5, 0.775, "规范里记作预消息 ← s —— 没有它,IK 脚本根本开不了场", ha="center", fontsize=9.5, color=GREY)

box(ax, 0.05, 0.60, 0.20, 0.11, "手机\n发起方 initiator", C_PHONE, ec=PURPLE, fs=11.5, bold=True)
box(ax, 0.75, 0.60, 0.20, 0.11, "Connector\n响应方 responder", C_CONN, ec=BLUE, fs=11.5, bold=True)
ax.plot([0.15, 0.15], [0.13, 0.60], color=GREY, lw=1.2, ls=":")
ax.plot([0.85, 0.85], [0.13, 0.60], color=GREY, lw=1.2, ls=":")

arrow(ax, 0.16, 0.545, 0.84, 0.545, text="→ e, es, s, ss(面具+身份证一次全交)", color=BLUE, fs=10.5, offset=(0, 0.024))
ax.text(0.50, 0.495, "第 1 句:「暗号!」—— 用你(已知的)身份证和我的面具先算 es,再互碰身份证 ss;\n顺带可以加密捎上第一段业务数据 = 0-RTT(零往返就送信)",
        ha="center", fontsize=9.5, color=GREY, linespacing=1.4)

arrow(ax, 0.84, 0.405, 0.16, 0.405, text="← e, ee, se(回面具,补上新鲜 DH)", color=GREEN, fs=10.5, offset=(0, 0.024))
ax.text(0.50, 0.355, "第 2 句:「对上了,换新面具再碰一次(ee/se)」—— 前向 secrecy 补齐,管道建成", ha="center", fontsize=9.5, color=GREY)

box(ax, 0.16, 0.26, 0.68, 0.07,
    "第 2 条回来即完成:全程 2 条消息 = 1 个往返,比 XX 少半圈", C_IK, ec=BLUE, fs=11, bold=True, lw=2)

box(ax, 0.04, 0.05, 0.44, 0.15,
    "特点:快、第一条消息就能带货\n但发起方身份证首条就发出\n(只加密给已知对端,旁观者能对暗号猜人)", C_NEUTRAL, ec=GREY, fs=10)
box(ax, 0.54, 0.05, 0.42, 0.15,
    "身份隐藏:发起方 4 级(中)\n响应方 3 级(中)\n且依赖「提前拿到真钥匙」这一前提", C_RELAY, ec=AMBER, fs=10)
fig.savefig(os.path.join(OUT, "d4a-fig4-ik.png"), bbox_inches="tight", facecolor=BG)
plt.close(fig)

# ============ 图5:XX vs IK 六维对比矩阵 ============
fig, ax = new_fig(11.5, 7.4, "图5 · XX vs IK 六维对比:快与稳妥的经典权衡")

cols = [0.04, 0.30, 0.63]
widths = [0.26, 0.33, 0.33]
headers = ["维度", "XX(陌生人互验)", "IK(老熟人直达)"]
rows = [
    ("消息数 / 往返", "3 条 = 1.5 RTT", "2 条 = 1 RTT(快半圈)"),
    ("开场前提", "无:双方互不认识也能握", "发起方必须事先可靠持有\n响应方静态公钥(硬门槛)"),
    ("0-RTT 捎带业务数据", "不支持", "支持(第 1 条消息即可带货)"),
    ("身份隐藏(发起方/响应方)", "8 级 / 1 级\n发起方保护更强", "4 级 / 3 级\n发起方身份证首条即发出"),
    ("与扫码+一次性 token 的相性", "天然兼容:身份握手中现场交换,\n正好接上指纹核对环节", "需要先解决「公钥从哪来、\n凭什么信它」的绑定问题"),
    ("业界角色", "WhatsApp/libp2p 的首次握手;\nlibp2p 最终只留 XX", "WireGuard 主力;WhatsApp\n缓存公钥后的快速重连"),
]
row_h = 0.108
y0 = 0.82
for j, htxt in enumerate(headers):
    box(ax, cols[j], y0, widths[j], 0.08, htxt, INK if j else C_NEUTRAL,
        ec=INK, fs=12, bold=True, tc="#ffffff" if j else INK)
for i, row in enumerate(rows):
    y = y0 - 0.085 - i * row_h - row_h
    fcs = [C_NEUTRAL, C_XX, C_IK]
    for j, cell in enumerate(row):
        box(ax, cols[j], y, widths[j], row_h - 0.012, cell, fcs[j],
            ec=GREY if j == 0 else (GREEN if j == 1 else BLUE), fs=9.3,
            bold=(j == 0), lw=1.4)

ax.text(0.5, 0.018, "一句话:XX 用「多半圈」换「零前提 + 发起方强隐藏」;IK 用「一个硬前提」换「快半圈 + 0-RTT」",
        ha="center", fontsize=11.5, fontweight="bold", color=RED)
fig.savefig(os.path.join(OUT, "d4a-fig5-matrix.png"), bbox_inches="tight", facecolor=BG)
plt.close(fig)

# ============ 图6:身份隐藏等级标尺 ============
fig, ax = new_fig(11.5, 6.2, "图6 · 身份隐藏等级:旁观者能从握手消息里「认出你是谁」吗?(0=裸奔,9=藏进保险箱)")

def gauge(y, label, grade, color, note):
    ax.text(0.16, y + 0.045, label, ha="center", fontsize=10.5, fontweight="bold", color=INK)
    ax.add_patch(FancyBboxPatch((0.24, y), 0.52, 0.05, boxstyle="round,pad=0.005",
                                fc=C_NEUTRAL, ec=GREY, lw=1))
    ax.add_patch(FancyBboxPatch((0.24, y), 0.52 * grade / 9.0, 0.05, boxstyle="round,pad=0.005",
                                fc=color, ec=color, lw=1))
    ax.text(0.78, y + 0.025, f"{grade} 级", ha="left", va="center", fontsize=11.5,
            fontweight="bold", color=color)
    ax.text(0.24, y - 0.032, note, ha="left", va="top", fontsize=8.8, color=GREY, linespacing=1.3)

gauge(0.80, "XX · 发起方(手机)", 8, GREEN, "身份证第 3 条消息才发、且已加密;主动攻击者日后拿到候选私钥才能「对暗号」确认")
gauge(0.60, "XX · 响应方(Connector)", 1, RED, "身份证第 2 条发出,虽有 ee 加密,但任何路人都能先发起握手骗它亮证(可探测)")
gauge(0.40, "IK · 发起方(手机)", 4, AMBER, "身份证第 1 条就发出(只加密给已知对端);被动旁观者可以拿候选公钥「对暗号」试认")
gauge(0.20, "IK · 响应方(Connector)", 3, BLUE, "响应方身份本来就是前提(发起方早知道),旁观者也能观察到「谁在响应」")

box(ax, 0.06, 0.015, 0.88, 0.10,
    "对 NEW-Utell 的含义:手机(发起方)是隐私权重更高的一端 —— 它随处移动、经 Relay 接入;\nXX 把手机身份藏到 8 级,代价只是多半圈握手。",
    C_XX, ec=GREEN, fs=10.5)
fig.savefig(os.path.join(OUT, "d4a-fig6-hiding.png"), bbox_inches="tight", facecolor=BG)
plt.close(fig)

# ============ 图7:结合扫码配对的完整首发流程(推荐路径) ============
fig, ax = new_fig(11.5, 8.6, "图7 · 推荐路径:扫码 + 一次性 token + 指纹核对 + XX 握手 —— 每一环扣一环")

steps = [
    (0.80, "① Connector 首启生成静态密钥对(身份证),\n亮出二维码:一次性 token(5 分钟)+ Relay 地址", C_CONN, BLUE),
    (0.66, "② 手机扫码 → 凭 token 向 Relay 换取配对票据\n(token 一次性、过期/已用即拒 —— B1 已冻结)", C_RELAY, AMBER),
    (0.52, "③ 手机作为发起方,与 Connector 开始 XX 握手\n第 2 条消息收到 Connector 加密身份证(静态公钥)", C_XX, GREEN),
    (0.38, "④ 手机屏显示公钥指纹,Connector 屏同步显示\n用户肉眼核对一致 → 点「确认配对」(挡住中间人)", C_RELAY, AMBER),
    (0.24, "⑤ 第 3 条消息手机亮出加密身份证 → 双向确认完成\npairing 落库(pairing_id + 两端公钥指纹),管道开通", C_XX, GREEN),
    (0.10, "⑥ 此后重连:双方已互存静态公钥 → 具备升级 IK 的\n前提(D4 未决项:是否引入 Noise Pipes 式加速)", C_NEUTRAL, GREY),
]
for y, txt, fc, ec in steps:
    box(ax, 0.04, y, 0.62, 0.11, txt, fc, ec=ec, fs=10, lw=1.8)
for i in range(len(steps) - 1):
    arrow(ax, 0.35, steps[i][0] - 0.004, 0.35, steps[i + 1][0] + 0.11 + 0.004, color=GREY, lw=1.6)

box(ax, 0.70, 0.24, 0.28, 0.67,
    "XX 与流程严丝合缝:\n\n身份在握手中「现场\n交换」,正好嵌进\n「先看到指纹、再确\n认配对」的顺序。\n\n若改用 IK:第③步开\n场就要先有对方身份\n证 —— 要么二维码扩\n容塞进整个静态公钥,\n要么被迫信任 Relay\n转交的公钥,等于新\n增「Relay 不可作恶」\n的信任假设,与蒙眼\n总机定位冲突。",
    C_WARN, ec=RED, fs=9.2, lw=1.8)
fig.savefig(os.path.join(OUT, "d4a-fig7-flow.png"), bbox_inches="tight", facecolor=BG)
plt.close(fig)

# ============ 图8:Noise Pipes 演进路线 + 业界参照 ============
fig, ax = new_fig(11.5, 7.0, "图8 · 演进路线:XX 首发不堵死未来 —— Noise Pipes 的「先 XX、后 IK」三段式")

box(ax, 0.04, 0.56, 0.26, 0.26, "首次配对\nXX 全握手\n\n互不认识 → 现场交换\n身份 → 手机缓存\nConnector 静态公钥", C_XX, ec=GREEN, fs=10.5, bold=True, lw=2)
box(ax, 0.38, 0.56, 0.26, 0.26, "日常重连\nIK 零往返\n\n用缓存的公钥直接开聊,\n第 1 条消息就捎业务数据\n(快半圈 + 0-RTT)", C_IK, ec=BLUE, fs=10.5, bold=True, lw=2)
box(ax, 0.72, 0.56, 0.26, 0.26, "对端换证了?\nXXfallback 兜底\n\nIK 解不开 → 自动退回\n一次 XX,重新交换身份", C_RELAY, ec=AMBER, fs=10.5, bold=True, lw=2)
arrow(ax, 0.30, 0.69, 0.38, 0.69, text="缓存公钥", color=GREEN, fs=9.5, offset=(0, 0.03))
arrow(ax, 0.64, 0.69, 0.72, 0.69, text="解密失败", color=AMBER, fs=9.5, offset=(0, 0.03))

ax.text(0.5, 0.47, "业界参照(真实生产验证过的取舍):", ha="center", fontsize=12.5, fontweight="bold", color=INK)
refs = [
    (0.04, "WhatsApp", "完整采用 Noise Pipes:首连 XX、缓存后 IK、\n失败 XXfallback —— 就是上图这套", GREEN),
    (0.38, "WireGuard", "只用 IK(实为 IKpsk2):配置时人工分发公钥,\n前提天然满足,吃到全部速度红利", BLUE),
    (0.72, "libp2p", "曾上 Noise Pipes,后砍掉 IK/XXfallback 只留 XX:\n「多半圈」的收益抵不过 ~1000 行复杂度与回退 bug", RED),
]
for x, name, desc, c in refs:
    box(ax, x, 0.22, 0.26, 0.20, name, C_NEUTRAL, ec=c, fs=12.5, bold=True, tc=c, lw=2)
    ax.text(x + 0.13, 0.205, desc, ha="center", va="top", fontsize=8.8, color=GREY, linespacing=1.45)

box(ax, 0.06, 0.02, 0.88, 0.11,
    "对 D4a 的含义:首发选 XX = 站在 WhatsApp 与 libp2p 两条路的共同起点上;\n未来若要快,可平滑加 IK(公钥已缓存);若嫌复杂,停在 XX 也有 libp2p 背书。",
    C_XX, ec=GREEN, fs=10.5, bold=True)
fig.savefig(os.path.join(OUT, "d4a-fig8-pipes.png"), bbox_inches="tight", facecolor=BG)
plt.close(fig)

print("D4a 图表已生成到", OUT)
