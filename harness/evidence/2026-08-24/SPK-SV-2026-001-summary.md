# SPK-SV-2026-001 证据摘要

- 日期：2026-08-24
- 范围：本机回环合成 Relay、Caddy 反代与全局保护门禁
- 不在范围：阿里云 ECS 资源容量、真实 Relay、Noise、Transport Schema、SQLite 审计和业务正文
- 环境：macOS arm64；Go `1.27.0`；Caddy `2.11.4`；`github.com/coder/websocket v1.8.15`
- 数据边界：仅合成 WebSocket 握手；没有真实业务正文、私钥、账号或稳定标识

## 命令

```text
GOPROXY=off go mod tidy
GOPROXY=off go build -o /tmp/utell-relay-spike .
GOPROXY=off go test -race ./...
caddy validate --config Caddyfile --adapter caddyfile
```

## 原始结果

并发门：服务端 `-concurrency 100 -rate-limit 300 -hold 250ms`，客户端 `-attempts 125 -parallel 125`。

```json
{"attempts":125,"parallel":125,"accepted":100,"rate_limited":25,"other_failures":0}
{"accepted_handshakes":100,"active":0,"attempts_in_window":125,"concurrency_limit":100,"rate_limit":300,"rejected_handshakes":25}
```

速率门：服务端 `-session-hold 0`，客户端 `-attempts 360 -parallel 1`。

```json
{"attempts":360,"parallel":1,"accepted":300,"rate_limited":60,"other_failures":0}
{"accepted_handshakes":300,"active":0,"attempts_in_window":360,"concurrency_limit":100,"rate_limit":300,"rejected_handshakes":60}
```

Caddy：配置校验为 `Valid configuration`；经 Caddy 的 `/healthz` 返回 `204`；经 `ws://127.0.0.1:18080/ws` 的合成握手 `10/10` 成功，`other_failures=0`。

竞态测试：`go test -race ./...` 通过。

## 结论与限制

- 支持：`100` 并发和 `60 秒/300 次`可以在合成 Relay 中作为独立全局保护门实现，超限稳定映射为 `RATE_LIMITED`。
- 未冻结：最终容量、ECS 规格、RSS/CPU/FD/P99、慢消费者背压、消息大小、Relay 重启和 Caddy reload 生产语义。
- 门禁：`integration-profile.yaml` 继续保持 `status: pending`；不得据此进入生产 Relay 实现或宣称容量已批准。

## 文件校验和

校验和以工作区最终文件为准，执行：

```text
find spikes/SPK-SV-2026-001-relay-capacity -maxdepth 1 -type f -print -exec shasum -a 256 {} \;
```

本次证据涉及文件 SHA-256：

```text
e4824f7882283f47e2dac2f2f88ec347d87d1fcdafb332a63972c479e2ac16f2  Caddyfile
9281c7f946027ad45b71ddfe36c238666084744748fbc50937ab35fd91aa6190  README.md
174b249f44421b781d6ac1e7824e7484dfc8e48919ca5526b0dc36ef5abd235e  go.mod
874a91c5fb043526bc117c0f260c77e4372ab11a28eb6ef2b754fdbb55101f7a  go.sum
ca10f3e04e7384a225bc110e8831e2b85545cee05f229c37c4169f994f5e9532  main.go
e468b01fc01476244e128a039584ac4906984a11cd2d1f133f3762c19227e5fe  main_test.go
```
