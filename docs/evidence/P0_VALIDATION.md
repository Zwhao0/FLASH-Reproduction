# P0 验证、失败与脱敏证据

日期：2026-10-15（Asia/Shanghai）。范围：[Issue #1](https://github.com/Zwhao0/FLASH-Reproduction/issues/1)。基线 `272a544095bad9dedc3a61a23e5f18a18a799233`；公共检查快照 `1e50e0871c4a0afb2aa416e3e1e5eeb1e55cc1e3`，Git tree `d3d1b5494a6a9454993b2fadbe71f88f862a936a`；分支 `codex/p0-evidence-contract`。这是研究及仓库自动化检查，**没有 FLASH 系统实现或科学通过声明**。

## 环境与对象

本地 macOS，系统 Python 3.9.6；PDF只读提取使用应用已提供的 Python/pypdf、Poppler，未安装或升级依赖。GitHub只读核验使用官方 REST GET，未读取凭据。CI草案使用 GitHub 托管 Ubuntu、runner内置python3和固定commit的checkout，不包含GPU、自托管runner或secret。

来源校验与版本详见 [SOURCES](../SOURCES.md)。FLASH哈希 `1221fe9eb75d19084b786265114b8a9a91dc1df5b96950ddd47bc827333470db`，105页；GREYHOUND哈希 `e9829d78bcdfb08029f4664f1e27e680f039a4e6c0fd858e2d0287dcfd8fcd88`，18页。FLASH文本提取约99,554字符，GREYHOUND约89,204字符（包含页标记，非字节同一性证明）。主智能体视觉核对FLASH PDF40/43/46/57/58：图3-1/图3-4/恢复比率/式3-1与3-2。截图、全文与原始元数据留在受控本地，不进入Public仓库。

## 已执行记录

| 对象 | 命令/操作（私有参数已用来源ID替代） | 实际结果/退出码 | 判定 |
| --- | --- | --- | --- |
| 仓库事实 | `git remote -v`、`git status --short --branch`、`git log -3 --format='%H %s'` | 0；唯一origin为授权仓库，启动main HEAD见基线；未纳入未经授权的本地材料 | PASS：入口核对 |
| main同步与分支 | `git fetch origin main`；`git switch -c codex/p0-evidence-contract origin/main` | 均0；origin/main为基线SHA；未更新main | PASS：隔离分支 |
| PDF完整性/可读性 | `shasum -a 256 <SRC-FLASH> <SRC-GH-PAPER>`；`PdfReader(...).pages`与逐页`extract_text()` | 0；哈希、页数如上；未加密阻塞 | PASS：文件证据，非论文正确性 |
| 页面核对 | `pdftoppm -f 40 -l 40 -scale-to 1800 -png <SRC-FLASH> <private-output>`；43、46、57–58同参数 | 0；渲染结果经图像查看；图3-4与正文数值差异已保留，未指定golden | PASS：图式可读；科学裁定OPEN |
| GREYHOUND固定来源 | `git ls-remote https://github.com/wutianyuan1/Greyhound.git HEAD`；官方API固定SHA递归tree与固定版文件GET | 0；HEAD为`d641b3997c17de700e1ef7d37e353418df7e336d`，tree完整；detector许可未确认 | PASS：静态来源；复用受阻 |
| GitHub配置快照 | `python3 scripts/inspect_github_public.py` | 0；repo/branch/rulesets HTTP200；main protected=false、checks off/[]、rulesets=[]；管理保护HTTP401 | PASS：只读事实收集；保护详情INCONCLUSIVE；权限负例NOT_RUN |
| 发布检查负例 | `python3 -m unittest discover -s scripts -p 'test_*.py' -v` | 0；4个测试方法、12个场景：缺链接、私有服务器文件、PDF、私有路径形状、尾空格、正常链接、符号链接，以及Paper ID合法/重复contract/重复trace/缺失/错配 | PASS：检查器的12个离线场景，不是GitHub权限测试 |
| 结构/链接/敏感形状 | `python3 scripts/check_p0.py` | 0；17个tracked文件、16项Paper ID对齐、规定文件/inline本地链接/UTF-8/空白/有限敏感形状通过 | PASS：仅文档与发布检查 |
| staged格式 | `git diff --cached --check` | 0；候选文件已显式暂存后核对，无PDF/截图/服务器说明/原始日志/第三方实质代码 | PASS：仅格式 |
| 独立智能体复核 | 另设只读复核者核对契约、来源、歧义与CI | 已完成并修订发现，见下文；不替代ChatGPT科学审查 | PASS：P0静态复核，不是科学验收 |
| 远端CI | PR/分支的`P0 documentation / p0-docs` | 公共快照的[push run](https://github.com/Zwhao0/FLASH-Reproduction/actions/runs/38742551982)及[PR run](https://github.com/Zwhao0/FLASH-Reproduction/actions/runs/38742615958)均completed/success；GitHub状态，不另伪造进程退出数值 | PASS：仅文档/发布检查 |

`inspect_github_public.py`对预期管理端点401仍返回进程0，只表示成功记录了可见性限制；输出逐端点HTTP，不能解释成所有权限设置已验证。文档检查只验证tracked文件、规定文档/16项Paper ID一致性、简单inline本地文件链接、UTF-8/空白和有限敏感形状。它不验证远端URL、锚点、全部Markdown语法、所有秘密或论文真实性，也不能防止拥有Owner权限的身份绕过规则。

## 提交完整性与交付状态

[Draft PR #2](https://github.com/Zwhao0/FLASH-Reproduction/pull/2)关联Issue #1，保持Open/Draft/Unmerged。首个公共提交以上述main为唯一父提交；通过连接器生成的Git tree与本地已检查快照一致（SHA见本页开头），17个tracked文件，其中16个相对main有变更。公共提交使用noreply身份元信息，本机默认身份提交只保存在本地恢复分支。

本记录写入时HEAD是上述公共检查快照。随后仅改三份文档：本记录、STATE与GREYHOUND对照中残留的“日志读取”措辞；不修改算法、测试预期或CI代码。最终提交在本地/远端重跑同一检查，最终HEAD及run链接写于PR描述，避免在其自身内容中循环包含自身commit hash。最终继续工作时必须从PR当前head重新取证，不把快照SHA当作永远最新的HEAD。

## 独立推导与未定义边界

恢复比率示例独立算得 `(26932-19323)/(26932-17345)=0.7936789402`，另一示例 `(26932-25000)/(26932-17345)=0.2015228956`。20%时延增长对应约16.67%吞吐下降，25%时延增长对应20%吞吐下降。共享内存写入范围与collective范围的占比为0.0005%–0.2%。这些用Python标准算术核对，退出0，**只是手算复核，没有实现检测器**；未定义域与触发选择仍OPEN。更多独立反例见 [TRACEABILITY](../TRACEABILITY.md)。

## 失败、限制及恢复

| 症状/尝试 | 结果 | 恢复与保留限制 |
| --- | --- | --- |
| 本机`gh issue view ...` / `gh auth status` | shell exit127，command not found | 不安装gh、不读取认证文件；改用已有GitHub连接器读取Issue成功 |
| 连接器最初Issue/评论/get_repo及PR schema探测 | 参数校验/argument binding失败，未产生HTTP权限结论；无进程退出码（N/A） | 根据明确字段改正；Issue/评论和get_user_login成功；仓库设置用公开GET，get_repo未作为已取得证据 |
| 子智能体GitHub连接器/浏览API不可用 | 工具通道错误，非GitHub权限拒绝；N/A | 使用无认证标准库GET成功；保留HTTP401管理可见性限制 |
| 两次文档patch未通过工具校验 | 一次上下文不匹配、一次同目标delete/add不受支持；N/A；均未写入失败补丁 | 改为准确Update后成功；无科学测试失败或预期改写 |
| Git HTTPS任务分支推送缺少认证 | 两次失败；隔离重试捕获push exit128（早先多命令shell整体返回0不代表push成功） | 不读取凭据；改用现有GitHub连接器发布任务分支。默认本机提交身份元信息未上传；以相同审查文件树、main为父提交创建公共提交，保留本地历史，不强推或改写历史 |
| GREYHOUND缺少已确认适用的detector许可 | UNKNOWN / ANALYSIS_ONLY | 不复制/移植实质代码；逐文件权利来源待审，静态分析可继续 |
| 论文参数/时序/评估存在冲突 | CONFLICT / OPEN | [DECISIONS](../DECISIONS.md)并列候选，未默认采纳推荐；没有运行后选更有利口径 |

本轮未发生系统实现测试失败；没有因此删减失败样本、降低断言、改写golden或更换实验定义。

## 独立复核与修订

独立复核者与初始撰稿子任务分开。初轮执行文档检查返回exit1：整合尚未完成（新增文件未tracked、evidence/STATE尚待补），以及clique的设计/实现CV门槛差异、无记录与实际无调用的区别、严格阈值数学措辞。主智能体补齐STATE/evidence、显式暂存，并保留CONFLICT/修正过强表述及严格不等号，未改变论文或测试golden。最终复核确认论文哈希、GREYHOUND缓存文件Git blob与固定tree一致性、许可限制、科学歧义和CI只读边界；追加指出的无依据“监视框架日志”已删除，改按论文两条上报叙述保留UNKNOWN；删除公共状态中无关的本地偏好元信息。Paper ID规则补充独立缺失/重复/错配反例。复核者最终在公共快照上重跑检查均exit0，并指出对照文档句尾残留的“后台日志读取”，最后更正为“后台定时Redis上报”。该复核不是最终科学批准。

## 未运行与审批

FLASH构建、CPU算法单测、CUDA/NCCL运行、真实训练、服务器连接/环境探查/日志读取、故障注入、端到端复现均 **NOT_RUN**。没有更改GitHub权限、main保护或自动合并，没有推送main、合并或关闭Issue。权限负面测试 GH-N01–N12 全部 **NOT_RUN**。

下一阶段须ChatGPT独立科学审查和Owner明确批准，见 [STATE](../STATE.md)、[GITHUB_POLICY](../GITHUB_POLICY.md)及[ROADMAP](../ROADMAP.md)。
