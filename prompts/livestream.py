from langchain.prompts.chat import HumanMessagePromptTemplate
from langchain.schema import HumanMessage


class LooseHumanMessagePromptTemplate(HumanMessagePromptTemplate):
    """Like HumanMessagePromptTemplate but silently drops unknown kwargs."""
    def format_messages(self, **kwargs):
        known = set(self.prompt.input_variables)
        filtered = {k: v for k, v in kwargs.items() if k in known}
        return [HumanMessage(content=self.prompt.format(**filtered))]

from .templates.human import HUMAN_CRITIQUES, RULE_TEMPLATE
from .livestream_utils import (
    LIVESTREAM_LLM_PARSER,
    LIVESTREAM_OBSERVATION_FORMATTER,
    LIVESTREAM_STEP_IDENTIFIER,
    LIVESTREAM_CYCLER,
    LIVESTREAM_REFLECTION_PREFIX,
    LIVESTREAM_PREVIOUS_TRIALS_FORMATTER,
    LIVESTREAM_STEP_STRIPPER,
)

LIVESTREAM_SYSTEM_INSTRUCTION = (
    "You are a livestream AI host. Your job is to keep the conversation natural, friendly, and engaging. "
    "You should reflect the creator persona, encourage continued conversation, and avoid unsafe or irrelevant content."
)

# Accepts {instruction} and {max_steps} injected by _build_fewshot_prompt / _build_agent_prompt
LIVESTREAM_HUMAN_INSTRUCTION = LooseHumanMessagePromptTemplate.from_template(
    "You are in a livestream companion chat.\n"
    "Goals: stay in character, keep the user engaged, give short warm replies with a follow-up question, "
    "and refuse unsafe/illegal/sexual/hateful content.\n"
    "{instruction}"
)

LIVESTREAM_REFLECTION_TASK_PROMPT = LooseHumanMessagePromptTemplate.from_template(
    "Reflect on the previous livestream conversation turn and summarize what went well or poorly."
)

LIVESTREAM_FEWSHOTS = [
    "User: hi\nAssistant: 欢迎宝子来直播间，今天想聊点什么呀？",
    "User: 你今天怎么这么晚\nAssistant: 来啦来啦，今天稍微忙了一点，但我还是想快点来陪大家聊天～你今天过得怎么样？",
    "User: 你推荐点什么\nAssistant: 可以呀宝子，你更想看轻松一点的内容，还是更实用一点的分享？",
]

LIVESTREAM_RULE_TEMPLATE = HumanMessagePromptTemplate.from_template(
    "The following are experiences you gathered on livestream companion chat tasks. "
    "Use these as references:\n{rules}\n"
)

LIVESTREAM_SYSTEM_CRITIQUE_INSTRUCTIONS = {
    "compare": "Compare a successful livestream reply trajectory against a failed one and summarize general rules for improving engagement, persona consistency, and safety.",
    "all_success": "Summarize general reusable rules from successful livestream reply trajectories.",
    "all_fail": "Summarize general reusable rules from failed livestream reply trajectories.",
    "all_reflection": "Summarize reusable rules from reflections on livestream reply trajectories.",
    "compare_existing_rules": "Compare a successful livestream reply trajectory against a failed one and update the existing rule set.",
    "all_success_existing_rules": "Summarize successful livestream reply trajectories and refine the existing rule set.",
}

LIVESTREAM_HUMAN_CRITIQUES = HUMAN_CRITIQUES
