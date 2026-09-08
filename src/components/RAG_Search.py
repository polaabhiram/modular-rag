from src.components.VectorStore import FaissVectorStore
from src.components.DataIngestion import DataIngestion
from src.components.Embeddings import EmbeddingManager
from langchain_groq import ChatGroq
import dotenv
import os

dotenv.load_dotenv()

print("Groq API key loaded:", bool(os.getenv("GROQ_API_KEY")))


class RAGSearch:

    def __init__(
        self,
        persist_dir: str = "faiss_store",
        embedding_model: str = "all-MiniLM-L6-v2",
        chunk_size: int = 1000,
        chunk_overlap: int = 200,
        llm_model: str = "openai/gpt-oss-20b",
        temperature: float = 0.2,
        max_tokens: int = 500
    ):
        self.vector_store = FaissVectorStore(
            persist_dir,
            embedding_model,
            chunk_size,
            chunk_overlap
        )

        self.embedding_manager = EmbeddingManager(
            embedding_model,
            chunk_size,
            chunk_overlap
        )

        self.llm_model = llm_model
        self.temperature = temperature
        self.max_tokens = max_tokens

        self.model = ChatGroq(
            model_name=self.llm_model,
            temperature=self.temperature,
            max_tokens=self.max_tokens
        )

    def ingest_documents(self, path: str):
        data_ingestion = DataIngestion(path)

        text_docs, pdf_docs = data_ingestion.load_documents()

        all_docs = text_docs + pdf_docs

        self.vector_store.build_from_documents(all_docs)

    def query(self, query_text: str, top_k: int = 5):
        return self.vector_store.query(
            query_text,
            top_k=top_k
        )

    def generate_answer(self, query: str, top_k: int = 3):

        results = self.query(query, top_k=top_k)

        context_parts = []

        for i, result in enumerate(results, start=1):

            metadata = result["metadata"]

            text = metadata.get("text", "")
            source = metadata.get("source", "Unknown source")
            doc_type = metadata.get("type", "unknown")

            if doc_type == "pdf":

                page = metadata.get(
                    "page_label",
                    metadata.get("page", "Unknown")
                )

                citation = f"{source}, page {page}"

            else:
                citation = source

            context_parts.append(
                f"[Source {i}]\n"
                f"Content: {text}\n"
                f"Source: {citation}"
            )

        context = "\n\n".join(context_parts)

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
7. If multiple sources support a claim, use multiple citations.
8. Do not create citation numbers that do not exist.
9. If the sources do not contain enough information to answer the question,
   say:
   "I don't have enough information in the provided sources."
10. Do not include filenames, file paths, page numbers, or a Sources section.
11. Keep the answer concise.

SOURCES:
{context}

QUESTION:
{query}

ANSWER:
"""

        response = self.model.invoke(prompt)

        answer = response.content

        # Replace [1], [2], [3] with actual citations
        for i, result in enumerate(results, start=1):

            metadata = result["metadata"]

            source = metadata.get(
                "source",
                "Unknown source"
            )

            filename = os.path.basename(source)

            if metadata.get("type") == "pdf":

                page = metadata.get(
                    "page_label",
                    metadata.get("page", "Unknown")
                )

                citation = f"[{i}] {filename}, page {page}"

            else:

                citation = f"[{i}] {filename}"

            answer = answer.replace(
                f"[{i}]",
                citation
            )

        return answer


if __name__ == "__main__":

    path = "/Users/abhiram/Documents/RAG with citation/files"

    rag_search = RAGSearch()

    rag_search.ingest_documents(path)

    query = "What is NovaDesk?"

    results = rag_search.query(
        query,
        top_k=3
    )

    print("\n--- Retrieved Sources ---")

    for i, result in enumerate(results, start=1):

        metadata = result["metadata"]

        print(f"\n[{i}]")
        print("Source:", metadata.get("source"))
        print("Type:", metadata.get("type"))
        print("Page:", metadata.get("page_label"))
        print("Distance:", result["distance"])
        print("Text:", metadata.get("text", "")[:300])

    answer = rag_search.generate_answer(
        query,
        top_k=3
    )

    print("\n--- Answer ---")
    print(answer)