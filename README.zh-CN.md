# oh-my-skills

个人 Agent skills 收藏仓库。

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

