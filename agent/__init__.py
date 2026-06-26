from .base import BaseAgent
from .react import ReactAgent
from .reflect import ReflectAgent
from .expel import ExpelAgent


AGENT = dict(
    reflection=ReflectAgent,
    react=ReactAgent,
    # 使用更直观的名称暴露
    rl_agent=ExpelAgent,
    expel=ExpelAgent,  # 向后兼容
)
