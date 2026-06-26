from langchain.schema import HumanMessage
from typing import Tuple, List

def LIVESTREAM_LLM_PARSER(raw_text: str, step_id: int, is_reflection: bool) -> Tuple[HumanMessage, str, dict]:
    """
    Parse LLM output for livestream chat.
    Expected format: the LLM output is just the reply text.
    """
    text = raw_text.strip()
    if text == "":
        text = "Sorry, I didn't catch that."
    return HumanMessage(content=text), "action", {"action": text}


def LIVESTREAM_OBSERVATION_FORMATTER(observation: str, step: int = None) -> Tuple[HumanMessage, str]:
    """
    Format observation from environment for livestream chat.
    """
    formatted = f"Observation: {observation}"
    return HumanMessage(content=formatted), "append"


def LIVESTREAM_STEP_IDENTIFIER(step: str) -> str:
    """
    Identify step type in livestream chat.
    All steps are 'action' or 'observation'.
    """
    if step.startswith("Observation:"):
        return "observation"
    return "action"


def LIVESTREAM_CYCLER(lines: List[str]) -> List[str]:
    """
    Cycle through lines for livestream chat.
    """
    return lines


def LIVESTREAM_REFLECTION_PREFIX(reflections: List[str]) -> str:
    """
    Format reflection prefix for livestream chat.
    """
    if not reflections:
        return ""
    reflection_text = "\n".join([f"- {r}" for r in reflections])
    return f"Reflection:\n{reflection_text}\n"


def LIVESTREAM_PREVIOUS_TRIALS_FORMATTER(previous_trials: List[str], include_prefix: bool = True) -> str:
    if not previous_trials:
        return ""
    trials_text = "\n".join(previous_trials)
    if not include_prefix:
        return trials_text
    return f"Previous interactions:\n{trials_text}\n"


def LIVESTREAM_STEP_STRIPPER(step: str, step_type: str) -> str:
    """
    Strip step text for livestream chat.
    """
    return step.strip()
