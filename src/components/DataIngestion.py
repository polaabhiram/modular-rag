import os
from langchain_community.document_loaders import TextLoader, PyPDFLoader



class DataIngestion:
    def __init__(self,path:str):
        self.path = path

    def load_documents(self):
        if not os.path.exists(self.path):
            raise FileNotFoundError(f"The specified path '{self.path}' does not exist.")

        text_documents = []
        pdf_documents = []

        for file in os.listdir(os.path.join(self.path,"pdfs")):
            loader= PyPDFLoader(os.path.join(self.path,"pdfs",file))
            docs=loader.load()
            for doc in docs:
                doc.metadata["type"] = "pdf"
            pdf_documents.extend(docs)
            print(docs[0].metadata)

        for file in os.listdir(os.path.join(self.path,"txt")):
            loader = TextLoader(os.path.join(self.path,"txt",file),encoding="utf-8")
            docs = loader.load()
            
            for doc in docs:
                doc.metadata["type"] = "text"
            text_documents.extend(docs)

        
        return text_documents, pdf_documents
    
if __name__ == "__main__":
    path = "/Users/abhiram/Documents/RAG with citation/files"
    print("Loading documents from path:", path)

    data_ingestion = DataIngestion(path)
    text_docs, pdf_docs = data_ingestion.load_documents()
    
    # for doc in pdf_docs:
    #     doc.metadata["type"] = "pdf"
    print(type(text_docs[0]), len(text_docs))
    print(type(pdf_docs[0]), len(pdf_docs))  
    print()
    print('--- Sample Document Metadata ---')
    print(text_docs[0].metadata)
    print()
    print('--- Sample PDF Document Metadata ---')
    print(pdf_docs[0].metadata)
   
    print("Total docs loaded:", len(text_docs) + len(pdf_docs))