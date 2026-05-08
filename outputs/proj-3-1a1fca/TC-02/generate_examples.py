#!/usr/bin/env python3
"""
Generate example prompts for TC-01 Task Card using different styles.
Demonstrates the stability and flexibility of the generator.
"""

import json
import os
from prompt_generator import TaskCardPromptGenerator


def main():
    # Load example Task Card
    example_path = "D:\\code\\half\\outputs\\proj-3-1a1fca\\TC-01\\task-card-v0.3.example.json"
    output_dir = "examples"
    
    os.makedirs(output_dir, exist_ok=True)
    
    print("Loading Task Card...")
    with open(example_path, 'r', encoding='utf-8') as f:
        task_card = json.load(f)
    
    # Generate detailed style
    print("\nGenerating DETAILED style prompt...")
    generator_detailed = TaskCardPromptGenerator(task_card, style="detailed")
    prompt_detailed = generator_detailed.generate_prompt()
    
    with open(os.path.join(output_dir, "prompt_detailed.txt"), 'w', encoding='utf-8') as f:
        f.write(prompt_detailed)
    print(f"✓ Saved to {os.path.join(output_dir, 'prompt_detailed.txt')}")
    
    # Generate concise style
    print("Generating CONCISE style prompt...")
    generator_concise = TaskCardPromptGenerator(task_card, style="concise")
    prompt_concise = generator_concise.generate_prompt()
    
    with open(os.path.join(output_dir, "prompt_concise.txt"), 'w', encoding='utf-8') as f:
        f.write(prompt_concise)
    print(f"✓ Saved to {os.path.join(output_dir, 'prompt_concise.txt')}")
    
    # Generate structured JSON output
    print("Generating structured JSON output...")
    generator_json = TaskCardPromptGenerator(task_card, style="detailed")
    output_dict = generator_json.to_dict()
    
    with open(os.path.join(output_dir, "prompt_structured.json"), 'w', encoding='utf-8') as f:
        json.dump(output_dict, f, ensure_ascii=False, indent=2)
    print(f"✓ Saved to {os.path.join(output_dir, 'prompt_structured.json')}")
    
    # Test stability: generate 3 times and verify identical output
    print("\n" + "="*60)
    print("STABILITY TEST: Generating same Task Card 3 times")
    print("="*60)
    
    outputs = []
    for i in range(3):
        gen = TaskCardPromptGenerator(task_card, style="detailed")
        output = gen.generate_prompt()
        outputs.append(output)
        print(f"Generation {i+1}: OK")
    
    if outputs[0] == outputs[1] == outputs[2]:
        print("✓ All 3 outputs IDENTICAL - Stability guaranteed")
    else:
        print("✗ Outputs differ - Stability issue detected!")
    
    print("\nAll examples generated successfully!")


if __name__ == "__main__":
    main()
