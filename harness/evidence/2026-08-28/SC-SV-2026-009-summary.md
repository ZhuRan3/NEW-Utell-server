# SC-SV-2026-009 Relay 不可解密

日期：2026-08-28（Asia/Shanghai）
状态：Harness 语义检查通过；不代表公开契约 approved 或生产 Relay 完成。

## 范围

- 验证 Relay 路由字节仅为密文，不读明文、不解密载荷；E2EE 在端点终止。
- 验证 Relay 持久化面精确等于 {pairing 元数据， 公钥， 审计元数据}，永不持久化业务载荷/私钥/明文。
- 验证完全失陷假设（Relay 主机与数据库全读）下不可恢复明文与私钥。
- fixture 不含真实业务正文、私钥或真实标识；forbidden_keys 脱敏扫描通过。

## 命令

```text
harness/scripts/verify_contract_gate.sh
ruby harness/scripts/verify_relay_cannot_decrypt_semantics.rb harness/fixtures/relay_cannot_decrypt.json
```

## 结果

```text
relay_cannot_decrypt_semantics=passed
cases=3
business_data=false
```

## 负向结果

将 `relay_holds_private_keys` 篡改为 `true`、或在 fixture 中加入 `private_key`/`plaintext` 字段时，runner 拒绝该 fixture。

## 证据文件

- Fixture：`harness/fixtures/relay_cannot_decrypt.json`
- Runner：`harness/scripts/verify_relay_cannot_decrypt_semantics.rb`
- 场景登记：`harness/scenarios/catalog.yaml` / `SC-SV-2026-009`
