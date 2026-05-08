#!/usr/bin/env python3
"""
Integration examples demonstrating workflow/handoff/experiment with Task Card.
Shows how the three record types work together in a complete task lifecycle.
"""

import json
import sys
import os
from datetime import datetime

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(__file__))
from task_card_integration import (
    WorkflowIntegrationAPI,
    TaskCardRecordFactory,
    RecordType
)


def print_section(title):
    """Print section header."""
    print("\n" + "="*70)
    print(f"  {title}")
    print("="*70)


def example_complete_task_lifecycle():
    """
    Demonstrate a complete task lifecycle:
    1. Load Task Card
    2. Execute via Workflow
    3. Handoff for review
    4. Run experiment (stability test)
    """
    
    # Load Task Card
    tc_path = "D:\\code\\half\\outputs\\proj-3-1a1fca\\TC-01\\task-card-v0.3.example.json"
    
    print_section("TASK LIFECYCLE EXAMPLE")
    print("\n[*] Loading Task Card...")
    
    with open(tc_path, 'r', encoding='utf-8') as f:
        task_card = json.load(f)
    
    task_code = task_card.get("metadata", {}).get("task_code", "UNKNOWN")
    print(f"OK Loaded: {task_code}")
    print(f"  Type: {task_card.get('task_type')}")
    print(f"  Background: {task_card.get('background')[:50]}...")
    
    # =========================================================================
    # PHASE 1: WORKFLOW EXECUTION
    # =========================================================================
    print_section("PHASE 1: WORKFLOW EXECUTION")
    print("\n[1] Starting workflow execution...")
    
    workflow_result = WorkflowIntegrationAPI.start_workflow_execution(
        task_card,
        workflow_id="wf-prod-001",
        execution_id="exec-20260508-001",
        prompt_strategy="candidate_a"
    )
    
    print(f"OK Workflow started")
    print(f"  Execution ID: {workflow_result['execution_id']}")
    print(f"  Task Code: {workflow_result['task_code']}")
    
    validation = workflow_result['validation']
    valid_fields = sum(1 for v in validation.values() if v)
    print(f"  Validation: {valid_fields}/12 fields present OK")
    
    # Simulate workflow completion
    print("\n[2]  Simulating Agent execution...")
    print("  [Agent processing...]")
    print("  [Generating output...]")
    
    workflow_completion = WorkflowIntegrationAPI.complete_workflow_execution(
        workflow_result['record'],
        output_path=f"outputs/{task_code}/{workflow_result['execution_id']}/result.json",
        result_summary="All 3 acceptance criteria verified. Output quality: HIGH",
        success=True
    )
    
    print(f"OK Workflow completed")
    print(f"  Status: {workflow_completion['status']}")
    print(f"  Duration: {workflow_completion['duration_seconds']:.2f}s")
    
    # =========================================================================
    # PHASE 2: HANDOFF FOR REVIEW
    # =========================================================================
    print_section("PHASE 2: HANDOFF FOR REVIEW")
    print("\n[1]  Initiating handoff to human reviewer...")
    
    handoff_result = WorkflowIntegrationAPI.initiate_handoff(
        task_card,
        from_entity="executor_agent",
        to_entity="human_reviewer",
        handoff_reason="quality_review_required",
        export_format="both"
    )
    
    print(f"OK Handoff initiated")
    print(f"  From: {handoff_result['from']}")
    print(f"  To: {handoff_result['to']}")
    print(f"  Reason: {handoff_result['handoff_reason']}")
    print(f"  Exported format: both (JSON + Markdown)")
    
    # Simulate human review
    print("\n[2]  Simulating human review...")
    print("  [Reviewer examining JSON...]")
    print("  [Reviewer reviewing Markdown...]")
    print("  [Reviewer checking acceptance criteria...]")
    
    handoff_completion = WorkflowIntegrationAPI.complete_handoff(
        handoff_result['record'],
        decision="approved",
        decision_reason="Output meets all quality standards. Criteria verified.",
        notes="Ready for production deployment. No issues detected."
    )
    
    print(f"OK Handoff decision: {handoff_completion['decision']}")
    
    # =========================================================================
    # PHASE 3: EXPERIMENT (STABILITY TEST)
    # =========================================================================
    print_section("PHASE 3: EXPERIMENT (PROMPT STABILITY)")
    print("\n[1]  Starting stability experiment...")
    
    exp_result = WorkflowIntegrationAPI.start_experiment(
        task_card,
        experiment_type="prompt_stability",
        experiment_id="exp-stability-001",
        hypothesis="Candidate A produces identical prompts across multiple generations"
    )
    
    print(f"OK Experiment started")
    print(f"  ID: {exp_result['experiment_id']}")
    print(f"  Type: {exp_result['experiment_type']}")
    print(f"  Hypothesis: {exp_result['hypothesis'][:60]}...")
    
    # Simulate experiment execution
    print("\n[2]  Running stability test (100 generations)...")
    
    # In real scenario, this would generate 100 prompts and check stability
    print("  [Generating 100 prompts from same Task Card...]")
    print("  [Comparing outputs...]")
    print("  [Computing stability metrics...]")
    
    exp_completion = WorkflowIntegrationAPI.complete_experiment(
        exp_result['record'],
        metrics={
            "total_runs": 100,
            "identical_outputs": 100,
            "stability_score": 1.0,
            "variance": 0.0,
            "execution_time_avg_ms": 45.2
        },
        findings="All 100 generations produced bit-identical output. Zero variance observed.",
        conclusion="Candidate A is 100% stable. Suitable for production.",
        next_steps="Ready to replace current prompt generator in production"
    )
    
    print(f"OK Experiment completed")
    print(f"  Stability Score: {exp_completion['metrics']['stability_score']}")
    print(f"  Identical Outputs: {exp_completion['metrics']['identical_outputs']}/100")
    
    # =========================================================================
    # SUMMARY
    # =========================================================================
    print_section("SUMMARY: COMPLETE LIFECYCLE")
    
    print("\nSUCCESS Task Execution Summary:")
    print(f"  Task Code: {task_code}")
    print(f"  Workflow Status: {workflow_completion['status']}")
    print(f"  Handoff Decision: {handoff_completion['decision']}")
    print(f"  Experiment Conclusion: {exp_completion['metrics']['stability_score']:.0%} stable")
    
    print("\nMETRICS Metrics:")
    print(f"  Workflow Duration: {workflow_completion['duration_seconds']:.2f}s")
    print(f"  Experiment Runs: {exp_completion['metrics']['total_runs']}")
    print(f"  Stability Score: {exp_completion['metrics']['stability_score']:.2%}")
    
    print("\nRECORDS Records Generated:")
    print("  1. WorkflowExecutionRecord (workflow_execution)")
    print("  2. HandoffRecord (handoff)")
    print("  3. ExperimentRecord (experiment)")
    print("\n  All records include:")
    print("    - Unified minimal fields (task_code, checksum, verification)")
    print("    - Type-specific fields")
    print("    - Full traceability and audit trail")
    
    print("\nRESULT Result: Task Card successfully integrated across all three contexts!")


def example_minimal_fields_validation():
    """Demonstrate minimal fields validation."""
    
    print_section("MINIMAL FIELDS VALIDATION EXAMPLE")
    
    tc_path = "D:\\code\\half\\outputs\\proj-3-1a1fca\\TC-01\\task-card-v0.3.example.json"
    
    with open(tc_path, 'r', encoding='utf-8') as f:
        task_card = json.load(f)
    
    # Validate
    verification = TaskCardRecordFactory.validate_task_card(task_card)
    
    print("\nOK Validation Results:")
    for field, is_present in verification.items():
        status = "OK" if is_present else "✗"
        print(f"  {status} {field}")
    
    all_valid = all(verification.values())
    print(f"\nOverall: {'OK PASS' if all_valid else '✗ FAIL'} - {'All fields present' if all_valid else 'Missing fields'}")
    
    # Checksum
    checksum = TaskCardRecordFactory.compute_checksum(task_card)
    print(f"\nChecksum: {checksum[:16]}...")
    print(f"  (Full: {checksum})")
    print("  Used for change detection during record lifecycle")


def example_record_serialization():
    """Demonstrate record serialization."""
    
    print_section("RECORD SERIALIZATION EXAMPLE")
    
    tc_path = "D:\\code\\half\\outputs\\proj-3-1a1fca\\TC-01\\task-card-v0.3.example.json"
    
    with open(tc_path, 'r', encoding='utf-8') as f:
        task_card = json.load(f)
    
    # Create record
    record = TaskCardRecordFactory.create_workflow_record(
        task_card,
        workflow_id="wf-001",
        execution_id="exec-001"
    )
    
    # Serialize
    from task_card_integration import TaskCardRecordSerializer
    json_str = TaskCardRecordSerializer.record_to_json(record)
    
    print("\nOK Workflow Record Serialized to JSON:")
    print("\n" + json_str[:400] + "...\n")
    
    print(f"OK JSON size: {len(json_str)} bytes")
    print(f"OK Records are self-contained and can be stored/transmitted independently")


def main():
    """Run all examples."""
    print("\n")
    print("╔" + "="*68 + "╗")
    print("║" + " "*68 + "║")
    print("║" + "  Task Card Integration Examples".center(68) + "║")
    print("║" + "  Workflow / Handoff / Experiment".center(68) + "║")
    print("║" + " "*68 + "║")
    print("╚" + "="*68 + "╝")
    
    try:
        # Example 1: Complete lifecycle
        example_complete_task_lifecycle()
        
        # Example 2: Validation
        example_minimal_fields_validation()
        
        # Example 3: Serialization
        example_record_serialization()
        
        print_section("ALL EXAMPLES COMPLETED SUCCESSFULLY OK")
        print("\nRESULT Task Card integration provides:")
        print("  OK Unified input unit across workflow/handoff/experiment")
        print("  OK Minimal required fields ensuring consistency")
        print("  OK Change detection via checksum")
        print("  OK Complete audit trail")
        print("  OK Backward compatibility with existing systems")
        
    except Exception as e:
        print(f"\nERROR Error: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
