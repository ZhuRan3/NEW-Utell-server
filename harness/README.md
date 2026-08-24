# 服务器端 Harness

harness 用于在不依赖真实手机、Connector 或生产云的情况下验证 Relay 的公开行为、安全失败和投递语义。它不是生产代码，不收集真实业务内容。

跨端契约入口是 `契约/integration-profile.yaml`；两端文件必须逐字节一致。契约治理、版本、同步、审批、时间盒和新会话交接规则见 `文档/架构与契约/跨端公开契约治理规范.md`。

## 目录

- `契约/`：Transport、错误码、兼容范围和向量索引。
- `fixtures/`：合成密文信封、配对和错误样本。
- `mocks/`：synthetic mobile、synthetic Connector 和测试密钥替身。
- `scenarios/`：Given/When/Then 与故障注入。
- `evidence/`：按日期保存测试摘要、脱敏日志和校验和。
- `scripts/`：可重复命令，不含凭据。

## 最小验收集

配对、单主约束、撤销、ACK、Connector 离线不入队、重放/篡改/过期拒绝、限流、大小限制、重启恢复、TLS/密钥轮换和 Relay 无法解密证明。
