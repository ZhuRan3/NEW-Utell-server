#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""生成 D3b 公网 TLS/WSS 边缘代理学习文档所需的 PNG 图表
与 gen_figures.py / gen_figures_d3a.py 同约定:matplotlib + Hiragino Sans GB,输出到 assets/"""
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
RED = "#dc2626"; GREY = "#6b7280"; BG = "#ffffff"
C_CADDY = "#dcfce7"; C_NGINX = "#dbeafe"; C_GO = "#fde8d8"
C_WARN = "#fee2e2"; C_RELAY = "#fef3c7"; C_NEUTRAL = "#f1f5f9"

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
    ax.text(0.5, 0.97, title, ha="center", va="top", fontsize=16, fontweight="bold", color=INK)
    return fig, ax

# ============ 图1:边缘代理站在哪 —— 公网门口的「前台」 ============
fig, ax = new_fig(11.5, 6.4, "图1 · 边缘代理的位置:站在公网门口的「前台 + 安检」")

box(ax, 0.02, 0.58, 0.17, 0.20, "手机 App", C_NGINX, fs=12.5, bold=True)
box(ax, 0.02, 0.30, 0.17, 0.20, "Connector\n(家中树莓派)", C_NGINX, fs=12.5, bold=True)

box(ax, 0.27, 0.42, 0.16, 0.24, "公网\nInternet", C_NEUTRAL, ec=GREY, fs=12)

box(ax, 0.51, 0.30, 0.22, 0.48, "边缘代理(本题主角)\n\n· 占住公网 443 端口\n"
    "· 终止 TLS(解开传输层加密)\n· 验明证书、挡住明文流量\n· 把连接转交给内网 Relay",
    C_CADDY, ec=GREEN, fs=10.5, bold=True, lw=2.2)

box(ax, 0.81, 0.36, 0.17, 0.36, "Relay\n(应用服务)\n监听 127.0.0.1\n:8080 明文", C_RELAY, ec=AMBER, fs=11, bold=True, lw=2)

arrow(ax, 0.19, 0.68, 0.27, 0.62, color=BLUE)
arrow(ax, 0.19, 0.40, 0.27, 0.46, color=BLUE)
arrow(ax, 0.43, 0.54, 0.51, 0.54, text="wss:// 443 端口", color=GREEN, offset=(0, 0.05))
arrow(ax, 0.73, 0.54, 0.81, 0.54, text="ws:// 明文内网", color=AMBER, offset=(0, 0.05))

box(ax, 0.04, 0.06, 0.60, 0.16,
    "关键区分:边缘代理解开的只是「传输层 TLS 加密」(防窃听的运输保险箱);\n"
    "业务正文的端到端加密(E2EE)仍在手机与 Connector 之间,Relay 和代理一样看不到内容。",
    C_NEUTRAL, ec=GREY, fs=10)
box(ax, 0.68, 0.06, 0.30, 0.16,
    "D3b 要回答的问题:\n这个「门口」让谁来站?\nCaddy / Nginx / 谁也不站(Go 直连)",
    C_WARN, ec=RED, fs=10, bold=False)
fig.savefig(os.path.join(OUT, "d3b-fig1-edge-position.png"), bbox_inches="tight", facecolor=BG)
plt.close(fig)

# ============ 图2:TLS 握手 + ACME 自动领证 ============
fig, ax = new_fig(11.5, 8.6, "图2 · 两件地基事:TLS 握手(每次连接)与 ACME 自动领证(每个季度)")

# 上半:TLS 握手
ax.text(0.5, 0.90, "上半 · TLS 握手:每条连接建立时的一次「查验身份证 + 现场配钥匙」",
        ha="center", fontsize=12, fontweight="bold", color=BLUE)
box(ax, 0.06, 0.60, 0.16, 0.10, "客户端\n(手机/Connector)", C_NGINX, fs=10.5, bold=True)
box(ax, 0.78, 0.60, 0.16, 0.10, "服务器\n(边缘代理)", C_CADDY, fs=10.5, bold=True)
ax.plot([0.14, 0.14], [0.36, 0.60], color=GREY, lw=1.2, ls=":")
ax.plot([0.86, 0.86], [0.36, 0.60], color=GREY, lw=1.2, ls=":")
arrow(ax, 0.15, 0.555, 0.85, 0.555, text="① ClientHello:我会这些加密算法", color=INK, offset=(0, 0.022))
arrow(ax, 0.85, 0.505, 0.15, 0.505, text="② 这是我的证书(身份证):域名 + CA 签名 + 公钥", color=BLUE, offset=(0, 0.022))
ax.text(0.50, 0.455, "③ 客户端验证书:CA 签名是真的吗?域名对吗?过期了吗?—— 不信就断开报警",
        ha="center", fontsize=10, color=RED, fontweight="bold")
arrow(ax, 0.15, 0.405, 0.85, 0.405, text="④ 用证书里的公钥完成密钥交换,双方各算出同一把会话密钥", color=GREEN, offset=(0, -0.04))
box(ax, 0.24, 0.325, 0.52, 0.05,
    "此后所有流量用会话密钥对称加密 —— 窃听者只看到乱码", C_CADDY, ec=GREEN, fs=10)

# 下半:ACME
ax.text(0.5, 0.27, "下半 · ACME 自动领证:服务器自己向 CA 证明「这域名归我管」,全程无人值守",
        ha="center", fontsize=12, fontweight="bold", color=AMBER)
box(ax, 0.04, 0.06, 0.17, 0.10, "边缘代理\n(或 Go 服务自己)", C_RELAY, fs=10, bold=True)
box(ax, 0.79, 0.06, 0.17, 0.10, "CA\nLet's Encrypt", C_NEUTRAL, ec=GREY, fs=10.5, bold=True)
arrow(ax, 0.21, 0.135, 0.79, 0.135, text="① 我要给 api.example.com 领证", color=INK, offset=(0, 0.02))
arrow(ax, 0.79, 0.095, 0.21, 0.095, text="② 出题:请在你的 80 端口放下这串令牌(HTTP-01 挑战)", color=AMBER, offset=(0, -0.035))
ax.text(0.50, 0.035, "③ CA 从公网访问该域名验证令牌 → 控制权属实 → 签发证书(有效期 90 天)→ 代理在过期前自动续期,循环往复",
        ha="center", fontsize=9.5, color=GREEN, fontweight="bold")
ax.text(0.50, 0.185, "另有两种题型:TLS-ALPN-01(在 443 端口做一次特殊握手)/ DNS-01(改一条 TXT 记录,唯一支持泛域名 *.example.com)",
        ha="center", fontsize=9, color=GREY)
ax.text(0.50, 0.225, "前提:域名 DNS 已指向这台服务器,且 80/443 端口从公网可达 —— 三种方案全都绕不开这一条",
        ha="center", fontsize=9.5, color=RED, fontweight="bold")
fig.savefig(os.path.join(OUT, "d3b-fig2-tls-acme.png"), bbox_inches="tight", facecolor=BG)
plt.close(fig)

# ============ 图3:WebSocket Upgrade 穿过反向代理 ============
fig, ax = new_fig(11.5, 7.2, "图3 · WebSocket 不是普通 HTTP:一次「升级」之后,变成一条不挂断的双向管道")

box(ax, 0.04, 0.66, 0.15, 0.12, "客户端", C_NGINX, fs=12, bold=True)
box(ax, 0.42, 0.66, 0.17, 0.12, "边缘代理\n(反代)", C_CADDY, fs=11.5, bold=True)
box(ax, 0.81, 0.66, 0.15, 0.12, "Relay\n(Go)", C_RELAY, ec=AMBER, fs=11.5, bold=True)
for x in (0.115, 0.505, 0.885):
    ax.plot([x, x], [0.14, 0.66], color=GREY, lw=1.2, ls=":")

arrow(ax, 0.12, 0.60, 0.50, 0.60, text="① GET /ws  HTTP/1.1 + Upgrade: websocket", color=INK, fs=9, offset=(0, 0.024))
arrow(ax, 0.51, 0.545, 0.88, 0.545, text="② 代理必须原样转发 Upgrade/Connection 头", color=BLUE, fs=9, offset=(0, 0.024))
arrow(ax, 0.88, 0.49, 0.51, 0.49, text="③ 101 Switching Protocols(换协议)", color=GREEN, fs=9, offset=(0, 0.024))
arrow(ax, 0.50, 0.435, 0.12, 0.435, text="④ 101 回给客户端 —— 升级完成", color=GREEN, fs=9, offset=(0, 0.024))

ax.plot([0.07, 0.95], [0.375, 0.375], color=GREY, lw=1, ls="--")
box(ax, 0.10, 0.22, 0.80, 0.11,
    "⑤ 从此这条 TCP 连接变成双向管道:双方随时互发消息,挂上几天几周\n"
    "代理退化为「搬运工」:不再看懂请求/响应,只是原样搬运字节流", C_CADDY, ec=GREEN, fs=10.5, bold=True)

box(ax, 0.06, 0.045, 0.42, 0.13,
    "对代理的三个特殊要求:\n· 必须转发 Upgrade 头(Nginx 要手工配)\n"
    "· 空闲超时必须放宽(默认 60s 会误杀)\n· reload/重启 = 剪断所有管道", C_WARN, ec=RED, fs=9.5)
box(ax, 0.54, 0.045, 0.42, 0.13,
    "这就是为什么 WSS 选型不能只看\n「能不能反代」——\n要看它怎么对待长连接:\n超时策略、reload 行为、心跳配合", C_RELAY, ec=AMBER, fs=9.5)
fig.savefig(os.path.join(OUT, "d3b-fig3-ws-upgrade.png"), bbox_inches="tight", facecolor=BG)
plt.close(fig)

# ============ 图4:三方案组件结构对比 ============
fig, ax = new_fig(11.5, 7.6, "图4 · 三个候选的组件结构:门口站几个人、各干几份活")

col_x = [0.04, 0.37, 0.70]
col_w = 0.27
titles = ["方案一 · Caddy(推荐)", "方案二 · Nginx", "方案三 · Go 直连(autocert)"]
colors = [C_CADDY, C_NGINX, C_GO]
ecs = [GREEN, BLUE, AMBER]
for x, t, c, e in zip(col_x, titles, colors, ecs):
    box(ax, x, 0.80, col_w, 0.08, t, c, ec=e, fs=12, bold=True, lw=2)

# 方案一:Caddy 单进程
box(ax, col_x[0], 0.47, col_w, 0.27,
    "Caddy 单进程\n\n· 监听 443 终止 TLS\n· 内置 ACME:自动领证/续期\n"
    "· 原生识别 WS 升级并转发", C_CADDY, ec=GREEN, fs=10.5)
box(ax, col_x[0], 0.30, col_w, 0.11, "Relay(Go):8080 明文", C_RELAY, ec=AMBER, fs=10.5)
arrow(ax, col_x[0]+col_w/2, 0.47, col_x[0]+col_w/2, 0.41, color=INK)
ax.text(col_x[0]+col_w/2, 0.245, "组件数:2(Caddy + Relay)\n配置:3 行 Caddyfile",
        ha="center", fontsize=9.5, color=GREEN, fontweight="bold")

# 方案二:Nginx + certbot/acme.sh 两件套
box(ax, col_x[1], 0.56, col_w, 0.18,
    "Nginx\n· 监听 443 终止 TLS\n· WS 需手工配 Upgrade 头", C_NGINX, ec=BLUE, fs=10.5)
box(ax, col_x[1]+0.02, 0.44, col_w-0.04, 0.09,
    "certbot / acme.sh(独立工具)\n负责领证,续期后触发 nginx reload", C_NEUTRAL, ec=GREY, fs=9)
box(ax, col_x[1], 0.30, col_w, 0.11, "Relay(Go):8080 明文", C_RELAY, ec=AMBER, fs=10.5)
arrow(ax, col_x[1]+col_w/2, 0.44, col_x[1]+col_w/2, 0.41, color=INK)
arrow(ax, col_x[1]+col_w/2, 0.53, col_x[1]+col_w/2, 0.56, color=GREY, ls="--")
ax.text(col_x[1]+col_w/2, 0.245, "组件数:3(nginx + 证书工具 + Relay)\n配置:server 块 + map + 证书钩子",
        ha="center", fontsize=9.5, color=BLUE, fontweight="bold")

# 方案三:Go 直连
box(ax, col_x[2], 0.47, col_w, 0.27,
    "Relay(Go 进程)直接监听 443\n\n· 自己终止 TLS(标准库)\n· autocert 库内置 ACME 自动领证\n"
    "· 无任何前置代理", C_GO, ec=AMBER, fs=10.5, lw=2)
ax.text(col_x[2]+col_w/2, 0.40, "", ha="center")
ax.text(col_x[2]+col_w/2, 0.245, "组件数:1(只有 Relay)\n配置:一段 Go 代码",
        ha="center", fontsize=9.5, color=AMBER, fontweight="bold")

box(ax, 0.04, 0.06, 0.93, 0.13,
    "同一条及格线:三个方案都能做到「443 公网加密入口 + 证书自动续期 + WSS 可达 Relay」。\n"
    "差别全在:组件多少、配置心智、reload 时对长连接的态度、以及未来要加新功能(多服务/限流/WAF)时谁接得住。",
    C_NEUTRAL, ec=GREY, fs=10.5)
fig.savefig(os.path.join(OUT, "d3b-fig4-three-options.png"), bbox_inches="tight", facecolor=BG)
plt.close(fig)

# ============ 图5:reload 时长连接的命运 —— Nginx vs Caddy ============
fig, ax = new_fig(11.5, 6.8, "图5 · 改一次配置(reload)时,已有长连接的命运 —— 三方案最大的分水岭")

# 时间轴
ax.text(0.06, 0.86, "Nginx(master + 多 worker 架构)", fontsize=12.5, fontweight="bold", color=BLUE)
ax.plot([0.08, 0.95], [0.78, 0.78], color=GREY, lw=1.2)
ax.annotate("reload 时刻", xy=(0.52, 0.78), xytext=(0.52, 0.83),
            ha="center", fontsize=10, color=RED, fontweight="bold",
            arrowprops=dict(arrowstyle="-|>", color=RED))
ax.plot([0.10, 0.90], [0.72, 0.72], color=GREEN, lw=3)
ax.text(0.91, 0.72, "旧连接 A:老 worker 继续服务,自然走完", fontsize=9, color=GREEN, va="center")
ax.plot([0.10, 0.78], [0.66, 0.66], color=GREEN, lw=3)
ax.text(0.79, 0.66, "旧连接 B:继续活着", fontsize=9, color=GREEN, va="center")
ax.plot([0.52, 0.92], [0.60, 0.60], color=BLUE, lw=3)
ax.text(0.93, 0.60, "新连接:由新 worker(新配置)接待", fontsize=9, color=BLUE, va="center")
ax.text(0.50, 0.545, "→ 优雅:旧连接零感断,代价是老 worker 要陪跑到长连接自然结束",
        ha="center", fontsize=10, color=INK, fontweight="bold")

ax.text(0.06, 0.42, "Caddy(单进程,整体换配置)", fontsize=12.5, fontweight="bold", color=GREEN)
ax.plot([0.08, 0.95], [0.34, 0.34], color=GREY, lw=1.2)
ax.annotate("reload 时刻", xy=(0.52, 0.34), xytext=(0.52, 0.39),
            ha="center", fontsize=10, color=RED, fontweight="bold",
            arrowprops=dict(arrowstyle="-|>", color=RED))
ax.plot([0.10, 0.52], [0.28, 0.28], color=GREEN, lw=3)
ax.plot([0.52, 0.56], [0.28, 0.28], color=RED, lw=3, ls=":")
ax.text(0.57, 0.28, "旧连接 A:被关闭 ✂", fontsize=9, color=RED, va="center")
ax.plot([0.10, 0.52], [0.22, 0.22], color=GREEN, lw=3)
ax.plot([0.52, 0.56], [0.22, 0.22], color=RED, lw=3, ls=":")
ax.text(0.57, 0.22, "旧连接 B:同样被关闭 ✂(stream_close_delay 只能让它「关得体面些」)", fontsize=9, color=RED, va="center")
ax.plot([0.52, 0.92], [0.16, 0.16], color=BLUE, lw=3)
ax.text(0.93, 0.16, "新连接:走新配置", fontsize=9, color=BLUE, va="center")
ax.text(0.50, 0.095, "→ 官方默认值是「立即关闭旧流」(stream_close_delay=0);#5471 已关闭、#6420 标记 Not planned、#7222 仍开放。\nstream_close_delay 只能给旧连接有限排空窗口;客户端仍需自动重连,运维上压低 reload 频率或改用 Admin API 动态改 upstream",
        ha="center", fontsize=10, color=RED, fontweight="bold")

ax.text(0.50, 0.025, "Go 直连:没有 reload 这回事 —— 证书热替换(GetCertificate 回调)无需重启;但改代码发版 = 进程重启 = 同样断全部连接",
        ha="center", fontsize=9.5, color=AMBER, fontweight="bold")
fig.savefig(os.path.join(OUT, "d3b-fig5-reload.png"), bbox_inches="tight", facecolor=BG)
plt.close(fig)

# ============ 图6:六维对比热力矩阵 ============
fig, ax = plt.subplots(figsize=(11.5, 6.8), dpi=160)
fig.patch.set_facecolor(BG)
ax.set_xlim(0, 4); ax.set_ylim(0, 7.6); ax.axis("off")
ax.text(2, 7.35, "图6 · 三候选六维对比热力矩阵(绿=占优 / 黄=可用但有条件 / 红=短板)",
        ha="center", fontsize=15, fontweight="bold", color=INK)

cols = ["维度", "方案一 · Caddy", "方案二 · Nginx", "方案三 · Go 直连"]
rows = [
    ("证书自动化",   "内置 ACME,开箱即续期", "certbot/acme.sh 拼装", "autocert 内置,自管缓存与限流", 0, 1, 1),
    ("WSS 开箱",     "原生识别,零配置",      "需手工 map+Upgrade 头", "无代理,本就直连",            0, 1, 0),
    ("reload 对长连接", "默认关闭旧流;可有限排空", "旧 worker 自然排空",  "无 reload;发版重启会断",      2, 0, 1),
    ("配置/心智负担", "3 行 Caddyfile",        "指令繁多,概念较老",     "全在 Go 代码里,无新组件",    0, 2, 0),
    ("运维组件数",    "2 个",                  "3 个(含证书工具)",      "1 个",                        1, 2, 0),
    ("生态与功能上限", "年轻,插件/API 现代",   "最成熟,资料案例最多",   "要新功能=自己写代码",         1, 0, 2),
]
shade = {0: "#dcfce7", 1: "#fef3c7", 2: "#fee2e2"}
tcol  = {0: "#166534", 1: "#92400e", 2: "#991b1b"}
col_x = [0.0, 1.0, 2.0, 3.0]
for j, c in enumerate(cols):
    box(ax, col_x[j]+0.03, 6.55, 0.94, 0.5, c, "#f1f5f9", ec=GREY, fs=11, bold=True)
for i, (dim, a, b, cc, sa, sb, sc) in enumerate(rows):
    y = 5.75 - i * 0.95
    box(ax, 0.03, y, 0.94, 0.8, dim, "#f8fafc", ec=GREY, fs=10.5, bold=True)
    for j, (txt, s) in enumerate([(a, sa), (b, sb), (cc, sc)]):
        box(ax, col_x[j+1]+0.03, y, 0.94, 0.8, txt, shade[s], ec=tcol[s], fs=9.5, tc=tcol[s])
ax.text(2, 0.12, "结论与 TS-SV-2026-001 一致:暂定推荐 Caddy —— 接受默认 reload 关闭旧流,用「有限排空 + 低频 reload + 客户端重连 + Admin API 动态 upstream」对冲",
        ha="center", fontsize=10.5, fontweight="bold", color=INK)
fig.savefig(os.path.join(OUT, "d3b-fig6-matrix.png"), bbox_inches="tight", facecolor=BG)
plt.close(fig)

print("done ->", OUT)
