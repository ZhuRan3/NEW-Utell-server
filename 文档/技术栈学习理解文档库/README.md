# 技术栈学习理解文档库

本目录存放 NEW-Utell 项目中关键概念、需求决策点的学习讲解文档(HTML + PNG 图表),帮助理解 PRD 决策背后的技术原理与业界依据。

## 目录结构

```
技术栈学习理解文档库/
├── README.md                    ← 本索引
├── gen_figures.py               ← C2 图表生成脚本(matplotlib,修改后重跑即可更新 PNG)
├── gen_figures_d3a.py           ← D3a 图表生成脚本
├── gen_figures_d3b.py           ← D3b 图表生成脚本
├── assets/                      ← PNG 图表
│   ├── fig1-architecture.png          (C2)链路结构图:Relay 的视野
│   ├── fig2-lifecycle.png             (C2)审计元数据生命周期流程图
│   ├── fig3-tradeoff.png              (C2)四选项「隐私 × 排障」权衡对比图
│   ├── fig4-benchmark.png             (C2)保留期限业界参照标尺
│   ├── d3a-fig1-relay-context.png     (D3a)Relay 的位置:蒙眼接线总机
│   ├── d3a-fig2-concurrency.png       (D3a)三种并发模型结构对比
│   ├── d3a-fig3-eventloop.png         (D3a)Node 事件循环阻塞 vs Go 多核并行时间轴
│   ├── d3a-fig4-deploy.png            (D3a)三候选部署产物形态对比
│   ├── d3a-fig5-matrix.png             (D3a)三候选六维对比热力矩阵
│   └── d3b-fig*.png                    (D3b)边缘代理、TLS/ACME、WSS、reload 与对比矩阵
├── C2-Relay脱敏审计元数据保留决策.html   ← 打开学习
├── D3a-Relay语言与运行时选型.html        ← 打开学习
└── D3b-公网TLS-WSS边缘代理.html          ← 打开学习
```

## 文档清单

| 文档 | 对应决策/章节 | 内容 |
|---|---|---|
| C2-Relay脱敏审计元数据保留决策.html | 需求问答 C2;PRD FR-008 / 7.2 / 9.2 | Relay 脱敏审计元数据是什么、保留期限的学问、30/7/90 天/不保留四选项对比与推荐 |
| D3a-Relay语言与运行时选型.html | 技术选型 TS-SV-2026-001(D3a) | Relay 语言/运行时三选一:并发模型(goroutine/tokio/事件循环)从零讲懂,Go / Rust / Node 优缺点与部署形态对比,AI 推荐 Go 的证据链与 Spike 空白清单 |
| D3b-公网TLS-WSS边缘代理.html | 技术选型 TS-SV-2026-001(D3b) | 公网 TLS/WSS 边缘代理从零讲解:Caddy、Nginx、Go autocert 直连的机制、配置、优缺点、reload 长连接风险、联网资料与上线验收流程 |

## 使用方式

直接用浏览器打开 HTML 文件即可(图片为相对路径引用,请保持目录结构完整)。

## 更新图表

```bash
cd 文档/技术栈学习理解文档库
python3 gen_figures.py       # C2 图表,需 matplotlib,中文字体 Hiragino Sans GB
python3 gen_figures_d3a.py   # D3a 图表
python3 gen_figures_d3b.py   # D3b 图表
```
