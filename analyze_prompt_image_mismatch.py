#!/usr/bin/env python3
"""
Analyze why generated images don't match the detailed generation prompts.

This script:
1. Loads an image world JSON
2. Compares the generation prompts with what the images actually show
3. Identifies common patterns of mismatch
4. Suggests improvements
"""

import json
import sys
from pathlib import Path
from typing import Dict, List

def analyze_image_world(world_json_path: str):
    """Analyze an image world to identify prompt-image mismatches."""
    
    print("=" * 80)
    print("IMAGE-PROMPT MISMATCH ANALYSIS")
    print("=" * 80)
    
    # Load the world
    with open(world_json_path, 'r') as f:
        world = json.load(f)
    
    print(f"\n📁 World: {world['name']}")
    print(f"   Model: {world['generation_metadata'].get('model', 'unknown')}")
    print(f"   States: {len(world['states'])}")
    
    # Analyze each state
    print("\n" + "=" * 80)
    print("ANALYZING STATES")
    print("=" * 80)
    
    issues = []
    
    for i, state in enumerate(world['states']):
        state_id = state['state_id']
        print(f"\n🔍 State {state_id}:")
        
        # Check if image exists
        image_path = state.get('image_path')
        if not image_path or not Path(image_path).exists():
            print(f"   ⚠️  Image not found: {image_path}")
            issues.append({
                'state': state_id,
                'issue': 'image_missing',
                'severity': 'high'
            })
            continue
        
        # Analyze prompt characteristics
        generation_prompt = state.get('generation_prompt', '')
        text_description = state.get('text_description', '')
        
        prompt_length = len(generation_prompt)
        prompt_word_count = len(generation_prompt.split())
        
        print(f"   📝 Prompt length: {prompt_length} chars, {prompt_word_count} words")
        print(f"   📄 Text description: {len(text_description)} chars")
        
        # Check for common issues
        state_issues = []
        
        # Issue 1: Extremely long prompts
        if prompt_length > 2000:
            print(f"   ⚠️  VERY LONG PROMPT ({prompt_length} chars)")
            print(f"      → Image variation APIs may not follow all details")
            state_issues.append({
                'type': 'prompt_too_long',
                'details': f'{prompt_length} characters',
                'severity': 'medium'
            })
        
        # Issue 2: Multiple conflicting instructions
        if generation_prompt.count('MUST') > 5 or generation_prompt.count('CRITICAL') > 5:
            print(f"   ⚠️  TOO MANY CRITICAL INSTRUCTIONS")
            print(f"      → Model may prioritize base image over prompt details")
            state_issues.append({
                'type': 'too_many_instructions',
                'details': 'Multiple MUST/CRITICAL clauses',
                'severity': 'medium'
            })
        
        # Issue 3: Complex scene descriptions
        if '**Elements that MUST STAY THE SAME:**' in generation_prompt:
            same_section = generation_prompt.split('**Elements that MUST STAY THE SAME:**')[1]
            if '**Elements that' in same_section:
                same_section = same_section.split('**Elements that')[0]
            same_length = len(same_section)
            if same_length > 1000:
                print(f"   ⚠️  VERY LONG 'MUST STAY SAME' SECTION ({same_length} chars)")
                print(f"      → May constrain model too much, preventing changes")
                state_issues.append({
                    'type': 'too_constraining',
                    'details': f'{same_length} chars of constraints',
                    'severity': 'high'
            })
        
        # Issue 4: Check if using variation vs from-scratch
        reference_image = state.get('reference_image')
        if reference_image:
            print(f"   🔗 Using variation from: {reference_image}")
            print(f"      → Variation APIs prioritize base image consistency")
            if prompt_length > 1500:
                state_issues.append({
                    'type': 'variation_with_long_prompt',
                    'details': 'Long prompt + base image = conflicting constraints',
                    'severity': 'high'
                })
        else:
            print(f"   🆕 Generated from scratch")
        
        # Issue 5: Check advanced generation metadata
        advanced = state.get('metadata', {}).get('advanced_generation', {})
        if advanced:
            print(f"   ⚙️  Advanced generation used")
            initial_desc_len = len(advanced.get('initial_description', ''))
            final_desc_len = len(advanced.get('final_description', ''))
            print(f"      Initial description: {initial_desc_len} chars")
            print(f"      Final description: {final_desc_len} chars")
            
            if initial_desc_len > 2000 or final_desc_len > 2000:
                state_issues.append({
                    'type': 'overly_detailed_descriptions',
                    'details': 'Very long intermediate descriptions may confuse model',
                    'severity': 'medium'
                })
        
        if state_issues:
            issues.append({
                'state': state_id,
                'issues': state_issues
            })
            print(f"   ❌ Found {len(state_issues)} potential issue(s)")
        else:
            print(f"   ✅ No obvious issues detected")
    
    # Summary
    print("\n" + "=" * 80)
    print("SUMMARY & RECOMMENDATIONS")
    print("=" * 80)
    
    if not issues:
        print("\n✅ No obvious issues found!")
        print("   However, image variation APIs still have inherent limitations.")
    else:
        print(f"\n⚠️  Found issues in {len(issues)} state(s)")
        
        # Group by issue type
        issue_types = {}
        for item in issues:
            for issue in item.get('issues', []):
                issue_type = issue['type']
                if issue_type not in issue_types:
                    issue_types[issue_type] = []
                issue_types[issue_type].append(item['state'])
        
        print("\n📊 Issue breakdown:")
        for issue_type, states in issue_types.items():
            print(f"   • {issue_type}: {len(states)} state(s)")
            print(f"     States: {', '.join(states)}")
        
        print("\n💡 RECOMMENDATIONS:")
        print("\n1. SHORTER PROMPTS:")
        print("   → Extract only the KEY CHANGE from the action")
        print("   → Remove redundant 'MUST STAY SAME' sections")
        print("   → Focus on what's DIFFERENT, not what's the same")
        
        print("\n2. CONSIDER FROM-SCRATCH GENERATION:")
        print("   → For states with dramatic changes, generate from scratch")
        print("   → Use variation only for subtle transitions")
        
        print("\n3. PROMPT STRUCTURE:")
        print("   → Put the CHANGE first, constraints second")
        print("   → Use bullet points, not paragraphs")
        print("   → Limit to 3-5 key instructions max")
        
        print("\n4. VALIDATION:")
        print("   → Add image validation after generation")
        print("   → Compare generated image to prompt requirements")
        print("   → Retry with simplified prompt if mismatch detected")
        
        print("\n5. MODEL LIMITATIONS:")
        print("   → Image variation APIs prioritize visual consistency")
        print("   → They may ignore or simplify complex instructions")
        print("   → Consider this a known limitation of current models")
    
    print("\n" + "=" * 80)
    print("ANALYSIS COMPLETE")
    print("=" * 80)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python analyze_prompt_image_mismatch.py <world_json_path>")
        print("\nExample:")
        print("  python analyze_prompt_image_mismatch.py worlds/image_worlds/cloth_folding_egocentric_image_world.json")
        sys.exit(1)
    
    world_json_path = sys.argv[1]
    if not Path(world_json_path).exists():
        print(f"Error: File not found: {world_json_path}")
        sys.exit(1)
    
    analyze_image_world(world_json_path)












