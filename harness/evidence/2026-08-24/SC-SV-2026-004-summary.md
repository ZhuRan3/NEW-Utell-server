# SC-SV-2026-004 ACK 与 Connector 持久接收回执

日期：2026-08-24（Asia/Shanghai）
状态：Harness 语义检查通过；不代表公开契约 approved 或生产 Relay 完成。

## 范围

- 仅验证 Relay ACK 与 Connector 持久接收回执不能混为同一状态。
- 仅使用合成布尔观察值和端点可见状态。
- 不包含业务正文、真实标识、私钥、Capture ID 或未冻结 Envelope 字段。

## 命令

```text
harness/scripts/verify_contract_gate.sh
ruby harness/scripts/verify_ack_receipt_semantics.rb
```

## 结果

```text
profile_gate=passed
status=pending
scenarios=9
ack_receipt_semantics=passed
cases=2
business_data=false
```

覆盖两个情况：

- 只有 Relay ACK：发送端不能把路由层观察当作 Connector 持久接收。
- 已观察 Connector 持久接收回执：才允许向端点传播 `RECEIVED` 语义，仍不能提前传播 `COMMITTED` 或 `PROJECTED`。

## 负向结果

将“只有 Relay ACK”篡改为 `RECEIVED` 时，runner 拒绝并报告状态映射错误。

## 证据文件

- Fixture：`harness/fixtures/ack_vs_persistent_receipt.json`
- Runner：`harness/scripts/verify_ack_receipt_semantics.rb`
- 场景登记：`harness/scenarios/catalog.yaml` / `SC-SV-2026-004`
