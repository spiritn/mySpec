# 方向审查者

一套跨项目使用的 Codex 角色和技能，从原始目标审查方案是否值得继续投入。它负责调查、拆解问题和提出建议；业务开发、实验和部署由执行任务完成。

## 两个角色，三个技能

| 组件 | 作用 |
| --- | --- |
| `project_director` | 项目负责人：把目标、方案和证据连起来，提出整体思路与下一步 |
| `independent_reviewer` | 独立评审人：从原始材料核对目标、推理、替代方案和投入条件 |
| `project-requirements` | 定义需求、拆解问题，组织独立双人审查并维护主文档 |
| `project-research` | 按项目开展竞品、市场或方案调研，把做法与关键证据讲清楚 |
| `project-adr` | 在主文档的一张表中维护建议、人工决定、依据与时间 |

两位评审先各自判断，再交换意见。允许保留分歧和未知；两人一致也不代表用户已批准。

## 安装

需要 Python 3.11+，以及支持自定义 Agent 角色和技能的 Codex。安装器只使用 Python 标准库。

```bash
git clone https://github.com/spiritn/mySpec.git
cd mySpec
python3 scripts/install-direction-review.py
```

安装器把三个技能目录链接到 `~/.agents/skills/`，把两个角色文件链接到 `~/.codex/agents/`；设置了 `CODEX_HOME` 时使用其 `agents/` 子目录。用户目录与仓库指向同一份文件，修改任一入口都会改变仓库内容。角色按技能列表中的实际路径读取技能，不再生成路径替换副本。

首次迁移已有配置时，先预览，再执行：

```bash
python3 scripts/install-direction-review.py --dry-run
python3 scripts/install-direction-review.py --overwrite
```

已有文件、目录和其他软链会先整体移动到角色目录上一级的 `direction-review-backups/`，保留原内容及恢复路径清单；默认不覆盖。已指向本仓库的软链会跳过，重复执行不会重复备份。自定义目标可用 `--skills-dir` 和 `--agents-dir`，Codex 仍须能够发现相应目录。

`python3 scripts/link-skills.py --user` 可链接仓库内全部技能和编码规范，与本脚本可以共同使用；先运行专用安装器可迁移旧的三个 `project-*` 技能。两个脚本都保留其他已安装技能。

保持仓库在固定位置。现有文件修改和 `git pull --ff-only` 更新会通过软链直接可见，Codex 请新开聊天加载；新增加技能时重跑链接脚本。编辑本地仓库不会自动提交或上传到 GitHub，仍需正常 `git add`、`git commit`、`git push`。

搜索、网页读取等工具由当前 Codex 环境提供。本仓库不创建账号、API 密钥或额外权限，也不单独启用定时任务。

## 怎么用

在项目聊天中说明项目根目录和本轮要判断的问题，例如：

```text
使用 $project-requirements。请调用 project_director 和 independent_reviewer，
从原始目标审查当前方向及下一步。两人先独立判断，再交叉复核。
统一更新本项目 docs/方向审查者/整体思路.md，保留待定项，
不执行开发或实验，不把建议记成人工决定。
```

如果当前接口不能按角色名调用，技能会要求如实说明，并可显式读取角色指令作为兼容方式；不会把同名子任务冒充成原生角色加载。

## 每个项目只维护这些资料

```text
docs/方向审查者/
├── 整体思路.md
├── 变更记录.md
└── 调研/          仅在需要专项材料时创建
```

主文档依次放：当前判断、目标背景、术语、竞品／市场／方案调研、整体方案与进度、待定与验证、决策记录。可复用模板在 [需求技能模板](../skills/project-requirements/references/templates.md)，竞品介绍格式在 [调研模板](../skills/project-research/references/templates.md)。

“当前判断”摘要最多 300 个可见字符，首段最多 100 个；聊天审阅和子 Agent 的简短判断同样遵守。整份主文档没有 300 字总上限，必要信息留在对应章节，不为控字拆出更多文件。复杂问题可附最多 7 节点的主流程图。

决策表固定五列：**决策点、描述、结论状态、论据、时间**。AI 可以给方案和建议，只有用户明确确认或已有可核验人工确认，才能写“已决策”。决定、执行进度、验证结果分别记录。

## 修改与验证

编辑仓库里的 `agents/` 与三个 `project-*` 技能，或用户目录中的对应软链；修改后新开聊天读取。两个角色不覆盖主会话的模型、权限或沙箱设置；角色指令中的职责边界不等于技术权限隔离。

检查生成的项目主文档：

```bash
python3 skills/project-requirements/scripts/check_document.py "/项目路径/docs/方向审查者/整体思路.md" --overview
```

检查器验证摘要字数和约定的 Markdown／Mermaid 格式，不判断方案是否正确。方向审查部分只保存可复用角色、技能、模板和工具，项目原始需求、实际决策及调研数据由各项目保存。
