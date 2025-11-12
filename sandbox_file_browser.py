# -*- coding: utf-8 -*-
"""
📂 FastAPI + Bootstrap5 + Jinja2 파일 브라우저
─────────────────────────────────────────────
✅ sandbox 루트 이하만 탐색 가능
✅ 업로드 / 다운로드 / breadcrumb / 검색 / 정렬
✅ ✅ 폴더 항상 위 + 이름순 정렬
✅ 유형 열 항상 표시
✅ ngrok-skip-browser-warning 헤더 자동 추가
"""
import os
import logging
from pathlib import Path
from urllib.parse import quote, unquote
from datetime import datetime

from fastapi import FastAPI, Request, File, UploadFile, Response
from fastapi.responses import HTMLResponse, FileResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

# ─────────────────────────────────────────────
ROOT_DIR = Path(r"C:/Users/qhfkd/Desktop/20251109_Spherical_harmonic")
PORT = 8127

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    handlers=[logging.FileHandler("browser.log"), logging.StreamHandler()],
)

app = FastAPI(title="Responsive File Browser")
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# ✅ datetimeformat 필터 추가
def datetimeformat(value):
    try:
        return datetime.fromtimestamp(value).strftime("%Y-%m-%d %H:%M")
    except Exception:
        return "-"
templates.env.filters["datetimeformat"] = datetimeformat

# ✅ ngrok 경고 제거
@app.middleware("http")
async def skip_ngrok_warning(request, call_next):
    response: Response = await call_next(request)
    response.headers["ngrok-skip-browser-warning"] = "true"
    return response

# ✅ 안전한 경로 조합
def safe_join(base: Path, target: str) -> Path:
    target_path = (base / unquote(target)).resolve()
    if not str(target_path).startswith(str(base.resolve())):
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
        if not abs_path.exists():
            return HTMLResponse(f"<h3>❌ 경로 없음: {path}</h3>", status_code=404)

        # ✅ 폴더가 항상 위로 오게 정렬
        entries = []
        for item in sorted(abs_path.iterdir(), key=lambda x: (not x.is_dir(), x.name.lower())):
            rel = os.path.relpath(item, ROOT_DIR)
            entries.append({
                "name": item.name,
                "path": rel.replace("\\", "/"),
                "is_dir": item.is_dir(),
                "size": item.stat().st_size if item.is_file() else "-",
                "mtime": item.stat().st_mtime,
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
        return HTMLResponse("<h3>🚫 접근 불가 경로</h3>", status_code=403)

# ─────────────────────────────────────────────
@app.get("/download")
async def download(path: str):
    try:
        file_path = safe_join(ROOT_DIR, path)
        if not file_path.is_file():
            return HTMLResponse("<h3>❌ 파일 없음</h3>", status_code=404)
        return FileResponse(file_path, filename=file_path.name)
    except PermissionError:
        return HTMLResponse("<h3>🚫 상위 경로 접근 불가</h3>", status_code=403)

# ─────────────────────────────────────────────
@app.post("/upload")
async def upload(path: str = "", file: UploadFile = File(...)):
    try:
        folder_path = safe_join(ROOT_DIR, path)
        dest = folder_path / file.filename
        with open(dest, "wb") as f:
            f.write(await file.read())
        logging.info(f"✅ Uploaded: {dest}")
        return RedirectResponse(url=f"/browse?path={quote(path)}", status_code=303)
    except PermissionError:
        return HTMLResponse("<h3>🚫 업로드 불가</h3>", status_code=403)

# ─────────────────────────────────────────────
if __name__ == "__main__":
    import uvicorn
    logging.info(f"🚀 Running: http://0.0.0.0:{PORT}")
    uvicorn.run(app, host="0.0.0.0", port=PORT)
