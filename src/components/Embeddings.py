from sentence_transformers import SentenceTransformer
from langchain_text_splitters import RecursiveCharacterTextSplitter
from src.components.DataIngestion import DataIngestion


class EmbeddingManager:
    def __init__(self,model_name:str = "all-MiniLM-L6-v2",chunk_size: int = 1000, chunk_overlap: int = 200):
        self.model_name=model_name
        self.model =SentenceTransformer(model_name)
        self.chunk_size=chunk_size
        self.chunk_overlap=chunk_overlap


    def chunk_docs(self,documents):
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=self.chunk_size, chunk_overlap=self.chunk_overlap)
        chunks = text_splitter.split_documents(documents)
        return chunks
 

    def generate_embeddings(self,chunks):

        # embeddings=[]
        texts=[chunk.page_content for chunk in chunks]

        embeddings = self.model.encode(
            texts,
            batch_size=32,
            show_progress_bar=True,
            normalize_embeddings=True,
        )

        return embeddings

if __name__ == "__main__":
    path = "/Users/abhiram/Documents/RAG with citation/files"
    data_ingestion = DataIngestion(path)
    text_docs, pdf_docs = data_ingestion.load_documents()
    print(type(text_docs), len(text_docs))
    print(type(pdf_docs), len(pdf_docs))  
    print("Total docs loaded:", len(text_docs) + len(pdf_docs))

    embedding_manager = EmbeddingManager()
    text_chunks = embedding_manager.chunk_docs(text_docs)
    pdf_chunks = embedding_manager.chunk_docs(pdf_docs)
    print("Total text chunks:", len(text_chunks))
    print("Total pdf chunks:", len(pdf_chunks)) 

    embeddings_text = embedding_manager.generate_embeddings(text_chunks)
    embeddings_pdf = embedding_manager.generate_embeddings(pdf_chunks)
    print("Embeddings for text chunks:", embeddings_text.shape)
    print("Embeddings for pdf chunks:", embeddings_pdf.shape)