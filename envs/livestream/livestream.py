from typing import Dict, Any, List, Tuple
import re

from envs.base import BaseEnv
from .user_simulator import LivestreamUserSimulator


class LivestreamChatEnv(BaseEnv):
    def __init__(self, creator_name: str = "主播A", persona_description: str = "热情、亲切、爱聊天",
                 max_steps: int = 8, user_mode: str = "template", **kwargs):
        self.env_name = "livestream"
        self.creator_name = creator_name
        self.persona_description = persona_description
        self.max_steps = max_steps
        self.curr_step = 1
        self.terminated = False
        self.truncated = False
        self.reward = 0
        self._last_user_text = ""
        self._history: List[Dict[str, Any]] = []

        # 用户模拟器
        self.user_mode = user_mode  # "template" 或 "none"（none=旧版固定回复）
        self.user_simulator = LivestreamUserSimulator()

    def reset(self):
        self.curr_step = 1
        self.terminated = False
        self.truncated = False
        self.reward = 0
        self._last_user_text = ""
        self._history = []
        self.user_simulator.reset()
        return self._build_observation("欢迎来到直播间，打个招呼吧")

    def _build_observation(self, text: str):
        return f"Observation: {text}"

    def _is_safe(self, text: str) -> bool:
        banned = ["色情", "赌博", "违法", "爆炸", "武器", "毒品"]
        return not any(w in text for w in banned)

    def _score_reply(self, action: str) -> float:
        score = 0.0
        if len(action.strip()) > 0:
            score += 1.0
        if any(w in action for w in ["欢迎", "家人们", "宝子", "聊聊", "想听"]):
            score += 1.0
        if any(w in action for w in ["吗", "呢", "怎么", "啥", "？", "呀", "吧"]):
            score += 0.5
        if not self._is_safe(action):
            score -= 5.0
        return score

    def step(self, action: str, *args, **kwargs) -> Tuple[str, float, bool, bool, Dict]:
        self._last_user_text = action

        # ----- 环境打分 -----
        env_reward = self._score_reply(action)

        if self.user_mode == "template":
            # ----- 用户模拟器 -----
            user_reply, sim_reward, user_left = self.user_simulator.respond(action)
            # 综合奖励：环境评分 + 用户模拟评分 的平均
            self.reward = (env_reward + sim_reward) / 2.0
        else:
            # ----- 旧版固定回复（兼容模式） -----
            user_reply = ""
            user_left = False
            self.reward = env_reward

        # ----- 记录历史 -----
        self._history.append({
            "step": self.curr_step,
            "action": action,
            "reward": self.reward,
            "user_reply": user_reply,
            "user_left": user_left,
        })
        self.curr_step += 1

        # ----- 终止条件 -----
        if not self._is_safe(action):
            self.terminated = True
            obs = "你触发了安全规则，请立即停止该话题。"
        elif user_left:
            self.terminated = True
            obs = f"用户说：{user_reply}\n（用户离开了直播间）"
        elif self.curr_step > self.max_steps:
            self.truncated = True
            obs = "对话轮次已达到上限。"
        else:
            obs = f"用户说：{user_reply}"

        return obs, self.reward, self.terminated, self.truncated, {}

    def success_fn(self) -> bool:
        return self.reward > 0 and not self.terminated
