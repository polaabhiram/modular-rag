import os
from langchain_community.document_loaders import TextLoader, PyPDFLoader

SUPPORTED = {".pdf": "pdf", ".txt": "text"}


class DataIngestion:
    def __init__(self, path: str):
        self.path = path

    @staticmethod
    def load_file(file_path: str):
        """Load a single .pdf or .txt file and tag every doc with its type."""
        ext = os.path.splitext(file_path)[1].lower()
        if ext not in SUPPORTED:
            raise ValueError(f"Unsupported file type: {ext}")
        if ext == ".pdf":
            docs = PyPDFLoader(file_path).load()
        else:
            docs = TextLoader(file_path, encoding="utf-8").load()
        for doc in docs:
            doc.metadata["type"] = SUPPORTED[ext]
        return docs

    def _load_dir(self, sub: str):
        folder = os.path.join(self.path, sub)
        docs = []
        if not os.path.isdir(folder):
            return docs
        for name in sorted(os.listdir(folder)):
            full = os.path.join(folder, name)
            if os.path.isfile(full) and os.path.splitext(name)[1].lower() in SUPPORTED:
                docs.extend(self.load_file(full))
        return docs

    def load_documents(self):
        if not os.path.exists(self.path):
            raise FileNotFoundError(f"The specified path '{self.path}' does not exist.")
        return self._load_dir("txt"), self._load_dir("pdfs")


if __name__ == "__main__":
    text_docs, pdf_docs = DataIngestion("files").load_documents()
    print("text:", len(text_docs), "pdf:", len(pdf_docs))