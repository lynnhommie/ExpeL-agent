"""
基于 trajectories.jsonl 数据的用户模拟器。

核心逻辑：
  1. 主播回复后 → 在 trajectories 中找到语义匹配的 agent_text
  2. 取该条记录的下一条 user_text 作为用户的回复
  3. 根据回复质量动态决定用户是否继续聊天
"""
import json
import random
from collections import defaultdict
from typing import List, Dict, Tuple, Optional


class LivestreamUserSimulator:
    def __init__(self, trajectories_path: str = "data/livestream/trajectories.jsonl"):
        self.trajectories_path = trajectories_path
        self._sessions: Dict[str, List[Dict]] = {}
        self._reply_pool: List[str] = []
        self._load_trajectories()

        # 用户状态
        self.engagement = 5.0       # 参与度 1-10
        self.dissatisfaction = 0.0  # 不满度
        self.turn_count = 0
        self.max_turns = 8

    # ------------------------------------------------------------------
    # 加载 & 索引
    # ------------------------------------------------------------------
    def _load_trajectories(self):
        """加载所有轨迹，按 session_id 分组并按 turn_id 排序"""
        with open(self.trajectories_path, encoding="utf-8") as f:
            records = [json.loads(line) for line in f if line.strip()]

        sessions = defaultdict(list)
        for r in records:
            sessions[r["session_id"]].append(r)

        for sid in sessions:
            sessions[sid].sort(key=lambda x: x["turn_id"])

        self._sessions = dict(sessions)

        # 收集所有 agent 回复，用于模糊匹配
        self._reply_pool = []
        for sid, turns in self._sessions.items():
            for t in turns:
                text = t.get("agent_text", "").strip()
                if text:
                    self._reply_pool.append(text)

    # ------------------------------------------------------------------
    # 重置
    # ------------------------------------------------------------------
    def reset(self, initial_user_text: str = None):
        """重置用户状态，可选指定第一条用户消息"""
        self.engagement = 5.0
        self.dissatisfaction = 0.0
        self.turn_count = 0

    # ------------------------------------------------------------------
    # 核心接口
    # ------------------------------------------------------------------
    def respond(self, agent_reply: str) -> Tuple[str, float, bool]:
        """
        根据主播回复生成用户的下一条回复

        Returns:
            (user_text, reward, user_left)
            - user_text:  用户的下一条回复（空串表示沉默离开）
            - reward:     对主播回复的打分（-5 ~ 3）
            - user_left:  用户是否离开
        """
        # 1. 对主播回复打分
        reward = self._score_reply(agent_reply)

        # 2. 更新用户状态
        self.engagement = max(0, min(10, self.engagement + reward * 0.5))
        self.dissatisfaction += max(0, 1.0 - reward) * 1.5
        self.turn_count += 1

        # 3. 判断用户是否离开
        if self.dissatisfaction >= 6.0 or self.engagement <= 0.5:
            return ("", reward, True)

        if self.turn_count >= self.max_turns:
            return ("", reward, True)

        # 4. 在 trajectories 中找到匹配的用户回复
        user_reply = self._find_reply(agent_reply)

        return (user_reply, reward, False)

    # ------------------------------------------------------------------
    # 匹配逻辑
    # ------------------------------------------------------------------
    def _find_reply(self, agent_reply: str) -> str:
        """找到与当前回复匹配的用户下一条回复"""
        agent_clean = agent_reply.strip()

        # ----- 策略 1: 完全匹配 -----
        for sid, turns in self._sessions.items():
            for i, t in enumerate(turns):
                if t.get("agent_text", "").strip() == agent_clean:
                    # 如果下一条存在，返回下一条的 user_text
                    if i + 1 < len(turns):
                        return turns[i + 1]["user_text"]
                    # 否则取当前 session 第一条 user_text 的变体
                    return self._fallback_user_text(turns)

        # ----- 策略 2: 关键词匹配 -----
        keywords = self._extract_keywords(agent_clean)
        best_score = 0
        best_user_text = None

        for sid, turns in self._sessions.items():
            for i, t in enumerate(turns):
                agent = t.get("agent_text", "").strip()
                if not agent:
                    continue
                score = self._keyword_match_score(agent, keywords)
                if score > best_score:
                    best_score = score
                    if i + 1 < len(turns):
                        best_user_text = turns[i + 1]["user_text"]
                    else:
                        best_user_text = self._fallback_user_text(turns)

        if best_score > 0 and best_user_text:
            return best_user_text

        # ----- 策略 3: 随机选取 -----
        sid = random.choice(list(self._sessions.keys()))
        turns = self._sessions[sid]
        return self._fallback_user_text(turns)

    def _fallback_user_text(self, turns: List[Dict]) -> str:
        """从一组对话轮次中随机选取一条用户消息"""
        candidates = [t["user_text"] for t in turns if t.get("user_text", "").strip()]
        return random.choice(candidates) if candidates else "嗯，继续说吧"

    # ------------------------------------------------------------------
    # 质量打分
    # ------------------------------------------------------------------
    def _score_reply(self, reply: str) -> float:
        """
        对主播回复质量打分，范围 -5 ~ 3

        +0.4  有追问（吗/呢/怎么/啥/？/呀）
        +0.3  有情感词（哈哈/哇/懂/抱抱/加油）
        +0.2  有称呼（宝子/家人们/家人们/宝）
        +0.2  长度 >= 10 字
        -0.5  过短 <= 4 字
        -2.0  不安全内容（违禁/毒品/赌博/色情/武器）
        """
        if not reply or not reply.strip():
            return -1.0

        score = 0.0

        # 正面特征
        if any(w in reply for w in ["吗", "呢", "怎么", "啥", "？", "呀", "吧"]):
            score += 0.4
        if any(w in reply for w in ["哈哈", "哇", "懂", "抱抱", "加油", "开心", "喜欢", "棒"]):
            score += 0.3
        if any(w in reply for w in ["宝子", "家人们", "家人", "宝"]):
            score += 0.2

        # 长度
        if len(reply.strip()) >= 10:
            score += 0.2
        elif len(reply.strip()) <= 4:
            score -= 0.5

        # 安全问题
        if any(w in reply for w in ["违禁", "毒品", "赌博", "色情", "武器", "爆炸"]):
            score -= 2.0

        return max(-5.0, min(3.0, score))

    # ------------------------------------------------------------------
    # 关键词工具
    # ------------------------------------------------------------------
    KEYWORD_SET = frozenset({
        "欢迎", "聊聊", "最近", "今天", "想聊", "推荐", "开心",
        "怎么", "什么", "为什么", "怎么", "哪里", "哪个",
        "喜欢", "觉得", "感觉", "有吗", "是吗",
        "哈哈", "哇", "懂", "棒", "厉害",
    })

    def _extract_keywords(self, text: str) -> List[str]:
        """提取文本中的关键词"""
        found = []
        for kw in self.KEYWORD_SET:
            if kw in text:
                found.append(kw)
        return found

    def _keyword_match_score(self, agent_text: str, keywords: List[str]) -> int:
        """
        计算 agent_text 与关键词列表的匹配得分

        返回命中的关键词数量（0 ~ len(keywords)）
        """
        if not keywords:
            return 0
        return sum(1 for kw in keywords if kw in agent_text)
