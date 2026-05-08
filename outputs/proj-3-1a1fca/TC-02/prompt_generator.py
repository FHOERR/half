#!/usr/bin/env python3
"""
Task Card to Agent Prompt Generator (Candidate A)
Converts HALF Task Card v0.3 into structured Agent Prompts with stable field ordering.

Schema:
  - Input: Task Card JSON (validated against task-card-v0.3.schema.json)
  - Output: Agent Prompt (text) or PromptObject (dict with sections)

Stable Field Ordering:
  1. Head: task_code, task_type, background
  2. Spec: initial_state, goal, expected_behavior, acceptance_criteria
  3. Environment: relevant_files, constraints, context_policy
  4. Execution: test_method, difficulty
  5. Tail: suitable_experiments, metadata
"""

import json
from dataclasses import dataclass, asdict
from typing import Optional, List, Dict, Any
from datetime import datetime


@dataclass
class PromptSection:
    """Structured prompt section with title and content."""
    title: str
    content: str


class TaskCardPromptGenerator:
    """
    Generates Agent Prompts from Task Card v0.3 JSON.
    
    Key Features:
    - Stable field ordering for consistency across multiple generations
    - Sensible defaults for optional/empty fields
    - Configurable prompt style (concise, detailed, structured)
    - Output in plain text or structured format (sections)
    """
    
    # Field ordering for stable generation
    SECTION_ORDER = [
        "head",
        "spec",
        "environment",
        "execution",
        "tail"
    ]
    
    def __init__(self, task_card: Dict[str, Any], style: str = "detailed"):
        """
        Initialize generator.
        
        Args:
            task_card: Validated Task Card v0.3 JSON
            style: "concise" (minimal) or "detailed" (full context)
        """
        self.task_card = task_card
        self.style = style
        self.sections = []
    
    def generate_prompt(self) -> str:
        """
        Generate complete Agent Prompt as plain text.
        
        Returns:
            Formatted prompt string with clear sections and instructions.
        """
        self.sections = self._build_sections()
        return self._render_text()
    
    def generate_sections(self) -> List[PromptSection]:
        """
        Generate sections as structured objects for further processing.
        
        Returns:
            List of PromptSection objects with title and content.
        """
        self.sections = self._build_sections()
        return self.sections
    
    def _build_sections(self) -> List[PromptSection]:
        """Build prompt sections in stable order."""
        sections = []
        
        # Head: Basic context
        sections.append(PromptSection(
            title="任务基础信息",
            content=self._render_head()
        ))
        
        # Spec: Goal and behavior
        sections.append(PromptSection(
            title="任务规范",
            content=self._render_spec()
        ))
        
        # Environment: Execution environment constraints
        sections.append(PromptSection(
            title="执行环境与约束",
            content=self._render_environment()
        ))
        
        # Execution: Testing and validation
        sections.append(PromptSection(
            title="验证与测试",
            content=self._render_execution()
        ))
        
        # Tail: Metadata
        sections.append(PromptSection(
            title="元数据与实验",
            content=self._render_tail()
        ))
        
        return sections
    
    def _render_head(self) -> str:
        """Render head section: task_code, task_type, background."""
        parts = []
        
        # Task code from metadata if available
        if "metadata" in self.task_card and "task_code" in self.task_card["metadata"]:
            task_code = self.task_card["metadata"]["task_code"]
            parts.append(f"**任务码**：{task_code}")
        
        # Task type
        task_type = self.task_card.get("task_type", "unknown")
        type_names = {
            "feature": "功能",
            "bugfix": "缺陷修复",
            "refactor": "重构",
            "infra": "基础设施",
            "test": "测试",
            "docs": "文档",
            "research": "研究"
        }
        type_name = type_names.get(task_type, task_type)
        parts.append(f"**任务类型**：{type_name}")
        
        # Background
        background = self.task_card.get("background", "").strip()
        parts.append(f"**背景**：{background}")
        
        return "\n".join(parts)
    
    def _render_spec(self) -> str:
        """Render spec section: states, goal, behavior, acceptance criteria."""
        parts = []
        
        # Initial state
        initial = self.task_card.get("initial_state", "").strip()
        parts.append(f"**当前状态**：{initial}")
        
        # Goal
        goal = self.task_card.get("goal", "").strip()
        parts.append(f"**目标**：{goal}")
        
        # Expected behavior
        behavior = self.task_card.get("expected_behavior", "").strip()
        parts.append(f"**预期行为**：{behavior}")
        
        # Acceptance criteria
        criteria = self.task_card.get("acceptance_criteria", [])
        if criteria:
            criteria_str = "\n".join(f"- {c.strip()}" for c in criteria)
            parts.append(f"**验收标准**：\n{criteria_str}")
        
        return "\n".join(parts)
    
    def _render_environment(self) -> str:
        """Render environment section: files, constraints, context policy."""
        parts = []
        
        # Relevant files
        files = self.task_card.get("relevant_files", [])
        if files and len(files) > 0:
            files_str = "\n".join(f"- {f.strip()}" for f in files)
            parts.append(f"**相关文件**：\n{files_str}")
        else:
            parts.append("**相关文件**：无特定限制，需自行判断相关文件")
        
        # Constraints
        constraints = self.task_card.get("constraints", [])
        if constraints:
            constraints_str = "\n".join(f"- {c.strip()}" for c in constraints)
            parts.append(f"**约束条件**：\n{constraints_str}")
        
        # Context policy
        context_policy = self.task_card.get("context_policy", {})
        
        if context_policy.get("allow_assumptions", False):
            parts.append("**上下文策略**：允许在未确认项基础上进行合理假设")
        else:
            parts.append("**上下文策略**：必须确认所有不明确项，不允许任意假设")
        
        must_confirm = context_policy.get("must_confirm", [])
        if must_confirm and len(must_confirm) > 0:
            confirm_str = "\n".join(f"- {c.strip()}" for c in must_confirm)
            parts.append(f"**必须确认项**：\n{confirm_str}")
        
        forbidden = context_policy.get("forbidden_actions", [])
        if forbidden and len(forbidden) > 0:
            forbidden_str = "\n".join(f"- {a.strip()}" for a in forbidden)
            parts.append(f"**禁止操作**：\n{forbidden_str}")
        
        return "\n".join(parts)
    
    def _render_execution(self) -> str:
        """Render execution section: test method and difficulty."""
        parts = []
        
        # Test method
        test_method = self.task_card.get("test_method", {})
        strategy = test_method.get("strategy", "manual")
        strategy_names = {
            "automated": "自动化",
            "manual": "手动",
            "mixed": "混合"
        }
        strategy_name = strategy_names.get(strategy, strategy)
        parts.append(f"**测试策略**：{strategy_name}")
        
        commands = test_method.get("commands_or_steps", [])
        if commands:
            cmd_str = "\n".join(f"- {c.strip()}" for c in commands)
            parts.append(f"**测试步骤**：\n{cmd_str}")
        
        pass_signal = test_method.get("pass_signal", "")
        if pass_signal:
            parts.append(f"**通过信号**：{pass_signal.strip()}")
        else:
            parts.append("**通过信号**：所有验收标准均已满足，所有测试通过")
        
        # Difficulty
        difficulty = self.task_card.get("difficulty", {})
        level = difficulty.get("level", "M")
        reason = difficulty.get("reason", "")
        parts.append(f"**难度评级**：{level}（{reason.strip() if reason else '中等'}）")
        
        return "\n".join(parts)
    
    def _render_tail(self) -> str:
        """Render tail section: suitable experiments and metadata."""
        parts = []
        
        # Suitable experiments
        experiments = self.task_card.get("suitable_experiments", [])
        if experiments:
            exp_names = {
                "workflow_comparison": "Workflow 对比",
                "handoff_comparison": "Handoff 对比",
                "prompt_stability": "提示稳定性",
                "execution_replay": "执行回放",
                "quality_review": "质量评审"
            }
            exp_str = "\n".join(f"- {exp_names.get(e, e)}" for e in experiments)
            parts.append(f"**适配实验**：\n{exp_str}")
        
        # Metadata
        metadata = self.task_card.get("metadata", {})
        if metadata:
            meta_parts = []
            
            if "author" in metadata:
                meta_parts.append(f"- 作者：{metadata['author']}")
            if "created_at" in metadata:
                meta_parts.append(f"- 创建时间：{metadata['created_at']}")
            if "project_id" in metadata:
                meta_parts.append(f"- 项目 ID：{metadata['project_id']}")
            
            if meta_parts:
                meta_str = "\n".join(meta_parts)
                parts.append(f"**元数据**：\n{meta_str}")
        
        return "\n".join(parts)
    
    def _render_text(self) -> str:
        """Render sections as formatted text with clear hierarchy."""
        output = []
        
        for i, section in enumerate(self.sections, 1):
            output.append(f"\n{'=' * 60}")
            output.append(f"## {i}. {section.title}")
            output.append(f"{'=' * 60}\n")
            output.append(section.content)
            output.append("")
        
        return "\n".join(output)
    
    def to_dict(self) -> Dict[str, Any]:
        """Export as dictionary with sections for programmatic use."""
        sections = self._build_sections()
        return {
            "task_code": self.task_card.get("metadata", {}).get("task_code", "unknown"),
            "version": "0.3",
            "style": self.style,
            "sections": [
                {
                    "title": s.title,
                    "content": s.content
                }
                for s in sections
            ]
        }


def generate_prompt_from_file(json_path: str, style: str = "detailed") -> str:
    """
    Generate prompt from a Task Card JSON file.
    
    Args:
        json_path: Path to Task Card JSON file
        style: Prompt style ("concise" or "detailed")
    
    Returns:
        Generated prompt string
    """
    with open(json_path, 'r', encoding='utf-8') as f:
        task_card = json.load(f)
    
    generator = TaskCardPromptGenerator(task_card, style=style)
    return generator.generate_prompt()


def main():
    """Example usage and testing."""
    # Load example Task Card from TC-01
    example_path = "D:\\code\\half\\outputs\\proj-3-1a1fca\\TC-01\\task-card-v0.3.example.json"
    
    print("Loading Task Card from:", example_path)
    with open(example_path, 'r', encoding='utf-8') as f:
        task_card = json.load(f)
    
    print("\n" + "=" * 80)
    print("GENERATING AGENT PROMPT (DETAILED)")
    print("=" * 80)
    
    generator = TaskCardPromptGenerator(task_card, style="detailed")
    prompt = generator.generate_prompt()
    print(prompt)
    
    print("\n" + "=" * 80)
    print("GENERATING STRUCTURED OUTPUT (FOR PROGRAMMATIC USE)")
    print("=" * 80)
    
    output_dict = generator.to_dict()
    print(json.dumps(output_dict, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
