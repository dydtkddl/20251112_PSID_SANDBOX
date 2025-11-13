import os
import sys
import logging
from pathlib import Path, PureWindowsPath
from urllib.parse import quote, unquote
from datetime import datetime

from fastapi import FastAPI, Request, File, UploadFile, Response
from fastapi.responses import HTMLResponse, FileResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

# ─────────────────────────────────────────────
ROOT_DIR = Path("C:/Users/KHU_PSID/Desktop/KHU_PSID").resolve()
ROOT_DIR = Path("D:/00_작업장").resolve()
PORT = 8127

logging.basicConfig(
    level=logging.INFO,
    stream=sys.stdout,
    encoding="utf-8",
    format="%(asctime)s | %(levelname)s | %(message)s",
)
app = FastAPI(title="Responsive File Browser")
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")
def human_readable_size(size_bytes: int) -> str:
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024**2:
        return f"{size_bytes / 1024:.2f} KB"
    elif size_bytes < 1024**3:
        return f"{size_bytes / 1024**2:.2f} MB"
    else:
        return f"{size_bytes / 1024**3:.2f} GB"

def datetimeformat(value):
    try:
        return datetime.fromtimestamp(value).strftime("%Y-%m-%d %H:%M")
    except Exception:
        return "-"
templates.env.filters["datetimeformat"] = datetimeformat

@app.middleware("http")
async def skip_ngrok_warning(request, call_next):
    response: Response = await call_next(request)
    response.headers["ngrok-skip-browser-warning"] = "true"
    return response

def safe_join(base: Path, target: str) -> Path:
    base = base.resolve()
    target_path = (base / unquote(target)).resolve(strict=False)
    if not str(PureWindowsPath(target_path)).startswith(str(PureWindowsPath(base))):
        raise PermissionError("상위 경로 접근 차단됨")
    return target_path

# ─────────────────────────────────────────────
@app.get("/", response_class=HTMLResponse)
async def home():
    return RedirectResponse(url="/browse")

@app.get("/browse", response_class=HTMLResponse)
async def browse(request: Request, path: str = ""):
    try:
        abs_path = safe_join(ROOT_DIR, path)
        logging.info(f"📁 탐색 중: {abs_path}")

        if not abs_path.exists():
            logging.warning(f"X 경로 없음: {abs_path}")
            return HTMLResponse(f"<h3>X 경로 없음: {abs_path}</h3>", status_code=404)

        entries = []
        for item in sorted(abs_path.iterdir(), key=lambda x: (not x.is_dir(), x.name.lower())):
            rel = os.path.relpath(item, ROOT_DIR)
            entries.append({
                "name": item.name,
                "path": rel.replace("\\", "/"),
                "is_dir": item.is_dir(),
                "size": "-" if item.is_dir() else human_readable_size(item.stat().st_size),
                "mtime": item.stat().st_mtime
            })

        parent = str(Path(path).parent).replace("\\", "/") if path else ""
        breadcrumb = path.split("/") if path else []

        return templates.TemplateResponse(
            "browse.html",
            {
                "request": request,
                "path": path,
                "abs_path": abs_path,
                "entries": entries,
                "parent": parent,
                "breadcrumb": breadcrumb,
            },
        )

    except PermissionError:
        return HTMLResponse("<h3>X 접근 불가 경로</h3>", status_code=403)

@app.get("/download")
async def download(path: str):
    try:
        file_path = safe_join(ROOT_DIR, path)
        if not file_path.is_file():
            return HTMLResponse("<h3>X 파일 없음</h3>", status_code=404)
        return FileResponse(file_path, filename=file_path.name)
    except PermissionError:
        return HTMLResponse("<h3>X 상위 경로 접근 불가</h3>", status_code=403)

@app.post("/upload")
async def upload(path: str = "", file: UploadFile = File(...)):
    try:
        folder_path = safe_join(ROOT_DIR, path)
        dest = folder_path / file.filename
        with open(dest, "wb") as f:
            f.write(await file.read())
        logging.info(f"[OK] Uploaded: {dest}")
        return RedirectResponse(url=f"/browse?path={quote(path)}", status_code=303)
    except PermissionError:
        return HTMLResponse("<h3>X 업로드 불가</h3>", status_code=403)

if __name__ == "__main__":
    import uvicorn
    logging.info(f"!!!!!!!!!!!!!!!!Running: http://127.0.0.1:{PORT}")
    uvicorn.run(app, host="0.0.0.0", port=PORT)
