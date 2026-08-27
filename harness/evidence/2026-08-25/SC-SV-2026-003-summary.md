# SC-SV-2026-003 Pairing 撤销

日期：2026-08-25（Asia/Shanghai）
状态：Harness 语义检查通过；不代表公开契约 approved 或生产 Relay 完成。

## 范围

- 验证 Connector 确认撤销后，Relay 拒绝该 pairing 后续路由和重新认证。
- 验证拒绝使用既有 `PAIRING_INVALID`，不建立会话。
- 验证 Connector 不删除权威历史数据，Relay 不持久化业务正文。
- fixture 不包含业务正文、真实标识或私钥。

## 命令

```text
harness/scripts/verify_contract_gate.sh
ruby harness/scripts/verify_revocation_semantics.rb harness/fixtures/revocation.json
```

## 结果

```text
revocation_semantics=passed
cases=2
business_data=false
```

## 负向结果

将撤销后的路由案例篡改为 `route_allowed=true` 时，runner 拒绝该 fixture。

## 证据文件

- Fixture：`harness/fixtures/revocation.json`
- Runner：`harness/scripts/verify_revocation_semantics.rb`
- 场景登记：`harness/scenarios/catalog.yaml` / `SC-SV-2026-003`
