# TC-03: 候选方案 B — Task Card 到 Agent Prompt 生成策略

## 1. 设计目标

候选 B 面向复杂任务，强调两件事：

1. **指令稳定性**：同一 Task Card 多次生成时，Prompt 结构、字段顺序、约束表达一致。
2. **上下文约束显式化**：把约束分层展开，减少 agent 在复杂场景中的“漏读约束”。

## 2. 核心策略（B）

### 2.1 固定骨架（Stable Skeleton）

Prompt 固定为 10 个区段，禁止按字段有无重排区段：

1. Role
2. Mission
3. Background
4. Initial State
5. Target Behavior
6. Hard Constraints
7. Acceptance Criteria
8. Execution Plan Guardrails
9. Test Method
10. Deliverables

字段缺省时使用占位语句（如“无补充背景”），而不是删段。

### 2.2 约束分层（Constraint Layering）

将 `constraints + context_policy` 合并后按强度拆为三层：

- **L1 Non-negotiable**：禁止动作、不可破坏契约、边界条件
- **L2 Required Process**：必须确认项、必须执行步骤
- **L3 Preferred**：非强制但建议遵循的执行偏好

在 Prompt 中显式标注 “MUST / SHOULD / MUST NOT”。

### 2.3 冲突消解（Conflict Resolver）

若出现“目标 vs 约束”冲突，固定决策顺序：

`安全与数据完整性 > 既有系统契约 > 验收标准 > 实现便捷性`

并在 Prompt 中要求 agent 输出“冲突与取舍说明”。

### 2.4 上下文预算（Context Budget）

复杂任务常见问题是冗长上下文淹没关键信息。候选 B 采用：

- 背景信息限缩为最多 5 条关键事实
- 约束按优先级排序并编号
- 验收标准映射为可执行 checklist

### 2.5 不确定性门控（Uncertainty Gate）

根据 `context_policy.allow_assumptions`：

- `true`：允许合理假设，但必须在输出中列出假设清单
- `false`：遇到关键缺口必须先确认，不得直接实现

## 3. 字段到 Prompt 的映射规则

见 `prompt-generator-b-rules.json`。其要点：

1. 字段顺序固定，不受输入 JSON 键顺序影响
2. 数组字段统一编号输出（1..N），避免 bullet 风格漂移
3. `difficulty.level` 驱动执行深度提示：
   - S/M：偏直接实现
   - L/XL：强制要求阶段化执行与风险显式化
4. `suitable_experiments` 直接映射到“建议实验记录维度”

## 4. 与候选 A 的可比性设计

候选 B 专门加入以下可比点，便于后续评审：

1. Prompt 结构稳定性（重复生成一致率）
2. 复杂任务中的约束遵循率
3. 对冲突场景的解释完整度
4. 交接场景下的可读性与可执行性

## 5. v0.3 边界遵循

候选 B 仅定义 Prompt 生成策略，不引入：

- 自动 Issue → Task Card 转换
- 自动难度评估
- Task Run 独立模型
- benchmark 管理系统
