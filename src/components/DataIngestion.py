import os
from langchain_community.document_loaders import TextLoader, PyPDFLoader



class DataIngestion:
    def __init__(self,path):
        self.path = path

    def load_documents(self):
        if not os.path.exists(self.path):
            raise FileNotFoundError(f"The specified path '{self.path}' does not exist.")

        text_documents = []
        pdf_documents = []

        for file in os.listdir(os.path.join(self.path,"pdfs")):
            loader= PyPDFLoader(os.path.join(self.path,"pdfs",file))
            docs=loader.load()
            pdf_documents.extend(docs)

        for file in os.listdir(os.path.join(self.path,"txt")):
            loader = TextLoader(os.path.join(self.path,"txt",file))
            docs = loader.load()
            text_documents.extend(docs)

        return text_documents, pdf_documents
    
if __name__ == "__main__":
    path = "/Users/abhiram/Documents/RAG with citation/files"
    data_ingestion = DataIngestion(path)
    text_docs, pdf_docs = data_ingestion.load_documents()
    print(type(text_docs), len(text_docs))
    print(type(pdf_docs), len(pdf_docs))  
    print("Total docs loaded:", len(text_docs) + len(pdf_docs))