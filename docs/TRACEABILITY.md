# 论文需求到实现与独立验证的映射（P0）

主证据、页码规则、状态与歧义定义见 [PAPER_CONTRACT.md](PAPER_CONTRACT.md)。本文件中的源码和测试路径全为 **planned**，不存在已实现声明。验证设想是待审核设计，**未执行，也不是已批准 golden**。科学审查需要来源核验与独立推导，不能由实现者独自验收。实现功能、CPU 算法单测、GPU/NCCL、真实训练与端到端复现当前均 **NOT_RUN**。

每行的行为含输入输出与生命周期约束；详细参数与 UNKNOWN 在论文规格同名 ID 下。可信度指论文来源可靠程度，不是行为已实证程度。

| Paper ID | 论文位置（印刷页 / PDF页） | 需求与来源可信度 | planned 源码路径 | 独立验证设想 / planned 测试路径 | 状态 |
|---|---|---|---|---|---|
| F-ARCH-01 | §3.2.1 图3-1，23–24 / 39–40；§3.3.2，33–34 / 49–50 | 三层数据流；状态0→1→0；100–500ms轮询；首次调用惰性初始化。F-direct；失败恢复 UNKNOWN | `src/flash/control/state.py`、`src/flash/probe/lifecycle.cc` | V-ARCH-01：独立时间线覆盖迟到节点、重复触发、失联与恢复；先确定部分结果语义。`tests/contracts/test_state_lifecycle.py` | NOT_RUN |
| F-PROBE-01 | §3.2.1，23–24 / 39–40；§3.3.1，32 / 48 | 包装函数调用原NCCL并保留结果；API清单/重入 UNKNOWN。F-limited | `src/flash/probe/interpose.cc` | V-PROBE-01：后续授权的 CPU 替身库检查参数、返回值、调用次数与递归；真实异步NCCL必须另验。`tests/contracts/test_interposition.py` | NOT_RUN |
| F-SHM-01 | §3.3.1，32–33 / 48–49 | 锁写/无锁读/清空；元数据+事件布局；数据丢失有明示但界限 UNKNOWN。F-limited | `src/flash/probe/shared_memory.h`、`src/flash/local/shared_memory.py` | V-SHM-01：独立布局审查；写入与读清空交错、回绕、溢出、进程退出反例；不能把无崩溃等同无丢失。`tests/contracts/test_shared_memory.py` | NOT_RUN |
| F-COMM-01 | §3.2.3，30 / 46；§3.3.1–3.3.3，32–35 / 48–51 | id_hash→clique；完整→简化降级；parallel states→标签；身份/特殊组 UNKNOWN。F-limited | `src/flash/topology/communicators.py` | V-COMM-01：相同成员不同ID、地址复用、缺成员、hash碰撞、重叠标签；独立人工成员表核对。`tests/contracts/test_topology.py` | NOT_RUN |
| F-ITER-01 | §3.2.2，25–26 / 41–42；§3.3.3，35 / 51 | Rank0；`iteration:time_ms`；列表500/窗口30；完整迭代计时。F-direct，计时边界 UNKNOWN | `src/flash/integration/iteration_reporter.py` | V-ITER-01：固定序列检查单位、重复乱序、缺样本、编号重启；异步工作覆盖须后续框架证据。`tests/contracts/test_iteration_input.py` | NOT_RUN |
| F-BOCD-01 | §3.2.2，26 / 42；§3.3.2，33 / 49 | Rbeast/BOCD；30、0.8、0.2；后验/退化公式 UNKNOWN。F-limited | `src/flash/detection/change_points.py` | V-BOCD-01：独立生成平稳、持续阶跃、轻微阶跃、恢复、多变点序列；首先审核概率含义与参数，禁止依实现反写golden。`tests/science/test_change_points.py` | NOT_RUN |
| F-FILTER-01 | §3.2.2，26–27 / 42–43；§3.4.3、3.4.5，40、44 / 56、60 | recovery>=0.75过滤；相距<2；预热3；z>3；持续时间 CONFLICT。F-limited | `src/flash/detection/filters.py` | V-FILTER-01：独立手算恢复比率、空切片/零分母、阈值两侧、原编号距离、z-score常量/持续阶跃。`tests/science/test_filters.py` | NOT_RUN |
| F-FAILSTOP-01 | §3.2.4，31 / 47；§3.3.2，34 / 50 | 动态无新调用窗口（2倍仅示例）；`failstop_ranks`；根因性 UNKNOWN。F-limited | `src/flash/local/failstop.py` | V-FAILSTOP-01：合成调用流含死亡rank、等待的健康rank、正常长计算；缺失记录不能自动算死亡。后续注入另授权。`tests/science/test_failstop_observation.py` | NOT_RUN |
| F-PROFILE-01 | §3.2.3，27–28 / 43–44；§3.3.2，34 / 50；§3.4.5，44 / 60 | 动态窗口max(2.2×iter_seconds,20s)；min/max/avg/std；结束回监控。F-limited；延迟口径 CONFLICT | `src/flash/local/profiler.py` | V-PROFILE-01：ms→s手算、迟到/空/过期统计、未完成事件、异常恢复；独立时间线核实际覆盖。`tests/contracts/test_profile_window.py` | NOT_RUN |
| F-TIMING-01 | §3.2.3，28–29 / 44–45；§3.3.1，33 / 49 | stream Event含GPU等待；Group一对事件且复制duration；per-call/Group CONFLICT。F-limited | `src/flash/probe/cuda_timing.cc` | V-TIMING-01：先独立审查stream/Event依赖图；获GPU授权后单/多stream、分组/非分组、ring/tree/不同算子、迟到rank与网络慢反例。`tests/gpu/test_timing_semantics.py` | NOT_RUN |
| F-CLIQUE-01 | §3.2.3 图3-4，30 / 46；§3.3.2，34 / 50；式(3-1)，41 / 57 | 排除单rank；多组CV门槛0.1；max_avg最大；单组直入；均值指标 CONFLICT。F-limited | `src/flash/analysis/cliques.py` | V-CLIQUE-01：独立构造max和mean排序相反的组；单组、CV边界、tie与缺rank。`tests/science/test_clique_selection.py` | NOT_RUN |
| F-RANK-01 | §3.2.3，30–31 / 46–47；§3.3.2，34 / 50；式(3-2)，42 / 58 | clique内rank平均时延最小；CV>=0.1；20%门槛公式 UNKNOWN。F-limited | `src/flash/analysis/ranks.py` | V-RANK-01：独立手算低时延rank、CV小而有argmin、CV大但得分<20%、tie/多故障/加权差异。`tests/science/test_rank_selection.py` | NOT_RUN |
| F-FUSION-01 | §3.2.3，31 / 47；§3.4.6，44–45 / 60–61 | 跨标签同rank证据与CRITICAL日志；评分和/门槛 UNKNOWN。F-limited | `src/flash/analysis/evidence.py` | V-FUSION-01：相同候选、冲突、重叠标签、单标签和多故障；核日志证据与原统计一致。`tests/science/test_cross_tag_evidence.py` | NOT_RUN |
| F-MOE-01 | §3.1.3，23 / 39；§3.4.6，44–45 / 60–61；§3.5.1，46 / 62 | 稳定DP/TP/PP/expert_dp辅助；不直接覆盖DeepEP/Gloo/MPI。F-direct | `src/flash/topology/parallel_states.py` | V-MOE-01：独立人工拓扑核4组论文配置、PP点对点和EP覆盖缺口；不能只用合成标签证明真实MoE支持。`tests/science/test_parallel_coverage.py` | NOT_RUN |
| F-INTEGRATION-01 | §3.2.1，24 / 40；§3.3.3，35 / 51；§3.4.2，37–38 / 53–54 | 迭代/parallel states少量框架适配；用户主逻辑透明；零适配 CONFLICT。F-limited | `src/flash/integration/` | V-INTEGRATION-01：分层审查脚本/框架/适配器改动，独立数核心行、验证关闭时行为；训练框架改动另授权。`tests/contracts/test_integration_contract.py` | NOT_RUN |
| F-LIMIT-01 | §3.4，36–45 / 52–61；§3.5.2–3.5.3，46–47 / 62–63 | duration-only基线；count/bandwidth属于改进；结果口径待审。F-direct | `src/flash/analysis/`（faithful）；改进另立路径/PR | V-LIMIT-01：不同消息量低时延反例应记录为已知局限，不能弱化断言或换成bandwidth以制造原方案PASS。`tests/science/test_known_limitations.py` | NOT_RUN |

## 不依赖实现的审查样例

以下算术用于说明为什么必须先定语义；不构成算法测试执行结果，也不宣称某解释已获批准。

| 样例 | 独立推导 | 用途 |
|---|---|---|
| V-FILTER-01-A | 左侧均值100，右侧 `[200,100,100]`：degraded=400/3、recent=100，恢复比率1，按明示规则过滤；右侧全为200则比率0 | 独立区分尖峰与持续阶跃；右侧单点、分母0仍UNKNOWN |
| V-PROFILE-01-A | 迭代1000ms=1s，窗口为20s；迭代10000ms=10s，窗口为22s | 捕捉把time_ms直接代入秒数公式的单位错误 |
| V-CLIQUE-01-A | 组A communicator均值 `[100,100]`，组B为`[10,150]`：max指标选B；组内均值指标选A | max与mean会改变实际候选，不能当文字差异忽略 |
| V-RANK-01-A | rank时延 `[100,100,60]`：组均值260/3，60的式(3-2)得分4/13≈30.77%；rank时延`[100,100,80]`：得分1/7≈14.29%，两者CV均可超过0.1（无论常见总体/样本定义） | 第二组显示CV+argmin与追加20%门槛可能产生不同判定；尚未批准门槛公式 |
| V-RANK-01-B | `[100,100,99]` 总有argmin，但CV远小于0.1 | 明确“最小”不能单独成为定位证据 |
| V-LIMIT-01-A | 1MB/100ms=10MB/s；10MB/700ms≈14.29MB/s | 原方案绝对时延排序与吞吐排序不同；预期为暴露局限，不能擅改基线 |
| V-FAILSTOP-01-A | 一个rank退出，其他rank进入一次永不返回的同步调用；此后所有rank都没有新调用 | 调用停滞集合不能单独推出唯一根因rank；不需要真实注入就能审查逻辑边界 |

## 后续验证记录要求

每项实际执行必须记录：需求/验证ID、状态 `PASS/FAIL/NOT_RUN/INCONCLUSIVE`、验证对象 commit、最小环境信息、可复现命令、真实退出码、脱敏证据路径与失败尝试。上表尚无测试文件与命令，因此不可补写执行退出码为0。文档完整性检查成功只证明文档结构，不证明任一机制成立。GPU、真实训练、注入和科学结论需要各自授权与证据；离线样例和独立Agent检查均不能替代 ChatGPT 的关键科学审查。
