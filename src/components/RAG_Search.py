import os
import re

import dotenv
from langchain_groq import ChatGroq

from src.components.DataIngestion import DataIngestion
from src.components.VectorStore import FaissVectorStore

dotenv.load_dotenv()

NO_INFO = "I don't have enough information in the provided sources."


class RAGSearch:
    def __init__(
        self,
        persist_dir: str = "faiss_store",
        embedding_model: str = "all-MiniLM-L6-v2",
        chunk_size: int = 1000,
        chunk_overlap: int = 200,
        llm_model: str = "openai/gpt-oss-20b",
        temperature: float = 0.2,
        max_tokens: int = 1500,  # gpt-oss is a reasoning model; 500 can truncate the visible answer
        
    ):
        if not os.getenv("GROQ_API_KEY"):
            raise RuntimeError("GROQ_API_KEY is not set. Add it to your .env file.")
        self.vector_store = FaissVectorStore(persist_dir, embedding_model, chunk_size, chunk_overlap)
        self.vector_store.load()  # reuse the saved index instead of re-embedding on every start
        self.model = ChatGroq(model_name=llm_model, temperature=temperature, max_tokens=max_tokens)
        self.ready = False

    @property
    def ready(self) -> bool:
        return self.vector_store.ready

    # ---------- ingestion ----------
    def ingest_documents(self, path: str):
        """Rebuild the whole index from <path>/pdfs and <path>/txt."""
        text_docs, pdf_docs = DataIngestion(path).load_documents()
        return self.vector_store.build_from_documents(text_docs + pdf_docs)

    def add_file(self, file_path: str):
        """Append one uploaded file to the existing index."""
        return self.vector_store.add_documents(DataIngestion.load_file(file_path))

    def query(self, query_text: str, top_k: int = 5):
        return self.vector_store.query(query_text, top_k=top_k)

    # ---------- answering ----------
    @staticmethod
    def _source_info(i: int, result: dict) -> dict:
        m = result["metadata"]
        is_pdf = m.get("type") == "pdf"
        page = None
        if is_pdf:
            page = m.get("page_label")
            if page is None and isinstance(m.get("page"), int):
                page = m["page"] + 1  # PyPDF pages are 0-indexed
        return {
            "id": i,
            "filename": os.path.basename(m.get("source", "Unknown source")),
            "type": m.get("type", "unknown"),
            "page": str(page) if page is not None else None,
            "text": m.get("text", ""),
            "score": round(result["score"], 3),
        }

    def generate_answer(self, query: str, top_k: int = 3) -> dict:
        results = self.query(query, top_k=top_k)
        if not results:
            return {"answer": NO_INFO, "sources": [], "cited": []}

        sources = [self._source_info(i, r) for i, r in enumerate(results, start=1)]
        context = "\n\n".join(f"[Source {s['id']}]\nContent: {s['text']}" for s in sources)

        prompt = f"""
You are a precise question-answering assistant.

Answer the question using ONLY the information provided in the sources.

IMPORTANT RULES:
1. Do not use outside knowledge.
2. Do not invent or assume information.
3. Every factual claim must have a citation.
4. Use citations in the format [1], [2], [3].
5. Put the citation immediately after the claim it supports.
6. The citation number must correspond exactly to the source number.
7. If multiple sources support a claim, use multiple citations like [1][2].
8. Do not create citation numbers that do not exist.
9. If the sources do not contain enough information to answer the question, say:
   "{NO_INFO}"
10. Do not include filenames, file paths, page numbers, or a Sources section.
11. Keep the answer concise.

SOURCES:
{context}

QUESTION:
{query}

ANSWER:
"""
        answer = self.model.invoke(prompt).content.strip()

        valid = {s["id"] for s in sources}
        cited = sorted({int(n) for n in re.findall(r"\[(\d+)\]", answer)} & valid)
        return {"answer": answer, "sources": sources, "cited": cited}