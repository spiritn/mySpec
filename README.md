# Shared AI Coding Skills

四个 Codex Skill 可独立调用，也可以在同一个需求上依次使用。共同约定是通过需求编号和验收条件衔接设计、实现与评审。

| Skill | 负责什么 | 默认产出 |
| --- | --- | --- |
| `$design` | 澄清业务需求，核对现有代码并形成技术方案 | `requirements.md`、`design.md` |
| `$task` | 按依赖拆分方案，为各任务定义完成条件 | `tasks.md` |
| `$code` | 按任务实施和验证，回填进度及结果 | 代码变更与任务执行记录 |
| `$review` | 对照需求、任务和实际 diff 评审 | 按严重程度排序的发现，按需写入 `review.md` |

## 在本机接入

初始化脚本需要 Python 3.8 或更新版本，以及本机创建软链的权限。在共享仓库根目录执行以下任一组命令。

```sh
# 在指定项目启用全部 Skill
python3 scripts/link-skills.py --project /path/to/project

# 在指定项目只启用设计和任务拆解
python3 scripts/link-skills.py --project /path/to/project design task

# 在当前用户范围启用全部 Skill
python3 scripts/link-skills.py --user
```

项目级适合先在一个仓库试用。全局和项目级同时链接同名 Skill 时，Codex 可能显示两个同名入口。给任一命令加 `--dry-run` 可预览目标路径和冲突。脚本会同时链接通用编码规范，重复执行会复用指向同一来源的链接。已有文件或其他来源的链接需要手动处理。

把 [AGENTS.example.md](AGENTS.example.md) 中适用的段落合并进目标项目的 `AGENTS.md`，填写真实的模块边界、验证命令和项目约束。模板会指示 Codex 在读取通用规范前检查路径。项目的 `AGENTS.md`、团队规范与项目内代码约定保留优先级。

默认每个需求有独立目录 `docs/changes/<work-item>/`。已有团队目录或工单编号时沿用。小改动可以缩短文档，就地修复可直接进入实现。下面的调用方式可以逐步试用。

- `$design` 帮我澄清「导出失败可重试」，并核对现有代码，写出技术方案。也可以指定只做需求澄清。
- `$task` 基于这个需求目录生成任务清单，标明依赖、验收条件和验证方式。
- `$code` 实现这个需求目录里的 T-01，验证后更新任务状态。
- `$review` 对照这个需求目录评审当前 diff，给出文件行号、触发条件和影响。

## 在两台电脑同步

1. 将这个目录作为独立仓库放到你选定的私有 Git 远端，两台电脑各克隆一份，再各自执行初始化。
2. 一台电脑改动后提交并推送，另一台执行 `git pull --ff-only`。软链目标路径相同的内容更新会随拉取生效。新增 Skill 时重跑初始化。若从使用旧名称的版本升级，移除原来创建的旧名称软链并重跑初始化。移动克隆目录时同样需要重建软链。
3. 在新的 Codex 会话中使用更新后的项目配置。公司环境和云端环境需要各自可读取软链目标。

脚本生成的链接使用本机绝对路径。若团队约定仅本地使用，可通过目标仓库的 `.git/info/exclude` 排除相应路径，例如 `/.agents/skills/design` 和 `/.agents/standards/coding.md`。共享仓库存放通用材料。公司代码、业务知识、需求文档与凭据按公司规则保存在指定位置。

目录和软链行为见 [Codex Skill 文档](https://learn.chatgpt.com/docs/build-skills)，项目指令加载见 [AGENTS.md 文档](https://learn.chatgpt.com/docs/agent-configuration/agents-md)。
