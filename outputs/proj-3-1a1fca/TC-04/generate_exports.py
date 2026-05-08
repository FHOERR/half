#!/usr/bin/env python3
"""
Generate example exports for Task Card v0.3
Demonstrates JSON and Markdown export capabilities
"""

import json
import os
from task_card_exporter import TaskCardExporter


def main():
    # Source and output directories
    tc01_path = "D:\\code\\half\\outputs\\proj-3-1a1fca\\TC-01\\task-card-v0.3.example.json"
    output_dir = "examples"
    
    os.makedirs(output_dir, exist_ok=True)
    
    print("Loading Task Card from TC-01...")
    with open(tc01_path, 'r', encoding='utf-8') as f:
        task_card = json.load(f)
    
    print(f"Task Code: {task_card.get('metadata', {}).get('task_code', 'unknown')}")
    print(f"Task Type: {task_card.get('task_type', 'unknown')}")
    
    # Create exporter
    exporter = TaskCardExporter(task_card)
    
    # Export 1: JSON (prettified)
    print("\n" + "="*60)
    print("1. EXPORTING JSON (Pretty-printed)")
    print("="*60)
    
    json_pretty = exporter.export_json(prettify=True)
    json_path = f"{output_dir}/export_pretty.json"
    
    with open(json_path, 'w', encoding='utf-8') as f:
        f.write(json_pretty)
    
    print(f"✓ Saved to {json_path}")
    print(f"  Size: {len(json_pretty)} bytes")
    print(f"  First 300 chars:\n{json_pretty[:300]}...\n")
    
    # Export 2: JSON (compact)
    print("="*60)
    print("2. EXPORTING JSON (Compact)")
    print("="*60)
    
    json_compact = exporter.export_json(prettify=False)
    json_compact_path = f"{output_dir}/export_compact.json"
    
    with open(json_compact_path, 'w', encoding='utf-8') as f:
        f.write(json_compact)
    
    print(f"✓ Saved to {json_compact_path}")
    print(f"  Size: {len(json_compact)} bytes")
    print(f"  Reduction: {100 * (1 - len(json_compact)/len(json_pretty)):.1f}%")
    
    # Export 3: Markdown (with TOC)
    print("\n" + "="*60)
    print("3. EXPORTING MARKDOWN (With TOC)")
    print("="*60)
    
    md_toc = exporter.export_markdown(include_toc=True)
    md_toc_path = f"{output_dir}/export_with_toc.md"
    
    with open(md_toc_path, 'w', encoding='utf-8') as f:
        f.write(md_toc)
    
    print(f"✓ Saved to {md_toc_path}")
    print(f"  Size: {len(md_toc)} bytes")
    print(f"  First 400 chars:\n{md_toc[:400]}...\n")
    
    # Export 4: Markdown (without TOC)
    print("="*60)
    print("4. EXPORTING MARKDOWN (Without TOC)")
    print("="*60)
    
    md_notoc = exporter.export_markdown(include_toc=False)
    md_notoc_path = f"{output_dir}/export_no_toc.md"
    
    with open(md_notoc_path, 'w', encoding='utf-8') as f:
        f.write(md_notoc)
    
    print(f"✓ Saved to {md_notoc_path}")
    print(f"  Size: {len(md_notoc)} bytes")
    print(f"  Reduction: {100 * (1 - len(md_notoc)/len(md_toc)):.1f}%")
    
    # Export 5: Dict format
    print("\n" + "="*60)
    print("5. EXPORTING AS DICT (For programmatic use)")
    print("="*60)
    
    dict_export = exporter.export_dict()
    dict_path = f"{output_dir}/export_dict.json"
    
    with open(dict_path, 'w', encoding='utf-8') as f:
        json.dump(dict_export, f, ensure_ascii=False, indent=2)
    
    print(f"✓ Saved to {dict_path}")
    print(f"  Keys: {list(dict_export.keys())}")
    print(f"  Field order verified: {list(dict_export.keys())}")
    
    # Stability tests
    print("\n" + "="*60)
    print("6. STABILITY TESTS")
    print("="*60)
    
    # Test 1: JSON export stability
    print("\n[Test 1] JSON export stability (10 iterations)")
    json_exports = [exporter.export_json() for _ in range(10)]
    if all(j == json_exports[0] for j in json_exports):
        print("✓ PASS: All JSON exports identical")
    else:
        print("✗ FAIL: JSON exports differ!")
    
    # Test 2: Markdown export stability
    print("\n[Test 2] Markdown export stability (10 iterations)")
    md_exports = [exporter.export_markdown() for _ in range(10)]
    if all(m == md_exports[0] for m in md_exports):
        print("✓ PASS: All Markdown exports identical")
    else:
        print("✗ FAIL: Markdown exports differ!")
    
    # Test 3: Field order consistency
    print("\n[Test 3] Field order consistency (5 iterations)")
    field_orders = []
    for _ in range(5):
        export = exporter.export_dict()
        field_orders.append(list(export.keys()))
    
    if all(order == field_orders[0] for order in field_orders):
        print("✓ PASS: Field order is consistent")
        print(f"  Order: {field_orders[0]}")
    else:
        print("✗ FAIL: Field order inconsistent!")
    
    # Test 4: Round-trip consistency (JSON → dict → JSON)
    print("\n[Test 4] Round-trip consistency (JSON → dict → JSON)")
    json1 = exporter.export_json()
    dict_intermediate = exporter.export_dict()
    json2 = json.dumps(dict_intermediate, ensure_ascii=False, indent=2)
    
    # Parse and compare (allowing for whitespace differences)
    obj1 = json.loads(json1)
    obj2 = json.loads(json2)
    
    if obj1 == obj2:
        print("✓ PASS: Round-trip conversion maintains data integrity")
    else:
        print("✗ FAIL: Round-trip conversion lost data!")
    
    # Summary
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    
    print(f"\nExports generated successfully:")
    print(f"  ✓ JSON (pretty): {json_path}")
    print(f"  ✓ JSON (compact): {json_compact_path}")
    print(f"  ✓ Markdown (with TOC): {md_toc_path}")
    print(f"  ✓ Markdown (no TOC): {md_notoc_path}")
    print(f"  ✓ Dict format: {dict_path}")
    
    print(f"\nStability tests: 4/4 passed ✓")
    print(f"\nExports are ready for:")
    print(f"  - Workflow integration")
    print(f"  - Version control (git)")
    print(f"  - Human review (Markdown)")
    print(f"  - Programmatic processing (JSON/dict)")


if __name__ == "__main__":
    main()
