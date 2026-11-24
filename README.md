# Shared AI Coding Skills

用 `$workflow` 编排设计、拆解、编码和评审，按需接上归档。各阶段也可独立调用，通过同一工作项目录和验收编号交接。

日常新需求只需输入：

```text
$workflow
[粘贴原始需求]
```

默认先澄清需求、调查代码并设计方案，停在方案审阅处。回复“按这个方案做”后，继续拆任务、编码、验证和代码评审，不逐阶段重复确认。需要时可直接指定“只拆任务”“按已有方案实现”或“本次直接做到编码评审”；提交、推送、创建或合并 PR、部署仍按明确授权处理。

| Skill | 负责什么 | 默认产出 |
| --- | --- | --- |
| `$init` | 读取项目文档，创建或刷新文档地图 | 项目根目录的 `AGENTS.md` |
| `$workflow` | 默认先澄清与设计，确认后实施；支持指定阶段和续跑 | 默认交付需求与方案，确认后补充任务、代码、验证和评审结果 |
| `$design` | 澄清业务需求，核对现有代码并形成技术方案 | `requirements.md`、`design.md` |
| `$task` | 按依赖拆分方案，为各任务定义完成条件 | `tasks.md` |
| `$code` | 按任务实施和验证，回填进度及结果 | 代码变更与任务执行记录 |
| `$review` | 结合需求、实际 diff、工程规则和上下游做独立评审 | 带证据的风险分流、变更摘要和验证范围，按需写入 `review.md` |
| `$complete` | 核对完成证据，判断主规格是否需要更新并归档工作项 | 归档目录及 `completion.md`，按范围同步主规格 |

## 通用协作规则

[AGENTS.md](AGENTS.md) 保存中文沟通、授权范围、改动完整性、实际验证和防止同类问题复发的通用要求。阶段方法仍放在 Skill，角色只补自身职责，不把整份规则复制九遍。方案默认先确认再编码，技术评审不替用户批准，评审者保持只读。

这份规则可用于配置 Codex 的用户级 `AGENTS.md`，不依赖指定电脑或 Claude、Gemini、专用脚本。现有安装器只链接 Skill、Agent 和编码规范，不会自动替换 `~/.codex/AGENTS.md`；接入用户级规则时应保留已有内容并明确处理差异。项目级规则继续使用 [AGENTS.example.md](AGENTS.example.md) 中的模块、验证与文档入口。

## 方向审查：两个 Agent 与三个 Skill

在立项、路线选择或项目中途重新检查：原始目标是什么，当前方案能否达到目标，下一步值得验证什么。`project_director` 负责提出整体思路，`independent_reviewer` 独立核对目标、证据与替代方案。两人先各自判断，再交叉复核。

配套技能是 `$project-requirements`（需求与问题拆解）、`$project-research`（竞品与路线调研）、`$project-adr`（简短决策表）。它们与上面的开发流程分工衔接；人工确认的方向可交给 `$design` 和 `$workflow` 继续实施。

```sh
# 安装方向审查的两个角色和三个技能，需要 Python 3.11+
python3 scripts/install-direction-review.py
```

默认安装到 `~/.codex/agents/` 和 `~/.agents/skills/`，采用软链引用本地仓库；迁移已有配置需加 `--overwrite`，迁移前会整体备份。以后修改用户目录中的对应文件，就会修改仓库源文件。安装或更新后新开聊天。主文档的“当前判断”摘要最多 300 字，正文按目标、术语、调研、方案进度、待定与验证、决策表组织；决定由人工确认。

详见 [方向审查安装与使用](docs/direction-review.md)，含调用示例、文档模板和更新方法。

## 需求澄清与方案设计

`$design` 由主会话负责需求澄清，用一句话讲清目标、可观察验收和影响下一步的未知。复杂方案可交给 `solution_designer` 深入调查，再由 `solution_reviewer` 独立核对需求完整性、依据与复杂度；简单需求不强制启动两个角色。

两个角色使用同一份 [design Skill](skills/design/SKILL.md)，只返回建议，正式需求与方案仍由主会话统一维护。方案检查记在 `design.md` 内，不为每轮新增文档；允许部分继续、部分待定。方案检查不代替方向审查或后续代码评审。

```sh
# 链接 design/workflow 与关联阶段技能，并链接仓库内全部 Agent；需要 Python 3.11+
python3 scripts/link-skills.py --user --agents design workflow
```

例如：“使用 `$design`，先帮我澄清这个需求，暂不写方案”；或“使用 `$workflow`，为这项跨模块需求设计方案并独立检查，先做到方案”。共享规则包含角色不可用时的完整指令兼容加载和未完成说明。

## 任务拆解与编码执行

`$task` 按实际成果、依赖和验收拆工作，复杂时可由 `task_planner` 只读提出建议；主会话统一维护任务清单。`$code` 可委派 `code_implementer` 在明确范围内实现与验证，小改动仍可由主会话直接完成。

任务交接包含原始目的、验收、代码基线、可写范围、前置产出及完成证据。只有依赖具备且范围和共享契约不会冲突时才并行；执行者保留他人改动，不同时回填 tasks.md。主会话验证集成后的完整需求，再按范围组织已有独立代码评审。

```sh
# 链接任务、编码、workflow 与关联 Skill，以及仓库内全部 Agent
python3 scripts/link-skills.py --user --agents task code workflow
```

方法和[任务模板](skills/task/assets/tasks.md)分别见 [task](skills/task/SKILL.md)、[code](skills/code/SKILL.md)。状态区分未开始、进行中、已实现待验证、已完成和阻塞，只有满足本项完成条件才勾选。只请求拆解时不编码；任务清单不额外授予提交、部署或数据操作权限。

## 三个独立代码评审 Agent

代码评审默认从三个独立上下文展开，优先确认需求是否完整、正确实现；由主会话核查证据、按根因去重，并按高／中／低等级汇报。

| Agent | 负责什么 |
| --- | --- |
| `code_review_functional` | 需求与逻辑正确性、真实边界、历史数据和上下游影响 |
| `code_review_architecture` | 项目规范、模块边界、类与方法职责，以及有具体后果的设计问题 |
| `code_review_performance` | 结合真实规模检查查询、重复工作、批量处理和资源成本 |

```sh
# 链接 review Skill、编码规范和仓库内全部 Agent；需要 Python 3.11+
python3 scripts/link-skills.py --user --agents review
```

以后说“使用 `$review` 评审这次变更”即可，需提供或能定位需求与代码范围。规则见 [review Skill](skills/review/SKILL.md) 和[专项举证细则](skills/review/references/angles.md)。角色类型入口不可用时显式传入完整角色指令，并如实说明兼容调用。缺少独立上下文或专项未完成时，不能声称三专项评审完成。

## 在本机接入

初始化脚本需要 Python 3.8 或更新版本，以及本机创建软链的权限。在共享仓库根目录执行以下任一组命令。

```sh
# 在指定项目启用全部 Skill
python3 scripts/link-skills.py --project /path/to/project

# 在指定项目启用文档初始化
python3 scripts/link-skills.py --project /path/to/project init

# 在指定项目启用总入口和阶段 Skill
python3 scripts/link-skills.py --project /path/to/project workflow

# 在指定项目只启用设计和任务拆解
python3 scripts/link-skills.py --project /path/to/project design task

# 在当前用户范围启用全部 Skill
python3 scripts/link-skills.py --user
```

项目级适合先在一个仓库试用。方向审查的两个角色需额外运行上方专用安装器；已有三个 `project-*` 普通目录时先用专用安装器迁移。全局和项目级同时链接同名 Skill 时，Codex 可能显示两个同名入口。给任一命令加 `--dry-run` 可预览目标路径和冲突。选择 `workflow` 会同时链接 `design`、`task`、`code`、`review` 和 `complete`。脚本会链接通用编码规范，重复执行会复用指向同一来源的链接。已有文件或其他来源的链接需要手动处理。

把 [AGENTS.example.md](AGENTS.example.md) 中适用的段落合并进目标项目的 `AGENTS.md`，填写真实的模块边界、验证命令和项目约束。模板会指示 Codex 在读取通用规范前检查路径。项目的 `AGENTS.md`、团队规范与项目内代码约定保留优先级。

在目标项目的 Codex 会话里运行 `$init`，读取 `docs/` 或 `doc/` 的实际内容，创建或更新根目录 `AGENTS.md` 的文档地图。地图会标注各类文档的阅读时机和可用入口。已有项目指令继续由团队维护。

每个工作项有独立目录。未特别约定时，进行中的工单放在 `docs/changes/<work-item>/`，完成后归档到 `docs/changes/archive/YYYY-MM-DD-<work-item>/`。已有 `increment/` 的项目沿用实际目录和归档约定。小改动可以缩短文档，已明确获准的就地修复可直接进入实现。下面是常用入口。

- `$init` 读取当前项目文档，建立或刷新 `AGENTS.md` 文档地图。
- `$workflow` 导出失败可重试。默认先澄清、设计，等用户确认再实施。
- `$workflow` 导出失败可重试，本次直接做到编码、验证和评审。明确授权后一次推进。
- `$workflow` 继续工单 ABC-123，从已有任务开始，做到实现和验证。
- `$design` 帮我澄清「导出失败可重试」，并核对现有代码，写出技术方案。也可以指定只做需求澄清。
- `$task` 基于这个需求目录生成任务清单，标明依赖、验收条件和验证方式。
- `$code` 实现这个需求目录里的 T-01，验证后更新任务状态。
- `$review` 在独立会话中评审这个 PR。对照需求和项目规则，给出文件行号、触发条件、影响和验证证据。
- `$complete` 归档 ABC-123，并判断主规格是否要回填。需要一并同步时可说「同步已确认的主规格并归档」。

`$code` 交付或创建 PR 前先做本地自查。PR 阶段在独立会话中运行 `$review`，维护者据证据决定如何修复与是否合并。项目的评审规则和关联契约可在 `AGENTS.md` 中指明来源。专项评审、规则沉淀以及精确率和召回率的评估见 [进阶评审](skills/review/references/advanced.md)。

## 在两台电脑同步

1. 将这个目录作为独立仓库放到你选定的私有 Git 远端，两台电脑各克隆一份，再各自执行初始化。
2. 一台电脑改动后提交并推送，另一台执行 `git pull --ff-only`。软链目标路径相同的内容更新会随拉取生效。新增 Skill 时重跑初始化。若从使用旧名称的版本升级，移除原来创建的旧名称软链并重跑初始化。移动克隆目录时同样需要重建软链。
3. 在新的 Codex 会话中使用更新后的项目配置。公司环境和云端环境需要各自可读取软链目标。

脚本生成的链接使用本机绝对路径。若团队约定仅本地使用，可通过目标仓库的 `.git/info/exclude` 排除相应路径，例如 `/.agents/skills/design` 和 `/.agents/standards/coding.md`。共享仓库存放通用材料。公司代码、业务知识、需求文档与凭据按公司规则保存在指定位置。

目录和软链行为见 [Codex Skill 文档](https://learn.chatgpt.com/docs/build-skills)，项目指令加载见 [AGENTS.md 文档](https://learn.chatgpt.com/docs/agent-configuration/agents-md)。
