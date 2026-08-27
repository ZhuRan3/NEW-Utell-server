# Scenarios

场景采用 Given/When/Then，必须同时写出 Relay 可见元数据、持久化副作用和用户/端点可见结果。场景编号使用 `SC-SV-YYYY-NNN`。

`catalog.yaml` 是当前 P0 场景的登记表。`planned` 只表示场景已拆解、尚未具备可执行实现；`ready` 只表示 Harness 语义检查已具备 fixture 和 runner，不代表公开契约已批准或生产实现已完成。

场景结果的对人汇报必须遵循 `../../开发规则规范/07-人类可读进度与技术沟通规范.md`，保留场景 ID、Given/When/Then、状态标签、技术术语和证据边界；`ready` 不得在驾驶舱中简写成“功能已完成”。

运行 `scripts/verify_contract_gate.sh` 会检查 `harness.yaml` 声明的每个 required scenario 都已登记，并校验其依赖的契约 section。
