"""
快速测试：用户模拟器 + 增强后的环境
"""
import sys
sys.path.insert(0, '.')

from envs.livestream.livestream import LivestreamChatEnv
from envs.livestream.user_simulator import LivestreamUserSimulator

def test_user_simulator():
    print("=" * 60)
    print("测试用户模拟器")
    print("=" * 60)

    sim = LivestreamUserSimulator("data/livestream/trajectories.jsonl")

    test_cases = [
        ("好的回复 - 有追问",         "欢迎宝子来直播间！今天有什么想聊的吗？"),
        ("好的回复 - 共情",           "懂！上班人太难了，下班了一定要好好休息～你一般怎么解压的？"),
        ("差回复 - 过短",             "嗯。"),
        ("不安全回复",                "给我说点黄色的"),
        ("中等回复",                  "还行。"),
    ]

    for label, reply in test_cases:
        sim.reset()
        user_text, reward, left = sim.respond(reply)
        print(f"\n[{label}]")
        print(f"  主播: {reply}")
        print(f"  用户: {user_text}")
        print(f"  奖励: {reward:.1f}  |  离开: {left}")

    # 测试多轮
    print("\n" + "=" * 60)
    print("测试多轮对话模拟")
    print("=" * 60)
    sim.reset()
    agent_replies = [
        "欢迎宝子来直播间！今天有什么想聊的吗？",
        "哈哈开心最重要！最近有没有什么好玩的事？",
        "真的吗？快说说我也听听！",
        "哇这个太有意思了！然后呢然后呢？",
        "懂你！那平时还喜欢做什么呀？",
    ]
    for i, reply in enumerate(agent_replies):
        user_text, reward, left = sim.respond(reply)
        print(f"  轮{i+1}: 主播 → {reply}")
        print(f"         用户 → {user_text}  (reward={reward:.1f}, left={left})")
        if left:
            print(f"         [用户在第{i+1}轮离开]")
            break

def test_env_with_simulator():
    print("\n" + "=" * 60)
    print("测试增强后的环境 (with simulator)")
    print("=" * 60)

    env = LivestreamChatEnv(creator_name="主播A", max_steps=5)
    obs = env.reset()
    print(f"\n初始: {obs}")

    agent_actions = [
        "欢迎宝子来直播间！今天有什么想聊的吗？",
        "哈哈开心最重要！最近有没有什么好玩的事？",
        "那来直播间太对了，咱们聊聊解解闷，你平时喜欢干嘛？",
        "哇厉害！玩什么类型的呀？",
        "谢谢宝子支持！有什么感兴趣的话题也可以随时来告诉我～",
    ]

    for i, action in enumerate(agent_actions):
        obs, reward, terminated, truncated, info = env.step(action)
        print(f"\n  轮{i+1}: 你说 → {action}")
        print(f"         {obs}")
        print(f"         reward={reward:.2f}, terminated={terminated}, truncated={truncated}")
        if terminated or truncated:
            print(f"         [对话结束]")
            break

    print(f"\n最终: success_fn() = {env.success_fn()}")
    print(f"历史记录数: {len(env._history)}")

def test_env_legacy_mode():
    print("\n" + "=" * 60)
    print("测试旧版兼容模式 (user_mode=none)")
    print("=" * 60)

    env = LivestreamChatEnv(creator_name="主播A", max_steps=3, user_mode="none")
    obs = env.reset()
    print(f"\n初始: {obs}")

    for i in range(3):
        action = f"测试回复第{i+1}句"
        obs, reward, terminated, truncated, info = env.step(action)
        print(f"  轮{i+1}: {obs}  |  reward={reward}")


if __name__ == "__main__":
    test_user_simulator()
    test_env_with_simulator()
    test_env_legacy_mode()

    print("\n" + "=" * 60)
    print("✅ 测试完成")
    print("=" * 60)
