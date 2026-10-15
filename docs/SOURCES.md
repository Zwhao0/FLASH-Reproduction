# 研究来源与权利边界（P0 初稿）

核验日期：2026-10-15。目标仅为 FLASH 第三章；GREYHOUND 是机制与接口对照，不是 FLASH 规格的替代来源。本次没有编译、导入或执行参考系统，没有读取参考仓库内训练日志，也未引入第三方实质代码。

## 1. 来源登记

| ID | 来源、版本与校验 | 阅读范围与页码 | 可信度及未验证部分 | 许可/复用状态 |
| --- | --- | --- | --- | --- |
| SRC-FLASH | 《面向大模型分布式训练稳定性的故障定位与弹性恢复研究》；英文题名 *Fault Localization and Elastic Recovery for Large-Scale Distributed Training Stability*；封面/答辩日期 2026-04-07；作者/导师为脱敏占位；105 页 PDF；SHA-256 `1221fe9eb75d19084b786265114b8a9a91dc1df5b96950ddd47bc827333470db` | 第三章 §§3.2–3.5，印刷页 23–47 = PDF 页 39–63；图表与公式是规格定位依据，页面复核记录由主流程汇总；第一章、第二章仅作术语与相关工作背景 | 本轮 Owner 提供的目标原始文献，目标规格最高来源；可以提取文本，公式/流程图须结合页面复核；不能证明是公开最终版，也不能证明实现/实验结论。作者身份未确认、不推断 | 已授权本地研究；未见向公共仓库再分发 PDF、截图或大段文字的授权。仅提交独立归纳、定位引用与校验摘要 |
| SRC-GH-PAPER | Tianyuan Wu 等，*GREYHOUND: Hunting Fail-Slows in Hybrid-Parallel Training at Scale*；USENIX ATC 2025，印刷页 731–747；本地文件 18 页，含会议封面；SHA-256 `e9829d78bcdfb08029f4664f1e27e680f039a4e6c0fd858e2d0287dcfd8fcd88` | §§4.1–4.3、§6 为检测/架构/实现对照；§5 仅辨别缓解方案不属 FLASH 范围。PDF 页 2 = 印刷页 731，换算 PDF 页 = 印刷页 −729；§4.2 PDF 7–8/印736–737；§4.3 PDF8–9/印737–738；§6 PDF11–12/印740–741 | 论文文字可提取；[USENIX 正式出版页](https://www.usenix.org/conference/atc25/presentation/wu-tianyuan) 核对题名、作者、会议与页码。未下载另一份 PDF 做逐字节等同性比较；论文声称不等于本项目验证结果 | 正式网站开放阅读不等于取得任意改编/再分发许可。本地 PDF 不提交 |
| SRC-GH-CODE | [wutianyuan1/Greyhound](https://github.com/wutianyuan1/Greyhound/tree/d641b3997c17de700e1ef7d37e353418df7e336d)，锁定 commit `d641b3997c17de700e1ef7d37e353418df7e336d`；2026-10-15 `git ls-remote … HEAD` 返回该 SHA；递归 Git tree 的 `truncated=false` | 先枚举许可文件，再读取 detector 关键接口与算法文件；见下表及[对照文档](GREYHOUND_COMPARISON.md)。未读取 `trainlog/` 内容，未执行启动器、安装脚本、注入器 | 固定版本源码的一手静态证据；仅能证明该文件的文本行为，不能证明正常运行、论文实验一致或目标 FLASH 语义 | 根目录和 detector 子树未发现 LICENSE/COPYING/NOTICE，已读 detector 文件未发现许可证头；状态 `UNKNOWN / ANALYSIS_ONLY`。`Megatron-LM/LICENSE` 不能未经确认外推到 sibling detector |
| SRC-NCCL-DOC | [NVIDIA NCCL Group Calls](https://docs.nvidia.com/deeplearning/nccl/user-guide/docs/usage/groups.html)，2026-10-15读取，页面标为2.32.3 | group延迟入队、嵌套group、非阻塞group | 正式API文档；只约束可验证的语义疑问，不代表论文或目标环境实际版本 | 仅链接/独立概括，无代码引入 |
| SRC-CUDA-DOC | [CUDA Runtime Event Management](https://docs.nvidia.com/cuda/cuda-runtime-api/cuda_runtime_api/group__CUDART__EVENT.html)，2026-10-15读取，页面标为13.4 | EventRecord、Synchronize、ElapsedTime | 正式API文档；event仅捕获指定stream的已有工作，可能受其他stream调度影响，同步等待可能扰动host；不能外推目标环境已经正确 | 仅链接/独立概括，无代码引入 |
| SRC-RBEAST-DOC | [zhaokg/Rbeast README](https://github.com/zhaokg/Rbeast)，2026-10-15读取，未固定包版本 | Bayesian模型平均、趋势/季节/变点分解、MCMC说明 | 作者项目说明，不是Adams–MacKay在线run-length后验等同性证明；未读/引入其实现、未安装包 | 仅README语义研究，不形成复用许可结论 |

FLASH 页码换算只针对正文阿拉伯页码：PDF 页 = 印刷页 +16。摘要等罗马页码不适用。上述 SHA-256 标识本轮文件字节，不构成真实性签名。私有绝对路径、PDF 元数据原始输出与提取全文仅在受控本地保存。

## 2. 固定源码的逐文件审阅与权利来源

以下相对路径均属于 SRC-GH-CODE 的固定 commit。`U` 表示该文件无已确认适用许可，仅作静态机制/接口分析，不复制或改编实质代码；这是一项保守的项目复用门禁，不是法律裁定。未审阅文件也不获复用授权。

| 路径 | 已审阅用途 | 权利状态 |
| --- | --- | --- |
| `README.md` | 官方 artifact 入口、ACF/BOCD/按需 profiling/validation 的描述；不运行其命令 | U |
| `detector/ncclprobe.cpp` | NCCL 包装、初始化、group 边界、记录与控制检查位置 | U |
| `detector/global_status.cpp` | 计时 event、同步、状态与控制器启动依赖；仅静态阅读 | U |
| `detector/global_status.hpp` | 状态、计时与运行时数据接口 | U |
| `detector/event_handler.cpp` | 暂停/恢复及微基准任务路径；未执行 | U |
| `detector/config.hpp` | 状态/记录编号与数据格式配置 | U |
| `detector/shm_storage.hpp` | 共享内存记录接口 | U |
| `detector/shm_topo.hpp` | 共享内存拓扑接口 | U |
| `detector/comm.hpp` | communicator 与拓扑描述接口 | U |
| `detector/control_plane/communicator.py` | communicator 序列化字段、rank 身份与 ring/tree 数据 | U |
| `detector/control_plane/slow_detection.py` | ACF、Rbeast 调用、离群过滤和变点验证 | U |
| `detector/control_plane/local_analyzer.py` | 迭代估计入口、按 communicator 聚合 duration/count | U |
| `detector/control_plane/local_controller.py` | 故障报告、profiling 统计、事件未增长判定 | U |
| `detector/control_plane/global_analyzer.py` | 并行状态、clique 构建、组级候选筛选 | U |
| `detector/control_plane/global_topo.py` | ring/tree 重建接口 | U |
| `detector/control_plane/global_controller.py` | monitor/profile/validate 状态及微基准调度 | U |
| `detector/control_plane/megatron_logger.py` | TP/DP/PP 框架元数据上报接口 | U |
| `detector/CMakeLists.txt` | 构建依赖与模块边界，只读 | U |
| `detector/setup.py` | 控制器包/入口登记，只读 | U |
| `Megatron-LM/LICENSE` | 唯一在递归树中命中的许可证文件；含 NVIDIA 条款及按文件声明适用的 Apache/MIT 等第三方条款 | 子目录存在混合许可文本；未逐文件核验 Megatron 实现，不能称整个参考仓库统一 MIT/Apache/BSD 许可 |

许可文件原文见 [固定版 Megatron-LM/LICENSE](https://github.com/wutianyuan1/Greyhound/blob/d641b3997c17de700e1ef7d37e353418df7e336d/Megatron-LM/LICENSE)。源码 tree 与文件内容的私人研究副本不属于公共交付。若后续拟复用任何片段，必须另外提交该片段的具体许可、原始权利链、归属/notice 要求及引入方式，经独立审查与 Owner 批准；当前默认保持独立重建。

## 3. 可复核方法与证据限度

- 文件核验使用 SHA-256；PDF 页数和文本提取仅证明可读性。页面级解释仍需科学审查。
- 源码固定：`git ls-remote https://github.com/wutianyuan1/Greyhound.git HEAD`，再读取 `https://api.github.com/repos/wutianyuan1/Greyhound/git/trees/d641b3997c17de700e1ef7d37e353418df7e336d?recursive=1`；必须核对 `sha` 与 `truncated`。随后文件读取 URL 都包含固定 SHA，不依赖漂移的 master。
- 许可检查覆盖完整 tree 的文件名和上表已读源码的许可头；不是全部源码内容审计，不代表权利链已经查清。
- 本轮只读静态证据可标为 `PASS`；参考系统构建、CPU 算法运行、CUDA/NCCL、真实训练与实验对比均为 `NOT_RUN`。源码与论文差异属于 `CONFLICT`，不能通过选一套默认值消除。
- [论文规格](PAPER_CONTRACT.md)、[追踪矩阵](TRACEABILITY.md)、[待决策项](DECISIONS.md) 应继续区分目标原文、参考论文、参考源码与独立假设。
