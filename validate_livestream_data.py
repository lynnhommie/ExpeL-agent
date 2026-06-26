#!/usr/bin/env python3
"""
Minimal validation script for livestream MVP
Tests basic data loading and system setup
"""
import json
import sys
import os

def test_data_files():
    """Test if all required data files exist and are valid JSON"""
    print("[TEST] Checking data files...")
    
    files_to_check = [
        'data/livestream/creator_profile.json',
        'data/livestream/trajectories.jsonl',
        'data/livestream/rules.jsonl',
        'data/livestream/safety_rules.jsonl',
        'data/livestream/tasks.json',
    ]
    
    for filepath in files_to_check:
        if not os.path.exists(filepath):
            print(f"✗ Missing: {filepath}")
            return False
        
        try:
            if filepath.endswith('.jsonl'):
                with open(filepath, 'r', encoding='utf-8') as f:
                    count = 0
                    for line in f:
                        json.loads(line)
                        count += 1
                print(f"✓ {filepath} ({count} lines)")
            else:
                with open(filepath, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                print(f"✓ {filepath}")
        except json.JSONDecodeError as e:
            print(f"✗ Invalid JSON in {filepath}: {e}")
            return False
    
    return True

def test_config_files():
    """Test if config files exist"""
    print("\n[TEST] Checking config files...")
    
    configs = [
        'configs/benchmark/livestream.yaml',
    ]
    
    for config in configs:
        if os.path.exists(config):
            print(f"✓ {config}")
        else:
            print(f"✗ Missing: {config}")
            return False
    
    return True

def test_source_files():
    """Test if source files exist"""
    print("\n[TEST] Checking source files...")
    
    sources = [
        'envs/livestream/livestream.py',
        'prompts/livestream.py',
        'prompts/livestream_utils.py',
    ]
    
    for source in sources:
        if os.path.exists(source):
            # Try to compile it
            try:
                with open(source, 'r') as f:
                    compile(f.read(), source, 'exec')
                print(f"✓ {source} (syntax OK)")
            except SyntaxError as e:
                print(f"✗ Syntax error in {source}: {e}")
                return False
        else:
            print(f"✗ Missing: {source}")
            return False
    
    return True

def test_data_stats():
    """Print statistics about the generated data"""
    print("\n[STATS] Data summary:")
    
    # Trajectories
    with open('data/livestream/trajectories.jsonl', 'r') as f:
        trajectories = [json.loads(line) for line in f]
    
    # Sessions
    sessions = {}
    for traj in trajectories:
        sid = traj['session_id']
        if sid not in sessions:
            sessions[sid] = {'turns': 0, 'reward': 0, 'success': 0}
        sessions[sid]['turns'] += 1
        sessions[sid]['reward'] += traj['reward']
        if traj['continue_flag'] == 1 and traj['safe_flag']:
            sessions[sid]['success'] += 1
    
    total_reward = sum(t['reward'] for t in trajectories)
    continue_count = sum(1 for t in trajectories if t['continue_flag'] == 1)
    
    print(f"  - Total trajectories: {len(trajectories)}")
    print(f"  - Total sessions: {len(sessions)}")
    print(f"  - Total reward: {total_reward}")
    print(f"  - Continue rate: {continue_count}/{len(trajectories)} ({100*continue_count/len(trajectories):.1f}%)")
    print(f"  - Avg turns per session: {sum(s['turns'] for s in sessions.values())/len(sessions):.1f}")
    
    # Rules
    with open('data/livestream/rules.jsonl', 'r') as f:
        rules = [json.loads(line) for line in f]
    print(f"  - Total rules: {len(rules)}")
    
    # Safety rules
    with open('data/livestream/safety_rules.jsonl', 'r') as f:
        safety_rules = [json.loads(line) for line in f]
    print(f"  - Safety rules: {len(safety_rules)}")
    
    # Creator profile
    with open('data/livestream/creator_profile.json', 'r') as f:
        profile = json.load(f)
    print(f"  - Creator: {profile['creator_name']}")
    print(f"  - Style tags: {', '.join(profile['style_tags'])}")

def main():
    print("="*60)
    print("LIVESTREAM MVP - MINIMAL DATA VALIDATION")
    print("="*60)
    
    all_pass = True
    
    # Run tests
    if not test_data_files():
        all_pass = False
    
    if not test_config_files():
        all_pass = False
    
    if not test_source_files():
        all_pass = False
    
    if not all_pass:
        print("\n✗ VALIDATION FAILED")
        sys.exit(1)
    
    # Print stats
    try:
        test_data_stats()
    except Exception as e:
        print(f"\n✗ Failed to compute stats: {e}")
        sys.exit(1)
    
    print("\n" + "="*60)
    print("✓ ALL VALIDATIONS PASSED")
    print("="*60)
    print("\nNext steps:")
    print("1. Test environment: python3 -c 'from envs.livestream.livestream import LivestreamChatEnv; env = LivestreamChatEnv(); print(\"✓ Environment loads\")'")
    print("2. Test prompts: python3 -c 'from prompts.livestream import LIVESTREAM_FEWSHOTS; print(f\"✓ {len(LIVESTREAM_FEWSHOTS)} few-shots loaded\")'")
    print("3. Run full system: python train.py benchmark=livestream testing=true run_name=test")
    print("="*60)

if __name__ == '__main__':
    main()
