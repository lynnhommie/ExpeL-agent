#!/usr/bin/env python3
"""
Minimal integration test for livestream MVP
Tests if core components work together
"""
import sys
import json

def test_import():
    """Test if all modules can be imported"""
    print("[TEST 1] Importing modules...")
    try:
        from envs.livestream.livestream import LivestreamChatEnv
        print("  ✓ LivestreamChatEnv imported")
        
        from prompts.livestream import (
            LIVESTREAM_SYSTEM_INSTRUCTION,
            LIVESTREAM_FEWSHOTS,
            LIVESTREAM_LLM_PARSER,
        )
        print("  ✓ livestream prompts imported")
        
        from envs import ENVS, INIT_TASKS_FN
        print("  ✓ ENVS registry imported")
        
        return True
    except ImportError as e:
        print(f"  ✗ Import failed: {e}")
        return False

def test_environment():
    """Test if environment works"""
    print("\n[TEST 2] Testing LivestreamChatEnv...")
    try:
        from envs.livestream.livestream import LivestreamChatEnv
        
        env = LivestreamChatEnv(creator_name="TestHost", max_steps=5)
        print("  ✓ Environment created")
        
        obs = env.reset()
        print(f"  ✓ Environment reset: {obs}")
        
        obs, reward, terminated, truncated, info = env.step("你好呀")
        print(f"  ✓ Step executed: reward={reward}, terminated={terminated}")
        
        return True
    except Exception as e:
        print(f"  ✗ Environment test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_prompts():
    """Test if prompts can be loaded"""
    print("\n[TEST 3] Testing prompts...")
    try:
        from prompts.livestream import (
            LIVESTREAM_SYSTEM_INSTRUCTION,
            LIVESTREAM_HUMAN_INSTRUCTION,
            LIVESTREAM_FEWSHOTS,
        )
        
        print(f"  ✓ System instruction: {LIVESTREAM_SYSTEM_INSTRUCTION[:50]}...")
        print(f"  ✓ Few-shots count: {len(LIVESTREAM_FEWSHOTS)}")
        
        return True
    except Exception as e:
        print(f"  ✗ Prompt test failed: {e}")
        return False

def test_data():
    """Test if data files can be loaded"""
    print("\n[TEST 4] Testing data files...")
    try:
        with open('data/livestream/creator_profile.json', 'r', encoding='utf-8') as f:
            profile = json.load(f)
        print(f"  ✓ Creator profile: {profile['creator_name']}")
        
        trajectories = []
        with open('data/livestream/trajectories.jsonl', 'r', encoding='utf-8') as f:
            for line in f:
                trajectories.append(json.loads(line))
        print(f"  ✓ Trajectories loaded: {len(trajectories)} records")
        
        rules = []
        with open('data/livestream/rules.jsonl', 'r', encoding='utf-8') as f:
            for line in f:
                rules.append(json.loads(line))
        print(f"  ✓ Rules loaded: {len(rules)} rules")
        
        return True
    except Exception as e:
        print(f"  ✗ Data test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_registries():
    """Test if registries are properly set up"""
    print("\n[TEST 5] Testing registries...")
    try:
        from prompts import (
            FEWSHOTS, LLM_PARSER, OBSERVATION_FORMATTER,
            STEP_IDENTIFIER, CYCLER, REFLECTION_PREFIX,
            PREVIOUS_TRIALS_FORMATTER, STEP_STRIPPER
        )
        
        checks = [
            ('FEWSHOTS', FEWSHOTS, 'livestream'),
            ('LLM_PARSER', LLM_PARSER, 'livestream'),
            ('OBSERVATION_FORMATTER', OBSERVATION_FORMATTER, 'livestream'),
            ('STEP_IDENTIFIER', STEP_IDENTIFIER, 'livestream'),
            ('CYCLER', CYCLER, 'livestream'),
            ('REFLECTION_PREFIX', REFLECTION_PREFIX, 'livestream'),
            ('PREVIOUS_TRIALS_FORMATTER', PREVIOUS_TRIALS_FORMATTER, 'livestream'),
            ('STEP_STRIPPER', STEP_STRIPPER, 'livestream'),
        ]
        
        for name, registry, key in checks:
            if key in registry:
                print(f"  ✓ {name}['{key}'] registered")
            else:
                print(f"  ✗ {name}['{key}'] NOT registered")
                return False
        
        return True
    except Exception as e:
        print(f"  ✗ Registry test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    print("="*70)
    print("LIVESTREAM MVP - MINIMAL INTEGRATION TEST")
    print("="*70)
    
    results = []
    
    results.append(("Import Test", test_import()))
    results.append(("Environment Test", test_environment()))
    results.append(("Prompt Test", test_prompts()))
    results.append(("Data Test", test_data()))
    results.append(("Registry Test", test_registries()))
    
    print("\n" + "="*70)
    print("TEST RESULTS")
    print("="*70)
    
    for name, passed in results:
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"{status}: {name}")
    
    all_passed = all(passed for _, passed in results)
    
    if all_passed:
        print("\n✓ ALL INTEGRATION TESTS PASSED!")
        print("\nYou can now run:")
        print("  python train.py benchmark=livestream testing=true run_name=test")
    else:
        print("\n✗ SOME TESTS FAILED")
        sys.exit(1)

if __name__ == '__main__':
    main()
