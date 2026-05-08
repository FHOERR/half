# 候选 B 示例：由 Task Card 生成 Prompt

## 输入（摘要）

- task_type: `feature`
- goal: 在不重构主模型的前提下引入 Task Card 并支持稳定 Prompt 生成
- difficulty.level: `L`
- context_policy.allow_assumptions: `false`

## 输出 Prompt（候选 B）

你是本项目的执行 Agent。

## 1. Role
你负责在既有运行时契约内完成任务，不得绕过现有完成哨兵与状态流转机制。

## 2. Mission
任务类型：feature。  
成功标准：在保持当前 Project/Plan/Task 主模型不重构的前提下，引入结构化 Task Card 并生成稳定 Prompt。

## 3. Background
1. 当前任务描述高度依赖自然语言，复盘与交接一致性较差。  
2. 需要支持 workflow/handoff 对比实验。  
3. v0.3 允许结构增强，不要求实体模型重构。

## 4. Initial State
系统当前以 task_name/description 作为主要任务表达，结构化字段未标准化。

## 5. Target Behavior
输出采用统一字段结构表达任务，并可稳定转换为执行 Prompt。

## 6. Hard Constraints
1. MUST 保持 result.json 完成契约不变。  
2. MUST NOT 引入 Task Run 独立模型。  
3. MUST NOT 引入自动难度评估。  
4. MUST 先确认任何影响默认行为的缺省策略后再实施（allow_assumptions=false）。

## 7. Acceptance Criteria
1. 字段覆盖 task card v0.3 要求。  
2. 同一输入多次生成 Prompt 的区段顺序与约束语句保持一致。  
3. 输出可用于 workflow/handoff/实验记录输入。

## 8. Execution Plan Guardrails
1. 本任务为 L 级，MUST 分阶段执行：结构定义 → 映射规则 → 输出样例。  
2. 每阶段输出必须显式说明风险与取舍。  
3. 若目标与约束冲突，按“安全与完整性 > 既有契约 > 验收标准 > 便捷性”决策，并记录原因。

## 9. Test Method
策略：mixed  
1. 校验字段完整性与顺序稳定性。  
2. 重复生成 Prompt 并对比关键区段一致率。  
3. 检查导出内容（Markdown/JSON）语义一致。

通过信号：字段完整、约束无遗漏、区段顺序稳定。

## 10. Deliverables
1. 结构定义文档与映射规则。  
2. Prompt 样例。  
3. 实验记录维度：workflow_comparison、handoff_comparison、prompt_stability。
