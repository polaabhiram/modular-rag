from src.components.VectorStore import FaissVectorStore
from src.components.DataIngestion import DataIngestion
from src.components.Embeddings import EmbeddingManager
from langchain_groq import ChatGroq
import dotenv
import os

dotenv.load_dotenv()  # Load environment variables from .env file
print("Groq API key loaded:", bool(os.getenv("GROQ_API_KEY")))

class RAGSearch:
    def __init__(self, persist_dir: str = "faiss_store", embedding_model: str = "all-MiniLM-L6-v2", chunk_size: int = 1000, chunk_overlap: int = 200 ,llm_model: str = "openai/gpt-oss-20b",temperature:float=0.7,max_tokens:int=500):
        self.vector_store = FaissVectorStore(persist_dir, embedding_model, chunk_size, chunk_overlap)
        self.embedding_manager = EmbeddingManager(embedding_model, chunk_size, chunk_overlap)
        self.llm_model = llm_model
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.model=ChatGroq(model_name=self.llm_model, temperature=self.temperature, max_tokens=self.max_tokens)

    def ingest_documents(self, path: str):
        data_ingestion = DataIngestion(path)
        text_docs, pdf_docs = data_ingestion.load_documents()
        all_docs = text_docs + pdf_docs
        self.vector_store.build_from_documents(all_docs)

    def query(self, query_text: str, top_k: int = 5):
        return self.vector_store.query(query_text, top_k=top_k)

    def generate_answer(self, query: str, top_k: int = 3):

        # Retrieve relevant chunks + metadata
        results = self.query(query, top_k=top_k)

        # Build context with explicit source IDs
        context_parts = []

        for i, result in enumerate(results, start=1):

            metadata = result["metadata"]

            text = metadata.get("text", "")
            source = metadata.get("source", "Unknown source")
            doc_type = metadata.get("type", "unknown")

            if doc_type == "pdf":
                page = metadata.get("page_label", metadata.get("page", "Unknown"))
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
    You are a question-answering assistant that answers questions using
    only the provided context.

    RULES:
    1. Use only information supported by the provided context.
    2. Do not invent or assume information that is not present.
    3. If the context does not contain enough information to answer the
    question, say: "I don't have enough information in the provided sources."
    4. Every factual claim in your answer must have a citation.
    5. Use citations in the format [1], [2], [3].
    6. The citation number must correspond to the [Source N] provided below.
    7. You may use multiple citations for a claim, such as [1][2].
    8. Do not create citations that are not present in the context.

    CONTEXT:
    {context}

    QUESTION:
    {query}

    ANSWER:
    """

        
        answer = self.model.invoke(prompt)

        return answer.content

if __name__ == "__main__":
    path = "/Users/abhiram/Documents/RAG with citation/files"
    rag_search = RAGSearch()
    rag_search.ingest_documents(path)
    query = "What is NovaDesk?"
    results = rag_search.query(query, top_k=3)

print("\n--- Retrieved Sources ---")

for i, result in enumerate(results, start=1):
    metadata = result["metadata"]

    print(f"\n[{i}]")
    print("Source:", metadata.get("source"))
    print("Type:", metadata.get("type"))
    print("Page:", metadata.get("page_label"))
    print("Distance:", result["distance"])
    print("Text:", metadata.get("text", "")[:300])

answer = rag_search.generate_answer(query, top_k=3)

print("\n--- Answer ---")
print(answer)
