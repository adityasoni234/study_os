"""Embedding providers behind ``app.retrieval.types.EmbeddingProvider``.

Two implementations, both 1536-dimensional so the pgvector column fits either:

* ``MockEmbedding`` — deterministic, offline, zero-dependency. Signed feature
  hashing of a positional-decay bag of words (see the class docstring).
* ``OpenAIEmbedding`` — POST /v1/embeddings over httpx with batching, timeout
  and retries; errors surface as safe ``AppError`` messages, never payloads.

Resolution (``get_embedding_provider``) mirrors settings.embedding_provider:
``auto`` uses OpenAI iff an API key exists and ai_mode != "mock", else mock.
"""

from __future__ import annotations

import hashlib
import math
import re
import time
from functools import lru_cache

try:  # httpx is only needed by the live provider; mock mode works without it.
    import httpx
except ImportError:  # pragma: no cover - exercised only on minimal installs
    httpx = None  # type: ignore[assignment]

from app.config import settings
from app.db.vector_type import EMBEDDING_DIM
from app.retrieval.types import EmbeddingProvider
from app.utils.errors import AppError

_TOKEN_RE = re.compile(r"[a-z0-9]+")

# Small, fixed stopword list: keeps function words from creating fake overlap
# between unrelated texts ("the", "of", ... appear everywhere).
_STOPWORDS = frozenset(
    """a an and are as at be been being by can cannot could did do does doing for from
    had has have having he her hers him his how i if in into is it its me my no nor not
    of on or our ours she so some such than that the their theirs them then there these
    they this those to too until up was we were what when where which while who whom why
    will with would you your yours""".split()
)

# Each token lands in two buckets (two salted hashes) with independent signs:
# a single hash collision between unrelated tokens then contributes only half
# a match, and expected collision noise cancels around zero.
_HASH_SALTS = (b"studyos-a", b"studyos-b")


class MockEmbedding:
    """Deterministic offline embedding: hashed positional-decay bag of words.

    Design:
    - tokenize to lowercase [a-z0-9]+ tokens, drop stopwords;
    - the occurrence at (stopword-filtered) position ``i`` weighs ``1/(1+i)``,
      so a chunk's opening tokens dominate its vector — chunks open with
      their theme, which acts like an implicit title;
    - each token is hashed (salted blake2b) into 2 of 1536 buckets with a
      ±1 sign (signed feature hashing), weights summed per bucket;
    - the vector is L2-normalised, so dot product == cosine similarity.

    RELATED texts share token buckets and score high (a "precision recall"
    query ranks the seeded p.14 passage, which opens with those words, first);
    unrelated texts share almost nothing and score ~0.
    """

    name = "mock"
    dim = EMBEDDING_DIM

    def embed(self, texts: list[str]) -> list[list[float]]:
        return [self._embed_one(text) for text in texts]

    def _embed_one(self, text: str) -> list[float]:
        vec = [0.0] * self.dim
        for position, token in enumerate(_tokenize(text)):
            weight = 1.0 / (1.0 + position)
            for index, signed in _token_buckets(token):
                vec[index] += signed * weight
        norm = math.sqrt(sum(x * x for x in vec))
        if norm > 0.0:
            vec = [x / norm for x in vec]
        return vec


def _tokenize(text: str) -> list[str]:
    return [t for t in _TOKEN_RE.findall(text.lower()) if t not in _STOPWORDS]


@lru_cache(maxsize=65536)
def _token_buckets(token: str) -> tuple[tuple[int, float], ...]:
    """Stable (bucket index, ±1/sqrt(2)) pairs for a token. Never uses hash()
    (per-process salted); blake2b keeps it identical across runs/machines."""
    out = []
    for salt in _HASH_SALTS:
        digest = hashlib.blake2b(token.encode("utf-8"), digest_size=8, key=salt).digest()
        value = int.from_bytes(digest, "big")
        sign = 1.0 if (value >> 13) & 1 else -1.0
        out.append((value % EMBEDDING_DIM, sign / math.sqrt(2.0)))
    return tuple(out)


_OPENAI_EMBEDDINGS_URL = "https://api.openai.com/v1/embeddings"
_BATCH_SIZE = 100
# Up to 2 extra attempts after the first (matches app/ai/providers.py).
_RETRY_BACKOFF_S: tuple[float, ...] = (0.5, 1.5)


class OpenAIEmbedding:
    """OpenAI /v1/embeddings over httpx. Batched, retried, safe errors only."""

    name = "openai"
    dim = EMBEDDING_DIM

    def __init__(self) -> None:
        self._client: "httpx.Client | None" = None

    def embed(self, texts: list[str]) -> list[list[float]]:
        vectors: list[list[float]] = []
        for start in range(0, len(texts), _BATCH_SIZE):
            vectors.extend(self._embed_batch(texts[start : start + _BATCH_SIZE]))
        return vectors

    def _embed_batch(self, batch: list[str]) -> list[list[float]]:
        if not batch:
            return []
        if httpx is None:  # pragma: no cover - minimal installs only
            raise AppError(
                "AI_UNAVAILABLE", "Embeddings are unavailable (HTTP client not installed).", 503
            )
        if self._client is None:
            self._client = httpx.Client(timeout=settings.request_timeout_s)
        model = settings.openai_embedding_model
        payload: dict = {"model": model, "input": batch}
        if model.startswith("text-embedding-3"):
            payload["dimensions"] = self.dim  # older models reject this param
        headers = {"Authorization": f"Bearer {settings.openai_api_key}"}

        attempts = len(_RETRY_BACKOFF_S) + 1
        for attempt in range(attempts):
            try:
                response = self._client.post(
                    _OPENAI_EMBEDDINGS_URL, headers=headers, json=payload
                )
            except httpx.HTTPError:
                response = None  # timeout / network error → retry
            else:
                if response.status_code < 400:
                    return self._parse(response, expected=len(batch))
                if not (response.status_code == 429 or response.status_code >= 500):
                    raise AppError(
                        "AI_UNAVAILABLE",
                        "The embedding service rejected the request.",
                        503,
                    )
            if attempt < attempts - 1:
                time.sleep(_RETRY_BACKOFF_S[attempt])
        raise AppError(
            "AI_UNAVAILABLE", "The embedding service is briefly unreachable — please retry.", 503
        )

    def _parse(self, response: "httpx.Response", expected: int) -> list[list[float]]:
        try:
            body = response.json()
            items = sorted(body["data"], key=lambda item: item["index"])
            vectors = [[float(x) for x in item["embedding"]] for item in items]
        except (ValueError, KeyError, TypeError) as exc:
            raise AppError(
                "AI_UNAVAILABLE", "The embedding service returned an unreadable response.", 503
            ) from exc
        if len(vectors) != expected or any(len(v) != self.dim for v in vectors):
            raise AppError(
                "AI_UNAVAILABLE", "The embedding service returned an unexpected shape.", 503
            )
        return vectors


def _resolved_provider_name() -> str:
    mode = settings.embedding_provider
    if mode == "auto":
        return "openai" if (settings.openai_api_key and settings.ai_mode != "mock") else "mock"
    return mode if mode in ("mock", "openai") else "mock"


@lru_cache(maxsize=4)
def _provider_instance(name: str) -> EmbeddingProvider:
    return OpenAIEmbedding() if name == "openai" else MockEmbedding()


def get_embedding_provider() -> EmbeddingProvider:
    """Provider for the current settings (instances cached per resolved name)."""
    return _provider_instance(_resolved_provider_name())
