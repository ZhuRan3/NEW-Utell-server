# Fixtures

只保存合成密文信封、配对元数据和错误样本。禁止真实 Capture、标题、摘要、Pi 输出、账号、私钥和可解密载荷。每个 fixture 注明契约版本、场景编号和预期结果。

当前 fixture：

- `pairing_expired_or_replayed.json`：只表达过期或已使用 token 的配对拒绝和 Relay 无副作用约束，不包含业务正文或内部标识。
- `primary_connector_only.json`：只表达单主 Connector、拒绝未撤销替换和显式撤销后替换，不包含业务正文或内部标识。
- `revocation.json`：只表达已确认撤销后的路由/重连拒绝和历史数据保留约束，不包含业务正文或内部标识。
- `envelope_replay_tamper_expiry.json`：只表达重复序号、完整性失败和过期封套的拒绝，不包含业务正文、具体封套字段或内部标识。
- `ack_vs_persistent_receipt.json`：只表达 Relay ACK、Connector 持久接收回执和端点可见状态的关系，不包含业务正文或内部标识。
- `connector_offline_no_queue.json`：只表达 Connector 在线/离线时的投递结果和 Relay 不建业务队列约束，不包含业务正文或内部标识。
