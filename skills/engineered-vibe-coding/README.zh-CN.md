# Engineered Vibe Coding

`engineered-vibe-coding` 是一个 Codex skill 草稿，用来把 vibe coding 升级成工程化开发流程。

它的目标不是让 Codex 写得更快，而是防止 Codex 在复杂开发任务里乱写：需求不清、跨文件重构、架构调整、登录鉴权、支付、数据库、依赖升级、CI/build/deployment 改动，以及任何会影响代码库长期健康的任务。

## 它解决什么

这个 skill 会把复杂编码任务变成一套按风险分级的工程流程：

- 实现前先判断风险等级：Light / Standard / Strict。
- 先探查仓库，再询问用户；能从代码里找到的问题不问用户。
- Standard 和 Strict 流程必须创建或更新 `.agent/dev-plan.md`。
- 一次只实现一个原子任务。
- 从项目文件里发现验证命令，不凭空发明命令。
- 绝不绕过已配置的 hooks 或 validation commands。
- 验证失败、无关修改、临时代码、审核不通过都会阻断继续推进。
- 最终交付必须说明修改文件、验证结果、审核结果、剩余风险和未验证项。

## V2 新增内容

- `.agent/dev-plan.md` 成为 Standard 和 Strict 工作流的 single source of truth。
- 更清晰的规划链路：需求澄清、架构规划、模块拆分、模块再细分为 atomic tasks。
- 三个 checkpoint：Plan、First Slice、Release。
- First Slice 是最小可验证 vertical slice。
- 最终交付前执行 self-review protocol。
- 固定 final response templates。
- 新增 Light / Standard / Strict 三个短示例，用来校准行为。

## V3 新增内容

- Agent Team 优先的角色执行模式。
- Subagent review 作为第二优先级。
- Main agent 自审只作为兜底。
- 新增 `references/roles.md`，定义角色职责、降级规则和角色输出格式。
- `.agent/dev-plan.md` 记录每个角色的审核证据。
- 新增 Anti-Spaghetti Control Model，解释如何通过多层闸门限制屎山。

## 流程等级

### Light

用于单文件、低风险修改，例如文案、小 bug、局部调整。

Light 不能涉及核心业务逻辑、状态、公开接口、安全、数据、build、CI、deployment 或依赖。默认不需要 `.agent/dev-plan.md`，除非用户明确要求计划。

### Standard

用于多文件改动、新功能、用户可见行为变化、中等重构，或需要拆任务的工作。

Standard 必须维护 `.agent/dev-plan.md`，一次只推进一个 active atomic task，并执行验证和审核。

### Strict

用于需求模糊、架构变更、登录鉴权、权限、支付、数据库迁移、public API、大型重构、安全相关、生产关键路径、依赖升级、build/CI/deployment 改动。

不确定风险时，升级到 Strict。

## 文件结构

```text
engineered-vibe-coding/
├── SKILL.md
├── README.md
├── README.zh-CN.md
├── agents/
│   └── openai.yaml
└── references/
    ├── workflow.md
    ├── roles.md
    ├── dev-plan-template.md
    └── review-checklists.md
```

## 关键文件

- `SKILL.md`：短、硬、可执行的核心规则，skill 触发时由 Codex 加载。
- `references/workflow.md`：Light / Standard / Strict 详细流程、质量门禁和失败回路。
- `references/roles.md`：角色定义、执行优先级、降级规则和角色输出格式。
- `references/dev-plan-template.md`：`.agent/dev-plan.md` 模板。
- `references/review-checklists.md`：质量门禁、测试清单、Reviewer 清单和反屎山红线。
- `references/examples/`：短示例，用于校准 Light / Standard / Strict 行为。
- `agents/openai.yaml`：展示信息和默认提示，不承载核心行为。

## 验证方式

使用以下命令验证草稿 skill：

```bash
uv run --with pyyaml python /Users/anhuike/.codex/skills/.system/skill-creator/scripts/quick_validate.py /Users/anhuike/Desktop/engineered-vibe-coding
```

期望结果：

```text
Skill is valid!
```

## 后续安装

当前草稿先放在桌面：

```text
/Users/anhuike/Desktop/engineered-vibe-coding
```

打磨稳定后，如果要全局安装，再移动或复制到：

```text
/Users/anhuike/.codex/skills/engineered-vibe-coding
```

最终安装版可以考虑是否保留 README。Codex skill 应该尽量轻量，核心行为仍然应该放在 `SKILL.md` 和 `references/` 里。

## Version Direction

- V1：硬工程规则。
- V2：带 checkpoint 和 First Slice 的 workflow state model。
- V3：Agent-Team-first role execution with evidence。
- V4：可选自动化脚本。

V3 会刻意保持 workflow-only，不新增脚本。V4 可以考虑加入可选脚本：

- `init_dev_plan.py`
- `discover_quality_gates.py`
- `validate_dev_plan.py`
