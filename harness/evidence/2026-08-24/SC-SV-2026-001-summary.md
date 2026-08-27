# SC-SV-2026-001 过期或重放配对 token

日期：2026-08-24（Asia/Shanghai）
状态：Harness 语义检查通过；不代表公开契约 approved 或生产 Relay 完成。

## 范围

- 验证过期 token 和已使用 token 的配对尝试都被拒绝。
- 验证 Relay 返回既有 `PAIRING_INVALID`，不建立 pairing、不启动握手、不允许路由，也不改变 pairing 状态。
- 验证 Relay 不持久化业务正文；fixture 不包含 token、业务正文、真实标识或私钥。

## 命令

```text
harness/scripts/verify_contract_gate.sh
ruby harness/scripts/verify_pairing_expired_or_replayed.rb harness/fixtures/pairing_expired_or_replayed.json
```

## 结果

```text
pairing_expired_or_replayed_semantics=passed
cases=2
business_data=false
```

## 负向结果

将重放 token 的 `route_allowed` 篡改为 `true` 时，runner 拒绝该 fixture。

## 证据文件

- Fixture：`harness/fixtures/pairing_expired_or_replayed.json`
- Runner：`harness/scripts/verify_pairing_expired_or_replayed.rb`
- 场景登记：`harness/scenarios/catalog.yaml` / `SC-SV-2026-001`
