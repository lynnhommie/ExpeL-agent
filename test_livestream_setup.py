#!/usr/bin/env python3
"""
Minimal test script to verify livestream MVP setup
"""
import sys
import os

# Test 1: Can we import the livestream environment?
print("[TEST 1] Importing livestream environment...")
try:
    from envs.livestream.livestream import LivestreamChatEnv
    print("✓ LivestreamChatEnv imported successfully")
except Exception as e:
    print(f"✗ Failed to import: {e}")
    sys.exit(1)

# Test 2: Can we instantiate the environment?
print("\n[TEST 2] Instantiating livestream environment...")
try:
    env = LivestreamChatEnv(creator_name="TestHost", max_steps=5)
    env.reset()
    print("✓ Environment instantiated and reset successfully")
except Exception as e:
    print(f"✗ Failed to instantiate: {e}")
    sys.exit(1)

# Test 3: Can we run a step in the environment?
print("\n[TEST 3] Running a step in environment...")
try:
    obs, reward, terminated, truncated, info = env.step("Hi there!")
    print(f"✓ Step executed successfully")
    print(f"  - Observation: {obs}")
    print(f"  - Reward: {reward}")
    print(f"  - Terminated: {terminated}")
    print(f"  - Truncated: {truncated}")
except Exception as e:
    print(f"✗ Failed to run step: {e}")
    sys.exit(1)

# Test 4: Can we import livestream prompts?
print("\n[TEST 4] Importing livestream prompts...")
try:
    from prompts.livestream import (
        LIVESTREAM_SYSTEM_INSTRUCTION,
        LIVESTREAM_HUMAN_INSTRUCTION,
        LIVESTREAM_FEWSHOTS,
        LIVESTREAM_LLM_PARSER,
    )
    print("✓ Livestream prompts imported successfully")
    print(f"  - System instruction preview: {LIVESTREAM_SYSTEM_INSTRUCTION[:50]}...")
    print(f"  - Fewshots count: {len(LIVESTREAM_FEWSHOTS)}")
except Exception as e:
    print(f"✗ Failed to import prompts: {e}")
    sys.exit(1)

# Test 5: Can we access livestream config?
print("\n[TEST 5] Checking livestream config...")
try:
    import json
    with open('configs/benchmark/livestream.yaml', 'r') as f:
        config_content = f.read()
    print("✓ Livestream config found")
    
    with open('data/livestream/tasks.json', 'r') as f:
        tasks = json.load(f)
    print(f"✓ Livestream tasks loaded ({len(tasks)} tasks)")
except Exception as e:
    print(f"✗ Failed to load config: {e}")
    sys.exit(1)

# Test 6: Can we import the prompts registry?
print("\n[TEST 6] Importing prompts registry...")
try:
    from prompts import (
        FEWSHOTS,
        LLM_PARSER,
        OBSERVATION_FORMATTER,
        STEP_IDENTIFIER,
    )
    print("✓ Prompts registry imported successfully")
    print(f"  - Livestream in FEWSHOTS: {'livestream' in FEWSHOTS}")
    print(f"  - Livestream in LLM_PARSER: {'livestream' in LLM_PARSER}")
    print(f"  - Livestream in OBSERVATION_FORMATTER: {'livestream' in OBSERVATION_FORMATTER}")
    print(f"  - Livestream in STEP_IDENTIFIER: {'livestream' in STEP_IDENTIFIER}")
except Exception as e:
    print(f"✗ Failed to import registry: {e}")
    sys.exit(1)

# Test 7: Can we parse LLM output?
print("\n[TEST 7] Testing LLM parser...")
try:
    from prompts.livestream import LIVESTREAM_LLM_PARSER
    message, msg_type, others = LIVESTREAM_LLM_PARSER("你好呀宝子", 1, False)
    print("✓ LLM parser works")
    print(f"  - Message type: {msg_type}")
    print(f"  - Action: {others['action']}")
except Exception as e:
    print(f"✗ Failed to parse: {e}")
    sys.exit(1)

# Test 8: Can we create and access ENVS registry?
print("\n[TEST 8] Checking ENVS registry...")
try:
    from envs import ENVS
    print("✓ ENVS imported")
    print(f"  - Livestream in ENVS: {'livestream' in ENVS}")
    if 'livestream' in ENVS:
        test_env = ENVS['livestream'](creator_name="Test")
        print(f"✓ Can instantiate livestream env from registry")
except Exception as e:
    print(f"✗ Failed: {e}")
    sys.exit(1)

print("\n" + "="*50)
print("✓ ALL TESTS PASSED! MVP infrastructure is ready.")
print("="*50)
print("\nNext: Run with `python train.py benchmark=livestream testing=true run_name=test`")
