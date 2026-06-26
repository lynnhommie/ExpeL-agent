"""Quick test for P0 compatibility fixes"""
print("=" * 60)
print("P0 Compatibility Test")
print("=" * 60)

# Test 1: Import all critical modules
print("\n[Test 1] Importing critical modules...")
try:
    from prompts import livestream
    print("  ✓ prompts.livestream imported")
    
    from prompts.templates.human import RULE_TEMPLATE, HUMAN_CRITIQUES
    print("  ✓ RULE_TEMPLATE imported")
    print(f"  ✓ RULE_TEMPLATE has livestream: {'livestream' in RULE_TEMPLATE}")
    
    from prompts import (
        SYSTEM_CRITIQUE_INSTRUCTION, 
        FEWSHOTS, LLM_PARSER, OBSERVATION_FORMATTER,
        STEP_IDENTIFIER, CYCLER, REFLECTION_PREFIX,
        PREVIOUS_TRIALS_FORMATTER, STEP_STRIPPER
    )
    print("  ✓ prompts registry imported")
    
    from envs import ENVS, INIT_TASKS_FN
    print("  ✓ envs imported")
    
    from agent import AGENT
    print("  ✓ AGENT registry imported")
    
    from models import LLM_CLS
    print("  ✓ models imported")
    
    from memory import EMBEDDERS, RETRIEVERS
    print("  ✓ memory imported")
    
    from utils import save_trajectories_log, load_trajectories_log
    print("  ✓ utils imported")
    
except Exception as e:
    print(f"  ✗ FAILED: {e}")
    import traceback
    traceback.print_exc()
    exit(1)

# Test 2: Check SYSTEM_CRITIQUE_INSTRUCTION livestream keys
print("\n[Test 2] SYSTEM_CRITIQUE_INSTRUCTION keys...")
try:
    sci = SYSTEM_CRITIQUE_INSTRUCTION['livestream']
    required_keys = ['compare', 'all_success', 'all_fail', 'all_reflection', 
                     'compare_existing_rules', 'all_success_existing_rules']
    for key in required_keys:
        if key in sci:
            print(f"  ✓ SCI['{key}'] = {str(sci[key])[:60]}...")
        else:
            print(f"  ✗ MISSING: SCI['{key}']")
except Exception as e:
    print(f"  ✗ FAILED: {e}")

# Test 3: Check RULE_TEMPLATE
print("\n[Test 3] RULE_TEMPLATE...")
try:
    rt = RULE_TEMPLATE['livestream']
    rendered = rt.format_messages(rules="Test rule")
    print(f"  ✓ RULE_TEMPLATE renders: {rendered[0].content[:60]}...")
except Exception as e:
    print(f"  ✗ FAILED: {e}")

# Test 4: Check ENVS and INIT_TASKS_FN
print("\n[Test 4] ENVS and INIT_TASKS_FN...")
try:
    env_cls = ENVS['livestream']
    env = env_cls(creator_name="Test", max_steps=3)
    obs = env.reset()
    print(f"  ✓ env.reset() = {obs}")
    obs, reward, term, trunc, info = env.step("你好呀")
    print(f"  ✓ env.step() -> obs={obs}, reward={reward}, term={term}")
    print(f"  ✓ env.success_fn() = {env.success_fn()}")
except Exception as e:
    print(f"  ✗ FAILED: {e}")
    import traceback
    traceback.print_exc()

# Test 5: Check LLM_PARSER
print("\n[Test 5] LLM_PARSER...")
try:
    parse_fn = LLM_PARSER['livestream']
    msg, msg_type, others = parse_fn("你好呀宝子", 1, False)
    print(f"  ✓ parser output: type={msg_type}, action={others['action']}")
except Exception as e:
    print(f"  ✗ FAILED: {e}")

# Test 6: Check INIT_TASKS_FN
print("\n[Test 6] INIT_TASKS_FN...")
try:
    from omegaconf import DictConfig
    cfg = DictConfig({
        "benchmark": {"task_prefix": "User: ", "task_file": "data/livestream/tasks.json"},
        "testing": True
    })
    tasks = INIT_TASKS_FN['livestream'](cfg)
    print(f"  ✓ INIT_TASKS_FN returned {len(tasks)} tasks")
    for t in tasks:
        print(f"    task={t['task'][:40]}... env_name={t['env_name']}")
except Exception as e:
    print(f"  ✗ FAILED: {e}")
    import traceback
    traceback.print_exc()

# Test 7: Test ReflectAgent with livestream config
print("\n[Test 7] Constructing agent (testing mode)...")
try:
    from prompts.templates.system import system_message_prompt
    from functools import partial
    from prompts import STEP_CYCLER
    
    agent = AGENT['reflect'](
        name="test_host",
        system_instruction=livestream.LIVESTREAM_SYSTEM_INSTRUCTION,
        human_instruction=livestream.LIVESTREAM_HUMAN_INSTRUCTION,
        tasks=INIT_TASKS_FN['livestream'](DictConfig({
            "benchmark": {"task_prefix": "User: ", "task_file": "data/livestream/tasks.json"},
            "testing": True
        })),
        fewshots=livestream.LIVESTREAM_FEWSHOTS,
        system_prompt=system_message_prompt,
        env=ENVS['livestream'],
        max_steps=3,
        openai_api_key='TEST_KEY',
        llm='gpt-3.5-turbo',
        llm_builder=lambda *args, **kwargs: lambda msgs, **kw: "宝子你好呀！今天想聊点什么？",
        reflection_fewshots=[],
        reflection_task_prompt=livestream.LIVESTREAM_REFLECTION_TASK_PROMPT,
        reflection_system_instruction=livestream.LIVESTREAM_SYSTEM_INSTRUCTION,
        reflection_system_prompt=livestream.LIVESTREAM_SYSTEM_INSTRUCTION,
        max_relfection_depth=2,
        llm_parser=LLM_PARSER['livestream'],
        observation_formatter=OBSERVATION_FORMATTER['livestream'],
        message_splitter=CYCLER['livestream'],
        identifier=STEP_IDENTIFIER['livestream'],
        message_step_splitter=partial(STEP_CYCLER, benchmark='livestream'),
        reflection_prefix=REFLECTION_PREFIX['livestream'],
        previous_trials_formatter=PREVIOUS_TRIALS_FORMATTER['livestream'],
        benchmark_name='livestream',
        testing=True,
    )
    print("  ✓ Agent constructed successfully")
    
    # Try running one step
    print("\n[Test 8] Running one step...")
    try:
        agent.run(reset=True)
        print("  ✓ run() completed")
        print(f"  ✓ curr_step = {agent.curr_step}")
        print(f"  ✓ success = {agent.is_success()}")
    except Exception as e:
        print(f"  ✗ run() failed: {e}")
        import traceback
        traceback.print_exc()
        
except Exception as e:
    print(f"  ✗ FAILED: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 60)
print("P0 Compatibility Test Complete")
print("=" * 60)
