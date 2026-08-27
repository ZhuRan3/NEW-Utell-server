# 服务器端 Harness

harness 用于在不依赖真实手机、Connector 或生产云的情况下验证 Relay 的公开行为、安全失败和投递语义。它不是生产代码，不收集真实业务内容。

跨端契约入口是 `契约/integration-profile.yaml`；两端文件必须逐字节一致。契约治理、版本、同步、审批、时间盒和新会话交接规则见 `文档/架构与契约/跨端公开契约治理规范.md`。

所有 Harness 会话和证据汇报必须遵循 `开发规则规范/07-人类可读进度与技术沟通规范.md`：先给项目驾驶舱，再给测试站证据；保留 English/缩写/字段/参数，每次最多教学 1–3 个新术语；明确 `已证实`、`待证据`、`待决策`、`待开发`，不得把 runner 通过写成产品或生产完成。会话开始先读 `文档/交流记录/项目驾驶舱.md`，结束时按需更新驾驶舱、术语学习卡和证据索引。

## 目录

- `契约/`：Transport、错误码、兼容范围和向量索引。
- `fixtures/`：合成密文信封、配对和错误样本。
- `mocks/`：synthetic mobile、synthetic Connector 和测试密钥替身。
- `scenarios/`：Given/When/Then 与故障注入。
- `evidence/`：按日期保存测试摘要、脱敏日志和校验和。
- `scripts/`：可重复命令，不含凭据。

## 最小验收集

配对、单主约束、撤销、ACK、Connector 离线不入队、重放/篡改/过期拒绝、限流、大小限制、重启恢复、TLS/密钥轮换和 Relay 无法解密证明。

## 当前下游门禁

在两个仓库都存在且逐字节同步的前提下运行：

```text
harness/scripts/verify_contract_gate.sh
```

该命令只验证公开契约和 Harness 登记完整性，不批准契约、不运行生产代码。场景登记见 `scenarios/catalog.yaml`；`planned` 场景仍需在契约获批后补齐 fixture、mock、执行脚本和脱敏证据。

运行全部已登记为 `ready` 的场景：

```text
ruby harness/scripts/run_ready_scenarios.rb
```

以上命令的退出状态只说明本次 Harness 检查结果；汇报时必须同时记录命令、环境、证据位置、可证明范围和限制。
