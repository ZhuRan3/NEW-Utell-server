# SC-SV-2026-007 限流与消息大小

日期：2026-08-28（Asia/Shanghai）
状态：Harness 语义检查通过；不代表公开契约 approved 或生产 Relay 完成。

## 范围

- 验证已确认限流参数的语义登记：全局 `100` 并发、全局 `60 秒/300 次`、pairing 级 `60 秒/5 次`，超限统一映射 `RATE_LIMITED`（Q-SV-2026-035/036/037）。
- 验证 pairing 级保护独立于全局层的语义（同 id 8 次进 5 拒 3；6 个独立 id 互不干扰）。
- 验证消息大小上限保持显式未冻结（G3 才定），且无论大小 Relay 均不持久化载荷。
- fixture 中 `e3_observed` 标记的数值来自 2026-08-27 ECS E3 实测（`harness/evidence/2026-08-27/SPK-SV-2026-001-ecs-summary.md`），非虚构。

## 命令

```text
harness/scripts/verify_contract_gate.sh
ruby harness/scripts/verify_rate_limit_and_size_semantics.rb harness/fixtures/rate_limit_and_size.json
```

## 结果

```text
rate_limit_and_size_semantics=passed
cases=5
business_data=false
```

## 负向结果

将全局并发 case 的 `accepted` 篡改为非 `100`、或将 `message_size_cap_frozen` 篡改为 `true` 时，runner 拒绝该 fixture。

## 证据文件

- Fixture：`harness/fixtures/rate_limit_and_size.json`
- Runner：`harness/scripts/verify_rate_limit_and_size_semantics.rb`
- 场景登记：`harness/scenarios/catalog.yaml` / `SC-SV-2026-007`
- E3 来源：`harness/evidence/2026-08-27/SPK-SV-2026-001-ecs-summary.md`
