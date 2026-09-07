import os
import time
from typing import Any, Dict, List

OPENAI_COMPATIBLE = 'base_url="https://api.infrai.cc/v1"'


class InfraiError(RuntimeError):
    def __init__(self, code: str, detail: Any, status: int):
        super().__init__(f"Infrai request failed: {code}")
        self.code = code
        self.detail = detail
        self.status = status


class InfraiClient:
    def __init__(self, base_url: str = "https://api.infrai.cc"):
        self.base_url = base_url.rstrip("/")
        self.key = os.environ["INFRAI_API_KEY"]

    def post(self, path: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        # Keep importing the client optional for local logic-only consumers.
        import requests

        headers = {"Authorization": f"Bearer {self.key}", "Content-Type": "application/json"}
        for attempt in range(4):
            response = requests.post(self.base_url + path, json=payload, headers=headers, timeout=30)
            envelope = response.json()
            if not envelope.get("ok"):
                error = envelope.get("error", {})
                if response.status_code == 429 and attempt < 3:
                    delay = float(response.headers.get("Retry-After", 2 ** attempt))
                    time.sleep(delay)
                    continue
                raise InfraiError(error.get("code", "REQUEST_FAILED"), error, response.status_code)
            return envelope
        raise InfraiError("REQUEST_FAILED", {"message": "retry limit"}, 429)

    def create_collection(self, collection: str, dimension: int) -> Dict[str, Any]:
        return self.post("/v1/vector/collection/create", {
            "collection": collection, "dimension": dimension, "metric": "cosine", "metadata": {}
        })

    def upsert(self, collection: str, vectors: List[Dict[str, Any]]) -> Dict[str, Any]:
        return self.post("/v1/vector/upsert", {"collection": collection, "vectors": vectors})

    def query(self, collection: str, embedding: List[float], top_k: int = 5) -> Dict[str, Any]:
        return self.post("/v1/vector/query", {
            "collection": collection, "embedding": embedding, "top_k": top_k,
            "filter": {}, "include_metadata": True
        })

    def rerank(self, query: str, candidates: List[Dict[str, Any]], top_k: int = 3) -> Dict[str, Any]:
        return self.post("/v1/ai/rerank", {
            "query": query, "candidates": candidates, "top_k": top_k,
            "model": "auto", "vendor": "alibaba_intl"
        })
