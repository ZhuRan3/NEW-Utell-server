# SC-SV-2026-008 Relay 重启

日期：2026-08-28（Asia/Shanghai）
状态：Harness 语义检查通过；不代表公开契约 approved 或生产 Relay 完成。

## 范围

- 验证重启后 pairing 注册表、公钥与审计元数据（14 天留存）保留。
- 验证在途未投递密文不恢复、不建离线队列，发送端在重启窗口观测 `RELAY_UNREACHABLE`。
- 验证旧会话不恢复、必须完整 Noise 重握手（Q-SV-2026-024）；重启后重连 5/5 与 `/healthz` 204 为 2026-08-27 ECS E3 实测值。
- 验证健康上报间隔语义为 10 秒（C4）。

## 命令

```text
harness/scripts/verify_contract_gate.sh
ruby harness/scripts/verify_relay_restart_semantics.rb harness/fixtures/relay_restart.json
```

## 结果

```text
relay_restart_semantics=passed
cases=4
business_data=false
```

## 负向结果

将 `inflight_undelivered_recovered` 篡改为 `true`、或将 `audit_retention_days` 篡改为非 `14` 时，runner 拒绝该 fixture。

## 证据文件

- Fixture：`harness/fixtures/relay_restart.json`
- Runner：`harness/scripts/verify_relay_restart_semantics.rb`
- 场景登记：`harness/scenarios/catalog.yaml` / `SC-SV-2026-008`
- E3 来源：`harness/evidence/2026-08-27/SPK-SV-2026-001-ecs-summary.md`
