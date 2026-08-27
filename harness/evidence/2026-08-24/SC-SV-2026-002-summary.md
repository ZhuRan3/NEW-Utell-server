# SC-SV-2026-002 单主 Connector 约束

日期：2026-08-24（Asia/Shanghai）
状态：Harness 语义检查通过；不代表公开契约 approved 或生产 Relay 完成。

## 范围

- 验证每个 pairing 最多一台 active 主 Connector。
- 未显式撤销旧 pairing 时，第二 Connector 不建立新 pairing，旧主继续可路由，状态不发生变化。
- 只有显式撤销旧 pairing 后，替换 Connector 才能成为新的主 Connector；旧主停止路由且 active 主数量仍为一。
- 不对尚未冻结的替换失败公开错误码作臆造；fixture 不包含业务正文、真实标识或私钥。

## 命令

```text
harness/scripts/verify_contract_gate.sh
ruby harness/scripts/verify_primary_connector_only_semantics.rb harness/fixtures/primary_connector_only.json
```

## 结果

```text
primary_connector_only_semantics=passed
cases=3
business_data=false
```

## 负向结果

将未撤销替换案例篡改为 `new_connector_route_allowed=true` 时，runner 拒绝该 fixture。

## 证据文件

- Fixture：`harness/fixtures/primary_connector_only.json`
- Runner：`harness/scripts/verify_primary_connector_only_semantics.rb`
- 场景登记：`harness/scenarios/catalog.yaml` / `SC-SV-2026-002`
