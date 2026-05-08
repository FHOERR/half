# TC-05: Workflow / Handoff / 实验记录输入对齐

## 概述

TC-05 将 Task Card v0.3 作为统一的输入单元，接入到三个核心流程：
1. **Workflow Execution**：任务自动执行的记录
2. **Handoff Communication**：人工交接的记录
3. **Experiment Recording**：科学实验的记录

目标是通过统一的 Task Card 输入、最小化的记录字段和一致的验证规则，使这三个流程可以相互配合、彼此验证、形成完整的任务生命周期记录。

---

## 1. 最小可用记录字段（Minimal Record Fields）

所有记录类型都包含以下最小字段集，确保可追溯性和一致性：

```python
@dataclass
class MinimalRecordFields:
    task_code: str                      # Task Card 的任务码
    task_card_version: str              # Task Card 版本（0.3）
    record_type: str                    # "workflow_execution" | "handoff" | "experiment"
    created_at: str                     # ISO 8601 时间戳
    agent_or_person: str                # 谁创建了这条记录
    status: str                         # "pending" | "in_progress" | "completed" | "failed"
    task_card_checksum: str             # SHA256 校验和（变更检测）
    verification_checklist: Dict        # 12 个 Task Card 字段的验证状态
```

### 1.1 验证清单（Verification Checklist）

为了确保使用了完整的 Task Card，所有记录都包含一个验证清单：

```python
verification_checklist = {
    "task_type": True,
    "background": True,
    "goal": True,
    "initial_state": True,
    "expected_behavior": True,
    "acceptance_criteria": True,
    "relevant_files": True,
    "constraints": True,
    "test_method": True,
    "difficulty": True,
    "context_policy": True,
    "suitable_experiments": True
}
```

**要求**：所有字段都必须为 `True`，否则无法启动记录。

### 1.2 变更检测（Checksum）

计算原始 Task Card 的 SHA256 校验和，用于检测源数据变更：

```python
# 过程
json_str = json.dumps(task_card, sort_keys=True)
checksum = hashlib.sha256(json_str.encode()).hexdigest()
```

**用途**：
- 如果同一 task_code 的 Task Card 在执行过程中被修改，checksum 会变化
- 用于 workflow/handoff/experiment 的数据完整性验证

---

## 2. 三个记录类型的规范

### 2.1 工作流执行记录（WorkflowExecutionRecord）

用于记录 Task Card 在 Workflow 中的自动执行。

```python
@dataclass
class WorkflowExecutionRecord:
    minimal_fields: MinimalRecordFields
    
    # 工作流上下文
    workflow_id: str                    # 工作流唯一标识
    execution_id: str                   # 执行实例唯一标识
    prompt_strategy: str                # "candidate_a" 或 "candidate_b"
    generated_prompt: Optional[str]     # 生成的实际 Prompt
    agent_version: str                  # Agent 软件版本
    
    # 执行周期
    start_time: str                     # 开始时间
    end_time: Optional[str]             # 结束时间
    duration_seconds: Optional[float]   # 总耗时
    
    # 输出跟踪
    output_path: str                    # 输出文件路径
    result_summary: str                 # 执行结果摘要
    success: bool                       # 是否成功
    error_message: Optional[str]        # 错误信息
```

#### 生命周期

```
1. 创建阶段：
   - 加载 Task Card
   - 验证所有字段
   - 计算 checksum
   - 状态：pending

2. 执行阶段：
   - 调用 Prompt 生成器（A 或 B）
   - 传递给 Agent
   - 记录生成的 Prompt
   - 状态：in_progress

3. 完成阶段：
   - Agent 输出完成
   - 记录输出路径、摘要、成功/失败
   - 计算执行耗时
   - 状态：completed 或 failed
```

### 2.2 交接记录（HandoffRecord）

用于记录人工交接或不同实体之间的任务转移。

```python
@dataclass
class HandoffRecord:
    minimal_fields: MinimalRecordFields
    
    # 交接方向
    from_entity: str                    # 源方（如 "executor_agent"）
    to_entity: str                      # 目标方（如 "human_reviewer"）
    handoff_reason: str                 # 交接原因
    
    # 导出与通信
    exported_format: str                # "json" | "markdown" | "both"
    exported_files: List[str]           # 导出的文件列表
    notes: str                          # 交接说明
    
    # 决策
    decision: str                       # "approved" | "needs_revision" | "escalated" | "closed"
    decision_reason: Optional[str]      # 决策原因
```

#### 生命周期

```
1. 启动阶段：
   - 确定源方、目标方、原因
   - 用 TC-04 导出器导出 Task Card（JSON/Markdown/Both）
   - 状态：in_progress

2. 传输阶段：
   - 传输导出文件
   - 可选：添加评论或建议
   - 等待目标方收到和审查

3. 决策阶段：
   - 目标方审查并做出决策
   - 记录决策和理由
   - 状态：completed
```

#### 交接原因示例

| 原因 | 描述 |
|---|---|
| `quality_review_required` | 需要人工质量审查 |
| `expertise_required` | 需要专家判断 |
| `high_complexity` | 任务过于复杂 |
| `ambiguity_resolution` | 需要澄清歧义 |
| `approval_needed` | 需要审批 |
| `handoff_to_qa` | 交接给 QA 测试 |
| `post_review_cleanup` | 评审后的清理工作 |

#### 决策选项

| 决策 | 含义 |
|---|---|
| `approved` | 接受，任务完成 |
| `needs_revision` | 需要修订，发回执行者 |
| `escalated` | 升级处理 |
| `closed` | 关闭记录 |

### 2.3 实验记录（ExperimentRecord）

用于记录科学实验，支持各类对比和验证。

```python
@dataclass
class ExperimentRecord:
    minimal_fields: MinimalRecordFields
    
    # 实验定义
    experiment_type: str                # 来自 Task Card suitable_experiments
    experiment_id: str                  # 实验唯一标识
    hypothesis: str                     # 假设
    
    # 测量
    metrics: Dict[str, Any]             # 灵活的指标字典
    
    # 结果
    findings: str                       # 发现
    conclusion: str                     # 结论
    next_steps: Optional[str]           # 后续步骤
```

#### 实验类型与指标

| 实验类型 | 假设示例 | 指标示例 |
|---|---|---|
| `workflow_comparison` | 候选 A 比 B 更稳定 | `{success_rate, avg_time, quality_score}` |
| `handoff_comparison` | Markdown 导出比 JSON 更易理解 | `{clarity_score, decision_time}` |
| `prompt_stability` | 同一 Task Card 生成的 Prompt 一致 | `{stability_score, identical_generations}` |
| `execution_replay` | 相同条件下可重现执行结果 | `{replay_success_rate, deviation}` |
| `quality_review` | 人工评分达到 4.5/5 以上 | `{quality_score, reviewer_count}` |

---

## 3. 集成 API（High-Level）

### 3.1 工作流执行 API

```python
# 启动执行
workflow_result = WorkflowIntegrationAPI.start_workflow_execution(
    task_card=task_card,
    workflow_id="wf-001",
    execution_id="exec-001",
    prompt_strategy="candidate_a"
)
# 返回：execution record + validation

# 完成执行
completion = WorkflowIntegrationAPI.complete_workflow_execution(
    record_json=workflow_result['record'],
    output_path="outputs/exec-001/result.json",
    result_summary="All criteria met",
    success=True
)
# 返回：status + duration + final record
```

### 3.2 交接 API

```python
# 启动交接
handoff_result = WorkflowIntegrationAPI.initiate_handoff(
    task_card=task_card,
    from_entity="executor_agent",
    to_entity="human_reviewer",
    handoff_reason="quality_review_required",
    export_format="both"
)
# 返回：handoff record + exported files + validation

# 完成交接
completion = WorkflowIntegrationAPI.complete_handoff(
    record_json=handoff_result['record'],
    decision="approved",
    decision_reason="Meets standards",
    notes="Ready for deployment"
)
# 返回：decision + final record
```

### 3.3 实验 API

```python
# 启动实验
exp_result = WorkflowIntegrationAPI.start_experiment(
    task_card=task_card,
    experiment_type="prompt_stability",
    experiment_id="exp-001",
    hypothesis="Candidate A is 100% stable"
)
# 返回：experiment record + validation

# 完成实验
completion = WorkflowIntegrationAPI.complete_experiment(
    record_json=exp_result['record'],
    metrics={"stability_score": 1.0, "runs": 100},
    findings="All 100 generations identical",
    conclusion="Candidate A is production-ready"
)
# 返回：metrics + final record
```

---

## 4. 与现有系统兼容性

### 4.1 保持 Task 主模型不变

- Task Card **不** 修改 Project/Plan/Task ORM 模型
- Task Card **作为** Task.description 的结构化来源
- 记录通过 `minimal_fields.task_code` 关联到任务

### 4.2 与现有 result.json 兼容

- 现有 result.json 完成契约不变
- 新增的 Record 类型通过额外的 JSON 文件存储
- 命名约定：`{task_code}.{record_type}.record.json`

示例：
```
outputs/
├── TC-01/
│   ├── result.json                          (既有完成契约)
│   ├── TC-01.workflow_execution.record.json (新增：执行记录)
│   ├── TC-01.handoff.record.json            (新增：交接记录)
│   └── TC-01.experiment.record.json         (新增：实验记录)
```

### 4.3 字段映射

| Task Card 字段 | 记录中的使用 | 说明 |
|---|---|---|
| `metadata.task_code` | 所有记录.task_code | 唯一标识 |
| `version` | 所有记录.task_card_version | 版本追踪 |
| `acceptance_criteria` | Workflow.result_summary | 验收标准检查 |
| `test_method` | Workflow.generated_prompt | 测试指导 |
| `suitable_experiments` | Experiment.experiment_type | 实验类型 |
| `context_policy` | Handoff notes | 交接注意事项 |

---

## 5. 数据流示例

### 5.1 完整的任务生命周期

```
1. 任务创建
   ↓
2. 创建 Task Card v0.3
   ├─ 验证所有 12 个字段
   └─ 计算 checksum
   ↓
3. 启动 Workflow 执行
   ├─ 创建 WorkflowExecutionRecord
   ├─ 选择 Prompt 生成策略（A 或 B）
   └─ 传递给 Agent
   ↓
4. Agent 执行完成
   ├─ 记录输出路径
   ├─ 标记为 success/failed
   └─ 完成 Workflow 记录
   ↓
5. 启动 Handoff（质量审查）
   ├─ 创建 HandoffRecord
   ├─ 导出 Task Card 为 Markdown
   └─ 传递给人工审查者
   ↓
6. 人工审查与决策
   ├─ 审查者记录决策（approved/needs_revision）
   └─ 完成 Handoff 记录
   ↓
7. 启动 Experiment（稳定性验证）
   ├─ 创建 ExperimentRecord
   ├─ 100 次生成同一 Prompt
   ├─ 测量稳定性指标
   └─ 完成 Experiment 记录
   ↓
8. 任务记录完成
   ├─ Workflow Record
   ├─ Handoff Record
   ├─ Experiment Record
   └─ 所有记录归档
```

### 5.2 JSON 记录示例

#### Workflow 执行记录

```json
{
  "minimal_fields": {
    "task_code": "TC-01",
    "task_card_version": "0.3",
    "record_type": "workflow_execution",
    "created_at": "2026-05-08T12:00:00",
    "agent_or_person": "executor_agent_v1",
    "status": "completed",
    "task_card_checksum": "abc123...",
    "verification_checklist": {
      "task_type": true,
      "background": true,
      // ... all 12 fields = true
    }
  },
  "workflow_id": "wf-001",
  "execution_id": "exec-001",
  "prompt_strategy": "candidate_a",
  "generated_prompt": "## 任务基础信息\n...",
  "agent_version": "1.0.0",
  "start_time": "2026-05-08T12:00:01",
  "end_time": "2026-05-08T12:05:30",
  "duration_seconds": 329.0,
  "output_path": "outputs/exec-001/result.json",
  "result_summary": "All 3 acceptance criteria met",
  "success": true,
  "error_message": null
}
```

#### Handoff 交接记录

```json
{
  "minimal_fields": { /* ... */ },
  "from_entity": "executor_agent",
  "to_entity": "human_reviewer",
  "handoff_reason": "quality_review_required",
  "exported_format": "both",
  "exported_files": [
    "handoff/TC-01.json",
    "handoff/TC-01.md"
  ],
  "notes": "Execution completed successfully. Review quality and approve for deployment.",
  "decision": "approved",
  "decision_reason": "Output meets quality standards and all criteria verified"
}
```

---

## 6. 验证与一致性

### 6.1 十二字段验证

每条记录启动时都验证 Task Card 的完整性：

```python
required_fields = {
    "task_type", "background", "goal", "initial_state",
    "expected_behavior", "acceptance_criteria", "relevant_files",
    "constraints", "test_method", "difficulty", "context_policy",
    "suitable_experiments"
}

verification = {field: field in task_card for field in required_fields}
# 所有值必须为 True，否则拒绝创建记录
```

### 6.2 Checksum 一致性检查

```python
# 首次记录时计算
original_checksum = compute_checksum(task_card)

# 后续操作时验证
if compute_checksum(current_task_card) != original_checksum:
    raise ValueError("Task Card was modified after record creation")
```

---

## 7. 与 TC-02、TC-03、TC-04 的关系

```
TC-01: Task Card Schema
   ↓
TC-02: Agent Prompt (Candidate A)
   ↓
TC-03: Agent Prompt (Candidate B)
   ↓
TC-04: Task Card Export (JSON/Markdown)
   ↓
TC-05: Workflow/Handoff/Experiment Integration ← 本任务
   │
   ├── Workflow 使用 TC-02/TC-03 生成的 Prompt
   ├── Handoff 使用 TC-04 导出的 JSON/Markdown
   └── Experiment 测量 TC-02/TC-03 的稳定性
```

---

## 8. 范围内 & 范围外

### ✓ 范围内（TC-05 实现）

- 三类记录的数据模型定义
- 最小字段集的规范
- 集成 API 设计与实现
- 生命周期管理
- 变更检测（checksum）
- 字段验证

### ✗ 范围外（未来任务）

- 数据库持久化实现
- 分布式交接协议
- 自动实验运行器
- 实验结果分析与可视化
- 记录版本化与迁移

---

## 9. 集成建议

### 9.1 Workflow 系统集成

```python
# 在 workflow_executor.py 中
from task_card_integration import WorkflowIntegrationAPI

def execute_task(task_code, task_card_json):
    # 启动
    record = WorkflowIntegrationAPI.start_workflow_execution(
        task_card_json, workflow_id="wf-001", ...
    )
    
    try:
        # 执行（使用 TC-02/TC-03 Prompt）
        result = agent.execute(record['generated_prompt'])
        
        # 完成
        completion = WorkflowIntegrationAPI.complete_workflow_execution(
            record_json, success=True, output_path=result['path']
        )
    except Exception as e:
        completion = WorkflowIntegrationAPI.complete_workflow_execution(
            record_json, success=False, error_message=str(e)
        )
    
    # 保存记录
    save_record(completion['record'], f"{task_code}.workflow.record.json")
```

### 9.2 人工审查 UI 集成

```python
# 在 handoff_ui.py 中
# 展示导出的 Markdown 和 JSON
# 用户审查后选择决策
# 通过 complete_handoff() 记录决策
```

### 9.3 实验框架集成

```python
# 在 experiment_runner.py 中
# 加载 Task Card
# 按 experiment_type 运行对应实验
# 记录指标和结论
```

---

## 10. 参考

- Task Card v0.3 Schema: TC-01
- Prompt 生成（候选 A）: TC-02
- Prompt 生成（候选 B）: TC-03
- 导出能力: TC-04
- 集成实现: `task_card_integration.py`
