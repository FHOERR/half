# TC-06 Final：Task Card v0.3 Prompt 生成规范（A+B 合并版）

## 1. 目标

在 v0.3 范围内定义统一 Prompt 生成规范，兼顾：

1. 复杂任务指令稳定性
2. 上下文与约束保真
3. 工程可实现性
4. workflow/handoff/实验可比性

## 2. 固定输出骨架（必须）

Prompt 必须按以下顺序输出，字段缺失不得删段，仅允许占位文本：

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

## 3. 字段映射（核心）

- `task_type + goal` → Mission
- `background` → Background（最多 5 条关键事实）
- `initial_state` → Initial State
- `expected_behavior` → Target Behavior
- `constraints + context_policy` → Hard Constraints（MUST/SHOULD/MUST NOT）
- `acceptance_criteria` → Acceptance Criteria（编号清单）
- `difficulty` → Execution Plan Guardrails（L/XL 强制阶段化与风险说明）
- `test_method` → Test Method（策略 + 步骤 + 通过信号）
- `relevant_files + suitable_experiments + metadata` → Deliverables

## 4. 缺省与占位策略（必须确定）

1. 缺失字符串：输出“未提供该字段，请按当前上下文补齐”
2. 缺失数组：输出 `[]` 并保留段落
3. 缺失 `pass_signal`：输出“所有验收标准均满足且关键测试通过”
4. `allow_assumptions=false`：必须输出“关键缺口需先确认，不得直接实现”

## 5. 冲突决策序（必须）

目标与约束冲突时，按以下顺序决策并输出取舍说明：

`安全与数据完整性 > 既有运行时契约 > 验收标准 > 实现便捷性`

## 6. 可比性要求

同一 Task Card 多次生成必须满足：

1. 段落顺序一致
2. 约束关键词一致（MUST/SHOULD/MUST NOT）
3. 列表编号方式一致
4. 缺省占位文本一致

## 7. v0.3 边界

本规范不包含：

- 自动 Issue → Task Card
- 自动难度评估
- Task Card / Task Run 完整分离模型
- benchmark 管理平台
