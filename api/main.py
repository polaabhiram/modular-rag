"""FastAPI backend + static frontend.   Run:  uvicorn main:app --reload"""
from pathlib import Path

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from src.components.RAG_Search import RAGSearch

DATA_DIR = Path("files")
FOLDERS = {".pdf": DATA_DIR / "pdfs", ".txt": DATA_DIR / "txt"}
MAX_UPLOAD_MB = 25
for folder in FOLDERS.values():
    folder.mkdir(parents=True, exist_ok=True)

app = FastAPI(title="RAG with citation")
rag = RAGSearch()

# First run: build the index from whatever is already in files/
if not rag.ready and any(f.is_file() for d in FOLDERS.values() for f in d.iterdir()):
    rag.ingest_documents(str(DATA_DIR))


class Question(BaseModel):
    question: str = Field(min_length=1, max_length=1000)
    top_k: int = Field(default=3, ge=1, le=10)


def _status():
    return {"ready": rag.ready, "documents": rag.vector_store.documents()}


@app.get("/api/status")
def status():
    return _status()


@app.post("/api/upload")
async def upload(files: list[UploadFile] = File(...)):
    saved, errors = [], []
    for f in files:
        name = Path(f.filename or "").name
        ext = Path(name).suffix.lower()
        if ext not in FOLDERS:
            errors.append(f"{name or 'file'}: only .pdf and .txt are supported")
            continue
        data = await f.read()
        if len(data) > MAX_UPLOAD_MB * 1024 * 1024:
            errors.append(f"{name}: larger than {MAX_UPLOAD_MB} MB")
            continue
        dest = FOLDERS[ext] / name
        if dest.exists():
            errors.append(f"{name}: already uploaded (use Rebuild index after replacing a file)")
            continue
        dest.write_bytes(data)
        try:
            rag.add_file(str(dest))
            saved.append(name)
        except Exception as e:  # unreadable PDF, bad encoding, ...
            dest.unlink(missing_ok=True)
            errors.append(f"{name}: could not be read ({e})")
    return {"saved": saved, "errors": errors, **_status()}


@app.post("/api/ingest")
def rebuild():
    """Re-embed everything in files/ from scratch."""
    n = rag.ingest_documents(str(DATA_DIR))
    return {"chunks": n, **_status()}


@app.post("/api/query")
def query(body: Question):
    if not rag.ready:
        raise HTTPException(400, "No documents indexed yet. Upload a PDF or TXT file first.")
    try:
        return rag.generate_answer(body.question.strip(), top_k=body.top_k)
    except Exception as e:
        raise HTTPException(502, f"The language model request failed: {e}")


# Serve the built React app (run `npm run build` in frontend/). API routes above take priority.
DIST = Path("frontend/dist")
if DIST.exists():
    app.mount("/", StaticFiles(directory=DIST, html=True), name="web")