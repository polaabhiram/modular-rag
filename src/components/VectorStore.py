import os
import pickle
from collections import Counter
from typing import Any, List

import faiss
import numpy as np

from src.components.Embeddings import EmbeddingManager


class FaissVectorStore:
    def __init__(self, persist_dir: str = "faiss_store", embedding_model: str = "all-MiniLM-L6-v2",
                 chunk_size: int = 1000, chunk_overlap: int = 200):
        self.persist_dir = persist_dir
        os.makedirs(self.persist_dir, exist_ok=True)
        self.index = None
        self.metadata: List[dict] = []
        # One embedding model shared for indexing AND querying
        self.emb = EmbeddingManager(embedding_model, chunk_size, chunk_overlap)
        print(f"[INFO] Loaded embedding model: {embedding_model}")

    # ---------- state ----------
    @property
    def ready(self) -> bool:
        return self.index is not None and self.index.ntotal > 0

    def reset(self):
        self.index = None
        self.metadata = []

    def documents(self):
        """One entry per source file: name, type, chunk count."""
        counts = Counter((m.get("source", "unknown"), m.get("type", "unknown")) for m in self.metadata)
        return [{"name": os.path.basename(s), "type": t, "chunks": c} for (s, t), c in counts.items()]

    # ---------- indexing ----------
    def add_documents(self, documents: List[Any]):
        """Chunk, embed and append documents to the index, then persist."""

        if not documents:
            return 0

        chunks = self.emb.chunk_docs(documents)

        # PDF may contain only images / scanned pages
        if not chunks:
            print("[WARNING] No text chunks extracted from document.")
            return 0

        embeddings = np.asarray(
            self.emb.generate_embeddings(chunks),
            dtype="float32"
        )

        # Extra safety check
        if embeddings.ndim != 2 or embeddings.shape[0] == 0:
            print("[WARNING] No embeddings generated.")
            return 0

        metadatas = [
            {
                "text": c.page_content,
                **c.metadata
            }
            for c in chunks
        ]

        if self.index is None:
            self.index = faiss.IndexFlatL2(embeddings.shape[1])

        self.index.add(embeddings)
        self.metadata.extend(metadatas)

        self.save()

        print(
            f"[INFO] Added {len(chunks)} chunks "
            f"(total {self.index.ntotal})"
        )

        return len(chunks)
    def build_from_documents(self, documents: List[Any]):
        """Full rebuild: drops the old index first so re-ingesting never duplicates chunks."""
        self.reset()
        n = self.add_documents(documents)
        if n == 0:
            self.save()
        return n

    # ---------- persistence ----------
    def save(self):
        if self.index is None:
            # keep disk consistent when everything was removed
            for f in ("faiss.index", "metadata.pkl"):
                p = os.path.join(self.persist_dir, f)
                if os.path.exists(p):
                    os.remove(p)
            return
        faiss.write_index(self.index, os.path.join(self.persist_dir, "faiss.index"))
        with open(os.path.join(self.persist_dir, "metadata.pkl"), "wb") as f:
            pickle.dump(self.metadata, f)

    def load(self) -> bool:
        fp = os.path.join(self.persist_dir, "faiss.index")
        mp = os.path.join(self.persist_dir, "metadata.pkl")
        if not (os.path.exists(fp) and os.path.exists(mp)):
            return False
        self.index = faiss.read_index(fp)
        with open(mp, "rb") as f:
            self.metadata = pickle.load(f)
        print(f"[INFO] Loaded index with {self.index.ntotal} chunks")
        return True

    # ---------- search ----------
    def search(self, query_embedding: np.ndarray, top_k: int = 5):
        if not self.ready:
            return []
        D, I = self.index.search(query_embedding, min(top_k, self.index.ntotal))
        results = []
        for idx, dist in zip(I[0], D[0]):
            if idx < 0 or idx >= len(self.metadata):
                continue
            # vectors are unit-length, so squared L2 distance d maps to cosine = 1 - d/2
            results.append({"index": int(idx), "distance": float(dist),
                            "score": float(1 - dist / 2), "metadata": self.metadata[idx]})
        return results

    def query(self, query_text: str, top_k: int = 5):
        # normalize like the indexed vectors, otherwise distances aren't comparable
        q = self.emb.model.encode([query_text], normalize_embeddings=True).astype("float32")
        return self.search(q, top_k=top_k)