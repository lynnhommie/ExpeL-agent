import joblib
import json
import random

from .base import BaseEnv
from .hotpotqa.hotpotqa import QAEnv
from .livestream.livestream import LivestreamChatEnv

try:
    from .fever.fever import FeverEnv
except Exception:
    FeverEnv = None

try:
    from .alfworld.alfworld import AlfworldEnv
except Exception:
    AlfworldEnv = None

try:
    from .webshop.webshop import WebshopEnv
except Exception:
    WebshopEnv = None

from utils import get_env_name_from_gamefile

# Taken from ReAct Github
idxs = list(range(7405))
random.Random(233).shuffle(idxs)

INIT_TASKS_FN = dict(
    hotpotqa=lambda cfg: [
        {
        'task': f'{cfg.benchmark.task_prefix}{row["question"]}',
        'env_kwargs': {
            'question': row['question'],
            'key': row['answer'],
        },
        'env_name': 'hotpotqa',
    } for _, row in joblib.load(cfg.benchmark.task_file).reset_index(drop=True).iterrows()],
    # 100 tasks for fever
    fever=lambda cfg: [{
        'task': cfg.benchmark.task_prefix + FeverEnv(idx).reset().replace('Claim: ', ''),
        'env_kwargs': {
            'idx': idx,
        },
        'env_name': 'fever',
    } for idx in idxs[:100]],
    alfworld=lambda cfg: [
        {
        'task': f'{cfg.benchmark.task_prefix}{row["goal"]}',
        'env_kwargs': {
            'config': cfg.benchmark,
            "gamefile": row["gamefile"],
        },
        'env_name': get_env_name_from_gamefile(row['gamefile'])
        } for row in json.load(open(cfg.benchmark.task_file, "r"))
    ],
    webshop=lambda cfg: [
        {
        'task': f'{cfg.benchmark.task_prefix}{row["task"]}',
        'env_kwargs': {
            'session_idx': row["session_idx"],
        },
        'env_name': 'webshop'
        } for row in json.load(open(cfg.benchmark.task_file, "r"))
    ],
    livestream=lambda cfg: [
        {
        'task': f'{cfg.benchmark.task_prefix}{row["task"]}',
        'env_kwargs': {
            'creator_name': 'host',
            'persona_description': 'friendly and engaging livestream host'
        },
        'env_name': 'livestream'
        } for row in json.load(open(cfg.benchmark.task_file, "r"))
    ],
)

ENVS = dict(hotpotqa=QAEnv, fever=FeverEnv, alfworld=AlfworldEnv, webshop=WebshopEnv, livestream=LivestreamChatEnv)
