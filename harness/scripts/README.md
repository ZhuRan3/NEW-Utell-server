# Scripts

脚本必须可重复执行、参数显式、失败返回非零状态，不依赖开发者私有路径、生产凭据或外部未锁定状态。

当前脚本：

- `verify_contract_gate.sh`：校验两端 `integration-profile` 逐字节一致、契约状态、Harness required scenarios、场景目录和契约 section 依赖。
- `run_ready_scenarios.rb`：先执行契约门禁，再按目录自动运行全部 `ready` fixture/runner。
- `verify_pairing_expired_or_replayed.rb`：执行 `pairing_expired_or_replayed` 脱敏语义检查。
- `verify_primary_connector_only_semantics.rb`：执行 `primary_connector_only` 脱敏语义检查。
- `verify_revocation_semantics.rb`：执行 `revocation` 脱敏语义检查。
- `verify_envelope_replay_tamper_expiry_semantics.rb`：执行 `envelope_replay_tamper_expiry` 脱敏语义检查。
- `verify_ack_receipt_semantics.rb`：执行 `ack_vs_persistent_receipt` 脱敏语义检查。
- `verify_connector_offline_no_queue.rb`：执行 `connector_offline_no_queue` 脱敏语义检查。
- `verify_rate_limit_and_size_semantics.rb`：执行 `rate_limit_and_size` 脱敏语义检查。
- `verify_relay_restart_semantics.rb`：执行 `relay_restart` 脱敏语义检查。
- `verify_relay_cannot_decrypt_semantics.rb`：执行 `relay_cannot_decrypt` 脱敏语义检查。

脚本执行结果必须按 `开发规则规范/07-人类可读进度与技术沟通规范.md` 登记到测试站证据：记录实际命令、退出码、环境、通过范围、未覆盖范围和证据位置。脚本通过不等于契约批准或生产就绪。
