# TC-01: Task Card v0.3 结构定义与边界约束

## 1. 目标与定位

Task Card v0.3 是对现有 Task 的结构化增强层，用于把“自然语言任务描述”标准化为可比较、可交接、可复盘的结构化输入单元。

v0.3 不重构 Project / Plan / Task 主数据模型，不引入 Task Run 独立实体。

## 2. 字段规范（v0.3）

字段见 `task-card-v0.3.schema.json`，本节给出语义约束：

| 字段 | 含义 | 约束 |
|---|---|---|
| `task_type` | 任务类别 | 枚举：feature/bugfix/refactor/infra/test/docs/research |
| `background` | 背景与上下文 | 必填，描述问题来源与业务/工程背景 |
| `goal` | 目标 | 必填，描述完成后达到的状态 |
| `initial_state` | 初始状态 | 必填，描述当前系统行为与边界 |
| `expected_behavior` | 预期行为 | 必填，描述目标行为 |
| `acceptance_criteria` | 验收标准 | 必填数组，至少 1 条，可执行且可验证 |
| `relevant_files` | 相关文件 | 建议数组，可为空 |
| `constraints` | 约束 | 必填数组，至少 1 条（如安全、兼容、性能、时序约束） |
| `test_method` | 测试方法 | 必填对象，含 strategy 与 commands_or_steps |
| `difficulty` | 难度标记 | 必填对象，含 level(S/M/L/XL) 与 reason |
| `context_policy` | 上下文策略 | 必填对象，定义允许假设、必须确认项、禁止动作 |
| `suitable_experiments` | 适配实验 | 必填数组，用于 workflow/handoff/稳定性实验 |

补充字段：
- `version`：固定为 `0.3`
- `metadata`：可选追踪信息（project_id/plan_id/task_code/author/timestamps）

## 3. 与现有 Project / Plan / Task 的兼容策略

基于当前运行时模型（Project → Plan → Task DAG，任务通过 `result.json` 完成契约推进状态）：

1. **保持 Task 主字段不变**  
   当前 `Task.task_name`、`Task.description`、`Task.expected_output_path`、`Task.depends_on_json` 等字段继续作为执行主入口；Task Card 作为 `description` 的结构化来源，不要求替换现有 ORM 表结构。

2. **保持计划生成与 finalize 机制不变**  
   `ProjectPlan.plan_json` 仍承载任务 DAG。v0.3 仅要求单个 task 节点可附带 Task Card 数据（例如嵌入节点扩展字段），不改变 finalize 触发方式与状态机。

3. **保持任务执行契约不变**  
   执行输出仍使用 `<collaboration_dir>/<task_code>/result.json` 作为完成哨兵；Task Card 不改变轮询与完成判定逻辑。

4. **Prompt 生成可复用现有接口**  
   现有 `generate_task_prompt` 可读取 Task Card 字段进行模板拼装（后续任务实现），但 v0.3 不要求新增独立运行通道。

## 4. 边界与不纳入范围（v0.3）

以下内容明确不纳入 v0.3：

1. 自动从 GitHub Issue 生成 Task Card
2. 自动难度评估（difficulty 仅允许人工或上游系统填写）
3. 大规模 benchmark 编排与管理平台
4. Task Card 与 Task Run 的完全实体分离与生命周期重构

## 5. 导出要求（为后续任务提供输入）

v0.3 统一支持两类导出：

1. JSON：作为机器可读、可验证输入（对应 schema）
2. Markdown：作为人类可读、评审与 handoff 输入

两种导出必须保持字段语义一致与顺序稳定，以支持 workflow 对比与复盘。
