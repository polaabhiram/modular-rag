from sentence_transformers import SentenceTransformer
from langchain_text_splitters import RecursiveCharacterTextSplitter
from src.components.DataIngestion import DataIngestion
import warnings


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
    warnings.filterwarnings("ignore")
    path = "/Users/abhiram/Documents/RAG with citation/files"
    data_ingestion = DataIngestion(path)
    text_docs, pdf_docs = data_ingestion.load_documents()
    print("Number of text documents:", len(text_docs))
    print("Number of PDF documents:", len(pdf_docs))

    for i, doc in enumerate(text_docs):
        print(f"\n--- Text document {i} ---")
        print("Content length:", len(doc.page_content))
        print("Preview:", repr(doc.page_content[:200]))
        print("Metadata:", doc.metadata)

    for i, doc in enumerate(pdf_docs):
        print(f"\n--- PDF document {i} ---")
        print("Content length:", len(doc.page_content))
        print("Preview:", repr(doc.page_content[:200]))
        print("Metadata:", doc.metadata)

     
    print("Total docs loaded:", len(text_docs) + len(pdf_docs))

    embedding_manager = EmbeddingManager()
    print("Chunking documents...")
    text_chunks = embedding_manager.chunk_docs(text_docs)
    pdf_chunks = embedding_manager.chunk_docs(pdf_docs)

    print("Chunked documents:")
    print("Total text chunks:", len(text_chunks))
    print("Total pdf chunks:", len(pdf_chunks)) 

    print("Generating embeddings...")
    embeddings_text = embedding_manager.generate_embeddings(text_chunks)
    embeddings_pdf = embedding_manager.generate_embeddings(pdf_chunks)

    print("Embeddings generated:")
    print("Embeddings for text chunks:", embeddings_text.shape)
    print("Embeddings for pdf chunks:", embeddings_pdf.shape)