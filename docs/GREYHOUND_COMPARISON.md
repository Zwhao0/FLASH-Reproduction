# GREYHOUND 与 FLASH 的机制对照（P0，仅静态研究）

目标是忠实重建 FLASH 第三章。参考版本固定为 `wutianyuan1/Greyhound@d641b3997c17de700e1ef7d37e353418df7e336d`（[固定源码树](https://github.com/wutianyuan1/Greyhound/tree/d641b3997c17de700e1ef7d37e353418df7e336d)）。来源校验与逐文件许可见 [SOURCES.md](SOURCES.md)；detector 许可未确认，未复制实质源码、未构建或执行参考系统。下文 `CONFIRMED_TEXT` 只表示文本可查，不是科学验收或运行验证。

## 1. 系统边界与接口地图

| 参考路径/接口 | 静态作用与数据边界 | 对 FLASH 的可借鉴内容及限制 |
| --- | --- | --- |
| [`detector/ncclprobe.cpp`](https://github.com/wutianyuan1/Greyhound/blob/d641b3997c17de700e1ef7d37e353418df7e336d/detector/ncclprobe.cpp) | 包装 NCCL 初始化、collective/P2P 和 GroupStart/GroupEnd；记录 communicator 地址、调用类型、时间、rank 与 count；group 暂存后集中处理 | 分清 hook、记录及 group 边界；不能把其接口覆盖当作 FLASH 所需覆盖已完成 |
| [`global_status.cpp`](https://github.com/wutianyuan1/Greyhound/blob/d641b3997c17de700e1ef7d37e353418df7e336d/detector/global_status.cpp#L214-L249)、`global_status.hpp` | monitor 时跳过 CUDA event；profile 时记录起止 event、同步 stop 并将 ms 转为 μs | 揭示同步/分组会影响观测时序；真实 CUDA 行为与扰动 `NOT_RUN` |
| `shm_storage.hpp`、`shm_topo.hpp`、`comm.hpp`、[`communicator.py`](https://github.com/wutianyuan1/Greyhound/blob/d641b3997c17de700e1ef7d37e353418df7e336d/detector/control_plane/communicator.py) | 共享内存记录/拓扑与控制面反序列化；communicator 包含 id_hash、地址、global/local/group rank、ring/tree 描述 | 独立设计时必须区分组身份、进程局部地址及全局 rank；不可仅用地址建立跨进程唯一性假设 |
| [`local_analyzer.py`](https://github.com/wutianyuan1/Greyhound/blob/d641b3997c17de700e1ef7d37e353418df7e336d/detector/control_plane/local_analyzer.py#L151-L222)、[`slow_detection.py`](https://github.com/wutianyuan1/Greyhound/blob/d641b3997c17de700e1ef7d37e353418df7e336d/detector/control_plane/slow_detection.py) | 调用 ID 周期识别、由相隔一个周期的时间戳估计迭代时间、变点与过滤；profile 汇总 communicator 的 count/duration | ACF 属于 GREYHOUND 迭代估计路径；FLASH 正文采用框架直接上报，不应暗中沿用 |
| [`local_controller.py`](https://github.com/wutianyuan1/Greyhound/blob/d641b3997c17de700e1ef7d37e353418df7e336d/detector/control_plane/local_controller.py) | 本地分析、Redis 报告；profile 最终仅发送 min/max/avg/std；检测前后事件 ID 未变/消失 | 窗口与缺失事件不能直接证明物理 fail-stop；count 曾在局部存在也不等于全局定位使用 count |
| [`global_controller.py`](https://github.com/wutianyuan1/Greyhound/blob/d641b3997c17de700e1ef7d37e353418df7e336d/detector/control_plane/global_controller.py)、[`event_handler.cpp`](https://github.com/wutianyuan1/Greyhound/blob/d641b3997c17de700e1ef7d37e353418df7e336d/detector/event_handler.cpp) | monitor/profile/validate 控制；触发暂停、计算/通信微基准及后续 mitigation | GREYHOUND 的 validation 暂停和微基准不是 FLASH 的两阶段 clique→rank 延迟分析；P0 不运行任何该路径 |
| [`global_analyzer.py`](https://github.com/wutianyuan1/Greyhound/blob/d641b3997c17de700e1ef7d37e353418df7e336d/detector/control_plane/global_analyzer.py)、`global_topo.py` | 利用 id_hash 和 TP/DP/PP 元数据形成 clique；跨组筛疑；重建通信拓扑供基准验证 | 名称相同不代表算法相同；FLASH 的 rank 最短平均延迟与多标签交叉证据不能用 GREYHOUND 验证器替代 |
| [`megatron_logger.py`](https://github.com/wutianyuan1/Greyhound/blob/d641b3997c17de700e1ef7d37e353418df7e336d/detector/control_plane/megatron_logger.py) | 指示在 Megatron 并行状态初始化尾部调用上报函数，将 rank 的 TP/DP/PP 写入 Redis | 证明公开 artifact 需要框架元数据适配；不支持“参考实现绝无框架改动”的推断；未见该接口的 EP 参数 |

以上仅列接口名称和独立归纳，不提供参考代码片段或可运行移植。

## 2. 逐机制对照

FLASH 引用页为印刷页（括号内 PDF 页）；GREYHOUND 引用采用节号及印刷页（其 PDF 页偏移见来源索引）。

| 机制 | GREYHOUND 论文/固定源码 | FLASH 第三章 | 结论/待审边界 |
| --- | --- | --- | --- |
| 检测入口 | §4.2，736–737：拦截 NCCL，ACF 找重复周期，调用时间戳差估计迭代时间；源码 `detect_failslow`→`find_period`→`find_performance_drop` | §3.2.2，25–26（41–42）：框架每迭代向 Redis 上报，Rank 0 为检测基准；§3.3.3，35（51）：Rank 0后台进程定期推送时长、初始化时上报parallel states | `CONFIRMED_TEXT`：观测对象不同。ACF 不进入 Faithful FLASH 基线；框架 callback 与后台日志读取的准确边界仍待审 |
| 非侵入性 | §4.2 声称框架无关检测；公开 `megatron_logger.py` 要求框架上报 TP/DP/PP；§5 明确 mitigation 需框架支持 | §3.2.1、§3.3.3、§3.4.2 承认约10行框架修改/状态上报；摘要、部分评估却称无训练代码或专用适配 | `CONFLICT`：不能把“无侵入”定为零源码修改；也不能将参考检测/缓解框架适配混成单一结论 |
| BOCD/模型 | §4.2 定义运行长度后验，概率阈值0.9；源码 `slow_detection.py` 使用 `Rbeast.beast`、`trend.cp/cpPr`，默认概率0.8 | §3.2.2，26（42）：称 BOCD/Rbeast，窗口30、概率0.8、退化0.2 | `CONFLICT/UNKNOWN`：Rbeast 输出不能未经验证视作运行长度后验。需核对数学模型、概率意义、在线更新和端点行为，不按参考源码默认裁定 |
| 过滤 | 论文 §4.2 比较变点前后均值，变化不足10%忽略；源码增加 z-score>3 移除、默认长度10、绝对均值差/较大均值>0.1 | §§3.2.2/3.3.2：预热3、z-score>3、变点距2、恢复比率0.75；§3.4.3 又提持续20迭代 | `CONFLICT`：不能复制参考长度10/对称变化定义；过滤后索引映射、零分母、迟到/重复上报和持续性要独立明确 |
| 按需 profiling | §§4.1/4.3：tracking→profiling→validation，CUDA events 按需采集，profiling 不暂停，validation 暂停 | §§3.2.2–3.2.3：monitor→profile→monitor；profiling 不主动停训，分析数据后恢复监控 | `CONFIRMED_TEXT`：阶段边界不同。同步 event 会阻塞 host，不能仅凭“不暂停”宣称零扰动 |
| CUDA/group | §4.3 只给 event 概述；固定 `global_status.cpp:214–249` 首个组内调用开始、group end 后同步 stop；`ncclprobe.cpp:304–355` 对零 duration 记录分配组耗时 | §3.2.3，29（45）：调用前 event，调用后特别是 GroupEnd 后 stop+同步；§3.3.1，32–33（48–49）称 group 统一计时 | `UNKNOWN`：多 stream、嵌套 group、组内多 communicator 的区间归属和重复计量未决定；参考实现单个 curr_stream 不是正确性证明 |
| 可比组/clique | 论文 §4.3：同数据量组可比；超过中位数10%筛疑。源码 `global_analyzer.py:106–121` 按 id_hash 形成组，TP/DP/PP 标签；`:204–220` 组内取最大均值，跨组用中位数+20%，单组直接验证 | §3.2.3，30–31（46–47）及§3.3.2，34（50）：同标签组最大均值、CV；候选组选择后做 rank 分析。§3.5.2承认缺少count带来的偏差 | `CONFLICT`：参考论文10%、源码20%与 FLASH 20%/CV 的对象不同；不能按数值相同视作同一算法 |
| rank 定位 | §§4.3/6：暂停训练后 GEMM 和实际通信拓扑 P2P benchmark，定位慢 GPU 或拥塞链路 | §3.2.3：选候选 clique，再选平均通信耗时最短 rank，利用晚到/少等待现象；跨标签 TP/DP/PP/EP 证据提高置信度 | `CONFIRMED_TEXT`：根本不同。FLASH 的最短rank现象要在授权环境验证适用条件；不能用参考微基准当目标 goldens |
| Fail-Stop | 论文侧重 fail-slow。源码 `local_controller.py:43–56` 将事件不增/消失标记停止 | §3.2.4，31（47）：窗口例如2倍迭代时间，无新 NCCL 调用判定 fail-stop | `UNKNOWN`：无事件可由长计算、采样丢失、通信组模式变化或观测失效导致；需保留原文判定与可证实故障类别的区别，由审查裁定 |
| 混合并行/MoE | 论文重点 TP/DP/PP；公开 logger/analyzer 接口为 TP/DP/PP，未据此证明 EP/MoE 定位能力 | §§3.3.2/3.4.6：expert_dp/expert_tp 及多标签；§3.5.1 承认非 NCCL/DeepEP 覆盖限制 | `UNKNOWN`：EP标签、同成员多组、communicator生命周期与元数据映射须单独规格；不能继承参考标签硬编码或声称完整MoE覆盖 |
| 缓解/恢复 | GREYHOUND §5 的负载分配、拓扑调整及checkpoint策略是额外子系统 | FLASH 第三章本轮只定位；SHIFT 第四章不在范围 | `CONFIRMED_TEXT`：不实现 GREYHOUND mitigation、不引入 SHIFT、不启动相关实验 |

## 3. 固定 artifact 自身的偏差与验证限制

以下是参考论文与参考代码的静态差异，均未运行复现，不能据此宣布参考系统失败：

1. ACF：论文阈值0.95；`find_period` 默认0.7，但检测实际调用显式0.95，profiling调用0.8。不能仅看默认值报告“检测使用0.7”。算法源码还用局部峰及相邻模式精确匹配，论文为首个超过阈值的lag。见 [`local_analyzer.py:166,195`](https://github.com/wutianyuan1/Greyhound/blob/d641b3997c17de700e1ef7d37e353418df7e336d/detector/control_plane/local_analyzer.py#L161-L199) 和 [`slow_detection.py:142–163`](https://github.com/wutianyuan1/Greyhound/blob/d641b3997c17de700e1ef7d37e353418df7e336d/detector/control_plane/slow_detection.py#L142-L163)。
2. 变点：论文0.9，源码默认0.8；源码实际调用为 `rb.beast`，在线 run-length 语义的等同性未验证。见 [`slow_detection.py:89–127`](https://github.com/wutianyuan1/Greyhound/blob/d641b3997c17de700e1ef7d37e353418df7e336d/detector/control_plane/slow_detection.py#L89-L127)。
3. 跨组阈值：论文超过median10%，源码>=median20%。见 [`global_analyzer.py:211–224`](https://github.com/wutianyuan1/Greyhound/blob/d641b3997c17de700e1ef7d37e353418df7e336d/detector/control_plane/global_analyzer.py#L211-L224)。
4. ring/tree：论文说两者均需验证；控制器实际只调 `topo.rings[0]`，tree调用被注释，不能称已覆盖所有channel/topology。见 [`global_controller.py:199–215`](https://github.com/wutianyuan1/Greyhound/blob/d641b3997c17de700e1ef7d37e353418df7e336d/detector/control_plane/global_controller.py#L199-L215)。
5. 身份与统计：全局 `Perf_*` 键按 communicator 地址建立，静态阅读尚未证明跨进程地址唯一；源数据含count但上报只有duration统计。见 [`local_controller.py:33–41`](https://github.com/wutianyuan1/Greyhound/blob/d641b3997c17de700e1ef7d37e353418df7e336d/detector/control_plane/local_controller.py#L33-L41)。FLASH 的安全身份与同量可比假设需要独立规格，不能直接把参考布局当已验证契约。

## 4. 后续独立验证建议（待授权，当前 NOT_RUN）

- 在确定模型语义后，以独立合成序列测试窗口边界、恢复/变慢方向、尖峰、持续阶跃、缺失上报、过滤索引映射；不得以未经确认许可的参考实现作为可执行测试依赖。
- 对 CUDA/group 先提出单stream/多stream、group嵌套、通信计算重叠和时钟域的观测矩阵，再经 ChatGPT 与 Owner 审查。只有获后续明确授权后才执行GPU验证。
- 定位样例分开覆盖同标签单组/多组、CV边界、并列最小值、多故障、不同count、多个标签交叉/冲突；重要预期应由独立推导确定。
- 复用问题单独升级；无许可澄清仍可依据目标论文独立实现，但不可移植 detector 代码、测试、配置或依赖安装逻辑。以上建议不构成进入 P1/P2 的授权。
