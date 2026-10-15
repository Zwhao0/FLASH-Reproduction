# GitHub 安全门禁方案（P0 草案）

日期：2026-10-15。适用仓库：`Zwhao0/FLASH-Reproduction`。依据：[Issue #1](https://github.com/Zwhao0/FLASH-Reproduction/issues/1)、[AGENTS.md](../AGENTS.md)。本文件及本次 CODEOWNERS/CI 草案属于 **H** 变更，等待 ChatGPT 独立审核与 Owner 批准；不会配置权限、开启自动合并或合并本 PR。

## 1. 已观测事实与未知

核对对象：启动 main/本地 HEAD `272a544095bad9dedc3a61a23e5f18a18a799233`。主智能体与权限研究子智能体在当日使用无认证的 GitHub 官方 REST GET 独立核对；不读取令牌或认证文件。

| 对象 | 实际结果 | 可得结论与限制 |
| --- | --- | --- |
| `GET /repos/Zwhao0/FLASH-Reproduction` | HTTP 200；`private=false`、`visibility=public`、`default_branch=main` | Public，默认分支 main；匿名响应的 `permissions`、`allow_auto_merge` 未提供，不能视为 false |
| `GET /repos/Zwhao0/FLASH-Reproduction/branches/main` | HTTP 200；`protected=false`、`protection.enabled=false`、`required_status_checks.enforcement_level=off`、`contexts=[]`、`checks=[]` | 当时 main 没有该接口报告的有效保护/必需检查；不得宣称“禁直推已生效” |
| `GET /repos/Zwhao0/FLASH-Reproduction/rulesets` | HTTP 200；`[]` | 当时未列出仓库 ruleset |
| `GET /repos/Zwhao0/FLASH-Reproduction/branches/main/protection` | HTTP 401；`Requires authentication` | 匿名读取管理配置受限；不是“已验证执行账号权限不足”，也不是“有保护”的证据 |
| 主智能体 GitHub connector `get_user_login` | `Zwhao0`，与仓库 Owner 相同 | 连接器身份并非独立受限执行身份；没有据此测试写入或绕过权限 |
| Git 传输身份 | **NOT_VERIFIED** | 连接器身份不能证明本地 Git push 使用谁的身份；不探查凭据以求确认 |
| 初始 main 的 CODEOWNERS / workflow | Git tree 中没有 `.github`、根 CODEOWNERS 或 `docs/CODEOWNERS` | 本 PR 的新增文件仅为待审草案；不是初始 main 的门禁 |
| 账户计划、Actions 仓库默认权限、Owner bypass、安装 App 权限、自动合并仓库开关 | **NOT_VERIFIED** | 需要 Owner 提供设置的脱敏导出/截图或允许有权限的只读核对 |
| 权限负面验证 | **NOT_RUN** | 本轮未尝试 main push/force push/delete、合并或修改规则 |

上述成功 HTTP 响应来自公开 API；子智能体的 GitHub connector 调用曾直接返回 `MCP tool ... is not available to the model`，浏览工具对 API URL 也不可读。随后改用 Python 标准库无认证 GET 成功；前两者是工具通道失败，不能冒充 GitHub HTTP 权限结果。公开证据只保存本表字段，不公开完整响应、账户环境或任何凭据。主智能体另保存整体检查命令、退出码与提交对象。

可重现的只读请求（不得加 Authorization 或打印环境）：`curl --fail-with-body -H 'Accept: application/vnd.github+json' https://api.github.com/repos/Zwhao0/FLASH-Reproduction/branches/main`；其他端点见表。若缺少 curl 可用 Python `urllib.request.urlopen`；HTTP 401 应单独记录而非当作检查 PASS。设置可能随后变化，进入下一阶段前重新核验。

## 2. Owner 待配置的 main 基线

选择一个清楚、可审计的规则集，明确作用于 `refs/heads/main` 并处于实际启用状态。若采用传统分支保护，则启用“Do not allow bypassing the above settings”，不能依赖管理员默认豁免。GitHub 的保护功能可阻止强推/删除，要求 PR、审核及检查，但这些设置必须由 Owner 实际配置。[官方说明](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-protected-branches/about-protected-branches)

| 目标 | 待落实设置 | 验收证据 |
| --- | --- | --- |
| 禁直接更新 main | Require a pull request before merging；执行身份无 bypass | 规则导出；独立受限身份直接 push 被拒绝 |
| 禁强推/删除 main | 禁止 force pushes、禁止删除 | 规则导出；后续隔离验收，不能在未批准的生产 main 做破坏性探测 |
| 必需审核 | 至少 1 位非实现者审核；要求 Code Owner；更新提交使旧审核失效；最新可审核 push 由另一人批准 | 当前 head 审核记录；旧审核失效案例 |
| 必需 CI | 唯一 job/check 名称；尽可能绑定预期 GitHub App 来源；要求基于当前 base/head 成功 | 故意失败/缺失/伪造来源检查无法合并；禁止把 skip/neutral 当成内容校验成功 |
| 讨论处理 | Require conversation resolution | 未解决 review thread 的拒绝结果 |
| 治理及核心机制保护 | CODEOWNERS 覆盖自身、AGENTS、CI、权限策略、论文规格、实现、测试基准 | 基础分支生效文件与 GitHub CODEOWNERS 错误检查；对应 PR 审核请求 |
| 禁自动合并 | 当前各级别一律人工审查；执行流程中无 enable-auto-merge 调用 | PR 保持 Draft/Unmerged，Owner 后续核对仓库与执行器设置 |

CODEOWNERS 草案将所有文件指定给实际仓库 Owner `@Zwhao0`，不虚构第二审核者。它只有进入 PR 的基础分支且 Owner 启用必需 Code Owner 审核后才形成相应合并约束；Draft PR 不会自动请求 Code Owner。多个 Owner 同行并不表示必须全部批准，因此不能把“Owner + 科学审核人”写在一行就宣称双重审核已实现。当前 ChatGPT 科学审查通过 Issue/PR 的审查记录供 Owner 决策，不假装成具有 write 权限的 GitHub 审核账号。[CODEOWNERS 规则](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/about-code-owners)

GitHub 禁止 PR 作者批准自己的 PR。若此次 PR 由 Owner 的连接器身份创建，不能随后以 Owner 自审满足必需批准；这也是将后续执行账号与 Owner 分离的实际必要条件。启用规则前须确定真实独立且具备相应权限的审核者/实现者身份，不能用临时关闭规则或 Admin bypass 充当验收。[官方审核限制](https://docs.github.com/en/pull-requests/how-tos/review-pull-requests/approving-a-pull-request-with-required-reviews)

## 3. 独立执行身份与 CI 最小权限

建议 Owner 单独创建/安装仅此仓库可用的 GitHub App，或单独受限的开发账号。优先按仓库选择与细粒度授权设计；执行器仅需读取代码、写任务分支、创建/更新 Draft PR，按需要增授 Issues 权限。不给 administration、规则编辑、bypass、成员管理、secrets、部署或仓库删除权限。权限细项须按选定实现与官方 API 要求再核实；这里不是实际已授予的权限清单。GitHub App 支持按仓库安装及独立于用户运行，适合与 Owner 管理身份分离。[官方 App 权限说明](https://docs.github.com/en/apps/creating-github-apps/about-creating-github-apps/deciding-when-to-build-a-github-app)

Owner 管理连接只用于明确批准的配置动作；日常开发不能以 Owner/Admin 成功操作来证明独立性。仓库级 contents 写权限通常不等于按分支隔离，任务分支写入与 main 禁直推仍依赖实际启用的分支规则。凭据由 Owner 在安全设置中配置，绝不提交到仓库或输出到日志。P0 不创建身份、邀请账号、请求 token 或变更现有权限。

基础 CI 只检查文档与本仓库结构：使用 GitHub 托管 runner；触发 `pull_request`，不使用 `pull_request_target`、特权 `workflow_run`、SSH 或自托管 GPU runner；顶层 `permissions: contents: read`，其余权限不显式授予；checkout 不持久化凭据。不注入 secrets，不批准 PR，不推送，不合并，不执行 FLASH/CUDA/NCCL 或外来参考源码，不根据 PR 标题/正文拼接 shell。GitHub 在显式指定权限时将其余未指定项设为 none；job 级覆写仍需检查。[工作流权限语法](https://docs.github.com/en/actions/reference/workflows-and-actions/workflow-syntax#permissions)

基础工作流的 action 固定完整 commit SHA，并核对其官方来源；不自动安装或升级本机依赖。PR 对检查脚本/工作流的修改属于 H，不能由该 PR 自己“测试通过”取代人工审核。未来负责合并决策的执行器必须从受保护的可信 base 获取策略，并以当前 head/base 和完整文件列表计算风险；不能执行 PR 提供的合并策略或接受 PR 自报标签为授权。[Actions 安全说明](https://docs.github.com/en/actions/reference/security/secure-use)

## 4. 风险分类及未来严格 L 白名单

这是未来设计，**当前白名单为空，自动合并不启用**。扩充白名单自身属于 H，须先独立审核、Owner 批准与负面验证。不能使用 `docs/**`、`*.md` 或“只有文档”作为 L 判据。

| 级别 | 范围 | 合并条件 |
| --- | --- | --- |
| L 候选 | 未来明确列出的完整文件路径内，只有非执行性的排版/错字/导航说明；不改变科研、接口、授权、验证定义或运行命令 | 未来才可能自动合并；先通过身份/保护/负面验证，并另获 Owner 开启授权 |
| M | 普通实现、一般测试与工具；不触及核心机制/重要预期 | 人工审核；本轮 P0 不编码实际系统 |
| H | 核心算法/阈值/时序/接口、论文规格、来源许可、实验与基准、CI、权限、AGENTS、CODEOWNERS、此策略、STATE 的授权结论 | ChatGPT 独立审核和 Owner 批准 |
| 未知/混合 | 路径未列入、内容无法分类、读取不全、策略异常；或 L/M/H 混合 | 最高级别；不确定按 H 升级，默认拒绝自动合并 |

未来白名单必须是 Owner 审核过的有限完整路径清单，且只允许普通 UTF-8 非执行 Markdown 的原地修改；新增、删除、改名、符号链接、可执行位改变、二进制、子模块和隐藏文件均默认拒绝。路径只是必要条件，还须确认内容没有嵌入可执行脚本、权限指令、科学定义、测试 golden 或影响发布的配置。采用完整 diff/完整分页文件列表；异常、截断、过期结果或 head/base 变化均拒绝自动合并。新提交撤销此前风险结论，重新检查。标签只能帮助分类，不能赋权。

## 5. 权限与绕过负面案例（全部 NOT_RUN）

后续须 Owner 批准验证范围；危险操作先在独立隔离的规则验证分支/环境实施，不能通过成功破坏 main 来“验证”。隔离结果不直接等同 main 实测，仍需规则匹配与真实执行身份核对。每个案例保留时间、规则版本、身份、base/head、请求摘要、实际拒绝/允许及脱敏证据；不得保存 token。当前仅列验收要求，不声称已经 PASS。

| ID | 用例 | 预期结果 |
| --- | --- | --- |
| GH-N01 | 白名单内单一非执行说明错字，满足所有检查和审核 | 未来开放 L 后允许；当前仍禁止自动合并 |
| GH-N02 | 核心 BOCD/CUDA/定位逻辑改动，伪装 `risk:L` | 自动合并拒绝；H 审核 |
| GH-N03 | 白名单说明与任一代码/测试/配置混合 PR | 自动合并拒绝；取最高风险 |
| GH-N04 | 修改 AGENTS、CODEOWNERS、workflow、此策略或分类器 | 自动合并拒绝；H 审核 |
| GH-N05 | 审核后追加提交/改变科学预期或 base | 旧审核/旧检查不满足新 head；重新审核检查 |
| GH-N06 | 独立开发身份直接 push/强推/删除受保护测试分支 | 均拒绝；另核对 main 匹配同等有效规则 |
| GH-N07 | 无审核、必需 CI 失败/缺失或来源不符时请求合并 | 拒绝；不能用任意同名 check 冒充 |
| GH-N08 | 将 H 文件改名到白名单，或通过 symlink/可执行位/二进制承载内容 | 拒绝自动合并 |
| GH-N09 | 实现者自审、最后推送者独自批准、旧审核或非 Owner 审核替代必需 Owner | 拒绝；保留最新 head 的有效独立审核 |
| GH-N10 | 执行身份尝试改规则/权限/绕过 main 保护 | 拒绝；Owner/Admin 测试不计为受限身份验收 |
| GH-N11 | 文件分页读取不全、API 出错、检查后 head 改变 | 默认拒绝；不得用缓存分类结果合并 |
| GH-N12 | fork PR 修改 CI 试图写仓库、读取 secret 或使用自托管 runner | 不获得这些能力；策略变更需 H 审查 |

## 6. 功能与启用前置条件

GitHub 官方目前列明：Public 仓库在 GitHub Free 可用 protected branches、CODEOWNERS 与 rulesets；组织专用的 push 限制、push rulesets、跨仓库治理及其他功能不能据此假设本个人仓库可用。具体计划和账户设置尚未核实；按个人 Public 仓库可用的 PR 审核/必需检查基线设计，不把迁移组织或升级计划当作本轮既定动作。[rulesets 适用范围](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-rulesets/about-rulesets)

未来启用 B 风险分级合并须同时满足：Owner 明确批准有限 L 白名单与自动合并；受限身份独立且无管理/bypass 能力；main 规则已启用且可审计；必需 CI/可信策略已生效；以上负面案例与一个正向 L 案例实际通过；Owner/ChatGPT 审核验收证据。任一项未知或失败则继续人工审核、禁止自动合并。P0 交付只是可审核方案与草案，不代表门禁安全性验收。
