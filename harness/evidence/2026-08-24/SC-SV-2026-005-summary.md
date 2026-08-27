# SC-SV-2026-005 Connector 离线不建业务队列

日期：2026-08-24（Asia/Shanghai）
状态：Harness 语义检查通过；不代表公开契约 approved 或生产 Relay 完成。

## 范围

- 验证 Connector 离线时 Relay 不建立离线业务队列。
- 验证 Connector 离线时路由错误为已定义的 `ROUTE_NOT_DELIVERED`；在线情况不预设新的公开枚举。
- 验证 Relay 不持久化业务正文或可解密载荷。

## 结果

```text
connector_offline_no_queue=passed
cases=2
business_data=false
```

## 证据文件

- Fixture：`harness/fixtures/connector_offline_no_queue.json`
- Runner：`harness/scripts/verify_connector_offline_no_queue.rb`
- 场景登记：`harness/scenarios/catalog.yaml` / `SC-SV-2026-005`
