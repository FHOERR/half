#!/usr/bin/env python3
"""
Task Card Integration for Workflow / Handoff / Experiment Recording

This module provides unified integration points for:
1. Workflow execution pipeline
2. Handoff communication
3. Experiment result recording

Goal: Make Task Card the canonical input unit across all these contexts.
"""

import json
import hashlib
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from enum import Enum


class RecordType(Enum):
    """Type of record: workflow execution, handoff, or experiment."""
    WORKFLOW_EXECUTION = "workflow_execution"
    HANDOFF = "handoff"
    EXPERIMENT = "experiment"


@dataclass
class MinimalRecordFields:
    """
    Minimal required fields for all record types.
    Ensures consistency across workflow/handoff/experiment contexts.
    """
    task_code: str
    task_card_version: str  # Should be "0.3"
    record_type: str  # RecordType enum value
    created_at: str  # ISO 8601 timestamp
    agent_or_person: str  # Who created this record
    status: str  # pending, in_progress, completed, failed
    
    # Checksum for detecting changes in source Task Card
    task_card_checksum: str  # SHA256 of original Task Card JSON
    
    # Required fields that must be present in Task Card
    verification_checklist: Dict[str, bool]  # Track which fields were validated


@dataclass
class WorkflowExecutionRecord:
    """Record for workflow task execution."""
    minimal_fields: MinimalRecordFields
    
    # Workflow-specific fields
    workflow_id: str
    execution_id: str
    prompt_strategy: str  # "candidate_a" or "candidate_b"
    generated_prompt: Optional[str]  # The actual Prompt used
    agent_version: str
    
    # Execution details
    start_time: str
    end_time: Optional[str]
    duration_seconds: Optional[float]
    
    # Output tracking
    output_path: str
    result_summary: Optional[str]
    success: bool
    error_message: Optional[str]


@dataclass
class HandoffRecord:
    """Record for handoff communication."""
    minimal_fields: MinimalRecordFields
    
    # Handoff-specific fields
    from_entity: str  # e.g., "initial_agent", "reviewer", "qa_engineer"
    to_entity: str
    handoff_reason: str  # e.g., "review_completed", "needs_expert", "high_complexity"
    
    # Communication
    exported_format: str  # "json", "markdown", or "both"
    exported_files: List[str]
    notes: str
    
    # Decision tracking
    decision: str  # "approved", "needs_revision", "escalated", "closed"
    decision_reason: Optional[str]


@dataclass
class ExperimentRecord:
    """Record for experiment (workflow comparison, stability testing, etc.)"""
    minimal_fields: MinimalRecordFields
    
    # Experiment-specific fields
    experiment_type: str  # From Task Card suitable_experiments
    experiment_id: str
    hypothesis: str
    
    # Comparison metrics (for workflow_comparison, prompt_stability, etc.)
    metrics: Dict[str, Any]  # Flexible dict for different experiment types
    
    # Results
    findings: str
    conclusion: str
    next_steps: Optional[str]


class TaskCardRecordFactory:
    """
    Factory for creating unified records from Task Cards.
    
    Ensures all records:
    1. Have consistent minimal fields
    2. Validate Task Card completeness
    3. Generate stable checksums for change detection
    4. Support the three record types uniformly
    """
    
    REQUIRED_FIELDS = {
        "task_type", "background", "goal", "initial_state", "expected_behavior",
        "acceptance_criteria", "relevant_files", "constraints", "test_method",
        "difficulty", "context_policy", "suitable_experiments"
    }
    
    @staticmethod
    def validate_task_card(task_card: Dict[str, Any]) -> Dict[str, bool]:
        """
        Validate that Task Card has all required fields.
        
        Returns:
            Dict mapping field names to validation status (True = present)
        """
        verification = {}
        for field in TaskCardRecordFactory.REQUIRED_FIELDS:
            verification[field] = field in task_card
        return verification
    
    @staticmethod
    def compute_checksum(task_card: Dict[str, Any]) -> str:
        """
        Compute stable checksum of Task Card for change detection.
        
        Returns:
            SHA256 hex digest
        """
        # Serialize with stable ordering for deterministic hash
        json_str = json.dumps(task_card, sort_keys=True, ensure_ascii=False)
        return hashlib.sha256(json_str.encode('utf-8')).hexdigest()
    
    @staticmethod
    def create_minimal_fields(
        task_card: Dict[str, Any],
        record_type: RecordType,
        agent_or_person: str
    ) -> MinimalRecordFields:
        """Create minimal fields common to all record types."""
        task_code = task_card.get("metadata", {}).get("task_code", "UNKNOWN")
        
        return MinimalRecordFields(
            task_code=task_code,
            task_card_version=task_card.get("version", "0.3"),
            record_type=record_type.value,
            created_at=datetime.now().isoformat(timespec='seconds'),
            agent_or_person=agent_or_person,
            status="pending",
            task_card_checksum=TaskCardRecordFactory.compute_checksum(task_card),
            verification_checklist=TaskCardRecordFactory.validate_task_card(task_card)
        )
    
    @staticmethod
    def create_workflow_record(
        task_card: Dict[str, Any],
        workflow_id: str,
        execution_id: str,
        prompt_strategy: str = "candidate_a",
        agent_version: str = "1.0",
        agent_name: str = "agent"
    ) -> WorkflowExecutionRecord:
        """
        Create workflow execution record.
        
        Args:
            task_card: Task Card v0.3 JSON
            workflow_id: Unique workflow identifier
            execution_id: Unique execution run identifier
            prompt_strategy: Which Prompt generation strategy was used
            agent_version: Agent software version
            agent_name: Name of executing agent
        
        Returns:
            WorkflowExecutionRecord with minimal fields initialized
        """
        minimal = TaskCardRecordFactory.create_minimal_fields(
            task_card,
            RecordType.WORKFLOW_EXECUTION,
            agent_name
        )
        
        return WorkflowExecutionRecord(
            minimal_fields=minimal,
            workflow_id=workflow_id,
            execution_id=execution_id,
            prompt_strategy=prompt_strategy,
            generated_prompt=None,  # Set after Prompt generation
            agent_version=agent_version,
            start_time=datetime.now().isoformat(timespec='seconds'),
            end_time=None,
            duration_seconds=None,
            output_path="",
            result_summary=None,
            success=False,
            error_message=None
        )
    
    @staticmethod
    def create_handoff_record(
        task_card: Dict[str, Any],
        from_entity: str,
        to_entity: str,
        handoff_reason: str,
        person_name: str = "reviewer"
    ) -> HandoffRecord:
        """
        Create handoff communication record.
        
        Args:
            task_card: Task Card v0.3 JSON
            from_entity: Source (e.g., "initial_agent")
            to_entity: Destination (e.g., "human_reviewer")
            handoff_reason: Why handoff is happening
            person_name: Who is conducting the handoff
        
        Returns:
            HandoffRecord initialized and ready for population
        """
        minimal = TaskCardRecordFactory.create_minimal_fields(
            task_card,
            RecordType.HANDOFF,
            person_name
        )
        
        return HandoffRecord(
            minimal_fields=minimal,
            from_entity=from_entity,
            to_entity=to_entity,
            handoff_reason=handoff_reason,
            exported_format="both",  # Default: export both JSON and Markdown
            exported_files=[],  # Populate during handoff
            notes="",
            decision="pending",
            decision_reason=None
        )
    
    @staticmethod
    def create_experiment_record(
        task_card: Dict[str, Any],
        experiment_type: str,
        experiment_id: str,
        hypothesis: str,
        person_name: str = "researcher"
    ) -> ExperimentRecord:
        """
        Create experiment record for scientific testing.
        
        Args:
            task_card: Task Card v0.3 JSON
            experiment_type: Type from suitable_experiments (e.g., "prompt_stability")
            experiment_id: Unique experiment identifier
            hypothesis: What we're testing
            person_name: Who is running the experiment
        
        Returns:
            ExperimentRecord initialized and ready for results
        """
        minimal = TaskCardRecordFactory.create_minimal_fields(
            task_card,
            RecordType.EXPERIMENT,
            person_name
        )
        
        return ExperimentRecord(
            minimal_fields=minimal,
            experiment_type=experiment_type,
            experiment_id=experiment_id,
            hypothesis=hypothesis,
            metrics={},  # Populate during experiment
            findings="",
            conclusion="",
            next_steps=None
        )


class TaskCardRecordSerializer:
    """
    Serialize/deserialize records to/from JSON with validation.
    
    Ensures records maintain consistency and can be stored in databases
    or passed between systems reliably.
    """
    
    @staticmethod
    def record_to_json(record: Any) -> str:
        """
        Convert any record type to JSON string.
        
        Handles dataclasses and nested objects.
        """
        def encoder(obj):
            if hasattr(obj, '__dataclass_fields__'):
                return asdict(obj)
            elif isinstance(obj, Enum):
                return obj.value
            raise TypeError(f"Object of type {type(obj)} is not JSON serializable")
        
        return json.dumps(record, default=encoder, ensure_ascii=False, indent=2)
    
    @staticmethod
    def json_to_record(json_str: str, record_type: RecordType) -> Dict[str, Any]:
        """
        Parse JSON string back to record dict.
        
        Note: Returns dict, not dataclass instance, for flexibility.
        """
        data = json.loads(json_str)
        
        # Basic validation
        minimal = data.get("minimal_fields", {})
        if minimal.get("record_type") != record_type.value:
            raise ValueError(f"Record type mismatch: expected {record_type.value}, got {minimal.get('record_type')}")
        
        return data


class WorkflowIntegrationAPI:
    """
    High-level API for integrating Task Card into workflow systems.
    
    Provides simplified interfaces for:
    1. Starting workflow execution
    2. Handoff communication
    3. Experiment recording
    """
    
    @staticmethod
    def start_workflow_execution(
        task_card: Dict[str, Any],
        workflow_id: str,
        execution_id: str,
        prompt_strategy: str = "candidate_a"
    ) -> Dict[str, Any]:
        """
        Start a workflow execution with Task Card.
        
        Returns:
            Dict with workflow context and record
        """
        record = TaskCardRecordFactory.create_workflow_record(
            task_card,
            workflow_id,
            execution_id,
            prompt_strategy=prompt_strategy
        )
        
        record.minimal_fields.status = "in_progress"
        
        return {
            "workflow_id": workflow_id,
            "execution_id": execution_id,
            "task_code": record.minimal_fields.task_code,
            "record": TaskCardRecordSerializer.record_to_json(record),
            "validation": record.minimal_fields.verification_checklist
        }
    
    @staticmethod
    def complete_workflow_execution(
        record_json: str,
        output_path: str,
        result_summary: str,
        success: bool,
        error_message: Optional[str] = None
    ) -> Dict[str, Any]:
        """Complete workflow execution and create final record."""
        record_data = json.loads(record_json)
        
        # Update execution details
        end_time = datetime.now().isoformat(timespec='seconds')
        start_time = datetime.fromisoformat(record_data["start_time"])
        end_datetime = datetime.fromisoformat(end_time)
        duration = (end_datetime - start_time).total_seconds()
        
        record_data["end_time"] = end_time
        record_data["duration_seconds"] = duration
        record_data["output_path"] = output_path
        record_data["result_summary"] = result_summary
        record_data["success"] = success
        record_data["error_message"] = error_message
        record_data["minimal_fields"]["status"] = "completed" if success else "failed"
        
        return {
            "status": "completed" if success else "failed",
            "duration_seconds": duration,
            "record": json.dumps(record_data, ensure_ascii=False, indent=2)
        }
    
    @staticmethod
    def initiate_handoff(
        task_card: Dict[str, Any],
        from_entity: str,
        to_entity: str,
        handoff_reason: str,
        export_format: str = "both"
    ) -> Dict[str, Any]:
        """
        Initiate handoff with Task Card.
        
        Args:
            export_format: "json", "markdown", or "both"
        """
        record = TaskCardRecordFactory.create_handoff_record(
            task_card,
            from_entity,
            to_entity,
            handoff_reason
        )
        
        record.exported_format = export_format
        record.minimal_fields.status = "in_progress"
        
        return {
            "from": from_entity,
            "to": to_entity,
            "task_code": record.minimal_fields.task_code,
            "handoff_reason": handoff_reason,
            "record": TaskCardRecordSerializer.record_to_json(record),
            "validation": record.minimal_fields.verification_checklist
        }
    
    @staticmethod
    def complete_handoff(
        record_json: str,
        decision: str,  # "approved", "needs_revision", "escalated", "closed"
        decision_reason: Optional[str] = None,
        notes: str = ""
    ) -> Dict[str, Any]:
        """Complete handoff with decision."""
        record_data = json.loads(record_json)
        
        record_data["decision"] = decision
        record_data["decision_reason"] = decision_reason
        record_data["notes"] = notes
        record_data["minimal_fields"]["status"] = "completed"
        
        return {
            "decision": decision,
            "record": json.dumps(record_data, ensure_ascii=False, indent=2)
        }
    
    @staticmethod
    def start_experiment(
        task_card: Dict[str, Any],
        experiment_type: str,
        experiment_id: str,
        hypothesis: str
    ) -> Dict[str, Any]:
        """Start experiment recording."""
        record = TaskCardRecordFactory.create_experiment_record(
            task_card,
            experiment_type,
            experiment_id,
            hypothesis
        )
        
        record.minimal_fields.status = "in_progress"
        
        return {
            "experiment_id": experiment_id,
            "experiment_type": experiment_type,
            "task_code": record.minimal_fields.task_code,
            "hypothesis": hypothesis,
            "record": TaskCardRecordSerializer.record_to_json(record),
            "validation": record.minimal_fields.verification_checklist
        }
    
    @staticmethod
    def complete_experiment(
        record_json: str,
        metrics: Dict[str, Any],
        findings: str,
        conclusion: str,
        next_steps: Optional[str] = None
    ) -> Dict[str, Any]:
        """Complete experiment recording."""
        record_data = json.loads(record_json)
        
        record_data["metrics"] = metrics
        record_data["findings"] = findings
        record_data["conclusion"] = conclusion
        record_data["next_steps"] = next_steps
        record_data["minimal_fields"]["status"] = "completed"
        
        return {
            "status": "completed",
            "metrics": metrics,
            "record": json.dumps(record_data, ensure_ascii=False, indent=2)
        }


def main():
    """Demonstrate integration API usage."""
    # Load example Task Card
    tc_path = "D:\\code\\half\\outputs\\proj-3-1a1fca\\TC-01\\task-card-v0.3.example.json"
    
    print("Loading Task Card...")
    with open(tc_path, 'r', encoding='utf-8') as f:
        task_card = json.load(f)
    
    print("\n" + "="*60)
    print("1. WORKFLOW EXECUTION RECORD")
    print("="*60)
    
    # Start workflow
    workflow_result = WorkflowIntegrationAPI.start_workflow_execution(
        task_card,
        workflow_id="wf-001",
        execution_id="exec-001",
        prompt_strategy="candidate_a"
    )
    
    print(f"✓ Workflow started: {workflow_result['execution_id']}")
    print(f"  Task Code: {workflow_result['task_code']}")
    print(f"  Validation: {sum(workflow_result['validation'].values())}/{len(workflow_result['validation'])} fields")
    
    # Complete workflow
    completion = WorkflowIntegrationAPI.complete_workflow_execution(
        workflow_result['record'],
        output_path="outputs/exec-001/result.json",
        result_summary="All acceptance criteria met",
        success=True
    )
    
    print(f"✓ Workflow completed in {completion['duration_seconds']:.2f} seconds")
    
    print("\n" + "="*60)
    print("2. HANDOFF RECORD")
    print("="*60)
    
    # Initiate handoff
    handoff_result = WorkflowIntegrationAPI.initiate_handoff(
        task_card,
        from_entity="executor_agent",
        to_entity="human_reviewer",
        handoff_reason="quality_review_required",
        export_format="both"
    )
    
    print(f"✓ Handoff initiated: {handoff_result['from']} → {handoff_result['to']}")
    print(f"  Reason: {handoff_result['handoff_reason']}")
    
    # Complete handoff
    handoff_completion = WorkflowIntegrationAPI.complete_handoff(
        handoff_result['record'],
        decision="approved",
        decision_reason="Output meets quality standards"
    )
    
    print(f"✓ Handoff decision: {handoff_completion['decision']}")
    
    print("\n" + "="*60)
    print("3. EXPERIMENT RECORD")
    print("="*60)
    
    # Start experiment
    exp_result = WorkflowIntegrationAPI.start_experiment(
        task_card,
        experiment_type="prompt_stability",
        experiment_id="exp-001",
        hypothesis="Candidate A produces stable prompts across 100 generations"
    )
    
    print(f"✓ Experiment started: {exp_result['experiment_id']}")
    print(f"  Type: {exp_result['experiment_type']}")
    print(f"  Hypothesis: {exp_result['hypothesis']}")
    
    # Complete experiment
    exp_completion = WorkflowIntegrationAPI.complete_experiment(
        exp_result['record'],
        metrics={"stability_score": 1.0, "runs": 100, "identical_outputs": 100},
        findings="All 100 generations produced identical output",
        conclusion="Candidate A is 100% stable",
        next_steps="Ready for production"
    )
    
    print(f"✓ Experiment completed")
    print(f"  Stability Score: {exp_completion['metrics']['stability_score']}")


if __name__ == "__main__":
    main()
