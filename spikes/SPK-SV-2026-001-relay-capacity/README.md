# SPK-SV-2026-001 Relay 容量与背压

> Owner：Zhu3xx
> 关联：Q-SV-2026-037、TS-SV-2026-001、PRD FR-008/7.3
> 时间盒：1 个工作日
> 状态：已完成本机合成门禁；ECS 容量仍待执行

## 假设

在单台阿里云 ECS 上，Go + `coder/websocket` 的 Relay 能以不泄露业务正文的方式承载全局最多 `100` 个并发握手、每 `60 秒`最多 `300` 次握手尝试，并在目标连接负载下保持可接受的背压、资源和重启行为。

## 环境

- 目标运行形态：Go 单二进制 + Caddy WSS 反代 + `modernc.org/sqlite` 元数据存储。
- 目标实例：单台阿里云 ECS；具体规格、系统版本、内核参数和 Caddy 版本在执行前记录。
- 测试数据：仅使用合成 pairing、公钥、密文和错误类别；禁止真实业务正文、私钥和真实标识。
- 基线：全局最多 `100` 个并发握手；每 `60 秒`最多 `300` 次握手尝试；全局或 pairing 级超限均返回 `RATE_LIMITED`。

## 阈值与观测

- 成功：达到基线时服务不崩溃、不泄露明文；全局并发/速率保护准确拒绝超限；慢消费者不会无界增长内存；重启后不恢复未投递业务正文；Caddy reload 影响可观测且有明确运维边界。
- 必测指标：握手成功率、P50/P95/P99 延迟、`RATE_LIMITED` 命中数、RSS、CPU、文件描述符、goroutine 数、写缓冲、连接存活、重连峰值和 SQLite 写入延迟。
- 失败：资源耗尽、消息/连接无界排队、错误码不稳定、Relay 落盘业务正文、Caddy reload 造成未记录的连接语义变化，或基线下无法维持服务稳定。
- 必留样本：成功与失败请求计数、超限边界样本、慢消费者样本、重启/reload 前后连接状态、脱敏日志和原始监控导出。

## 步骤

1. 记录 ECS、Go、Caddy、内核和文件描述符配置。
2. 使用合成端点启动 Relay/Caddy；验证基础健康检查和错误码。
3. 分阶梯施加 `25/50/100/125` 并发握手，并分别施加每 `60 秒` `150/300/360` 次尝试。
4. 单独施加 pairing 级 `60 秒/5 次` 限流，确认不会被全局保护语义替代。
5. 注入慢消费者、断网、Relay 重启和 Caddy reload，记录背压与恢复行为。
6. 保存原始结果、失败样本、解释和对架构/参数的影响；未达到阈值不得将 profile 标记为 approved。

## 原始结果

执行日期：2026-08-24（Asia/Shanghai）

环境：macOS arm64；Go `1.27.0`；Caddy `2.11.4`；`github.com/coder/websocket v1.8.15`；合成 Relay，非生产代码；本机回环地址；无真实业务数据、私钥或业务明文。

构建命令：

```text
GOPROXY=off go mod tidy
GOPROXY=off go build -o /tmp/utell-relay-spike .
```

并发门（服务端 `-concurrency 100 -rate-limit 300 -hold 250ms`）：

```json
{"attempts":125,"parallel":125,"accepted":100,"rate_limited":25,"other_failures":0,"target":"ws://127.0.0.1:18081/ws"}
{"accepted_handshakes":100,"active":0,"attempts_in_window":125,"concurrency_limit":100,"rate_limit":300,"rate_window_seconds":60,"rejected_handshakes":25}
```

速率门（服务端 `-session-hold 0`，客户端串行，避免并发门干扰）：

```json
{"attempts":360,"parallel":1,"accepted":300,"rate_limited":60,"other_failures":0,"target":"ws://127.0.0.1:18081/ws"}
{"accepted_handshakes":300,"active":0,"attempts_in_window":360,"concurrency_limit":100,"rate_limit":300,"rate_window_seconds":60,"rejected_handshakes":60}
```

Caddy 配置校验：`caddy validate --config Caddyfile --adapter caddyfile` -> `Valid configuration`。

Caddy 反代回环验证：`/healthz` 返回 HTTP `204`；经 `ws://127.0.0.1:18080/ws` 的合成 WebSocket 握手 `10/10` 成功，`other_failures=0`。

## 解释

- 观察事实：合成实现准确执行了 `100` 并发门和 `60 秒/300 次`速率门，超限均映射为 `RATE_LIMITED`；客户端主动关闭成功会话后，速率测试不再受到活动连接残留干扰。
- 观察事实：Caddy 能加载当前反代配置并转发健康检查和 WebSocket 升级。
- 未知：本机回环不代表阿里云 ECS 的 CPU、RSS、FD、网络、Caddy reload、慢消费者和长连接容量；本 Spike 没有实现 Noise、Relay Transport Schema、SQLite 审计或真实握手密码学。

## 对决策的影响

- 支持：本机合成门禁支持 Q037 的 `100` 并发、`60 秒/300 次`初始参数可被实现为独立全局保护层，且 pairing 级保护仍可独立存在。
- 仍未知：不得据此把 `integration-profile.yaml` 标记为 `approved`，不得冻结最终容量或 Caddy/应用层职责边界；必须在目标 ECS 上完成资源、背压、消息大小、重启和 reload 演练。
- 代码处置：Spike 代码保留在本目录作为可重复验证工具，禁止直接复制到生产 Relay；正式实现需另建生产工程并补齐契约测试。
