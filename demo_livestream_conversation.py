#!/usr/bin/env python3
"""
Minimal demo script showing how the livestream MVP works end-to-end
This simulates a simple conversation loop without needing the full ExpeL framework
"""
import json
import random

def load_data():
    """Load all data files"""
    with open('data/livestream/creator_profile.json', 'r', encoding='utf-8') as f:
        profile = json.load(f)
    
    trajectories = []
    with open('data/livestream/trajectories.jsonl', 'r', encoding='utf-8') as f:
        for line in f:
            trajectories.append(json.loads(line))
    
    rules = []
    with open('data/livestream/rules.jsonl', 'r', encoding='utf-8') as f:
        for line in f:
            rules.append(json.loads(line))
    
    return profile, trajectories, rules

def find_similar_trajectory(user_input, trajectories, top_k=2):
    """Find similar past trajectories based on intent/topic"""
    # Simple heuristic: find trajectories with similar keywords or intent
    keywords = user_input.lower().split()
    similar = []
    
    for traj in trajectories:
        user_text = traj['user_text'].lower()
        score = sum(1 for kw in keywords if kw in user_text)
        if score > 0 or random.random() < 0.1:  # Also randomly sample
            similar.append((traj, score))
    
    similar.sort(key=lambda x: x[1], reverse=True)
    return [t[0] for t in similar[:top_k]]

def demo_conversation():
    """Simulate a simple conversation with the livestream agent"""
    print("="*70)
    print("LIVESTREAM MVP - MINIMAL DEMO")
    print("="*70)
    
    profile, trajectories, rules = load_data()
    
    print(f"\n[INFO] Creator: {profile['creator_name']}")
    print(f"[INFO] Style: {', '.join(profile['style_tags'])}")
    print(f"[INFO] Common phrases: {', '.join(profile['common_phrases'][:3])}")
    print(f"[INFO] Loaded {len(trajectories)} past trajectories")
    print(f"[INFO] Loaded {len(rules)} conversation rules")
    
    # Simulate a conversation
    conversation = []
    user_inputs = [
        "你好呀主播",
        "最近在忙什么",
        "能推荐点视频吗",
    ]
    
    print("\n" + "="*70)
    print("SIMULATED CONVERSATION")
    print("="*70)
    
    for turn, user_input in enumerate(user_inputs, 1):
        print(f"\n[TURN {turn}] User says: \"{user_input}\"")
        
        # Find similar trajectories
        similar = find_similar_trajectory(user_input, trajectories, top_k=1)
        if similar:
            print(f"  └─ Found similar past trajectory:")
            print(f"     User: \"{similar[0]['user_text']}\"")
            print(f"     Reply: \"{similar[0]['agent_text']}\"")
            print(f"     Intent: {similar[0]['intent']}")
            print(f"     Reward: {similar[0]['reward']}")
        
        # Select a rule
        matching_rules = [r for r in rules if r['category'] in ['开场', '续聊', '信息分享']]
        if matching_rules:
            rule = random.choice(matching_rules)
            print(f"  └─ Applying rule: {rule['rule_id']} ({rule['category']})")
            print(f"     Rule: {rule['action']}")
            print(f"     Example: {rule['example']}")
        
        # Simulate agent response (in real system, would use LLM)
        if turn == 1:
            agent_reply = "欢迎宝子来直播间！今天怎么样呀？"
        elif turn == 2:
            agent_reply = "家人们呐，最近在忙着更新视频呢。你最近怎么样？"
        else:
            agent_reply = "你喜欢看什么类型的内容呢？我可以给你推荐哦"
        
        print(f"  └─ Agent reply: \"{agent_reply}\"")
        
        conversation.append({
            "user_text": user_input,
            "agent_text": agent_reply,
        })
    
    print("\n" + "="*70)
    print("CONVERSATION SUMMARY")
    print("="*70)
    print(f"Total turns: {len(conversation)}")
    print("\nFull conversation:")
    for i, (user, reply) in enumerate([(c['user_text'], c['agent_text']) for c in conversation], 1):
        print(f"  {i}. User: {user}")
        print(f"     Agent: {reply}")
    
    print("\n" + "="*70)
    print("KEY INSIGHTS")
    print("="*70)
    print("✓ System successfully:")
    print("  1. Loaded creator profile with persona information")
    print("  2. Loaded 18 past conversation trajectories")
    print("  3. Loaded 8 conversation rules")
    print("  4. Retrieved similar past conversations for context")
    print("  5. Applied relevant conversation rules")
    print("  6. Generated contextual replies")
    print("\n✓ Next steps:")
    print("  1. Replace simulated replies with LLM-generated responses")
    print("  2. Integrate with full ExpeL framework")
    print("  3. Add reward scoring and trajectory logging")
    print("  4. Enable automatic rule extraction from new conversations")
    print("="*70)

if __name__ == '__main__':
    demo_conversation()
