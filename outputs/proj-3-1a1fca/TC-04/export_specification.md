# TC-04: Task Card v0.3 导出能力实现

## 概述

TC-04 实现了 Task Card v0.3 的双格式导出能力：

1. **JSON 导出**：规范化的结构化格式，用于机器处理和跨系统交换
2. **Markdown 导出**：人类可读的格式，用于文档、评审和 handoff

两种导出格式保证：
- **字段顺序统一**：按固定的字段类别顺序输出，确保可对比性
- **空值处理一致**：统一的缺省值处理规则
- **版本标记清晰**：版本号明确标记，便于版本管理

---

## 1. 字段顺序规范

所有导出格式遵循以下固定的字段顺序，分为 6 个类别：

### 类别 1: 元数据与版本（Meta）
- `version`（必须）：固定为 `"0.3"`
- `metadata`（可选）：项目、作者、时间戳等追踪信息

### 类别 2: 任务类型与背景（Type & Context）
- `task_type`（必填）：任务分类（feature/bugfix/refactor/infra/test/docs/research）
- `background`（必填）：问题背景与上下文

### 类别 3: 规范（Specification）
- `initial_state`（必填）：当前系统状态
- `goal`（必填）：目标状态
- `expected_behavior`（必填）：预期行为
- `acceptance_criteria`（必填）：验收标准列表

### 类别 4: 约束（Constraints）
- `relevant_files`（可选，默认空数组）：相关文件列表
- `constraints`（必填）：约束条件列表
- `context_policy`（必填）：上下文策略（假设策略、确认项、禁止项）

### 类别 5: 测试（Testing）
- `test_method`（必填）：测试策略与步骤
- `difficulty`（必填）：难度评级与原因

### 类别 6: 实验（Experiments）
- `suitable_experiments`（必填）：适配的实验类型

**优势**：
- 类别化顺序更易理解（从基础 → 约束 → 测试）
- 版本和元数据始终居前，便于版本控制系统处理
- 同一类别内的字段逻辑相关，易于批量处理

---

## 2. JSON 导出规范

### 2.1 输出格式

**标准 JSON，字段按定义顺序排列**：

```json
{
  "version": "0.3",
  "metadata": {
    "task_code": "TC-01",
    "author": "Claude Max",
    "created_at": "2026-05-08T11:09:51+08:00",
    "updated_at": "2026-05-08T12:00:00+08:00"
  },
  "task_type": "feature",
  "background": "...",
  "initial_state": "...",
  "goal": "...",
  "expected_behavior": "...",
  "acceptance_criteria": ["...", "..."],
  "relevant_files": [],
  "constraints": ["..."],
  "context_policy": {
    "allow_assumptions": false,
    "must_confirm": [],
    "forbidden_actions": []
  },
  "test_method": {
    "strategy": "mixed",
    "commands_or_steps": ["..."],
    "pass_signal": "..."
  },
  "difficulty": {
    "level": "M",
    "reason": "..."
  },
  "suitable_experiments": ["workflow_comparison"]
}
```

### 2.2 缺省值处理

| 字段 | 缺省行为 | 示例 |
|---|---|---|
| `version` | 如缺失，自动补充 `"0.3"` | 导出时自动添加 |
| `metadata` | 可完全缺失 | 如无作者，则不包含 author 字段 |
| `relevant_files` | 空数组保留，不删除 | `"relevant_files": []` |
| `context_policy.must_confirm` | 空数组保留 | `"must_confirm": []` |
| `context_policy.forbidden_actions` | 空数组保留 | `"forbidden_actions": []` |
| `test_method.pass_signal` | 可缺失，不添加默认值 | 如无则不包含 |
| `metadata.updated_at` | 可缺失 | 仅 created_at 导出 |

### 2.3 紧凑与美化模式

支持两种导出模式：

```python
# 美化模式（默认）：带缩进和换行，便于人读
exporter.export_json(prettify=True)
# 输出：{"version": "0.3", ...}

# 紧凑模式：最小化空格，便于传输
exporter.export_json(prettify=False)
# 输出：{"version":"0.3",...}
```

---

## 3. Markdown 导出规范

### 3.1 整体结构

```markdown
# Task Card: TC-01

_Version: 0.3_

## 目录

- [元数据](#元数据)
- [任务类型与背景](#任务类型与背景)
- [任务规范](#任务规范)
- [约束条件](#约束条件)
- [测试与验证](#测试与验证)
- [适配实验](#适配实验)

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

### 约束条件

- 不重构现有 Project/Plan/Task 主模型。
- 保持 result.json 完成契约不变。

### 执行上下文

- **假设**：必须确认所有不明确项，不允许任意假设

**必须确认项**：
- 涉及行为变更的默认值策略
- 字段缺省时的降级规则

**禁止操作**：
- 修改既有 result.json 完成判定机制

## 测试与验证

**测试策略**：混合

**测试步骤**：
- 用 schema 校验示例 Task Card JSON。
- 用同一 Task Card 多次生成 Prompt。

**通过信号**：字段完整、导出一致、Prompt 映射稳定。

**难度**：🟡 M (中等)
_原因：需要兼容现有运行时模型并定义清晰边界。_

## 适配实验

- Workflow 对比
- Handoff 对比
- 提示稳定性
```

### 3.2 特殊处理

#### 难度显示

使用 emoji 和文字结合，便于快速识别：

```
🟢 S (简单)
🟡 M (中等)
🟠 L (复杂)
🔴 XL (很复杂)
```

#### 枚举值映射

在 Markdown 中自动转换为中文易读形式：

| 字段 | 转换 |
|---|---|
| `task_type: "feature"` | 类型：功能 |
| `strategy: "automated"` | 测试策略：自动化 |
| `experiments: "workflow_comparison"` | Workflow 对比 |

#### 空值处理

- 空数组：显示 `_无相关文件_` 或 `_无约束条件_`
- 缺失字段：完全省略对应小节
- 空字符串：显示为空（不添加占位符）

---

## 4. 稳定性保证

### 4.1 字段顺序确定性

实现了 `FIELD_ORDER` 常量，定义了每个字段的排序键：

```python
FIELD_ORDER = {
    "version": (FieldCategory.METADATA, 0),
    "metadata": (FieldCategory.METADATA, 1),
    "task_type": (FieldCategory.TYPE_AND_CONTEXT, 0),
    # ...
}
```

**保证**：同一 Task Card 多次导出，字段顺序完全相同。

### 4.2 缺省值幂等性

所有导出操作都遵循相同的缺省处理规则：

- `version` 缺失 → 自动补充
- 空数组保留 → 不删除字段
- 可选字段缺失 → 完全省略

**保证**：同一输入 N 次导出完全一致。

### 4.3 测试方法

```python
# 稳定性测试示例
exporter = TaskCardExporter(task_card)
exports = [exporter.export_json() for _ in range(100)]
assert all(e == exports[0] for e in exports), "Export instability!"
```

---

## 5. 使用指南

### 5.1 基础用法

```python
from task_card_exporter import TaskCardExporter

# 加载 Task Card
with open("task.json") as f:
    task_card = json.load(f)

# 创建导出器
exporter = TaskCardExporter(task_card)

# 导出 JSON
json_str = exporter.export_json(prettify=True)

# 导出 Markdown
md_str = exporter.export_markdown(include_toc=True)
```

### 5.2 批量导出

```python
from task_card_exporter import load_and_export

# 一次性导出到目录
result = load_and_export(
    json_path="task.json",
    output_dir="exports"
)
# 返回 {"json": "...", "markdown": "..."}
```

### 5.3 集成建议

#### 与 workflow 集成

```python
# 在 task execution 前导出文档
task_card = load_task_card(task_code)
exporter = TaskCardExporter(task_card)

# 保存为 Markdown 用于人类评审
with open(f"docs/{task_code}.md", "w") as f:
    f.write(exporter.export_markdown())

# 保存为 JSON 用于机器处理
with open(f"data/{task_code}.json", "w") as f:
    f.write(exporter.export_json())
```

#### 与 version control 集成

```bash
# 定期导出 JSON 用于版本比对
git diff task-card-v1.json task-card-v2.json
# JSON 格式的字段顺序一致，便于 diff

# 导出 Markdown 用于人类评审
git show HEAD:task.md | diff - task-card-latest.md
```

---

## 6. 对比 JSON vs Markdown

| 特性 | JSON | Markdown |
|---|---|---|
| **机器可读** | ✓ | △ (需 markdown parser) |
| **人类可读** | △ | ✓ |
| **版本对比** | ✓ (结构化) | ✓ (文本差异) |
| **用途** | API、workflow、存储 | 文档、评审、handoff |
| **字段顺序** | 固定且可序列化 | 固定但不可序列化 |
| **扩展性** | ✓ | ✓ (添加新 section) |

---

## 7. 与 TC-01、TC-02 的关系

- **TC-01**：定义 Task Card Schema 和字段规范
- **TC-02**：从 Task Card 生成 Agent Prompt（候选 A）
- **TC-04**：导出 Task Card 本身（JSON / Markdown）

三者配合使用流程：

```
1. 用户创建 Task Card (满足 TC-01 Schema)
   ↓
2. 导出 Task Card (TC-04)
   - JSON 用于 workflow 处理
   - Markdown 用于评审和文档
   ↓
3. 生成 Agent Prompt (TC-02)
   - 从 Task Card 生成稳定的 Prompt
   - 用于 agent 执行任务
```

---

## 8. 范围内 & 范围外

### ✓ 范围内（TC-04 实现）

- JSON 导出（标准化字段顺序）
- Markdown 导出（人读格式）
- 空值处理规则
- 版本标记
- 稳定性保证
- 双向映射（部分）

### ✗ 范围外（未来任务）

- YAML / TOML 导出
- CSV / Excel 导出
- 自动 Markdown ↔ JSON 转换
- 版本迁移（v0.3 → v0.4）
- Task Card 编辑 UI

---

## 9. 示例输出

### 9.1 JSON 导出示例

见 `examples/TC-01.json`

### 9.2 Markdown 导出示例

见 `examples/TC-01.md`

---

## 10. 参考

- Task Card v0.3 Schema: TC-01 输出
- Task Card v0.3 Example: TC-01 输出
- Exporter 实现: `task_card_exporter.py`
- 生成示例脚本: `generate_exports.py`
