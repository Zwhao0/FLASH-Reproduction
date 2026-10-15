# FLASH 第三章论文机制规格（P0 审查稿）

本文件只把论文证据转为待审查规格，不表示算法、接口或科学预期已经获准实现。P0 不实现 FLASH 算法，不访问训练服务器。核心语义由 ChatGPT 独立科学审查、Owner 最终批准后，才能形成实现基线。本文所有功能与科学验证均为 **NOT_RUN**。

## 证据与标记

主证据 F：2026-04-07 版本《面向大模型分布式训练稳定性的故障定位与弹性恢复研究》，105 页，第三章 PDF 页 35–64，对应印刷页 19–48。SHA-256：`1221fe9eb75d19084b786265114b8a9a91dc1df5b96950ddd47bc827333470db`。PDF 页码从封面起按 1 计数。原件、抽取全文和私人文件位置不进入公共仓库；这里只公开必要的机制摘要。来源版本不因后续工程实现而改变。

- `EXPLICIT`：论文明确描述；这是文本证据，仍不是环境验证。
- `UNKNOWN`：论文没有给出足以唯一实现的语义。
- `ASSUMPTION`：待审查备选解释，不能当作已批准需求。
- `CONFLICT`：不同段落或计量口径存在张力，保留双方证据。
- 来源可信度 `F-direct` 表示论文直接证据；`F-limited` 表示论文明示但缺关键条件；`proposal` 表示本项目建议。参考源码不能静默覆盖主证据。

下列路径全为 **planned**：目录与代码尚未创建，不声称来自论文原始实现。完整需求到来源、测试与状态的映射见 [TRACEABILITY.md](TRACEABILITY.md)。

## 数据流与生命周期

### F-ARCH-01：三层架构与状态机

证据：§3.2.1，图 3-1，印刷 pp.23–24 / PDF pp.39–40；§3.3.1–3.3.2，印刷 pp.32–34 / PDF pp.48–50。可信度：`F-direct`。

`EXPLICIT`：训练进程中的 C++ NCCL Probe 通过 `LD_PRELOAD` 拦截 NCCL；节点内以共享内存传递事件和控制状态；每节点一个 Python 本地控制器；主节点全局控制器经 Redis 汇总与控制。状态 `0` 为监控，只记录时间戳等元数据；状态 `1` 为剖析，启用 CUDA Event。全局控制器触发剖析并在分析后返回监控。本地控制器周期为 100–500 ms；Probe 在 Group 结束处感知状态。状态字段单写多读、原子维护。

输入：NCCL 调用、Rank 0 迭代时间、parallel states、控制状态。输出：事件、communicator 信息、剖析统计、可疑 rank 与证据、fail-stop 告警。资源在首次 NCCL 调用惰性初始化。`UNKNOWN`：状态传播确认、不同节点采样窗口对齐、重复请求/过期响应、异常退出后的恢复以及 Pre-check 内容。不能补成已获准的分布式协议。

### F-PROBE-01：透明劫持与调用语义

证据：§3.2.1、§3.3.1，印刷 pp.23–24、32 / PDF pp.39–40、48。可信度：`F-limited`。

`EXPLICIT`：包装与 NCCL 同名的函数，解析原始符号，记录事件并调用原函数，返回原函数结果。通信元数据包含 communicator 地址、调用序号、时间戳等；剖析时增加 GPU 时延。`UNKNOWN`：完整 API 覆盖清单、符号解析方式、重入与线程模型、嵌套 Group、异步错误、非阻塞 communicator、CUDA Graph 等条件下语义。`ASSUMPTION`：任何“所有 NCCL 版本/调用均透明”说法均超出当前证据。

### F-SHM-01：共享内存事件通道

证据：§3.3.1，印刷 pp.32–33 / PDF pp.48–49。可信度：`F-limited`。

`EXPLICIT`：环形缓冲区包括配置/头尾指针/计数/初始化魔数/事件计数器/控制状态和记录区。事件含 communicator、序号、数据量、duration、group 标识。C++ 写入加锁；Python 读取无锁，读后清空并重置相关计数；论文承认少量记录可能丢失。组计数器在 Group 开始时递增。

`UNKNOWN`：二进制 ABI、字段宽度/单位、内存序、跨进程锁、溢出策略、多生产者安全、读清空与写入竞态、丢失统计以及资源命名/销毁。不能把“允许丢失”解释为允许丢失 fail-stop 活性证据，亦不能静默替换为新的并发算法。论文的状态字段无锁与写记录加锁是不同对象，并非必然矛盾。

### F-COMM-01：communicator 与标签构建

证据：§3.2.3、§3.3.1–3.3.3，印刷 pp.30、32、34–35 / PDF pp.46、48、50–51。可信度：`F-limited`。

`EXPLICIT`：以 `id_hash` 聚合不同 rank 的 communicator；简化信息为 communicator 地址、id 哈希和 global rank。优先读取包含 ring/tree 信息的完整对象，失败时降级。parallel states 提供 TP/DP/PP/EP 成员关系，形成“标签 → clique → communicator”映射；未知归属标为特殊组。

`UNKNOWN`：哈希算法/原始标识获取/碰撞处理、进程局部地址与全局身份的关联、communicator 销毁重建、同成员不同 communicator、标签优先级、特殊组可否诊断。完整模式依赖 NCCL 内部结构；简化模式是论文允许的模式，但不等于其跨版本行为已证实。

## 常态监控

### F-ITER-01：迭代时间输入

证据：§3.2.2、§3.3.2–3.3.3，印刷 pp.25–26、33–35 / PDF pp.41–42、49–51。可信度：`F-direct`。

`EXPLICIT`：框架回调上报完整迭代时间，涵盖前向、反向、同步和优化器更新；全局分析使用 Rank 0 序列。Redis 列表键为 `iter_time_{rank}`，值为 `iteration:time_ms`，默认最多留 500 条；BOCD 滑窗为 30 迭代。训练初始化上报 parallel states。

`UNKNOWN`：迭代边界实际计时 API、异步 GPU 工作是否同步、流水线/梯度累积定义、恢复后的编号、缺样本/重复/乱序、Redis 截断是否原子。论文“每迭代回调”与“后台进程定期上报”的顺序和投递语义不完整。

### F-BOCD-01：候选变点

证据：§3.2.2，印刷 p.26 / PDF p.42；§3.3.2，印刷 p.33 / PDF p.49。可信度：`F-limited`。

`EXPLICIT`：论文以运行长度后验 `P(r_t = 0 | x_1:t)` 描述 BOCD，并声称使用 Rbeast；窗口 30、`thresh_prob=0.8`、`degradation_thresh=0.2`。先产生候选变点，再过滤。不能以通用 BOCD 实现或 Rbeast 默认参数代替未说明的原始配置。

`UNKNOWN`：Rbeast 版本、调用入口、模型/先验、采样参数、随机种子、结果字段到在线后验的对应、候选变点索引和概率比较的严格性、20% 的分母与方向。Rbeast 是否能与论文所述在线后验严格对应，需要独立文档/源码证据；本稿不裁定对应关系。

### F-FILTER-01：持久性、距离、预热与离群过滤

证据：§3.2.2，印刷 pp.26–27 / PDF pp.42–43。可信度：`F-limited`。

`EXPLICIT`：令左侧序列不含变点、右侧序列含变点，`baseline_mean = mean(left)`、`degraded_mean = mean(right)`、`recent_mean = mean(right excluding its first point)`：

```text
recovery_ratio = (degraded_mean - recent_mean)
                 / (degraded_mean - baseline_mean)
```

恢复比率 `>=0.75` 过滤，`<0.75` 视为持续退化；候选变点相距 `<2` 迭代时保留首个；跳过最初 3 个迭代；执行 BOCD 前移除 `z-score >3.0` 的点。论文给出的四重过滤顺序包含先于 BOCD 的预处理，不能机械按叙述编号排列代码。

`UNKNOWN`：z-score 是单侧值还是绝对值、标准差自由度、常量序列、移除后保留原始迭代索引的方式、空切片/单点右侧/分母为零、负恢复比率、多个候选的排序、跨窗口去重。`CONFLICT`：§3.4.3 另写持续超过 20 迭代；§3.4.5 写右侧保护 1–2 迭代。未经审核不得自行增加或删除任一触发条件。

### F-FAILSTOP-01：无新 NCCL 调用告警

证据：§3.2.2、§3.2.4、§3.3.2，印刷 pp.25、31、34 / PDF pp.41、47、50。可信度：`F-limited`。

`EXPLICIT`：本地控制器观察每 rank 的新 NCCL 调用；动态窗口内无新调用即报告，窗口示例为迭代时间 2 倍；结果写 Redis `failstop_ranks`，由全局控制器汇总告警。该路径与 Rank 0 BOCD 路径并行。

`UNKNOWN`：2 倍是示例还是固定默认、冷启动与尚无 iter_time、调用时间戳与记录序号使用方式、阻塞的幸存 rank 如何排除、正常长计算/PP 气泡/外部通信如何避免误报、进程死亡导致共享内存消失、全节点失联、报告去重与清除。

科学边界：本监测路径在窗口内未观察到新 NCCL 记录，尚不能据此证明实际没有 NCCL 调用、该 rank 是根因或真实停止；正常无通信区间和记录丢失也会产生该观测。后续应分别验证死亡 rank、等待的存活 rank、正常无调用区间；不能用“全部停滞 rank 都算命中”制造 fail-stop 定位通过。

## 按需剖析与两阶段定位

### F-PROFILE-01：窗口与统计上报

证据：§3.2.3、§3.3.2，印刷 pp.27–28、34 / PDF pp.43–44、50。可信度：`F-limited`。

`EXPLICIT`：有效退化触发状态 `1`；本地控制器采集并按 communicator 计算 duration 的 min/max/avg/std 后上报；全局分析后恢复 `0`。剖析周期为 `max(latest_iter_time * 2.2, 20.0)`，下限为 20 秒。迭代上报为毫秒，执行该式前需要明确单位转换；数值 20 不能直接同毫秒相比较。

`UNKNOWN`：采样从全局请求还是本地确认起算、延迟节点覆盖、窗口尾未完成事件、无统计/缺 rank/过期数据处理、std 自由度、多个 communicator 的均值是等权还是按样本数加权。`CONFLICT`：§3.4.5 把剖析采样延迟表述为约 1 个迭代，不能等同于 2.2 倍且至少 20 秒的实际周期。

### F-TIMING-01：CUDA Event 观测对象

证据：§3.2.3，印刷 pp.28–29 / PDF pp.44–45；§3.3.1，印刷 p.33 / PDF p.49。可信度：`F-limited`。

`EXPLICIT`：开始 Event 放在 stream 的通信前，结束 Event 放在通信后，尤其 `ncclGroupEnd()` 后；等待结束 Event，再计算 elapsed time。论文强调 GPU kernel 的 `waitPeer()` 等等待包含在区间内。§3.3.1 的实际优化为每 Group 一对事件：第一个 NCCL 调用处开始、Group 结束处结束，总 duration 赋给组内各记录，复用事件对象。

`CONFLICT/UNKNOWN`：逐调用表述与 Group 共享区间并不产生同样的 per-call 指标；多 stream Group、嵌套 Group、未分组调用、跨 communicator Group、事件复用生命周期、错误/尚未完成 Event、同步扰动均未规定。不能把 CUDA Event 普遍解释为端到端通信时延，也不能假设当前 NCCL 的所有算法均满足“慢 rank 时延最短”。这些是需要独立验证的论文假设，不能只引用正文宣称成立。图3-4中慢rank的纯通信示例为120ms，同页正文另举慢rank约3ms；图例与正文的上下文未足以证明是同一次观测，不能将任一值用作golden。主智能体已视觉核对图3-1、图3-4与恢复比率、式(3-1)/(3-2)；图3-4未额外给出CV或20%公式。

外部语义约束：[NCCL Group官方文档](https://docs.nvidia.com/deeplearning/nccl/user-guide/docs/usage/groups.html)允许Group多stream、多device和嵌套，且组内API返回不保证已经提交到stream；最外层GroupEnd的完成及非阻塞状态另有约束。这是主智能体核验的当前官方文档（2.32.3），用于反证无条件的计时推广，不能当作论文环境NCCL 2.26.5已经验证，也不替代后续版本固定与授权实验。

### F-CLIQUE-01：第一阶段组筛选

证据：§3.2.3、图 3-4、§3.3.2，印刷 pp.30、34 / PDF pp.46、50；式 (3-1)，印刷 p.41 / PDF p.57。可信度：`F-limited`。

`EXPLICIT`：每标签排除单 rank 组；对于多个 clique，组指标为其内部 communicator 的平均延迟最大值 `max_avg_latency`；组间 CV `<0.1` 时跳过，否则选择该指标最大的组。某标签仅一个组时直接进入 rank 分析。论文评估另给 `score_clique=(t_clique-mean_cliques)/mean_cliques`，其中 `t_clique` 描述为组平均时延。

`CONFLICT/UNKNOWN`：§3.2.3只写按max_avg选择候选，§3.3.2才增加组间CV门槛；设计与实现章节在过滤条件上不完整一致，不能视为已冻结的统一规则。max of means 与 mean of rank/communicator means 不同；评估式是否只用于画图、是否用于生产筛选、是否有 20% 阈值未明确。组间 CV 的标准差自由度、tie、缺失成员、消息大小和算子混合也未定义。组间 CV 不足时“跳过”是无候选还是进入下一阶段需确认。

### F-RANK-01：第二阶段 rank 筛选

证据：§3.2.3、§3.3.2，印刷 pp.30–31、34 / PDF pp.46–47、50；式 (3-2)，印刷 p.42 / PDF p.58。可信度：`F-limited`。

`EXPLICIT`：候选 clique 内按 rank 汇总其 communicator 的时延，得到 `avg_latency`。rank 间 CV `<0.1` 跳过；CV `>=0.1` 才筛选。最小时延 rank 为可疑慢 rank，依据是快 rank 的等待时间更长。§3.2.3 还给出默认 20% 百分比阈值；式 (3-2) 为 `score_rank=(mean_clique-t_rank)/mean_clique`，正值对应更短时延。

`CONFLICT/UNKNOWN`：§3.3.2 省略 20% 门槛；不能未经审查认定式 (3-2) 就是该门槛的分母。rank 均值是否按调用数加权、多个低时延候选/并列最小/多故障、CV 等于 0.1、阈值等于 20% 的比较方式待定。

### F-FUSION-01：跨标签证据

证据：§3.2.3、§3.4.6，印刷 pp.31、44–45 / PDF pp.47、60–61。可信度：`F-limited`。

`EXPLICIT`：汇集不同标签指向同一 rank 的证据，增加诊断可信度；输出 CRITICAL 日志，含 rank、标签、clique 与平均时延。混合并行评估使用该 rank 参与的并行组得分之和。

`UNKNOWN`：单标签是否足以输出最终定位、证据数门槛、冲突候选/多故障处理、得分和是否作为生产排序、标签重叠带来的相关性和权重、rank 到节点映射。不能把两个相关标签当作两次独立科学验证，也不能自行新增投票/加权算法。

### F-MOE-01：MoE 与非 NCCL 覆盖

证据：§3.1.3、§3.4.6、§3.5.1，印刷 pp.23、44–46 / PDF pp.39、60–62。可信度：`F-direct`。

`EXPLICIT`：利用 Attention 等部分稳定的 DP/TP/PP 通信及 expert_dp 等辅助证据定位；避免直接用动态 EP All-to-All 建立稳定基线。当前只覆盖 NCCL，不能直接监控 DeepEP、Gloo、MPI。混合并行实验列出 EP/TP/PP 分别为 `(8,1,1)`、`(4,2,1)`、`(4,1,2)`、`(4,2,2)`。

边界：支持 MoE 场景不等于直接检测全部 EP 通信故障；EP 活性/非 NCCL 覆盖缺口应出现在结果中。扩展 DeepEP 或新 All-to-All 定位算法属于独立研究变更，不进入 faithful 基线。PP 点对点的信号也不能直接假定同于 AllReduce。

### F-INTEGRATION-01：无侵入定义

证据：§3.2.1、§3.3.3、§3.4.2，印刷 pp.24、35、37–38 / PDF pp.40、51、53–54。可信度：`F-limited`。

`EXPLICIT`：Probe 对 NCCL 的动态劫持保持用户训练主体逻辑；框架提供迭代时间和 parallel states，论文称核心改动少于 10 行；部署包含 Python 包、`FAILSLOW_AWARE=TRUE` 与 `LD_PRELOAD`。

`CONFLICT`：论文另有“无需框架专用适配代码”等宽泛说法；§3.4.2 列出框架内 logger、training 及 parallel states 改动，约 5+3+2 行，与严格“小于 10”也存在边界张力。faithful 候选应统计用户脚本、框架核心、适配器和部署四层改动，而不能未经审查以“零源码修改”替代论文接口。任何实际训练框架修改仍需后续明确授权。

### F-LIMIT-01：duration-only 基线与评估边界

证据：§3.4、§3.5.2–3.5.3，印刷 pp.36–47 / PDF pp.52–63。可信度：`F-direct`。

`EXPLICIT`：当前上报只有 duration 统计，没有 count；不同数据量/阶段可能使低时延 rank 被误判。duration+count 并以吞吐量判断是论文提出的未来改进，不能静默纳入 faithful 基线。现方案主要定位慢 rank，尚不能区分故障类型。论文的硬件、基准和精确率/召回率/开销数字是论文报告，均不是本项目结果。

后续实验需分别报告监控触发、剖析定位、端到端诊断、fail-stop 活性与根因归属；不能用定位条件通过率替代端到端召回率。故障强度、分母、重复次数与正常场景样本须先审查；服务器与故障注入仍未授权。

## 需要审查的语义决策

具体对照方案、未决事项与批准门槛集中在 [DECISIONS.md](DECISIONS.md)，避免多个文件各自维护不同决策。关联如下：U01 BOCD/Rbeast；U02 20%退化口径；U03 变点保护时间；U04 离群预处理与索引；U05 recovery边界；U06 CUDA/Group计时与图文数值；U07 clique指标；U08 rank百分比门槛；U09 Group记录与统计权重；U10 fail-stop因果性；U11 时窗与状态传播；U12 无侵入范围；U13 communicator/共享内存ABI；U14 跨标签与MoE覆盖；U15 评估与扩展边界。上述事项均未批准，不可由实现默认值代替。

## 审查与实施门槛

本文件提供研究交付，不授予实现、服务器、训练或注入权限。先独立审查 U01–U15、接口与独立反例，再由 Owner 明确授权下一离线里程碑。论文未交代的关键语义应继续显示 `UNKNOWN`，不能因为时间安排而自动转成默认值。后续若得到作者信息、论文补充材料或批准源码，应追加证据、记录冲突解决依据和批准人，保留本轮来源哈希。
