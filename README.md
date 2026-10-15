# FLASH-Reproduction

独立重建师兄硕士论文第三章 **FLASH：大模型分布式训练的无侵入低开销故障定位**。目标不是改写论文方案，也不是仅复现实验曲线，而是获得**可运行、可验证、可演示**的完整系统。

## 工作边界
- **唯一工程仓库：** 本仓库。禁止从任何历史失败复现仓库复制代码、日志或构建产物；仅依据本次批准的论文与公开参考源码开展独立实现。
- **主要证据：** 项目所有者电脑上可供 Codex 读取的 FLASH 中文论文、GREYHOUND 论文；参考公开仓库 [wutianyuan1/Greyhound](https://github.com/wutianyuan1/Greyhound)。由 Codex 首先核实本地论文文件、版本及 SHA-256，并锁定公开仓库 commit；不得把未经授权的论文、原始训练日志或秘密上传到 Public 仓库。
- **目标范围：** FLASH 第三章 NCCL Probe / 共享内存 / 本地及全局控制器 / BOCD 检测和过滤 / on-demand CUDA profiling / 两阶段 clique→rank 定位 / Fail-Stop / 混合并行、MoE 支持 / 真实端到端验证。SHIFT 不在本轮范围。
- **研究路线：** Faithful FLASH 先行；改进方案单独登记，在忠实复现基线可验证前不混入主线。
- **项目协作：** Owner 决策并授权；ChatGPT 负责独立科学审查；Codex 主智能体协调离线开发及子智能体；GitHub Issues/PR/CI 保存可恢复记录。

## Codex 启动入口
1. 阅读 [AGENTS.md](AGENTS.md)、[当前状态](docs/STATE.md)、GitHub 最新 Issue / PR。
2. 先执行标记为可授权执行的 **P0** 工作；未授权不进入实际服务器或破坏性实验。
3. 工作完成后以 Draft PR、测试记录、问题清单及状态更新提交审查；不凭聊天结论声明复现成功。

## 当前状态
**P0 离线研究审查阶段。** 本次成果关联 [Issue #1](https://github.com/Zwhao0/FLASH-Reproduction/issues/1)，不代表任何 FLASH 功能已经实现，也不代表 GPU、训练、NCCL 或论文忠实性经过验证。

审查入口：[来源与许可](docs/SOURCES.md) → [论文机制契约](docs/PAPER_CONTRACT.md) / [逐项追踪](docs/TRACEABILITY.md) → [关键待决策项](docs/DECISIONS.md)。另见 [GREYHOUND 对照](docs/GREYHOUND_COMPARISON.md)、[P0–P6 路线](docs/ROADMAP.md)、[GitHub 保护方案](docs/GITHUB_POLICY.md) 和 [验证与失败证据](docs/evidence/P0_VALIDATION.md)。当前事实、提交及 PR 以 [STATE](docs/STATE.md) 为准。

## 安全
当前仓库为 Public。不要提交 SSH 信息、IP/用户名、令牌、论文 PDF（未经授权时）、未脱敏服务器信息或真实任务日志。真实服务器可连通不等于获得运行/改动授权。
