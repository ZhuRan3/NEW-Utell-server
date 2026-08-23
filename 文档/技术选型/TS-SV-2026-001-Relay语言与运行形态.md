# TS-SV-2026-001 Relay 语言与运行形态

> 状态：开发者已批准（2026-08-23）
> **注意：本文件的候选框架与 AI 建议仅为调研参考材料（证据本身为 2026-08-22 实时核实，有效）；正式选型结论以逐项 Q&A 确认为准，确认前不得据此开始实现。**
> Owner：Zhu3xx
> 创建日期：2026-08-22
> 关联：Q-SV-2026-001（重新开放选型）
> AI 建议不得替代文末的开发者决定

## 1. 问题定义

为安全路由 Relay 选择语言/运行时与运行形态。Relay 必须稳定承载手机与 Connector 的公网 WSS 会话，完成身份、公钥登记、二维码配对、单主 Connector 约束、撤销和密文路由，同时保持为无法解密业务正文的轻量中转层。

- 范围：Relay 服务语言/运行时、并发模型、部署产物形态；边缘代理与元数据存储随本决定一并给出建议，但允许单独重审。
- 非范围：Connector、Pi、手机端技术；业务数据库与长期消息队列（PRD 明确禁止）。
- 最晚决定时间：开始 Relay 生产骨架前。

**架构前提（来自本仓库架构基线与 PRD）**：应用层 E2EE 在手机与 Connector 端点终止，Relay 只转发密文信封、不持任何解密密钥。因此 **Relay 自身不需要 Noise/E2EE 协议实现**，密码库生态不是本决策的维度；它是手机端（TS-PH-2026-001）与 Connector 侧的维度。

## 2. 硬约束（来自 PRD）

- 公网入口 443/TLS/WSS；证书可自动续期。
- Relay 不持端点私钥，不读取、解密或持久化业务正文；不建立离线业务队列。
- 一个账号最多一台 active 主 Connector；replacement/撤销必须原子化。
- 只保存 pairing、设备公钥、撤销、限流和最小脱敏审计元数据；审计留存 14 天（Q-SV-2026-011 已确认）。
- 必须支持心跳、ACK、序号、背压、限流、消息大小上限和稳定错误码。
- 首发为单台云主机可承载的轻量部署；不引入 Kubernetes、Redis、Kafka 等重型依赖。
- 必须提供健康检查、结构化脱敏日志、指标、备份/恢复和回滚。

## 3. 候选方案

| 候选 | 组成 | 当前版本（2026-08-22 核实） | 许可证 |
| --- | --- | --- | --- |
| A. Go | Go + coder/websocket + modernc.org/sqlite（纯 Go 无 cgo）+ 标准库 crypto/tls | Go 1.27.0（2026-08-19）；coder/websocket v1.8.15（2026-06-15）；modernc.org/sqlite v1.57.0（2026-08-19） | BSD-3-Clause / MIT 系 |
| B. Rust | tokio + axum/tokio-tungstenite + rusqlite（bundled）+ rustls | Rust 1.98.0（2026-08-20）；axum 0.8.9；tokio-tungstenite 0.30.0；rusqlite 0.40.2；rustls 0.23.43 | MIT OR Apache-2.0 |
| C. Node/TypeScript | Node LTS + ws + better-sqlite3 | Node v24.19.0 Active LTS（2026-08-03）；ws 8.21.3（2026-08-07）；better-sqlite3 13.0.3（2026-08-05） | MIT |

边缘代理候选（附属决定）：Caddy v2.11.4（自动 HTTPS、原生 WSS 反代；默认配置卸载会关闭既有 WSS，`stream_close_delay` 只能提供有限排空窗口）；Nginx stable 1.30.4（WSS 需手工配置 Upgrade 头，证书自动化需自行组合）。

## 4. 证据

证据等级：E1=官方资料；E2=本机环境核实（2026-08-22 审计）。全部 E1 事实由官方 API/文档于 2026-08-22 实时检索。

| 证据 | 等级 | 结论 |
| --- | --- | --- |
| Go 发布历史与下载 JSON（go.dev） | E1 | 1.27.0 于 2026-08-19 发布；半年节奏，两大版本受支持 |
| coder/websocket 仓库 API | E1 | 维护活跃（2026-06 仍发版）；gorilla/websocket 事实停滞（最后提交 2025-03），不选用 |
| modernc.org/sqlite（GitLab） | E1 | 纯 Go 无 cgo，2026-08 当月发版，配合 CGO_ENABLED=0 可全静态单二进制 |
| Rust releases / crates.io | E1 | 1.98.0 发布；tokio 已 1.x，但 axum 0.8 / tokio-tungstenite 0.30 / sqlx 0.9 均为 0.x，允许 minor 破坏性变更 |
| Node dist index.json / npm registry | E1 | v24 Active LTS（Krypton）；ws 与 better-sqlite3 均在 2026-08 当月发版，维护最活跃 |
| Node SEA 文档 | E1 | 单文件打包为实验性，且对 better-sqlite3 这类 native 模块有限制；Node 非单二进制部署 |
| Node "Don't block the event loop" 文档 | E1 | 单线程事件循环下 CPU 密集操作会阻塞全部连接，需 worker_threads 规避 |
| Caddy reverse_proxy 文档与社区 issue（#5471/#6420/#7222） | E1 | 原生 WSS 反代 + 自动 HTTPS；默认 `stream_close_delay=0` 时配置卸载关闭旧流，延迟参数只能有限排空，客户端仍需重连 |
| Nginx WebSocket proxying 文档 | E1 | 功能成熟，需手工 Upgrade 头与自行证书自动化 |
| 本机工具链审计 | E2 | Rust 1.94.1、Node v24.14.0 已就绪；Go 未安装（需安装工具链） |

Noise 生态说明（不计入本决策）：Rust snow 0.10.0 维护活跃；Go flynn/noise 停更约 2.5 年；Node noise-handshake 仅覆盖握手。该事实影响手机端与 Connector 的 E2EE 选型，不影响 Relay。

## 5. 候选矩阵

| 维度 | A. Go | B. Rust | C. Node/TS |
| --- | --- | --- | --- |
| WSS 连接并发模型 | goroutine 连接级并发，适配度高 | tokio async，适配度高 | 事件循环，CPU 密集会阻塞全局 |
| 单机部署产物 | 纯静态单二进制（全链路可无 cgo） | 单二进制（musl/bundled） | 需 Node 运行时；SEA 实验性 |
| 核心库稳定性 | 标准库 + 活跃 1.x 库 | Web 栈核心库全部 0.x | ws/better-sqlite3 成熟活跃 |
| 本机就绪（E2） | 未安装，需装工具链 | 已安装 1.94.1 | 已安装 v24.14.0 |
| 单 Owner 交付成本 | 预计低到中 | 预计高（async/借用检查） | 预计低 |
| 资源可预测性 | 待 Spike（E3） | 强，待 Spike | 基线内存最高，待 Spike |
| 最强失败场景 | 库细节未实测；工具链需安装 | 0.x 升级破坏 + 迭代速度税 | 事件循环阻塞、native ABI、无单二进制 |
| 退出路线 | 保持契约重写服务 | 保持契约重写服务 | 保持契约重写服务 |

容量、背压、内存与尾部延迟数字目前**无官方基准**，一律待 Spike，不以主观分数补齐。

## 6. 失败、迁移和退出路线

三者都只在 Relay Transport 契约之下实现，语言退出不改变业务载荷、错误码和端点语义。迁移成本集中在服务实现本身与运维脚本；元数据 Schema 以 Migration 管理，可随实现导出。最可能失败场景见矩阵末行；各自的容量门槛由 Spike 证据空白清单验证。

## 7. AI 建议

- 推荐：候选 A（Go + coder/websocket + modernc.org/sqlite），边缘代理暂定推荐 Caddy（接受默认 reload 关闭旧流的约束并用低频 reload、有限排空、客户端重连和后续管理 API 动态 upstream 对冲）。
- 理由：Relay 的本职是 WSS 连接级路由 + 最小元数据 + 单机轻量部署。Go 在该边界内证据面最整齐：goroutine 天然匹配连接并发；纯 Go SQLite 使全链路无 cgo、单静态二进制；标准库 TLS 无第三方依赖；核心依赖均为活跃维护的稳定版。Noise 短板与 Relay 无关（E2EE 在端点终止）。
- 关键假设：单 Owner 能在合理成本内安装并维护 Go 工具链；P0 容量为单机量级。
- 置信度：中等（E1/E2 充分，E3 容量证据缺失）。
- 最强反对理由：Rust 资源可预测性更强且本机已就绪；Node 生态维护最活跃且开发最快。若 Spike 显示 Go 连接管理/背压实现成本被低估，应重审 B/C。
- 剩余风险：长连接容量、背压、reload 断连影响均无实测数据；goroutine 泄漏与慢消费者防护需工程验证。
- 仍需证据：见下方 Spike 清单。

### 需 Spike（E3）验证的空白

1. 1 万/10 万空闲 WSS 连接下的 RSS、FD 与心跳开销（容量输入待 ZD 类 Q&A 给出阈值）。
2. 慢消费者背压行为与写缓冲上限。
3. Caddy reload 断连影响面与规避方案。
4. 消息大小上限与分片在反代链路下的实际行为。
5. 静态二进制 RSS 基线与 GC 尾部延迟。

## 8. 开发者决定

- 决定：候选 A——Go（1.27+）+ coder/websocket + modernc.org/sqlite（纯 Go 无 cgo）；边缘代理 Caddy（v2.11+，自动 HTTPS + 原生 WSS 反代）；云服务商阿里云（单台 ECS 轻量部署）（Q-SV-2026-014）
- 批准人 / 日期：Zhu3xx / 2026-08-23
- 理由：Relay 本职为 WSS 连接级路由 + 最小元数据 + 单机轻量部署；Go 证据面最整齐（goroutine 连接并发、全链路无 cgo 静态单二进制、标准库 TLS、活跃稳定依赖）；E2EE 在端点终止，Go 的 Noise 生态短板与 Relay 无关
- 接受的剩余风险：长连接容量/背压无实测数据；Caddy reload 断连需运维规避（低频 reload、客户端重连、后续管理 API 动态 upstream）；Go 工具链需新装
- 必须补齐的证据：第 7 节 Spike 清单 1-5（容量阶梯、背压、reload 影响、消息上限、资源基线）
- 重审条件：Spike 证据显示 Go 路线不达标时，保持 Relay Transport 契约重审 Rust/Node；阿里云区域/备案问题出现时重审服务商
