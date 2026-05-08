# Task Card: TC-01

_Version: 0.3_

## 元数据

- **任务码**：`TC-01`
- **作者**：Claude Max
- **创建时间**：2026-05-08T11:09:51+08:00

## 任务类型与背景

**类型**：功能

**背景**：

当前任务描述依赖自然语言，难以进行 workflow 对比与 handoff 复盘。


## 任务规范

### 当前状态

系统现有 Task 以 task_name/description 表达，不具备结构化字段约束。

### 目标

引入可复用的 Task Card 结构，作为任务执行输入。

### 预期行为

任务可通过标准字段完整表达，并可导出为 JSON/Markdown。

### 验收标准

1. Task Card 包含并校验 v0.3 规定字段。
2. 可从 Task Card 稳定生成执行 Prompt。
3. 可用于 workflow、handoff、实验记录输入。


## 约束条件

### 相关文件

- `src/backend/services/prompt_service.py`
- `src/backend/routers/tasks.py`
- `src/frontend/src/pages/TasksPage.tsx`

### 约束条件

- 不重构现有 Project/Plan/Task 主模型。
- 不引入 Task Run 独立实体。
- 保持 result.json 完成契约不变。

### 执行上下文

- **假设**：必须确认所有不明确项，不允许任意假设

**必须确认项**：
- 涉及行为变更的默认值策略
- 字段缺省时的降级规则

**禁止操作**：
- 修改既有 result.json 完成判定机制
- 引入 v0.3 范围外的大规模 benchmark 子系统


## 测试与验证

**测试策略**：混合

**测试步骤**：
- 用 schema 校验示例 Task Card JSON。
- 用同一 Task Card 多次生成 Prompt，检查字段顺序与语义稳定。
- 检查 Markdown/JSON 导出字段一致性。

**通过信号**：字段完整、导出一致、Prompt 映射稳定。

**难度**：🟡 M (中等)

_原因：需要兼容现有运行时模型并定义清晰边界。_


## 适配实验

- Workflow 对比
- Handoff 对比
- 提示稳定性
