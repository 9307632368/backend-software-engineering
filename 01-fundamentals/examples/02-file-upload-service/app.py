"""Streaming upload/download example with file size and extension checks."""
from pathlib import Path
from tempfile import gettempdir
from uuid import uuid4
from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.responses import FileResponse

ALLOWED = {".csv", ".pdf", ".txt"}
MAX_BYTES = 1_048_576

def create_app(upload_dir: Path | str | None = None) -> FastAPI:
    api = FastAPI(title="File Upload Service")
    folder = Path(upload_dir) if upload_dir is not None else Path(gettempdir()) / "backend_upload_lab"
    folder.mkdir(parents=True, exist_ok=True)
    registry: dict[str, dict] = {}

    @api.post("/files", status_code=201)
    async def upload(file: UploadFile = File(...)):
        original = Path(file.filename or "").name
        suffix = Path(original).suffix.lower()
        if suffix not in ALLOWED:
            raise HTTPException(415, detail="Only .txt, .csv, and .pdf files are accepted")
        uid = uuid4().hex
        destination = folder / f"{uid}{suffix}"
        size = 0
        try:
            with destination.open("wb") as output:
                while chunk := await file.read(64 * 1024):
                    size += len(chunk)
                    if size > MAX_BYTES:
                        raise HTTPException(413, detail="Maximum upload size is 1 MiB")
                    output.write(chunk)
            registry[uid] = {"id": uid, "filename": original, "size": size, "path": str(destination)}
            return {key: registry[uid][key] for key in ("id", "filename", "size")}
        except Exception:
            destination.unlink(missing_ok=True)
            raise
        finally:
            await file.close()

    @api.get("/files/{file_id}")
    def download(file_id: str):
        record = registry.get(file_id)
        if record is None or not Path(record["path"]).exists():
            raise HTTPException(404, detail="File not found")
        return FileResponse(record["path"], filename=record["filename"], media_type="application/octet-stream")

    @api.delete("/files/{file_id}", status_code=204)
    def delete(file_id: str):
        record = registry.pop(file_id, None)
        if record is None:
            raise HTTPException(404, detail="File not found")
        Path(record["path"]).unlink(missing_ok=True)

    return api

app = create_app()
