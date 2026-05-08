# Task Card v0.3 使用指南

**Table of Contents** | [简体中文](#目录)

---

## 目录

1. [快速入门](#快速入门)
2. [核心概念](#核心概念)
3. [Task Card 结构](#task-card-结构)
4. [完整工作流](#完整工作流)
5. [代码示例](#代码示例)
6. [常见场景](#常见场景)
7. [验收标准](#验收标准)
8. [常见问题](#常见问题)

---

## 快速入门

### 1 分钟概览

Task Card v0.3 是一个**结构化任务描述标准**，将自由文本转换为 12 个关键字段，支持：

- ✓ 稳定的 Agent Prompt 生成（10 段固定骨架）
- ✓ JSON/Markdown 双格式导出
- ✓ Workflow/Handoff/Experiment 统一集成
- ✓ 完整的生命周期追踪

### 最小化示例

```json
{
  "task_code": "FEATURE-001",
  "task_card_version": "0.3",
  "task_type": "Feature Implementation",
  "background": ["System needs X", "Constraint is Y"],
  "goal": "Implement X with Y constraint",
  "initial_state": "Current state: Z",
  "expected_behavior": "After task: X should work as Y",
  "acceptance_criteria": ["Criterion 1", "Criterion 2"],
  "relevant_files": ["src/main.py", "tests/test_main.py"],
  "constraints": ["Must use Python 3.8+", "No breaking changes"],
  "test_method": "Unit tests + integration tests",
  "difficulty": "Medium",
  "context_policy": {"allow_assumptions": false},
  "suitable_experiments": ["workflow_comparison", "prompt_stability"]
}
```

---

## 核心概念

### 三大核心组件

#### 1. Task Card 结构化描述 (TC-01)

**12 个必需字段**，覆盖从背景到实验的完整任务定义。

| 字段 | 含义 | 示例 |
|------|------|------|
| `task_code` | 任务唯一标识 | FEATURE-001 |
| `task_card_version` | 版本号 | 0.3 |
| `task_type` | 任务类型 | Feature Implementation |
| `background` | 背景信息（数组） | ["需求 A", "约束 B"] |
| `goal` | 目标 | 实现 X 功能 |
| `initial_state` | 初始状态 | 当前状态为 Y |
| `expected_behavior` | 期望行为 | 任务完成后应为 Z |
| `acceptance_criteria` | 验收标准 | [标准 1, 标准 2] |
| `relevant_files` | 相关文件 | [src/main.py] |
| `constraints` | 约束条件 | [约束 1, 约束 2] |
| `test_method` | 测试方法 | 单元测试 + 集成测试 |
| `difficulty` | 难度 | Medium / Large |
| `context_policy` | 上下文策略 | {allow_assumptions: false} |
| `suitable_experiments` | 适用实验 | [workflow_comparison] |

#### 2. Prompt 生成 (TC-02/TC-03/TC-06)

**Final 规范：10 段固定骨架** + 分层约束

```
1. Role（角色）
2. Mission（任务）
3. Background（背景）
4. Initial State（初始状态）
5. Target Behavior（目标行为）
6. Hard Constraints（硬约束）
7. Acceptance Criteria（验收标准）
8. Execution Plan Guardrails（执行计划护栏）
9. Test Method（测试方法）
10. Deliverables（交付物）
```

**约束分层：**
- MUST（必须）：不可违反
- SHOULD（应该）：优先遵循
- MUST NOT（不能）：绝对禁止

**冲突决策序：**
```
安全与数据完整性 > 既有运行时契约 > 验收标准 > 实现便捷性
```

#### 3. 导出与集成 (TC-04/TC-05)

**导出格式：** JSON（结构化） + Markdown（人读）

**集成点：**
- **Workflow**：自动化执行记录
- **Handoff**：人工交接与审查
- **Experiment**：科学实验与对比

**最小记录字段集（所有类型统一）：**
```
- task_code           (关联 Task Card)
- task_card_version   (版本追踪)
- record_type         (记录类型)
- created_at          (时间戳)
- agent_or_person     (创建者)
- status              (生命周期状态)
- task_card_checksum  (变更检测)
- verification_checklist (12 字段验证)
```

---

## Task Card 结构

### 字段详细说明

#### task_code（必需）
- 类型：string
- 格式：`[PROJECT]-[NUMBER]` 或 `[CODE]`
- 示例：`FEATURE-001`, `BUG-FIX-123`
- 用途：唯一标识、关联记录、构建文件名

#### task_card_version（必需）
- 类型：string
- 固定值：`0.3`（当前版本）
- 说明：版本追踪，便于向后兼容

#### task_type（必需）
- 类型：string
- 示例：
  - Feature Implementation（特性实现）
  - Bug Fix（缺陷修复）
  - Refactoring（重构）
  - Documentation（文档）
  - Performance Optimization（性能优化）

#### background（必需）
- 类型：string[]（数组）
- 说明：关键背景信息，最多 5 条
- 示例：
  ```json
  [
    "系统当前缺少用户认证模块",
    "用户已有密码哈希实现",
    "需要支持 OAuth2 集成",
    "现有 API 设计基于 REST",
    "后续需要支持 GraphQL"
  ]
  ```

#### goal（必需）
- 类型：string
- 说明：任务目标，清晰简洁
- 示例：`实现用户登录功能，支持本地认证和 OAuth2`

#### initial_state（必需）
- 类型：object 或 string
- 说明：任务启动时的系统状态
- 示例：
  ```json
  {
    "database": "PostgreSQL 14, schema v2",
    "api_version": "v1.0",
    "current_users": "authentication_basic_only",
    "constraints": "No breaking changes to existing API"
  }
  ```

#### expected_behavior（必需）
- 类型：object（primary + secondary）
- 说明：任务完成后的期望状态
- 示例：
  ```json
  {
    "primary": "用户可以通过账号密码和 OAuth2 登录",
    "secondary": [
      "登录后返回 JWT token",
      "Token 自动刷新",
      "现有登录方式继续有效"
    ]
  }
  ```

#### acceptance_criteria（必需）
- 类型：string[]（数组）
- 说明：验收标准，编号清单
- 要求：至少 3 项，最多 10 项
- 示例：
  ```json
  [
    "用户可以使用账号密码登录",
    "用户可以使用 OAuth2 登录",
    "登录成功返回 JWT token",
    "Token 在 1 小时内自动刷新",
    "登录失败返回明确错误信息",
    "现有 API 完全兼容（无 breaking changes）",
    "单元测试覆盖率 >90%"
  ]
  ```

#### relevant_files（必需）
- 类型：string[]（数组）
- 说明：涉及的代码文件/资源
- 示例：
  ```json
  [
    "src/auth/login.py",
    "src/auth/oauth2.py",
    "src/models/user.py",
    "tests/test_login.py",
    "docs/auth_spec.md"
  ]
  ```

#### constraints（必需）
- 类型：string[]（数组）
- 说明：实现约束，分层表达
- 示例：
  ```json
  [
    "MUST: 不能修改现有数据库 schema",
    "MUST: 登录延迟 <200ms",
    "SHOULD: 使用业界标准加密算法",
    "SHOULD: 添加登录审计日志",
    "MUST NOT: 明文存储密码",
    "MUST NOT: 暴露用户隐私信息"
  ]
  ```

#### test_method（必需）
- 类型：object（strategy + steps + pass_signal）
- 说明：测试策略、步骤、通过信号
- 示例：
  ```json
  {
    "strategy": "单元测试 + 集成测试 + 端到端测试",
    "steps": [
      "运行 unittest discover tests/",
      "运行 pytest tests/ --cov",
      "运行 behave tests/bdd/",
      "手工测试登录流程"
    ],
    "pass_signal": "所有测试通过，覆盖率 >90%，无 critical bug"
  }
  ```

#### difficulty（必需）
- 类型：string
- 可选值：Small, Medium, Large, XLarge
- 说明：任务难度，影响执行计划
- Guardrails：
  - Large/XLarge：必须详细规划阶段、风险、资源

#### context_policy（必需）
- 类型：object（allow_assumptions, critical_unknowns）
- 说明：上下文完整性策略
- 示例：
  ```json
  {
    "allow_assumptions": false,
    "critical_unknowns": [
      "OAuth2 提供商选择（Google? GitHub?）",
      "Token 过期时间（1小时还是24小时？）"
    ],
    "handoff_readiness": "full_specification"
  }
  ```

#### suitable_experiments（必需）
- 类型：string[]（数组）
- 可选值：
  - workflow_comparison（工作流对比）
  - prompt_stability（Prompt 稳定性）
  - export_consistency（导出一致性）
  - integration_load_test（集成负载测试）
  - backward_compatibility（向后兼容性）

---

## 完整工作流

### 端到端流程

```
┌─────────────────────────────────────────────────────────────┐
│ 1. 创建 Task Card                                            │
│    ├─ 填充 12 个必需字段                                    │
│    ├─ 验证所有字段非空                                      │
│    └─ 生成 SHA256 checksum                                  │
└────────────────────┬────────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────────┐
│ 2. 生成 Agent Prompt（Final 规范）                          │
│    ├─ 应用 10 段固定骨架                                    │
│    ├─ 映射字段到各段                                        │
│    ├─ 应用约束分层（MUST/SHOULD/MUST NOT）                │
│    └─ 输出文本 + JSON 结构                                  │
└────────────────────┬────────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────────┐
│ 3. 导出（Markdown/JSON）                                    │
│    ├─ 6 类字段排序（metadata/spec/constraints 等）        │
│    ├─ 确定性排序，保证 diff 友好                           │
│    └─ 同时生成 JSON（交换）和 Markdown（评审）             │
└────────────────────┬────────────────────────────────────────┘
                     │
         ┌───────────┴───────────┬───────────┐
         │                       │           │
    ┌────▼─────┐          ┌─────▼────┐  ┌──▼───────┐
    │ Workflow │          │ Handoff  │  │Experiment│
    │Execution │          │  Review  │  │ (Optional)│
    └────┬─────┘          └─────┬────┘  └──┬───────┘
         │                       │           │
    ┌────▼─────────────────────┬─┴──────────┬┘
    │ 创建记录                  │
    │ - MinimalRecordFields    │
    │ - 验证 12 字段           │
    │ - 存储 checksum          │
    │ - 追踪生命周期           │
    └────┬────────────────────┘
         │
    ┌────▼─────────────────────────────────┐
    │ 4. 完成 & 归档                       │
    │    ├─ 记录输出/决策/指标             │
    │    ├─ 验证 checksum（无变更）        │
    │    └─ 所有三类记录统一储存            │
    └─────────────────────────────────────┘
```

### 记录类型与生命周期

#### Workflow Execution Record

```
状态流转：pending → in_progress → completed/failed

关键字段：
  - workflow_id, execution_id
  - prompt_strategy (final/candidate_a/candidate_b)
  - generated_prompt (实际 prompt)
  - agent_version
  - start_time, end_time, duration_seconds
  - output_path, result_summary
  - success (true/false), error_message
```

#### Handoff Record

```
状态流转：pending → in_progress → completed

关键字段：
  - from_entity (谁发起)
  - to_entity (谁接收)
  - handoff_reason (质量审查/需要专业知识/etc.)
  - exported_format (json/markdown/both)
  - exported_files
  - decision (approved/needs_revision/escalated/closed)
  - decision_reason, notes
```

#### Experiment Record

```
状态流转：pending → in_progress → completed

关键字段：
  - experiment_type (workflow_comparison/prompt_stability/etc.)
  - experiment_id
  - hypothesis
  - metrics (灵活 dict，记录实验指标)
  - findings, conclusion
  - next_steps
```

---

## 代码示例

### 示例 1：创建与验证 Task Card

```python
from task_card_integration import TaskCardRecordFactory, WorkflowIntegrationAPI

# 创建 Task Card
task_card = {
    "task_code": "FEATURE-001",
    "task_card_version": "0.3",
    "task_type": "Feature Implementation",
    "background": ["需求 A", "约束 B"],
    "goal": "实现登录功能",
    "initial_state": "当前状态 X",
    "expected_behavior": "用户可以登录",
    "acceptance_criteria": ["标准 1", "标准 2"],
    "relevant_files": ["src/auth.py"],
    "constraints": ["MUST: 安全", "SHOULD: 快速"],
    "test_method": {"strategy": "单元测试", "steps": [], "pass_signal": "通过"},
    "difficulty": "Medium",
    "context_policy": {"allow_assumptions": False},
    "suitable_experiments": ["workflow_comparison"]
}

# 验证
try:
    factory = TaskCardRecordFactory(task_card)
    print("Task Card 验证通过")
except ValueError as e:
    print(f"验证失败：{e}")
```

### 示例 2：Workflow Execution

```python
# 启动 Workflow
record = WorkflowIntegrationAPI.start_workflow_execution(
    task_card=task_card,
    workflow_id="WF-001",
    agent_name="GPT-4-Agent"
)

# ... Agent 执行任务 ...

# 完成 Workflow
completion = WorkflowIntegrationAPI.complete_workflow_execution(
    record=record,
    success=True,
    output_path="outputs/FEATURE-001/result.json",
    result_summary="登录功能成功实现",
    duration_seconds=120.5
)

print(f"Workflow 完成，状态：{completion['status']}")
```

### 示例 3：Handoff

```python
# 启动 Handoff
handoff_record = WorkflowIntegrationAPI.initiate_handoff(
    task_card=task_card,
    from_entity="Agent",
    to_entity="Senior Reviewer",
    reason="quality_review"
)

# 完成 Handoff
decision = WorkflowIntegrationAPI.complete_handoff(
    record=handoff_record,
    decision="approved",
    decision_reason="实现完整，测试覆盖充分",
    notes="建议添加审计日志"
)

print(f"Handoff 完成，决策：{decision['decision']}")
```

### 示例 4：Experiment

```python
# 启动 Experiment
exp_record = WorkflowIntegrationAPI.start_experiment(
    task_card=task_card,
    experiment_type="prompt_stability",
    hypothesis="Final prompt 生成稳定输出"
)

# ... 运行实验 ...

# 完成 Experiment
result = WorkflowIntegrationAPI.complete_experiment(
    record=exp_record,
    metrics={
        "consistency_score": 0.98,
        "pass_rate": 1.0,
        "avg_tokens": 450
    },
    conclusion="假设验证成功",
    findings="10 次运行结果一致",
    next_steps="集成到生产"
)

print(f"Experiment 完成，结论：{result['conclusion']}")
```

---

## 常见场景

### 场景 1：一个 Task Card 支持多个 Workflow 实验

```
Task Card v0.3 (single)
  ├─ Workflow Execution #1 (candidate_a)
  ├─ Workflow Execution #2 (candidate_b)  
  ├─ Workflow Execution #3 (final)
  └─ 可以对比三个执行的指标
```

**好处：** 所有实验共享统一的上下文，便于对比 A/B/C。

### 场景 2：Handoff 并行审查

```
Task Card v0.3
  ├─ Handoff Record #1 (Quality Team)
  ├─ Handoff Record #2 (Security Team)
  └─ Handoff Record #3 (PM)
  
所有 Handoff 记录引用同一 Task Card 的 checksum，
确保每个审查者看到的上下文一致。
```

### 场景 3：完整生命周期追踪

```
时间线：
  T0: Task Card 创建（checksum A）
  T1: Workflow 执行开始
  T2: Workflow 执行完成
  T3: 导出 JSON/Markdown
  T4: Handoff 开始
  T5: Handoff 批准
  T6: Experiment 开始
  T7: Experiment 完成
  T8: 所有记录归档

每条记录都包含完整的：
  - created_at（创建时间）
  - task_card_checksum（源数据哈希）
  - verification_checklist（12 字段清单）
  - status（当前状态）

可以完整回溯整个任务生命周期。
```

---

## 验收标准

### TC-07 端到端验收清单

✓ **T-001：Task Card 结构**
- 12 个必需字段完整
- 字段类型正确
- 至少 6 项验收标准

✓ **T-002：Prompt 生成**
- 10 段固定骨架
- 字段映射正确
- 长度合理（500-10000 字符）

✓ **T-003：导出格式**
- JSON 有效且可往返
- Markdown 人可读
- 6 类字段确定性排序

✓ **T-004：记录类型**
- 3 类记录（Workflow/Handoff/Experiment）
- 8 个最小字段
- 12 字段验证清单

✓ **T-005：变更检测**
- SHA256 checksum 确定性
- 变更可检测
- 无变更时 checksum 相同

✓ **T-006：向后兼容**
- Task Card 与现有 Task model 兼容
- result.json 结构不变
- 记录命名规范统一

✓ **T-007：生命周期**
- 8 阶段完整流程
- 所有验证通过
- 路径覆盖 creation → archival

---

## 常见问题

### Q1：Task Card 与现有 Task 模型的关系？

**A：** Task Card 是 Task.description 的结构化来源。
- Task Card：结构化的 12 字段描述
- Task 模型：保持不变，新增可选字段指向 Task Card
- 兼容性：完全向后兼容，不修改 ORM

### Q2：为什么要使用 Final Prompt 规范而不是 A 或 B？

**A：** Final 是 A+B 合并版，兼顾三个方面：
- 采用 B 的 10 段骨架：复杂任务约束表达更强
- 采用 A 的字段映射：工程实现更直接
- 采用 B 的约束分层：MUST/SHOULD/MUST NOT 更清晰

### Q3：checksum 检测的是什么变更？

**A：** SHA256 计算 Task Card 的完整内容（排序后）。
- 任何字段变更都会改变 checksum
- 用途：检测在 Workflow/Handoff/Experiment 过程中 Task Card 是否被修改
- 好处：防止记录与不同版本的 Task Card 关联

### Q4：能否跳过某些字段？

**A：** 不能。所有 12 个字段必需。
- 缺失字段的 Task Card 无法通过验证
- 缺失时可使用占位文本，但仍需提供
- 示例：
  ```json
  "background": ["字段未提供，请补齐"],
  "goal": "字段未提供，请补齐"
  ```

### Q5：能否扩展 Task Card 字段？

**A：** 可以，但需谨慎。
- 核心 12 字段不可删除或重命名
- 可增加 `custom_fields` 对象用于扩展
- 示例：
  ```json
  {
    "task_code": "...",
    ...
    "custom_fields": {
      "team": "Platform Team",
      "priority": "P1"
    }
  }
  ```

### Q6：Handoff Record 中 decision 的可选值有哪些？

**A：** 支持 4 种决策：
- `approved`：批准，可进行下一步
- `needs_revision`：需要修改，返工
- `escalated`：升级，提交更高层审查
- `closed`：关闭，任务终止

### Q7：Experiment Record 支持哪些 experiment_type？

**A：** v0.3 预定义 5 种，可扩展：
- `workflow_comparison`：Workflow 对比（A/B/C）
- `prompt_stability`：Prompt 稳定性（100 次生成）
- `export_consistency`：导出一致性（JSON/Markdown）
- `integration_load_test`：集成负载测试
- `backward_compatibility`：向后兼容性

### Q8：如何处理 Task Card 中的多语言内容？

**A：** v0.3 支持 UTF-8，建议：
- 在 `background` 中标记语言
- 示例：
  ```json
  "background": [
    "[EN] System requires authentication",
    "[ZH] 系统需要用户认证"
  ]
  ```

### Q9：record_naming 规范？

**A：** 统一格式：`{task_code}.{record_type}.record.json`
- 示例：
  - `FEATURE-001.workflow_execution.record.json`
  - `FEATURE-001.handoff.record.json`
  - `FEATURE-001.experiment.record.json`

### Q10：性能考虑？

**A：** v0.3 轻量级设计：
- Task Card JSON：通常 1-5 KB
- Prompt 生成：<100ms
- SHA256 checksum：<1ms
- 导出 JSON/Markdown：<50ms
- 无数据库依赖，纯内存操作

---

## 版本历史与支持

### v0.3 特性

- ✓ 12 字段结构化描述
- ✓ Final Prompt 规范（10 段 + 分层约束）
- ✓ JSON/Markdown 双导出
- ✓ 3 类集成记录
- ✓ SHA256 变更检测
- ✓ 完整生命周期追踪

### 向后兼容性

- ✓ Task 模型不变
- ✓ result.json 格式不变
- ✓ 现有 Workflow 系统可直接集成

### 限制（暂不包含）

- ✗ 自动从 GitHub Issue 生成 Task Card
- ✗ 自动难度评估
- ✗ 大规模 benchmark 管理
- ✗ 完整的 Task Card/Task Run 分离模型
- ✗ 数据库持久化（由下游系统提供）

---

## 反馈与改进

如有问题或建议，请通过以下方式提交：

1. 在 Task Card 中的 `context_policy.critical_unknowns` 记录疑问
2. 在 Handoff Record 中的 `notes` 字段反馈改进建议
3. 创建 Experiment Record 并记录发现

---

## 附录：完整 JSON Schema

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "Task Card v0.3",
  "type": "object",
  "required": [
    "task_code", "task_card_version", "task_type", "background",
    "goal", "initial_state", "expected_behavior", "acceptance_criteria",
    "relevant_files", "constraints", "test_method", "difficulty",
    "context_policy", "suitable_experiments"
  ],
  "properties": {
    "task_code": {"type": "string"},
    "task_card_version": {"type": "string", "enum": ["0.3"]},
    "task_type": {"type": "string"},
    "background": {"type": "array", "items": {"type": "string"}, "minItems": 1},
    "goal": {"type": "string"},
    "initial_state": {},
    "expected_behavior": {"type": "object"},
    "acceptance_criteria": {"type": "array", "items": {"type": "string"}, "minItems": 3},
    "relevant_files": {"type": "array", "items": {"type": "string"}},
    "constraints": {"type": "array", "items": {"type": "string"}},
    "test_method": {"type": "object"},
    "difficulty": {"type": "string", "enum": ["Small", "Medium", "Large", "XLarge"]},
    "context_policy": {"type": "object"},
    "suitable_experiments": {"type": "array", "items": {"type": "string"}}
  }
}
```

---

**Last Updated:** 2026-05-08  
**Version:** 0.3  
**Status:** Release Ready
