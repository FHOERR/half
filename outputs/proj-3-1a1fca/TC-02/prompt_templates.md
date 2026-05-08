# TC-02: Task Card 到 Agent Prompt 生成器 - 候选方案 A

## 概述

本文档描述候选方案 A：从 HALF Task Card v0.3 结构化字段映射为稳定的 Agent Prompt。

**核心目标**：
1. 保证 Prompt 生成稳定性（多次生成同一 Task Card 得到完全相同的 Prompt）
2. 清晰表达约束与上下文策略
3. 支持多种输出格式（文本、结构化 JSON）
4. 为 workflow、handoff 实验提供统一的 Prompt 输入

---

## 1. 生成策略

### 1.1 字段映射顺序（稳定性基础）

Prompt 生成按以下 **固定顺序** 进行，确保多次生成完全一致：

```
1. Head (基础信息)
   ├── task_code (from metadata)
   ├── task_type
   └── background

2. Spec (任务规范)
   ├── initial_state
   ├── goal
   ├── expected_behavior
   └── acceptance_criteria[]

3. Environment (执行环境)
   ├── relevant_files[]
   ├── constraints[]
   └── context_policy
       ├── allow_assumptions
       ├── must_confirm[]
       └── forbidden_actions[]

4. Execution (验证测试)
   ├── test_method
   │   ├── strategy
   │   ├── commands_or_steps[]
   │   └── pass_signal
   └── difficulty
       ├── level
       └── reason

5. Tail (元数据与实验)
   ├── suitable_experiments[]
   └── metadata
```

### 1.2 字段映射细节

#### Head 部分

| Task Card 字段 | Prompt 中的表达 | 示例 |
|---|---|---|
| `metadata.task_code` | **任务码**：{value} | **任务码**：TC-01 |
| `task_type` | **任务类型**：{枚举名} | **任务类型**：功能 |
| `background` | **背景**：{value} | **背景**：当前任务描述... |

#### Spec 部分

| Task Card 字段 | Prompt 中的表达 | 说明 |
|---|---|---|
| `initial_state` | **当前状态**：{value} | 描述系统现状与边界 |
| `goal` | **目标**：{value} | 描述完成后达到的状态 |
| `expected_behavior` | **预期行为**：{value} | 描述目标行为 |
| `acceptance_criteria[]` | **验收标准**：<br>- {criteria[0]}<br>- {criteria[1]}<br>... | 以项目列表呈现 |

#### Environment 部分

| Task Card 字段 | Prompt 中的表达 | 缺省处理 |
|---|---|---|
| `relevant_files[]` | **相关文件**：<br>- {file[0]}<br>- {file[1]}<br>... | 如果为空：提示"无特定限制，需自行判断相关文件" |
| `constraints[]` | **约束条件**：<br>- {constraint[0]}<br>... | 必填，至少 1 条 |
| `context_policy.allow_assumptions` | **上下文策略**：<br>- True: 允许在未确认项基础上进行合理假设<br>- False: 必须确认所有不明确项，不允许任意假设 | 必填，默认 False |
| `context_policy.must_confirm[]` | **必须确认项**：<br>- {item[0]}<br>... | 如果为空：省略该小节 |
| `context_policy.forbidden_actions[]` | **禁止操作**：<br>- {action[0]}<br>... | 如果为空：省略该小节 |

#### Execution 部分

| Task Card 字段 | Prompt 中的表达 | 缺省处理 |
|---|---|---|
| `test_method.strategy` | **测试策略**：{枚举名} | 自动化/手动/混合 |
| `test_method.commands_or_steps[]` | **测试步骤**：<br>- {step[0]}<br>... | 必填，至少 1 条 |
| `test_method.pass_signal` | **通过信号**：{value} | 如果为空：生成默认值"所有验收标准均已满足，所有测试通过" |
| `difficulty.level` | **难度评级**：{level} | S/M/L/XL |
| `difficulty.reason` | （同上）（{reason}） | 说明难度原因 |

#### Tail 部分

| Task Card 字段 | Prompt 中的表达 | 说明 |
|---|---|---|
| `suitable_experiments[]` | **适配实验**：<br>- {exp[0]}<br>... | 列出适配的实验类型 |
| `metadata` | **元数据**：<br>- 作者：{author}<br>- 创建时间：{created_at}<br>... | 展示关键元数据 |

---

## 2. 缺省字段处理

### 2.1 Optional vs Required

| 字段 | Required | 缺省处理 |
|---|---|---|
| `relevant_files[]` | Required (可为空数组) | 空数组 → "无特定限制，需自行判断相关文件" |
| `context_policy.must_confirm[]` | Required (可为空数组) | 空数组 → 省略"必须确认项"小节 |
| `context_policy.forbidden_actions[]` | Required (可为空数组) | 空数组 → 省略"禁止操作"小节 |
| `test_method.pass_signal` | Optional | 缺失 → "所有验收标准均已满足，所有测试通过" |
| `metadata` | Optional | 缺失 → 省略"元数据"小节 |

### 2.2 Type Mapping（枚举类型转换）

#### task_type 映射

```python
{
    "feature": "功能",
    "bugfix": "缺陷修复",
    "refactor": "重构",
    "infra": "基础设施",
    "test": "测试",
    "docs": "文档",
    "research": "研究"
}
```

#### test_method.strategy 映射

```python
{
    "automated": "自动化",
    "manual": "手动",
    "mixed": "混合"
}
```

#### suitable_experiments 映射

```python
{
    "workflow_comparison": "Workflow 对比",
    "handoff_comparison": "Handoff 对比",
    "prompt_stability": "提示稳定性",
    "execution_replay": "执行回放",
    "quality_review": "质量评审"
}
```

---

## 3. 提示措辞规范

### 3.1 约束表达（Constraints）

**原则**：使用强制性措辞

```markdown
**约束条件**：
- 必须使用 PostgreSQL 作为持久化存储（不能使用 SQLite）
- 必须支持 TLS 1.3 及以上版本
- 必须在 2 秒内完成响应，延迟不能超过 100ms
```

### 3.2 建议表达（Allow Assumptions）

**原则**：使用可选性措辞

```markdown
**上下文策略**：允许在未确认项基础上进行合理假设

可以假设：
- API 接口默认返回成功响应
- 用户输入有效且格式正确
```

### 3.3 禁止操作（Forbidden Actions）

**原则**：使用明确的禁止措辞

```markdown
**禁止操作**：
- 禁止修改既有的 result.json 完成判定机制
- 禁止直接写入数据库 migration 记录
- 不允许删除任何已发布的 API 端点
```

### 3.4 必须确认项（Must Confirm）

**原则**：使用疑问表达，明确标记需要确认的内容

```markdown
**必须确认项**：
- 涉及行为变更的默认值策略是什么？
- 字段缺省时的降级规则由谁定义？
```

---

## 4. 输出格式

### 4.1 文本格式（Plain Text）

用于直接 Agent 输入，包含完整的 Markdown 格式化：

```
================================================================================
## 1. 任务基础信息
================================================================================

**任务码**：TC-01
**任务类型**：功能
**背景**：当前任务描述依赖自然语言，难以进行 workflow 对比与 handoff 复盘。


================================================================================
## 2. 任务规范
================================================================================

**当前状态**：系统现有 Task 以 task_name/description 表达，不具备结构化字段约束。
...
```

### 4.2 结构化 JSON 格式

用于程序化处理，每个部分作为独立对象：

```json
{
  "task_code": "TC-01",
  "version": "0.3",
  "style": "detailed",
  "sections": [
    {
      "title": "任务基础信息",
      "content": "**任务码**：TC-01\n**任务类型**：功能\n**背景**：..."
    },
    {
      "title": "任务规范",
      "content": "..."
    }
  ]
}
```

### 4.3 Markdown 格式（导出用）

可直接作为 handoff 文档使用，包含完整的 Markdown 标记。

---

## 5. 稳定性保证

### 5.1 不变量

生成器实现以下不变量，确保 Prompt 稳定性：

1. **字段顺序不变**：同一 Task Card 输入，生成的 Prompt 字段顺序始终相同
2. **缺省行为一致**：对缺失字段的处理始终遵循相同规则
3. **文本格式一致**：同一输入产生的文本格式、缩进、空行完全一致
4. **类型映射确定**：枚举值映射总是确定的

### 5.2 测试方法

```bash
# 稳定性测试：多次生成同一 Task Card，确保输出完全一致
python -c "
  import prompt_generator as pg
  with open('task.json') as f:
    tc = json.load(f)
  
  outputs = [pg.TaskCardPromptGenerator(tc).generate_prompt() for _ in range(10)]
  assert all(o == outputs[0] for o in outputs), 'Instability detected!'
  print('✓ All 10 outputs identical - Stability guaranteed')
"
```

---

## 6. 集成建议

### 6.1 与现有系统集成

在 `prompt_service.py` 中引入：

```python
from prompt_generator import TaskCardPromptGenerator

def generate_agent_prompt(task_card_dict: dict, style: str = "detailed") -> str:
    """Generate Agent Prompt from Task Card v0.3"""
    generator = TaskCardPromptGenerator(task_card_dict, style=style)
    return generator.generate_prompt()
```

### 6.2 与 Workflow 集成

```python
# In workflow handoff
task_card = load_task_card(task_code)
agent_prompt = TaskCardPromptGenerator(task_card).generate_prompt()
result = workflow.execute_with_prompt(agent_prompt)
```

### 6.3 与实验框架集成

```python
# Prompt stability experiment
task_card = load_task_card("TC-02")
prompts = [
    TaskCardPromptGenerator(task_card, style="detailed").generate_prompt()
    for _ in range(100)
]
stability_score = len(set(prompts)) == 1  # All identical -> 100% stable
```

---

## 7. 限制与未来扩展

### 7.1 当前限制

1. 不支持条件性字段：所有字段处理都是固定的逻辑
2. 不支持自定义 Prompt 模板：生成逻辑写死在代码中
3. 不支持多语言导出：仅支持中文

### 7.2 未来扩展方向（不在 v0.3 范围内）

1. **模板引擎**：支持自定义 Prompt 模板，允许不同团队定制措辞
2. **条件字段**：支持根据 task_type 动态调整 Prompt 内容
3. **多语言**：支持英文、日文等多语言 Prompt 生成
4. **AI 优化**：使用 LLM 优化 Prompt 措辞以提高响应质量

---

## 8. 示例

### 8.1 简单任务卡 → Agent Prompt

**输入**（简化的 Task Card）：

```json
{
  "version": "0.3",
  "task_type": "bugfix",
  "background": "用户反馈 API 在高并发下返回 500 错误",
  "goal": "修复并发竞态条件，保证 API 稳定性",
  "initial_state": "GET /users/:id 在 100+ 并发请求时出现 500 错误",
  "expected_behavior": "GET /users/:id 即使在 1000+ 并发请求下也能快速返回正确结果",
  "acceptance_criteria": [
    "压力测试通过：1000 并发请求，99.9% 成功率",
    "响应时间 < 100ms (p99)",
    "无内存泄漏"
  ],
  "relevant_files": ["src/api/users.py", "src/db/connection.py"],
  "constraints": ["不能修改数据库 schema", "向后兼容"],
  "test_method": {
    "strategy": "automated",
    "commands_or_steps": ["pytest src/tests/test_concurrent.py -n 1000"],
    "pass_signal": "所有并发测试通过，响应时间满足要求"
  },
  "difficulty": {
    "level": "L",
    "reason": "需要理解并发模式与竞态条件排查"
  },
  "context_policy": {
    "allow_assumptions": false,
    "must_confirm": ["并发级别上限是否有新要求？"],
    "forbidden_actions": ["修改现有 API 签名"]
  },
  "suitable_experiments": ["execution_replay", "quality_review"]
}
```

**输出** Prompt（部分）：

```
================================================================================
## 1. 任务基础信息
================================================================================

**任务码**：unknown
**任务类型**：缺陷修复
**背景**：用户反馈 API 在高并发下返回 500 错误

================================================================================
## 2. 任务规范
================================================================================

**当前状态**：GET /users/:id 在 100+ 并发请求时出现 500 错误
**目标**：修复并发竞态条件，保证 API 稳定性
**预期行为**：GET /users/:id 即使在 1000+ 并发请求下也能快速返回正确结果

**验收标准**：
- 压力测试通过：1000 并发请求，99.9% 成功率
- 响应时间 < 100ms (p99)
- 无内存泄漏

...
```

---

## 9. 参考

- Task Card v0.3 Schema: `task-card-v0.3.schema.json`
- Task Card v0.3 Spec: `task-card-v0.3-spec.md`
- Example Task Card: `task-card-v0.3.example.json`
- Generator Implementation: `prompt_generator.py`
- Example Outputs: `examples/`
