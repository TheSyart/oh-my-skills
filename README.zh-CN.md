# oh-my-skills

`oh-my-skills` 是一个个人 Agent skills 收藏仓库，用来把松散的 AI 协作方式沉淀成可复用、可检查、可演进的工作流。

当前收录的第一个 skill 是 `engineered-vibe-coding`：一个 Agent-Team-first 的工程化编码 workflow skill。它面向复杂开发任务，要求 Agent 先澄清需求、规划架构、拆分模块、细分 atomic tasks，再通过 checkpoint、验证、角色审核证据和反屎山闸门后交付。

这个仓库的目标不是收集普通 prompt，而是收集一组“小型 Agent 工作系统”：有明确触发条件、硬规则、references、examples、验证方式和给人看的说明文档。

## 当前重点

- 工程化 Agent Coding。
- 需求、架构、模块、任务规划。
- Agent Team / subagent / self-review 降级规则。
- 基于证据的审核和反屎山闸门。
- 可移植的 skill 草稿，后续可安装到 Codex 或适配其他 Agent 环境。

## Skills

| Skill | 说明 |
| --- | --- |
| [`engineered-vibe-coding`](skills/engineered-vibe-coding) | Agent-Team-first 工程化编码 workflow skill，用于需求规划、架构规划、模块拆分、checkpoint、验证、角色审核证据和反屎山闸门。 |

## 目录结构

```text
oh-my-skills/
├── skills/
│   └── engineered-vibe-coding/
└── skills.json
```

每个 skill 保留自己的 `SKILL.md`、references、examples 和 README。

## 验证

验证 Codex skill：

```bash
uv run --with pyyaml python /Users/anhuike/.codex/skills/.system/skill-creator/scripts/quick_validate.py skills/engineered-vibe-coding
```

## 本地安装

之后如果要安装到 Codex：

```bash
cp -R skills/engineered-vibe-coding /Users/anhuike/.codex/skills/
```
