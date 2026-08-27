# SC-SV-2026-006 封套重放、篡改和过期

日期：2026-08-25（Asia/Shanghai）
状态：Harness 语义检查通过；不代表公开契约 approved 或生产 Relay 完成。

## 范围

- 验证重复序号重放、完整性失败篡改和过期封套均被 Relay 拒绝。
- 验证被拒绝封套不可路由，Relay 不持久化业务正文。
- 公开错误映射尚未冻结，因此 fixture 明确禁止新增错误码，不把内部失败原因暴露为公开契约。
- fixture 不包含业务正文、真实标识、私钥或具体封套字段。

## 命令

```text
harness/scripts/verify_contract_gate.sh
ruby harness/scripts/verify_envelope_replay_tamper_expiry_semantics.rb harness/fixtures/envelope_replay_tamper_expiry.json
```

## 结果

```text
envelope_replay_tamper_expiry_semantics=passed
cases=3
business_data=false
```

## 负向结果

将重放案例篡改为 `envelope_rejected=false` 时，runner 拒绝该 fixture。

## 证据文件

- Fixture：`harness/fixtures/envelope_replay_tamper_expiry.json`
- Runner：`harness/scripts/verify_envelope_replay_tamper_expiry_semantics.rb`
- 场景登记：`harness/scenarios/catalog.yaml` / `SC-SV-2026-006`
