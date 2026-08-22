# PRD：Utell（油条）第一代智能日志 MVP

> 基于用户提供的原始 PRD 整理，并补充 P0 评审与验收内容。标注“待确认”的阈值和事项须在评审中确认。
> 
> 

## 0\. 项目概述

### 0\.1 产品定义

Utell 是一款以用户个人电脑为权威数据源、手机为在线采集和查看端的记录工具。用户在手机输入自然语言；电脑端 Connector 通过 TypeScript Adapter Host 承载 Utell Pi 插件完成解析，Connector 负责权威保存，并将可确认、可纠正的时间事件卡片回传手机。

### 0\.2 核心架构与数据边界

仅当手机至 Connector 的链路就绪时，手机开放新内容输入。手机内容经端到端加密通过中继服务 Relay 转发至个人电脑。Relay 仅路由密文，不读取或长期持久化业务正文；个人电脑是唯一业务数据权威方，手机卡片是其状态投影。

### 0\.3 文档信息

|项目|内容|
|---|---|
|文档状态|草稿（待 P0 评审）|
|当前版本|v0\.2|
|产品、技术、测试负责人|待指定|
|目标发布版本与日期|待确认|
|关联原型、技术方案、测试用例|待补充|

## 1\. 背景、目标与成功指标

### 1\.1 背景

- 传统待办工具要求先选分类、字段和页面，使碎片化的一句话意图难以低成本沉淀。

- 模型调用和业务数据集中在服务端会带来算力压力与用户数据集中存储的安全面。

### 1\.2 目标

- 用户输入一句话后，由个人电脑上的 Utell Pi 理解为日期、事件等结构化提案；Connector 权威落库；手机卡片展示并允许确认或纠正。

- Relay 只做加密路由，不读取或长期持久化业务正文。

- 只有电脑权威库已持久接收或提交后，手机才可显示相应状态。

- 链路不完整时不允许创建新 Capture，手机不持久化待发送业务原文。

### 1\.3 成功指标（P0，待确认）

统计周期为首发后连续 28 天；仅统计脱敏技术事件，不采集 Capture 原文、标题、摘要或 Pi 输出。

|指标|统计口径|P0 建议目标|
|---|---|---|
|首次配对成功率|完成配对设备数 / 发起扫码设备数|不低于 90%|
|有效提交接收率|Connector 持久接收数 / 手机发起提交数（剔除主动取消）|不低于 99%|
|接收时延|点击提交至收到 Connector 持久接收回执|P95 不高于 5 秒|
|卡片投影时延|Capture 接收至手机收到最新 Projection，Pi 正常时|P95 不高于 15 秒|
|解析可用率|返回可校验提案数 / 已接收 Capture 数|不低于 95%|
|无原文残留|手机持久化存储、日志、分析、崩溃报告中检出的业务原文条数|0|

非目标：P0 不以日活、留存、自动提醒、离线录入、跨设备同步或系统日历读写为成功标准。

## 2\. 项目范围

### 2\.1 本期包含（P0）

- 文字日志采集：手机仅在链路就绪时提交文字，Capture 首次持久化发生在电脑权威库。

- 信息传输链路安全。

- Connector（Rust Core \+ TypeScript Adapter Host）与 Utell Pi 插件：完成日志理解、日期/事件结构化与权威事务落库。

- 卡片基本功能：按日期展示、展开详情、回溯原文、在线确认、纠正日期和冲突事件。

- 链路状态可视化：未就绪、正在提交、电脑已接收、处理中、已提交、已投影、失败、提交结果未知；Relay ACK 不得冒充完成。

- 配对、设置与脱敏诊断；Relay 服务；Connector 安装、升级备份及回滚。

### 2\.2 本期不包含

- 手机 Outbox、离线 Capture、未确认原文的自动重发。

- 手机持久化 Capture、Event、Card 或 Projection 业务缓存。

- 系统日历读写、提醒、Memo、Chat/RAG、语音输入。

- Utell Pi 不可用时自动回退其他 Agent。

范围门禁：未写入本期包含的能力默认不进本期；发布物不得出现非本期功能，以仓库依赖、路由、安装包和测试清单扫描为准。

### 2\.3 P0 约束

- P0 限定一名用户配对一台个人电脑和一台手机；多设备与共享不在本期。

- 手机临时草稿和本次会话的卡片仅存内存；页面销毁、App 退出、崩溃或系统回收后丢弃。

- 权威数据仅存在 Connector 管理的本机数据目录。

## 3\. 用户与核心场景

|角色|权限和职责|
|---|---|
|个人用户|配对电脑、提交文字、查看最新卡片、确认/纠正事件、撤销配对、导出脱敏诊断。|
|Connector|验签、权威持久化、运行 Pi、校验提案、生成 Projection、处理幂等与版本。|
|Relay|管理已配对设备认证和在线路由，仅处理密文信封与最小运行元数据。|
|Utell Pi|仅生成受控 Schema 的结构化提案，无直接数据库、Shell、任意 HTTP 或未注册能力访问权。|

- 快速记录：用户在 READY 状态下输入“明天下午三点开会”，无需选择分类。

- 审阅纠错：用户发现日期或事件理解错误后在线纠正。

- 首次配对：用户安装 Connector 后扫描二维码、核对公钥指纹、确认配对。

- 链路断点：输入框禁用，展示准确断点和恢复提示。

## 4\. 核心业务流程

扫描电脑二维码 → 核对公钥指纹 → 用户确认配对 → 已配对 → 连接 Relay → 验证 Connector 能力与游标 → 进入智能日志时间线。

唯一 P0 主链路：链路健康检查通过 → READY，输入开放 → 用户提交文字 Capture → WSS Relay 与应用层端到端加密中转 → Connector 接收、验签并依 capture\_id 幂等去重 → Capture 写入权威数据库并标记 received → Connector 回传持久接收回执 → Pi 生成提案 → Connector 校验 → LogEntry 与 Event 单事务提交并标记 committed → Projection 回传手机并标记 projected → 用户确认或纠正（携带 expectedVersion）→ Connector 新事务提交 → 新 Projection 回传。

若手机在收到持久接收回执前断线，显示“提交结果未知”。手机不得显示成功或失败、不得自动重发原文；仅在当前 App 会话恢复 READY 后用内存中的 capture\_id 查询结果。App 退出或崩溃后不恢复原文或该提交任务。

### 4\.1 端到端提交闭环

## 5\. 术语、状态与数据规则（P0）

### 5\.1 术语

|术语|定义|
|---|---|
|Capture|一次原始文本记录；首次且唯一的业务持久化位置是 Connector 权威库。|
|LogEntry|Connector 对 Capture 的权威日志记录；与 Capture 一对一。|
|Event|从 LogEntry 提取的一项可展示事件；一个 LogEntry 可生成零至多项 Event。|
|Card Projection|Connector 生成并发送给手机渲染的只读、版本化视图，不是手机权威数据。|
|Card Command|用户确认或纠正单张卡片的命令，必须携带 event\_id、命令类型与 expectedVersion。|
|持久接收回执|Capture 已提交到权威数据库后，由 Connector 签发的回执；不等同于 Relay ACK。|

### 5\.2 链路状态

|状态|判定条件|手机行为|
|---|---|---|
|UNPAIRED|无有效 pairing 或设备已撤销|展示配对入口，禁用输入。|
|CONNECTING|已配对，正在建立或恢复链路|禁用输入，展示连接中。|
|NOT\_READY\_RELAY|手机无法连接 Relay|禁用输入，展示 Relay 连接断点。|
|NOT\_READY\_CONNECTOR|Relay 未确认 Connector 在线，或能力不兼容|禁用输入，展示电脑不可用。|
|NOT\_READY\_STORAGE|Connector 健康检查显示权威数据库不可接收|禁用输入，展示电脑存储不可用。|
|UNKNOWN|健康状态过期、回执无法验证或查询未完成|禁用输入，必须先恢复查询。|
|READY|手机至 Relay 已连接、Relay 确认 Connector 在线、Connector 在最近 30 秒内健康检查通过、权威库可接收 Capture|开放输入，允许读取最新 Projection。|

最近 30 秒是 P0 建议值，变更时必须同步测试用例与状态文案。

### 5\.3 Capture 与解析状态机

手机内存状态：DRAFT → SENDING → UNKNOWN\_RESULT；收到持久接收回执后为 RECEIVED。

Capture 处理状态：RECEIVED → AWAITING\_PARSE → COMMITTED；解析不可用或无效输出转为 PARSE\_FAILED；其他可重试处理失败转为 PROCESSING\_FAILED。

Projection 交付状态独立于 Capture 处理状态：每个已 COMMITTED 的 Event 版本进入 PROJECTION\_PENDING；Connector 成功向当前在线手机连接写出该版本视图后为 PROJECTED。新的 Card Command 成功提交 Event 新版本后，新版本再次进入 PROJECTION\_PENDING。

#### 提交结果状态转换

- RECEIVED 表示 Capture 和最小审计字段已在权威数据库事务提交。相同 capture\_id 的重复请求返回同一回执，不创建第二条 Capture。

- COMMITTED 表示 LogEntry 和全部 Event 已在同一事务中提交。Capture 已达到此状态后，不因 Projection 写出失败而回退为处理失败。

- PROJECTION\_PENDING 表示 Connector 存在已提交但尚未向当前在线手机连接写出的 Event 版本。它是可由 Event 当前版本推导的交付状态，不要求持久化完整 Projection 内容。

- PROJECTED 表示 Connector 已向当前在线手机连接成功写出该版本视图，不代表手机已永久保存。

- PARSE\_FAILED 表示 Pi 不能产出可校验提案；仅当 Pi 已修复且四级 doctor 通过后，用户可从设置与诊断页显式触发同一 Capture 的重试。

- PROCESSING\_FAILED 表示非 Pi 解析的可重试处理失败。Connector 必须记录 failure\_stage、attempt\_count 和 next\_retry\_at，并以 1 分钟、5 分钟、30 分钟的退避策略自动重试，最多 3 次；超过次数后保留失败状态和修复指引，待技术评审确认。

- Connector 每次启动并确认权威库健康后，必须扫描 RECEIVED、AWAITING\_PARSE 及未耗尽重试次数的 PROCESSING\_FAILED，并恢复处理；不得重新创建 Capture 或 Event。PARSE\_FAILED 不自动重试。

- UNKNOWN\_RESULT 仅是手机临时状态，不能推断电脑是否收到内容。

### 5\.4 时间与版本

- 协议时间使用 ISO 8601 UTC；卡片按手机当前时区分组。

- 相对时间解析基准为 Connector 接收 Capture 时记录的用户时区，该时区随 Capture 保存。

- 不能可靠解析时间时，start\_at 为空、time\_precision 为 UNKNOWN，展示在“时间待确认”分组。

- event\_version 从 1 开始递增。expectedVersion 不等于权威库版本时，拒绝写入并返回 VERSION\_CONFLICT。

- 手机仅接受版本更高的 Projection；相同或较低版本一律丢弃。

### 5\.5 Projection 同步与重新下发

- 重新下发仅适用于 Connector 已提交 Event 所生成的 Card Projection；不得重新发送手机原始 Capture，也不得自动重发 Card Command。

- 触发时机：手机每次进入 READY、App 冷启动或从后台恢复、以及 Card Command 结果未知后恢复 READY 时，均须发起一次 Projection 同步。

- 当前 App 会话可在内存中维护同步游标，并据此拉取增量 Projection；游标不得持久化，App 退出、崩溃或被系统回收后即失效。

- 冷启动或不存在内存游标时，手机必须向 Connector 请求当前权威快照。Connector 基于已提交的最新 Event 重新生成 Projection，并通过端到端加密链路发送。

- Connector 未向离线手机发送 Projection，也不要求 Relay 保存离线投递队列；手机恢复 READY 后通过上述同步获取最新视图。

- 手机离线、App 退出或当前连接写出失败时，已 COMMITTED 的 Event 版本保持为 PROJECTION\_PENDING；Connector 重启后可从权威 Event 的当前版本重新推导该状态。手机恢复 READY 后同步该版本。

- 手机仅在当前前台会话内按 event\_id 和 event\_version 去重；没有内存中既有版本时接受当前同步的版本，已有版本时仅以更高版本覆盖。

## 6\. 功能需求与验收标准（P0）

### FR\-001 配对

- 操作入口：启动后处于 UNPAIRED 状态时，进入手机扫码页。

- 前置条件：电脑端 Connector 已启动并展示有效二维码。

- 正常操作流程：手机扫码后展示 Connector 名称、版本、公钥指纹和一次性 token 剩余有效期；用户核对并确认后建立 pairing，开始端到端加密握手。建议 token 有效期为 5 分钟且仅可使用一次，待安全评审确认。

- 异常/边界情况：token 过期或已使用、指纹不匹配、设备已撤销时拒绝建立会话；Relay 认证失败时按错误类型提示重试或解除后重新配对。

- 优先级：P0。

- AC\-001：Given Connector 已生成未过期二维码；When 手机扫描、显示指纹且用户确认；Then 建立有效 pairing 并进入 CONNECTING。

- AC\-002：Given token 过期、已使用、指纹不匹配或设备已撤销；When 用户确认配对；Then 系统拒绝配对、不建立会话，并展示对应修复提示。

### FR\-002 输入门禁与文字提交

- 操作入口：时间线页底部的文字输入框。

- 前置条件：链路状态为 READY。

- 正常操作流程：仅 READY 时输入框可编辑；去除首尾空白后为空的文本不可提交。用户提交时，手机在内存生成 capture\_id 并加密发送；只在收到有效的 Connector 持久接收回执后显示“电脑已接收”。

- 异常/边界情况：非 READY 时输入框禁用并按断点显示原因；提交后、持久接收回执前断线时显示“提交结果未知”；编辑中断线时立即禁用输入。业务原文不得写入持久化存储、日志、分析、崩溃报告或 Outbox，也不得自动重发。

- 优先级：P0。

- AC\-003：Given READY 且输入非空；When 用户提交 Capture；Then 手机进入 SENDING，且仅在收到有效持久接收回执后显示“电脑已接收”。

- AC\-004：Given Capture 已发出但未收到持久接收回执；When 链路断开；Then 显示“提交结果未知”，不显示成功/失败、不自动重发，也不持久化原文。

- AC\-005：Given 编辑时链路转为非 READY；When 用户继续编辑或提交；Then 输入立即禁用，临时草稿仅保留内存，退出或崩溃后不可恢复。

### FR\-003 连接与状态诊断

- 操作入口：手机顶部连接状态区和链路诊断页。

- 前置条件：已完成有效 pairing。

- 正常操作流程：Connector 每 10 秒报告能力和权威库健康状态，待确认；手机按 5\.2 的状态定义显示唯一主状态与具体断点。每次进入 READY 后，手机按 5\.5 发起 Projection 同步；恢复连接后只恢复健康检查、查询当前会话内未知结果和刷新 Projection。

- 异常/边界情况：Relay ACK 仅表示路由层收到，不能展示为接收、提交或投影成功；Connector 离线、能力不兼容、数据库不可用或健康状态过期时禁用输入；状态 UNKNOWN 时必须先完成状态查询。

- 优先级：P0。

- AC\-006：Given Relay 已 ACK 密文但 Connector 未给出持久接收回执；When 手机刷新提交状态；Then 不得展示“电脑已接收”“已提交”或“已投影”。

- AC\-007：Given Connector 健康信息超过 30 秒未更新或数据库不可接收；When 手机判定链路；Then 状态为 UNKNOWN 或 NOT\_READY\_STORAGE，输入不可用。

- AC\-023：Given Connector 已提交 Event，但手机在收到对应 Projection 前断线或重启；When 手机恢复 READY 并进入时间线；Then 手机从 Connector 获取该 Event 的最新 Projection，且不依赖手机持久化业务缓存。

### FR\-004 时间线与卡片

- 操作入口：手机主壳默认的智能日志时间线。

- 前置条件：链路状态为 READY，且本次前台会话已从 Connector 获取 Card Projection。

- 正常操作流程：手机只渲染本次前台会话从 Connector 获取的最新 Projection；卡片按手机当前时区日期分组，展示标题、摘要、状态、原文入口、展开、确认和纠正入口。

- 异常/边界情况：无数据时展示空状态；非 READY 时展示链路断点，不得读取或展示手机持久化业务缓存；时间未知时进入“时间待确认”分组；App 重启或恢复后必须重新获取最新 Projection。

- 优先级：P0。

- AC\-008：Given READY 且 Connector 返回 Event Projection；When 用户进入时间线；Then 卡片按日期分组显示，仅展示不低于当前内存版本的数据。

- AC\-009：Given Event 的 time\_precision 为 UNKNOWN；When 展示该 Event；Then 卡片进入“时间待确认”分组，不显示伪精确时间。

- AC\-010：Given App 重启或被系统回收；When 用户重新进入时间线；Then 清空旧业务内存视图，并从 Connector 获取最新 Projection。

- AC\-024：Given 手机当前会话已展示 event\_id 对应的 Projection v8；When 收到重复的 v8、迟到的 v7 或更高的 v9；Then 手机保留 v8、丢弃 v7，并仅在收到 v9 时更新卡片。

### FR\-005 卡片确认与纠正

- 操作入口：卡片展开详情中的确认和纠正操作。

- 前置条件：链路状态为 READY，手机已持有该卡片的最新 Projection。

- 正常操作流程：用户确认提取结果，或修改日期/事件后提交。Card Command 必须包含 event\_id、命令类型、修改值与 expectedVersion；Connector 成功提交后递增 event\_version 并下发新 Projection。

- 异常/边界情况：命令回执前断线时显示“修改结果未知”，不得自动重发；离线时拦截操作且不产生 Outbox；版本冲突时刷新最新 Projection 后由用户重新确认；迟到旧版本 Projection 不得覆盖新版本。

- 优先级：P0。

- AC\-011：Given expectedVersion 等于权威库当前版本；When 用户确认或纠正；Then Connector 事务提交修改并返回版本更高的新 Projection。

- AC\-012：Given Card Command 已发出但未收到提交回执；When 链路断开；Then 显示“修改结果未知”，不自动重发；恢复 READY 后拉取最新 Projection。

- AC\-013：Given expectedVersion 已过期；When Connector 接收命令；Then 返回 VERSION\_CONFLICT，不写入修改，并要求刷新后重新确认。

### FR\-006 Connector 权威落库与 Pi 解析

- 操作入口：无用户界面入口；由 Capture 或 Card Command 触发。

- 前置条件：Connector、权威数据库和受限 Pi 运行环境可用。

- 正常操作流程：Connector 先验签并按 capture\_id 幂等写入 Capture，成功后回传持久接收回执，再运行 Pi。Pi 只能提交符合受控 Schema 的提案；Connector 校验 Schema、时间、字段完整性与白名单能力后，在同一事务中提交 LogEntry 与 Event。每个已提交 Event 版本进入 PROJECTION\_PENDING，并在手机 READY 同步时生成和下发最新 Projection。Connector 重启后按 5\.3 恢复未终结的处理任务。

- 异常/边界情况：Pi 不可用、超时或输出无效时进入 PARSE\_FAILED，返回稳定错误码和修复指引，不回退其他 Agent；非 Pi 的可重试处理失败进入 PROCESSING\_FAILED 并按 5\.3 退避重试；事务失败时不提交 Event；投影写出失败不影响已提交 Event；重复请求不产生重复数据；Pi 不得直接写入权威数据库。

- 优先级：P0。

- AC\-014：Given Connector 首次收到合法 capture\_id；When 权威持久化成功；Then 仅创建一条 Capture，状态为 RECEIVED，并回传持久接收回执。

- AC\-015：Given Connector 重复收到相同合法 capture\_id；When 幂等处理完成；Then 不创建重复 Capture/Event，返回原 Capture 的接收结果。

- AC\-016：Given Pi 不可用、超时或输出不符合 Schema；When Connector 处理 Capture；Then 状态变为 PARSE\_FAILED 或 PROCESSING\_FAILED，返回稳定错误码和修复指引，不回退其他 Agent 且不提交 Event。

- AC\-025：Given Connector 在 Capture 为 RECEIVED、AWAITING\_PARSE 或未耗尽重试次数的 PROCESSING\_FAILED 时重启；When 权威库健康检查通过；Then Connector 恢复对应处理任务，不创建重复 Capture 或 Event。

- AC\-026：Given Event 已 COMMITTED 但手机离线或 Projection 当前连接写出失败；When 手机后续恢复 READY；Then Connector 基于该 Event 的当前版本生成 Projection 并下发，且不依赖 Relay 离线队列或手机业务缓存。

- AC\-027：Given Capture 处于 PARSE\_FAILED；When Pi 修复并通过四级 doctor，且用户在设置与诊断页显式重试；Then Connector 使用同一 Capture 重新进入 AWAITING\_PARSE，不创建重复 Capture。

### FR\-007 设置与诊断

- 操作入口：手机设置页。

- 前置条件：无；部分信息在已完成 pairing 后展示。

- 正常操作流程：展示 pairing、公钥指纹、链路状态和断点、Connector 能力/健康、当前会话未知结果项，以及 Connector 中 PARSE\_FAILED 的 Capture 数量、错误码和修复指引；Pi 四级 doctor 通过后，用户可显式重试相应 Capture。用户可撤销配对或确认后导出脱敏诊断。

- 异常/边界情况：诊断导出前必须确认并完成脱敏；私钥不得离开安全存储，也不得写入日志或导出物；撤销配对失败时保留原状态并提示重试。

- 优先级：P0。

- AC\-017：Given 用户确认导出诊断；When 导出完成；Then 导出物不含私钥、Capture 原文、卡片标题/摘要、Pi 完整输出或可直接还原业务内容的数据。

- AC\-018：Given 用户撤销 pairing；When Connector 确认撤销；Then Relay 拒绝该 pairing 后续路由，手机进入 UNPAIRED，Connector 不删除权威历史数据。

- AC\-028：Given 设置与诊断页展示 PARSE\_FAILED Capture，且 Pi 未通过四级 doctor；When 用户尝试重试；Then 手机禁用重试并展示 Pi 修复指引。

### FR\-008 Relay 服务

- 操作入口：无用户界面入口；由已配对端点的连接、路由和重连行为触发。

- 前置条件：Relay 已部署，端点具有有效 pairing 和认证信息。

- 正常操作流程：Relay 处理身份、配对、公钥登记、密文路由、ACK、重连、限流和最小脱敏审计；进程重启后，已配对端点可重新认证并恢复健康检查。

- 异常/边界情况：Relay 不建立离线业务队列；未即时投递的密文必须丢弃并向发件端报告；不得保存可解密业务正文；限流或认证失败返回稳定错误码。

- 优先级：P0。

- AC\-019：Given Connector 不在线；When Relay 收到 Capture 密文；Then Relay 不将其持久化为离线队列，返回路由不可投递，手机不展示“已接收”。

- AC\-020：Given Relay 重启；When 已配对端点恢复网络；Then 两端重新认证并恢复健康检查，Relay 不恢复未投递业务正文。

### FR\-009 Connector 安装与运维

- 操作入口：电脑端安装包或 CLI。

- 前置条件：用户使用首发兼容矩阵内的桌面系统；具体系统版本待指定。

- 正常操作流程：安装包区分程序、用户数据、日志和备份目录；首启生成设备身份；完成配对并通过 Pi 四级 doctor 后，Connector 才报告可用。升级前创建可恢复备份，默认卸载不删除权威数据。

- 异常/边界情况：备份失败、doctor 未通过、升级校验失败或数据迁移失败时，Connector 不得报告 READY，必须提供失败原因与修复步骤；回滚不得破坏权威数据。

- 优先级：P0。

- AC\-021：Given 用户执行默认卸载；When 卸载完成；Then 程序文件被移除，权威数据保留，并展示位置及后续清理说明。

- AC\-022：Given 升级前备份失败或 Pi doctor 未通过；When Connector 启动；Then Connector 不报告 READY，并提供失败原因和修复步骤。

## 7\. 数据、安全与接口边界（P0）

### 7\.1 最小数据模型

|对象|关键字段|保存位置与规则|
|---|---|---|
|Capture|capture\_id、原文、received\_at、用户时区、状态、错误码、failure\_stage、attempt\_count、next\_retry\_at|仅 Connector 权威库；手机只在本次提交内存短暂持有。|
|LogEntry|log\_entry\_id、capture\_id、解析版本、创建时间|仅 Connector 权威库；与 Capture 一对一。|
|Event|event\_id、log\_entry\_id、标题、摘要、start\_at、time\_precision、event\_version、状态|仅 Connector 权威库；一个 LogEntry 可对应多条。|
|Card Projection|event\_id、event\_version、展示字段、投影时间|经端到端加密发送，手机仅前台内存使用。|
|Pairing|pairing\_id、两端公钥指纹、创建/撤销时间、权限状态|端点安全存储与 Relay 最小登记；禁止保存私钥。|

### 7\.2 Relay 保留规则

- 不保存可解密业务正文，不建立离线投递队列。

- 可保存 pairing 标识的不可逆哈希、时间戳、消息大小区间、投递结果和错误类别；不得保存明文内容、可解密载荷、标题、摘要或 Pi 输出。

- 脱敏审计元数据最长保留 30 天，待确认；到期自动删除。

### 7\.3 安全硬约束

- 使用 TLS 与手机/Connector 应用层端到端加密，基于成熟密码库；禁止自创算法。

- 私钥只在端点安全存储，不进配置、日志、二维码、诊断导出或明文备份。

- Connector 权威库及其备份必须采用经安全评审的静态加密方案。

- 加密消息绑定 pairing\_id、单调递增 nonce/序号、协议版本和过期时间；验签失败、重放、篡改、过期消息均拒绝。

- Relay 无法解密证明、重放/篡改拒绝、密钥轮换、撤销 pairing、静态数据加密均为发布门禁。

- 手机禁止持久化业务原文、待发送队列、自动重发任务和业务卡片缓存；该禁令覆盖数据库、文件、剪贴板、日志、分析与崩溃报告。

- 禁止通用 Shell/HTTP 执行器；Pi 只能使用 Connector 注册的白名单能力，且有超时、取消、输出上限与审计。

### 7\.4 稳定错误码

|错误码|用户可见含义|建议处理|
|---|---|---|
|PAIRING\_INVALID|配对已失效或已撤销|重新扫描并确认配对。|
|RELAY\_UNREACHABLE|手机无法连接 Relay|检查网络后重试。|
|CONNECTOR\_UNAVAILABLE|电脑端未在线或能力不兼容|启动或升级 Connector。|
|AUTHORITY\_STORAGE\_UNAVAILABLE|电脑权威数据库不可用|在电脑端修复存储。|
|PI\_UNAVAILABLE|Pi 未安装、不可用或 doctor 未通过|在电脑端按指引修复 Pi。|
|PI\_OUTPUT\_INVALID|Pi 输出未通过校验|查看脱敏诊断后重试解析。|
|VERSION\_CONFLICT|卡片已更新|刷新最新卡片后重新确认。|
|ROUTE\_NOT\_DELIVERED|Relay 未即时投递|不重发原文；恢复 READY 后重新输入。|

## 8\. 非功能要求、依赖与风险（P0）

### 8\.1 非功能要求

|类别|P0 要求|
|---|---|
|性能|READY 时，提交至持久接收回执 P95 不高于 5 秒；Pi 正常时，最新 Projection P95 不高于 15 秒。|
|稳定性|Connector 升级后可恢复至上一个可用版本；升级失败不得破坏权威数据。|
|兼容性|首发桌面与移动端平台、最低系统版本、打包格式待指定；不在矩阵内的平台不宣称支持。|
|可观测性|记录配对结果、状态转换、回执时延、解析结果、投影结果、错误码和冲突；不得记录正文。|
|可访问性|关键状态、错误和确认结果必须提供文本，不能只依赖颜色或图标。|

### 8\.2 外部依赖

|依赖|交付物/验收|负责人|截止时间|不可用兜底|
|---|---|---|---|---|
|Utell Pi|Schema、四级 doctor、稳定错误码|待指定|待指定|标记 PI\_UNAVAILABLE，不启用替代 Agent。|
|Relay|认证、路由、限流、最小审计|待指定|待指定|显示链路断点，禁止输入。|
|Connector 权威库|加密、事务、备份、恢复、幂等|待指定|待指定|显示 AUTHORITY\_STORAGE\_UNAVAILABLE。|
|移动安全存储|配对密钥和设备身份安全保存|待指定|待指定|禁止完成配对或进入 READY。|

### 8\.3 风险与待确认项

|项目|风险或待确认内容|负责人|截止时间|
|---|---|---|---|
|指标阈值|接收、解析、投影指标是否符合首发网络与 Pi 能力|待指定|P0 评审前|
|数据恢复|电脑损坏、设备丢失、换机时的权威数据恢复策略|待指定|安全评审前|
|静态加密|各桌面系统的加密实现与密钥可用性|待指定|技术方案冻结前|
|平台范围|桌面与移动端首发兼容矩阵|待指定|开发排期前|
|多设备限制|一手机一电脑限制及超出限制时的文案|待指定|评审前|
|隐私合规|Relay 元数据、30 天保留和诊断导出|待指定|发布前|

## 9\. 发布、回滚与验收门禁

### 9\.1 发布计划

- 先部署兼容的 Connector 与 Relay 并完成端到端验证，再发布手机端。

- 首批只向内部测试用户开放；每阶段观察至少 7 天，满足成功指标且无 P0 安全事故后扩大范围。

- 手机端停止分发可回滚；Relay 回滚至兼容版本；Connector 仅在升级前备份成功时支持回滚。任何回滚不得删除用户权威数据。

- 手机、Relay、Connector、Pi 的协议兼容矩阵须在上线前确定；不兼容组合不得进入 READY。

### 9\.2 发布验收清单

* [ ] FR\-001 至 FR\-009 的 AC\-001 至 AC\-028 全部通过。

* [ ] 手机持久化存储、日志、分析、崩溃报告中未发现 Capture 原文、卡片业务缓存或自动重发任务。

* [ ] 重放、篡改、密钥轮换、设备撤销、Relay 无法解密、数据库加密、升级备份与回滚测试通过。

* [ ] Pi 不可用、数据库不可用、Connector 离线、Relay 不可达、版本冲突、未知结果的文案和恢复路径通过测试。

* [ ] 依赖负责人、平台兼容矩阵、指标阈值和风险待确认项均已关闭或书面接受。

* [ ] 脱敏日志检查、告警配置、发布说明和用户支持指引已完成。

### 9\.3 变更记录

|日期|版本|变更内容|确认人|
|---|---|---|---|
|2026\-08\-19|v0\.1|保存并结构化原始 PRD；补齐 P0 状态、验收、数据安全、依赖与发布内容。|待确认|
|2026\-08\-19|v0\.2|补齐 Connector 重启恢复、Pi 显式重试、Projection 待同步状态与相关验收标准。|待确认|

