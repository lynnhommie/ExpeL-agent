from typing import Callable, Any, Dict, List, Optional
import os

from pydantic import BaseModel, Extra, Field
from langchain.retrievers import SVMRetriever, KNNRetriever
from langchain.embeddings import OpenAIEmbeddings, HuggingFaceEmbeddings
from pydantic import BaseModel
from langchain.embeddings.base import Embeddings

from .episode import Trajectory


class DashScopeEmbeddings(BaseModel, Embeddings):
    """Embeddings via DashScope text-embedding-v2 — no local model download needed."""

    model_name: str = "text-embedding-v2"
    api_key: Optional[str] = None

    class Config:
        extra = Extra.forbid

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if self.api_key is None:
            object.__setattr__(self, 'api_key',
                os.getenv('QWEN_API_KEY') or os.getenv('OPENAI_API_KEY'))

    def _embed(self, texts: List[str]) -> List[List[float]]:
        from openai import OpenAI
        client = OpenAI(
            api_key=self.api_key,
            base_url="https://dashscope.aliyuncs.com/compatible-mode/v1"
        )
        # DashScope supports up to 25 texts per call
        result = []
        batch = 25
        for i in range(0, len(texts), batch):
            resp = client.embeddings.create(
                model=self.model_name,
                input=texts[i:i + batch],
            )
            result.extend([d.embedding for d in resp.data])
        return result

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        return self._embed([t.replace("\n", " ") for t in texts])

    def embed_query(self, text: str) -> List[float]:
        return self._embed([text.replace("\n", " ")])[0]


def choose_embedder(key: str) -> Callable:
    if key == 'openai':
        return OpenAIEmbeddings
    if key == 'huggingface':
        return DashScopeEmbeddings   # swap HuggingFace for DashScope when no local model
    if key == 'dashscope':
        return DashScopeEmbeddings
    return DashScopeEmbeddings       # default fallback


def choose_retriever(key: str) -> Callable:
    if key == 'svm':
        return SVMRetriever
    return KNNRetriever


EMBEDDERS = choose_embedder
RETRIEVERS = choose_retriever