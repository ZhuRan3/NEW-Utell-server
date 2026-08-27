# Connector 职责边界与公开接口范围(第一代 · 最小公开面)

> **状态：草案(pending),2026-08-27 起草,待逐项 Q&A 确认**
> 适用范围：NEW-Utell-phone、NEW-Utell-server,以及消费 `integration-profile` 的 Connector 工程。
> 依据真源:PRD v0.5、两端需求确认台账(A1–A7、B1–B8、D4)、`harness/契约/integration-profile.yaml`(0.1.0)、架构基线。
> 确认口径：本文只**归并**已确认语义，不设默认值；凡"待确认"条目须按 `开发规则规范/01-需求对齐与Q&A规范.md` 一次一问走 Q&A 后回写。Owner 未指定，本文按中立口径起草，签署段落留待确认。
> 粒度约定(2026-08-27 用户拍板):**最小公开面**——只覆盖 Relay↔Connector 传输契约与 Connector 对手机/Relay 公开的服务接口;Pi 内部、Connector 内部数据库 Schema、文件路径、安装运维实现细节**不属于**本文与公开契约。

## 1. 定位

Connector 是四层链路(手机 ↔ Relay ↔ PC Connector ↔ Utell Pi)中的**唯一业务权威**(台账 A2、PRD 0.2):

- Capture 首次且唯一的业务持久化位置是 Connector 权威库(PRD 5.1)。
- 手机卡片是 Connector 状态的只读投影;Connector 生成并下发 Card Projection(PRD 5.1)。
- Connector 是 E2EE 的端点之一(Noise Responder),Relay 只见密文(台账 A3、integration-profile `initiator: phone / responder: connector`)。
- 链路 READY 判定依赖 Connector 的健康上报与能力宣告(PRD 5.2、FR-003)。

## 2. 职责边界

### 2.1 Connector 做(公开面可见行为)

| 职责 | 依据 |
| --- | --- |
| 首启生成并持久化设备静态密钥对；公钥指纹绑定 `pairing_id` | 架构基线 P0 状态与数据、Q-PH/SV-2026-023 |
| 生成配对二维码(名称、版本、公钥指纹、一次性 token,token 建议 5 分钟一次性) | FR-001、B1 |
| 作为 Noise Responder 完成握手；验签；拒绝过期/已用 token、指纹不匹配、已撤销设备 | D4(Q-021/022/023)、FR-001、AC-002 |
| 每 10 秒向链路报告能力与权威库健康状态 | FR-003、C4(10s/30s) |
| Capture 验签、按 `capture_id` 幂等写入权威库、标记 RECEIVED、签发**持久接收回执** | FR-006、AC-014/015 |
| 运行受限 Pi、校验提案 Schema,LogEntry 与 Event 单事务提交并标记 COMMITTED | FR-006、5.3 |
| 维护处理状态机与退避重试(1/5/30 分钟、最多 3 次);重启后扫描恢复 RECEIVED/AWAITING_PARSE/未耗尽 PROCESSING_FAILED | 5.3、AC-025 |
| 为已提交 Event 版本生成 Card Projection 并下发;维护 PROJECTION_PENDING/PROJECTED;响应手机同步(内存游标增量或权威快照) | 5.3/5.5、AC-023/026 |
| 接收 Card Command(`event_id` + 命令类型 + 修改值 + `expectedVersion`),版本不符返回 `VERSION_CONFLICT`,成功则递增 `event_version` 并下发新 Projection | FR-005、AC-011/013 |
| 响应原文追溯在线请求(仅按 `event_id` 读取) | A7、FR-004、AC-029 |
| 确认撤销 pairing;撤销后不删除权威历史数据 | FR-007、AC-018 |
| 向手机暴露 PARSE_FAILED 数量、错误码、修复指引与 Pi 四级 doctor 状态;支持用户显式重试 | FR-007、AC-027/028 |
| 权威库及其备份采用经安全评审的静态加密(方案待确认) | 7.3、8.3 |

### 2.2 Connector 不做(公开面硬约束)

- 不把 Relay ACK 当作自身持久接收/提交/投影成功;持久接收回执由 Connector 独立签发(台账 A6)。
- 不要求 Relay 保存离线投递队列;不向离线手机推送 Projection(5.5)。
- 不重新发送手机原始 Capture,不自动重发 Card Command(5.5)。
- Pi 不得直接写权威数据库;禁止通用 Shell/HTTP 执行器,Pi 仅用注册白名单能力(7.3)。
- 不在公开契约暴露内部数据库、Pi RPC、Prompt、文件路径(跨端公开契约治理规范)。
- `capture_id`、`log_entry_id` 不进入手机/Relay 公开字段(integration-profile `confirmed_invariants`)。
- 第一代不支持多设备、多手机配对(台账 A4)。

## 3. 公开接口范围(最小公开面)

以下 7 组是 Connector 对手机/Relay 的**全部**公开交互面,与 `integration-profile` 的 10 个 section 的映射见第 4 节。字段级 Schema 在契约冻结(G3)时进入 `harness/契约/`。

### 3.1 配对与身份(pairing_and_identity)

- 二维码载荷:Connector 名称、版本、静态公钥指纹、一次性 token(5 分钟,已确认 B1)。
- Noise 角色:Responder;静态密钥首启生成并持久化;握手后双方校验公钥指纹与 `pairing_id` 绑定(已确认 D4)。
- 失败语义:token 过期/已用、指纹不匹配、已撤销 → 拒绝建立会话,映射 `PAIRING_INVALID`(AC-002、7.4)。

### 3.2 E2EE 传输(e2ee_handshake_and_vectors / relay_transport)

- Pattern `Noise_XX_25519_ChaChaPoly_SHA256`;会话重建时完整握手 rekey;P0 禁用会话内 rekey 控制帧(已确认 D4)。
- 每会话每方向单调 `uint64` 序号,拒绝重复/回退;新会话序号重置(已确认 D4;**正式字段位置与乱序窗口待确认**)。
- 握手固定总超时 10 秒(初始值,待 Spike 校准);失败统一映射 `HANDSHAKE_FAILED`,细节仅端点本地诊断(已确认 D4)。
- 与 Rust snow 的互操作固定向量已存在(SPK-PH-2026-001),**待 Connector Owner 共同签收**。

### 3.3 健康上报与能力宣告(health_and_ready)

- 每 10 秒上报:Connector 版本/能力集、权威数据库是否可接收、Pi doctor 状态(已确认 C4、FR-003)。
- 上报经 Relay 转达;手机按 30 秒新鲜度判定 READY / NOT_READY_CONNECTOR / NOT_READY_STORAGE / UNKNOWN(PRD 5.2)。
- 能力不兼容(不在兼容矩阵内)时 Connector 必须上报不兼容,不得进入 READY(PRD 9.1)。

### 3.4 Capture 接收与持久接收回执(capture_receipt_semantics)

- 输入:E2EE 密文 Capture(手机内存生成 `capture_id`)。
- 行为:验签 → 幂等检查 → 权威库事务写入(RECEIVED)→ 签发持久接收回执。
- 重复 `capture_id` 返回同一回执,不创建第二条(AC-015)。
- 回执与 Relay ACK 严格区分;Connector 离线时 Relay 返回 `ROUTE_NOT_DELIVERED`(AC-019)。

### 3.5 处理状态与重试(语义归 Connector,公开面为状态查询与诊断摘要)

- 状态机:RECEIVED → AWAITING_PARSE → COMMITTED;异常转 PARSE_FAILED 或 PROCESSING_FAILED(5.3)。
- PROCESSING_FAILED:记录 `failure_stage`、`attempt_count`、`next_retry_at`,1/5/30 分钟退避最多 3 次(已确认,PRD 5.3;**超次数后处置文案待技术评审**)。
- 重启恢复:扫描并恢复未终结任务,不重建 Capture/Event(AC-025);PARSE_FAILED 不自动重试。

### 3.6 Projection 下发与同步(projection_sync)

- 触发:手机进入 READY、冷启动/后台恢复、Card Command 结果未知后恢复 READY(5.5)。
- 支持两种同步:手机内存游标增量;无游标时 Connector 基于已提交最新 Event 重新生成权威快照(5.5)。
- 手机只接受更高 `event_version`;Connector 不下发旧版本覆盖(5.4、AC-024)。
- Projection 不含 Capture 原文(7.1)。

### 3.7 Card Command 与原文追溯(card_command / original_trace)

- Card Command:`event_id` + 命令类型 + 修改值 + `expectedVersion`;冲突返回 `VERSION_CONFLICT` 且不写入(AC-013)。
- 成功提交后递增 `event_version`,新版本进入 PROJECTION_PENDING 并下发(5.4)。
- 原文追溯:在线请求仅携带 `event_id`,响应仅供手机当前会话内存展示;失败/断线不重试(A7、AC-029)。

### 3.8 撤销与诊断摘要以外的管理面

- 撤销配对:Connector 确认后 Relay 拒绝后续路由,手机进 UNPAIRED,权威历史数据保留(AC-018)。
- 诊断摘要:PARSE_FAILED 计数、错误码、修复指引、doctor 状态——只出脱敏摘要,不出原文(FR-007)。

## 4. 与 integration-profile section 的映射

| profile section | Connector 是否签字方 | Connector 侧现状 |
| --- | --- | --- |
| relay_transport | 是(消费方) | 语义已确认,封套字段待冻结 |
| pairing_and_identity | 是(被配对方) | 语义已确认(B1/D4),二维码载荷字段待冻结 |
| e2ee_handshake_and_vectors | 是(Responder) | 参数全确认;**固定向量待共同签收** |
| health_and_ready | 是(上报方) | 10s/30s 已确认;上报载荷字段待冻结 |
| capture_receipt_semantics | 是(签发方) | 语义已确认并有场景证据(SC-004) |
| projection_sync | 是(生成方) | 语义已确认并有场景证据(SC-005) |
| original_trace | 是(响应方) | 语义已确认(A7) |
| card_command | 是(处理方) | 语义已确认并有场景证据(SC-006) |
| errors_and_close_codes | 是(共同遵守) | 8 个稳定错误码已在 PRD 7.4 |
| limits_and_backpressure | 间接(经 Relay) | 初始基线已确认,**待 ECS 容量 Spike 校准** |

## 5. 待确认清单(一次一问,逐项走 Q&A)

| # | 待确认项 | 当前口径 | 建议 Q&A |
| --- | --- | --- | --- |
| 1 | Connector Owner 归属 | 未定(Painfox 候选) | 待提问 |
| 2 | Noise 固定向量与失败语义的共同签收 | 单向已完成 Spike | 依赖 #1 |
| 3 | 正式封套字段位置、乱序窗口、错误映射 | 仅序号规则已确认 | 待提问 |
| 4 | Connector Service 正式版本号与能力集编码 | 未定义 | 待提问 |
| 5 | 桌面首发兼容矩阵(系统版本/打包格式) | PRD 8.3 待指定 | 待提问 |
| 6 | 权威库静态加密方案 | 必须通过安全评审,方案未定 | 待提问 |
| 7 | 数据恢复策略(电脑损坏/换机) | PRD 8.3 待指定 | 待提问 |
| 8 | PROCESSING_FAILED 超 3 次后的文案与处置 | PRD 注"待技术评审确认" | 待提问 |
| 9 | 单会话时长/消息量上限与失败恢复语义 | 基线注明须 Spike 补齐 | 待 Spike 后提问 |

## 6. 签收流程(依跨端公开契约治理规范)

1. 本文逐条走 Q&A(第 5 节),确认后回写两端台账与架构基线。
2. 字段级 Schema 进入两端 `harness/契约/` 同名文件,`integration-profile` 逐 section 由 `pending` 转 `proposed`。
3. Connector Owner 接受后,`connector_acceptance` gate 转通过,profile 升 `approved`。
4. 只有 `approved` 且两端校验和一致,才允许 Connector 生产实现(G5);此前只能进 `spikes/`。

## 7. 变更记录

| 日期 | 版本 | 变更内容 | 确认人 |
| --- | --- | --- | --- |
| 2026-08-27 | v0.1 | 首版草案:归并 PRD v0.5 与台账已确认语义,划定最小公开面,列出 9 项待确认清单。 | 待确认 |
