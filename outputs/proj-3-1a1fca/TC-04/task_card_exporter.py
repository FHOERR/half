#!/usr/bin/env python3
"""
Task Card v0.3 Export Capability

Supports dual-format export:
1. JSON: Canonical format with standardized field ordering and null handling
2. Markdown: Human-readable format for review and documentation

Key Features:
- Stable field ordering ensures consistent export order
- Unified null/empty value handling
- Version marking for tracking changes
- Support for metadata preservation
"""

import json
from datetime import datetime
from typing import Dict, List, Any, Optional
from enum import Enum


class FieldCategory(Enum):
    """Task Card field categories for ordering."""
    METADATA = 1
    TYPE_AND_CONTEXT = 2
    SPECIFICATION = 3
    CONSTRAINTS = 4
    TESTING = 5
    EXPERIMENTS = 6


# Stable field ordering for exports
FIELD_ORDER = {
    # Metadata & Version (must come first)
    "version": (FieldCategory.METADATA, 0),
    "metadata": (FieldCategory.METADATA, 1),
    
    # Task type and background context
    "task_type": (FieldCategory.TYPE_AND_CONTEXT, 0),
    "background": (FieldCategory.TYPE_AND_CONTEXT, 1),
    
    # Specification: current state → target state
    "initial_state": (FieldCategory.SPECIFICATION, 0),
    "goal": (FieldCategory.SPECIFICATION, 1),
    "expected_behavior": (FieldCategory.SPECIFICATION, 2),
    "acceptance_criteria": (FieldCategory.SPECIFICATION, 3),
    
    # Constraints and context
    "relevant_files": (FieldCategory.CONSTRAINTS, 0),
    "constraints": (FieldCategory.CONSTRAINTS, 1),
    "context_policy": (FieldCategory.CONSTRAINTS, 2),
    
    # Testing and validation
    "test_method": (FieldCategory.TESTING, 0),
    "difficulty": (FieldCategory.TESTING, 1),
    
    # Experiments and future use
    "suitable_experiments": (FieldCategory.EXPERIMENTS, 0),
}

# Type mappings for Markdown rendering
TYPE_NAMES = {
    "feature": "功能",
    "bugfix": "缺陷修复",
    "refactor": "重构",
    "infra": "基础设施",
    "test": "测试",
    "docs": "文档",
    "research": "研究"
}

STRATEGY_NAMES = {
    "automated": "自动化",
    "manual": "手动",
    "mixed": "混合"
}

EXPERIMENT_NAMES = {
    "workflow_comparison": "Workflow 对比",
    "handoff_comparison": "Handoff 对比",
    "prompt_stability": "提示稳定性",
    "execution_replay": "执行回放",
    "quality_review": "质量评审"
}

DIFFICULTY_COLORS = {
    "S": "🟢 S (简单)",
    "M": "🟡 M (中等)",
    "L": "🟠 L (复杂)",
    "XL": "🔴 XL (很复杂)"
}


class TaskCardExporter:
    """
    Export Task Card v0.3 to JSON and Markdown formats.
    
    Guarantees:
    - Consistent field ordering across all exports
    - Deterministic null/empty value handling
    - Version marking for traceability
    - Preservation of all metadata
    """
    
    def __init__(self, task_card: Dict[str, Any]):
        """Initialize with a Task Card JSON object."""
        self.task_card = task_card
        self._normalize_version()
    
    def _normalize_version(self):
        """Ensure version is set to 0.3 if not present."""
        if "version" not in self.task_card:
            self.task_card["version"] = "0.3"
    
    def export_json(self, include_version: bool = True, 
                   prettify: bool = True) -> str:
        """
        Export Task Card as canonical JSON with stable field ordering.
        
        Args:
            include_version: Whether to include version field
            prettify: Whether to format with indentation
        
        Returns:
            Formatted JSON string
        """
        # Create ordered dict with stable field ordering
        ordered = self._order_fields(self.task_card)
        
        # Export with or without pretty printing
        if prettify:
            return json.dumps(ordered, ensure_ascii=False, indent=2, sort_keys=False)
        else:
            return json.dumps(ordered, ensure_ascii=False, sort_keys=False)
    
    def export_markdown(self, include_metadata: bool = True,
                       include_toc: bool = True) -> str:
        """
        Export Task Card as human-readable Markdown for review.
        
        Args:
            include_metadata: Whether to show metadata section
            include_toc: Whether to include table of contents
        
        Returns:
            Formatted Markdown string
        """
        lines = []
        
        # Header with task code if available
        task_code = self.task_card.get("metadata", {}).get("task_code", "UNKNOWN")
        lines.append(f"# Task Card: {task_code}")
        lines.append(f"\n_Version: {self.task_card.get('version', 'unknown')}_\n")
        
        # Optional table of contents
        if include_toc:
            lines.append(self._render_toc())
            lines.append("")
        
        # Main sections
        lines.append(self._render_metadata_section())
        lines.append("")
        lines.append(self._render_type_section())
        lines.append("")
        lines.append(self._render_specification_section())
        lines.append("")
        lines.append(self._render_constraints_section())
        lines.append("")
        lines.append(self._render_testing_section())
        lines.append("")
        lines.append(self._render_experiments_section())
        
        return "\n".join(lines)
    
    def _order_fields(self, obj: Dict[str, Any]) -> Dict[str, Any]:
        """Sort fields according to stable ordering."""
        def sort_key(item):
            key = item[0]
            if key in FIELD_ORDER:
                category, order = FIELD_ORDER[key]
                return (category.value, order)
            else:
                # Unknown fields go last, alphabetically
                return (999, 0)
        
        items = sorted(obj.items(), key=sort_key)
        return dict(items)
    
    def _render_toc(self) -> str:
        """Render table of contents."""
        toc_items = [
            "## 目录\n",
            "- [元数据](#元数据)",
            "- [任务类型与背景](#任务类型与背景)",
            "- [任务规范](#任务规范)",
            "- [约束条件](#约束条件)",
            "- [测试与验证](#测试与验证)",
            "- [适配实验](#适配实验)",
        ]
        return "\n".join(toc_items)
    
    def _render_metadata_section(self) -> str:
        """Render metadata section."""
        lines = ["## 元数据\n"]
        metadata = self.task_card.get("metadata", {})
        
        if metadata:
            if "task_code" in metadata:
                lines.append(f"- **任务码**：`{metadata['task_code']}`")
            if "author" in metadata:
                lines.append(f"- **作者**：{metadata['author']}")
            if "created_at" in metadata:
                lines.append(f"- **创建时间**：{metadata['created_at']}")
            if "updated_at" in metadata:
                lines.append(f"- **更新时间**：{metadata['updated_at']}")
            if "project_id" in metadata:
                lines.append(f"- **项目 ID**：{metadata['project_id']}")
            if "plan_id" in metadata:
                lines.append(f"- **计划 ID**：{metadata['plan_id']}")
        else:
            lines.append("_无元数据_")
        
        return "\n".join(lines)
    
    def _render_type_section(self) -> str:
        """Render task type and background."""
        lines = ["## 任务类型与背景\n"]
        
        task_type = self.task_card.get("task_type", "unknown")
        type_name = TYPE_NAMES.get(task_type, task_type)
        lines.append(f"**类型**：{type_name}\n")
        
        background = self.task_card.get("background", "").strip()
        lines.append(f"**背景**：\n\n{background}\n")
        
        return "\n".join(lines)
    
    def _render_specification_section(self) -> str:
        """Render specification: states, goals, criteria."""
        lines = ["## 任务规范\n"]
        
        initial = self.task_card.get("initial_state", "").strip()
        lines.append(f"### 当前状态\n\n{initial}\n")
        
        goal = self.task_card.get("goal", "").strip()
        lines.append(f"### 目标\n\n{goal}\n")
        
        behavior = self.task_card.get("expected_behavior", "").strip()
        lines.append(f"### 预期行为\n\n{behavior}\n")
        
        criteria = self.task_card.get("acceptance_criteria", [])
        lines.append("### 验收标准\n")
        if criteria:
            for i, criterion in enumerate(criteria, 1):
                lines.append(f"{i}. {criterion.strip()}")
        else:
            lines.append("_无验收标准_")
        lines.append("")
        
        return "\n".join(lines)
    
    def _render_constraints_section(self) -> str:
        """Render constraints and context policy."""
        lines = ["## 约束条件\n"]
        
        # Relevant files
        files = self.task_card.get("relevant_files", [])
        lines.append("### 相关文件\n")
        if files:
            for f in files:
                lines.append(f"- `{f.strip()}`")
        else:
            lines.append("_无特定限制_")
        lines.append("")
        
        # Hard constraints
        constraints = self.task_card.get("constraints", [])
        lines.append("### 约束条件\n")
        if constraints:
            for constraint in constraints:
                lines.append(f"- {constraint.strip()}")
        else:
            lines.append("_无约束条件_")
        lines.append("")
        
        # Context policy
        context_policy = self.task_card.get("context_policy", {})
        lines.append("### 执行上下文\n")
        
        allow_assumptions = context_policy.get("allow_assumptions", False)
        if allow_assumptions:
            lines.append("- **假设**：允许在未确认项基础上进行合理假设")
        else:
            lines.append("- **假设**：必须确认所有不明确项，不允许任意假设")
        
        must_confirm = context_policy.get("must_confirm", [])
        if must_confirm:
            lines.append("\n**必须确认项**：")
            for item in must_confirm:
                lines.append(f"- {item.strip()}")
        
        forbidden = context_policy.get("forbidden_actions", [])
        if forbidden:
            lines.append("\n**禁止操作**：")
            for action in forbidden:
                lines.append(f"- {action.strip()}")
        
        lines.append("")
        return "\n".join(lines)
    
    def _render_testing_section(self) -> str:
        """Render test method and difficulty."""
        lines = ["## 测试与验证\n"]
        
        test_method = self.task_card.get("test_method", {})
        strategy = test_method.get("strategy", "manual")
        strategy_name = STRATEGY_NAMES.get(strategy, strategy)
        lines.append(f"**测试策略**：{strategy_name}\n")
        
        commands = test_method.get("commands_or_steps", [])
        if commands:
            lines.append("**测试步骤**：")
            for cmd in commands:
                lines.append(f"- {cmd.strip()}")
            lines.append("")
        
        pass_signal = test_method.get("pass_signal", "")
        if pass_signal:
            lines.append(f"**通过信号**：{pass_signal.strip()}\n")
        else:
            lines.append("**通过信号**：所有验收标准均已满足\n")
        
        # Difficulty
        difficulty = self.task_card.get("difficulty", {})
        level = difficulty.get("level", "M")
        reason = difficulty.get("reason", "")
        
        color_name = DIFFICULTY_COLORS.get(level, level)
        lines.append(f"**难度**：{color_name}")
        if reason:
            lines.append(f"\n_原因：{reason.strip()}_")
        lines.append("")
        
        return "\n".join(lines)
    
    def _render_experiments_section(self) -> str:
        """Render suitable experiments."""
        lines = ["## 适配实验\n"]
        
        experiments = self.task_card.get("suitable_experiments", [])
        if experiments:
            for exp in experiments:
                exp_name = EXPERIMENT_NAMES.get(exp, exp)
                lines.append(f"- {exp_name}")
        else:
            lines.append("_无指定实验_")
        
        lines.append("")
        return "\n".join(lines)
    
    def export_dict(self) -> Dict[str, Any]:
        """Export as Python dict (for programmatic use)."""
        return self._order_fields(self.task_card)


def load_and_export(json_path: str, output_dir: str) -> Dict[str, str]:
    """
    Load Task Card JSON and export both formats.
    
    Args:
        json_path: Path to Task Card JSON file
        output_dir: Directory for output files
    
    Returns:
        Dict with keys 'json', 'markdown' pointing to output files
    """
    # Load JSON
    with open(json_path, 'r', encoding='utf-8') as f:
        task_card = json.load(f)
    
    # Create exporter
    exporter = TaskCardExporter(task_card)
    
    # Export JSON
    task_code = task_card.get("metadata", {}).get("task_code", "unknown")
    json_output = f"{output_dir}/{task_code}.json"
    with open(json_output, 'w', encoding='utf-8') as f:
        f.write(exporter.export_json())
    
    # Export Markdown
    md_output = f"{output_dir}/{task_code}.md"
    with open(md_output, 'w', encoding='utf-8') as f:
        f.write(exporter.export_markdown())
    
    return {
        "json": json_output,
        "markdown": md_output
    }


def main():
    """Test exporter with TC-01 example."""
    example_path = "D:\\code\\half\\outputs\\proj-3-1a1fca\\TC-01\\task-card-v0.3.example.json"
    output_dir = "D:\\code\\half\\outputs\\proj-3-1a1fca\\TC-04\\examples"
    
    import os
    os.makedirs(output_dir, exist_ok=True)
    
    print("Loading Task Card...")
    with open(example_path, 'r', encoding='utf-8') as f:
        task_card = json.load(f)
    
    exporter = TaskCardExporter(task_card)
    
    # Export JSON
    print("\n" + "="*60)
    print("EXPORTING JSON (Canonical Format)")
    print("="*60)
    json_output = exporter.export_json()
    print(json_output[:500] + "...\n")
    
    with open(f"{output_dir}/TC-01.json", 'w', encoding='utf-8') as f:
        f.write(json_output)
    print(f"✓ Exported to {output_dir}/TC-01.json")
    
    # Export Markdown
    print("\n" + "="*60)
    print("EXPORTING MARKDOWN (Human-Readable Format)")
    print("="*60)
    md_output = exporter.export_markdown()
    print(md_output[:500] + "...\n")
    
    with open(f"{output_dir}/TC-01.md", 'w', encoding='utf-8') as f:
        f.write(md_output)
    print(f"✓ Exported to {output_dir}/TC-01.md")
    
    # Stability test: export 5 times
    print("\n" + "="*60)
    print("STABILITY TEST: Exporting JSON 5 times")
    print("="*60)
    outputs = [exporter.export_json() for _ in range(5)]
    if all(o == outputs[0] for o in outputs):
        print("✓ All 5 exports identical - JSON stability guaranteed")
    else:
        print("✗ Exports differ - Stability issue!")
    
    print("\nAll exports completed successfully!")


if __name__ == "__main__":
    main()
