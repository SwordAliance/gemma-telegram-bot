"""Это база знаний. Для старта подойдет TF-IDF retrieval.
читает все файлы из knowledge/;
делит их на чанки;
строит TF-IDF матрицу;
по запросу возвращает самые релевантные куски."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from joblib import dump, load
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


@dataclass
class Chunk:
    source: str
    text: str


class KnowledgeBase:
    def __init__(self, knowledge_dir: Path, index_path: Path) -> None:
        self.knowledge_dir = knowledge_dir
        self.index_path = index_path
        self.vectorizer: TfidfVectorizer | None = None
        self.matrix = None
        self.chunks: list[Chunk] = []

    def _read_text_file(self, path: Path) -> str:
        return path.read_text(encoding="utf-8", errors="ignore")

    def _chunk_text(self, text: str, max_chars: int = 1200, overlap: int = 150) -> list[str]:
        text = " ".join(text.split())
        if not text:
            return []
        chunks = []
        start = 0
        while start < len(text):
            end = min(len(text), start + max_chars)
            chunks.append(text[start:end])
            if end == len(text):
                break
            start = end - overlap
        return chunks

    def rebuild(self) -> None:
        texts: list[str] = []
        chunks: list[Chunk] = []

        for path in sorted(self.knowledge_dir.rglob("*")):
            if path.is_dir():
                continue
            if path.suffix.lower() not in {".txt", ".md", ".rst"}:
                continue
            content = self._read_text_file(path)
            for piece in self._chunk_text(content):
                texts.append(piece)
                chunks.append(Chunk(source=str(path.relative_to(self.knowledge_dir)), text=piece))

        self.vectorizer = TfidfVectorizer(stop_words=None, max_features=25000)
        self.matrix = self.vectorizer.fit_transform(texts) if texts else None
        self.chunks = chunks
        dump({"chunks": self.chunks, "vectorizer": self.vectorizer, "matrix": self.matrix}, self.index_path)

    def load(self) -> bool:
        if not self.index_path.exists():
            return False
        payload = load(self.index_path)
        self.chunks = payload["chunks"]
        self.vectorizer = payload["vectorizer"]
        self.matrix = payload["matrix"]
        return True

    def search(self, query: str, top_k: int = 4, min_score: float = 0.12) -> list[Chunk]:
        if not query.strip():
            return []
        if self.vectorizer is None or self.matrix is None or not self.chunks:
            return []

        q_vec = self.vectorizer.transform([query])
        scores = cosine_similarity(q_vec, self.matrix).ravel()
        ranked = sorted(enumerate(scores), key=lambda x: x[1], reverse=True)

        results: list[Chunk] = []
        for idx, score in ranked[:top_k]:
            if score < min_score:
                continue
            results.append(self.chunks[idx])
        return results
