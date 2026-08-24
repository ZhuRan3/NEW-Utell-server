# Noise 首发 Pattern 选择学习包

这是 NEW-Utell 在技术栈冻结前的 D4 学习与决策材料，回答“首发采用 `Noise_XX_25519_ChaChaPoly_SHA256` 还是 IK，以及为什么”。

## 文件

- `Noise首发Pattern选择.html`：带目录、流程图、思维导图、对比图和生动例子的学习页面。
- `Noise首发Pattern选择学习讲义.md`：可维护文字真源。
- `来源与证据台账.md`：官方规范、实现文档、论坛/Issue、教学材料和项目内部证据。
- `冻结前决策清单.md`：正式冻结前要由 Phone/Connector 共同关闭的事项。
- `assets/`：SVG 图形，直接嵌入 HTML，相对路径可离线打开。

## 当前结论

首发建议使用 `Noise_XX_25519_ChaChaPoly_SHA256`：它不要求握手前已绑定 Connector 静态公钥，能自然接上扫码、一次性 token 和指纹核对；代价是比 IK 多半个握手往返。IK 适合未来“已完成可信配对、静态公钥已缓存”的重连优化，但不是首发默认。

本机 Spike 和固定向量已完成，但这不会自动把两端契约状态改成 `approved`；仍需 Connector 共同验收和正式封套冻结后再更新 `integration-profile.yaml`。

## 打开方式

直接用浏览器打开 `Noise首发Pattern选择.html`。页面不依赖网络，SVG 图在同目录 `assets/` 下。
