from typing import Callable, List
import time

from langchain.chat_models import ChatOpenAI
from langchain.schema import ChatMessage
import openai


DASHSCOPE_OPENAI_BASE_URL = "https://dashscope.aliyuncs.com/compatible-mode/v1"


class OpenAICompatibleWrapper:
    def __init__(self, llm_name: str, api_key: str, long_ver: bool):
        self.model_name = llm_name
        if long_ver and 'gpt' in llm_name:
            llm_name = 'gpt-3.5-turbo-16k'
        self.llm = ChatOpenAI(
            model=llm_name,
            temperature=0.0,
            openai_api_key=api_key,
            openai_api_base=DASHSCOPE_OPENAI_BASE_URL if 'qwen' in llm_name else None,
        )

    def __call__(self, messages: List[ChatMessage], stop: List[str] = [], replace_newline: bool = True) -> str:
        kwargs = {}
        if stop != []:
            kwargs['stop'] = stop
        for i in range(6):
            try:
                output = self.llm(messages, **kwargs).content.strip('\n').strip()
                break
            except openai.error.RateLimitError:
                print(f'\nRetrying {i}...')
                time.sleep(1)
        else:
            raise RuntimeError('Failed to generate response')

        if replace_newline:
            output = output.replace('\n', '')
        return output


def LLM_CLS(llm_name: str, openai_api_key: str, long_ver: bool) -> Callable:
    if 'gpt' in llm_name or 'qwen' in llm_name:
        return OpenAICompatibleWrapper(llm_name, openai_api_key, long_ver)
    raise ValueError(f"Unknown LLM model name: {llm_name}")
