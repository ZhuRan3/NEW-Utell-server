# SPK-SV-2026-001 ECS 证据摘要(E3)

- 日期:2026-08-27(Asia/Shanghai)
- 范围:目标阿里云 ECS 上的合成 Relay 容量、背压、消息大小、pairing 级限流、重启与 Caddy reload 演练
- 不在范围:Noise、Transport Schema、SQLite 审计、真实业务正文、公网 TLS/域名路径、断网注入(归入手机真机 E3 项)
- 环境:单台阿里云 ECS,地域 cn-hangzhou,规格 ecs.c7.large(2 vCPU Intel Xeon Platinum 8369B / 4 GiB / 40 GiB 系统盘),Ubuntu 24.04.4 LTS,kernel 6.8.0-137-generic,`ulimit -n 65535`;Go `1.27.0` linux/amd64;Caddy `v2.11.4`(`caddy build-info` 确认);`github.com/coder/websocket v1.8.15`
- 数据边界:仅合成 pairing id、合成 WebSocket 握手与全零字节载荷;无真实业务正文、私钥、账号或稳定标识;实例 ID/公网 IP/密钥按纪律登记在仓库外,不进入证据
- 执行窗口:窗口一 17:38–17:43(并发/速率/持有/重启/reload,旧版合成二进制);窗口二 22:45–22:52(延迟分位数/消息大小/pairing 级/慢消费者,扩展版二进制,含 commit `4dc9a86` 后未提交的 main.go/main_test.go 扩展,校验和见文末)

## 命令(窗口二,部署与执行)

```text
GOOS=linux GOARCH=amd64 GOPROXY=off go build -o relay-spike .
GOPROXY=off go vet ./... && GOPROXY=off go test -race ./...   # 本机,通过
relay-spike -mode server -addr 127.0.0.1:18081 -concurrency 100 -rate-limit 300 \
  -session-hold 30s -pairing-rate 5 -pairing-window 60s -echo
relay-spike -mode server -addr 127.0.0.1:18081 -concurrency 100 -rate-limit 300 \
  -push-interval 50ms -push-size 65536
```

执行脚本与全部原始输出留存于 ECS `/root/spike-results/`(`run-ecs-phase2.sh`、`client-p2-*.json`、`res-p2-*.txt`、`stats-p2-*.json`);窗口一原始输出同目录(`client-conc-*.json`、`client-rate-*.json`、`res-*.txt`、`caddy-*.log`)。

## 原始结果

### 门禁复测(窗口一 17:38–17:43)

并发阶梯 25/50/100/125 精确:`125 attempts/125 parallel → accepted=100, rate_limited=25, other_failures=0`;速率阶梯 150/300/360 精确:`360 attempts → accepted=300, rate_limited=60`。100 连接持有 8 秒:`rss_kb=11368 threads=5 fds=107` 全程稳定,关闭后 `fds=7` 无泄漏。Relay 重启后合成重连 5/5。Caddy reload(`POST /load`,config unchanged)期间经反代持有的 3 条连接不断线,`accepted=3, other_failures=0`。窗口一并发峰值资源:`rss_kb=12404 threads=6 fds` 峰值 109。

### 延迟分位数(窗口二)

100 并发握手+客户端持有 2 秒:`accepted=100, rate_limited=0, other_failures=0`,端到端 p50=2009 ms / p95=2013 ms / p99=2013 ms;扣除 2 秒合成持有,**100 并发下握手 p95≈13 ms、p99≈18 ms**。新二进制并发门复测 `125 → accepted=100, rate_limited=25` 仍精确。

### 消息大小 echo 阶梯(窗口二,10 次/档,parallel 4)

| 载荷 | p50 | p95 |
|---|---|---|
| 1 KiB | 0.83 ms | 1.47 ms |
| 64 KiB | 1.72 ms | 2.98 ms |
| 256 KiB | 3.28 ms | 5.46 ms |
| 1 MiB | 11.71 ms | 18.83 ms |

经 Caddy 反代 echo 64 KiB:p50=1.81 ms / p95=2.29 ms,`other_failures=0`。`/healthz` 直连与经 Caddy 均 `204`。

### pairing 级限流(窗口二)

同一 pairing id 60 秒窗内 8 次尝试:`accepted=5, rate_limited=3, other_failures=0`(精确执行 `60 秒/5 次`);6 个独立 pairing id 各 1 次:`accepted=6, rate_limited=0`,`tracked_pairings=7`,确认 pairing 级保护独立于全局 `100 并发/60 秒 300 次`层,不被其语义替代。

### 慢消费者背压(窗口二)

20 条连接拨号后不读,服务端每连接 `64 KiB/50 ms` 推送,持续 15 秒:

```text
pushed_bytes 于 53,739,520(≈2.6 MiB/连接,内核与库缓冲)封顶,随后 12 秒零增长
goroutines 全程恒定 43(20 会话读 + 20 推送写 + 基线 3)
rss_kb 6,468 → 8,068 后稳定;fds 稳定 27
连接关闭后:goroutines=3,fds=7,active=0
```

每条慢连接至多一个被阻塞的写 goroutine,无内部无界队列;背压有界且关闭后完全回收。

## 结论与限制

- 支持(E3):`100` 并发、`60 秒/300 次` 全局保护与 `60 秒/5 次` pairing 级保护可在目标 ECS 上作为相互独立的层精确实现,超限稳定映射 `RATE_LIMITED`;ecs.c7.large(2C4G)承载基线余量充足(RSS 峰值 <13 MiB,FD 峰值 109/65535)。
- 支持(E3):慢消费者不会无界增长内存或 goroutine;Relay 重启不恢复未投递正文(合成实现无持久化,符合"不建离线队列"约束);Caddy reload 对已建立连接语义无可观测影响。
- 支持(E3):1 MiB 合成载荷 echo p95 <20 ms,消息大小不构成本规格实例的容量瓶颈;100 并发握手 p95≈13 ms,相对 PRD 接收 P95≤5s 余量充足——但真实链路含 Noise 解密与 Connector 处理,不得宣称端到端达标。
- 未冻结:公网 WSS(TLS/域名/安全组开放,当前安全组仅放行 22,18080 未公开)、真实 Noise+Schema+SQLite 路径的容量、断网注入、单会话时长/消息量上限(Connector 清单 #9)、生产运维形态(systemd/重启策略,本次为 nohup 直跑,演练后进程已停止)。
- 门禁:`integration-profile.yaml` 继续保持 `status: pending`;本证据关闭"ECS 容量/背压/消息大小/reload 无 E3 证据"缺口,但契约 approved 仍待 Noise 固定向量签收与 Connector 公开面 #3–#9。

## 文件校验和

```text
e4824f7882283f47e2dac2f2f88ec347d87d1fcdafb332a63972c479e2ac16f2  Caddyfile
174b249f44421b781d6ac1e7824e7484dfc8e48919ca5526b0dc36ef5abd235e  go.mod
874a91c5fb043526bc117c0f260c77e4372ab11a28eb6ef2b754fdbb55101f7a  go.sum
bb267890ca769da358151f79697ce61fd62d52e291c3fbc417eb10a0a9f15062  main.go(扩展版)
351ef51ae578a1c344414164cce74f03af759d7c0ae326963e48f31d92cb59a7  main_test.go(扩展版)
b74b666feffd5958fa1b4737149e8efd6fde5bb685f8199ed872a72e50d5bbe5  relay-spike linux/amd64 二进制(窗口二部署)
```

窗口一(17:38–17:43)使用的旧版二进制构建自 2026-08-24 证据中 `ca10f3…9532` 版本的 main.go。
