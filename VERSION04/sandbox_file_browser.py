import os, sys, logging
from pathlib import Path, PureWindowsPath
from urllib.parse import quote, unquote
from datetime import datetime

from fastapi import FastAPI, Request, File, UploadFile, Response, Form
from fastapi.responses import HTMLResponse, FileResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
import json
ROOT_DIR = Path("C:/Users/KHU_PSID/Desktop/KHU_PSID").resolve()
# ─────────────────────────────────────────────
ROOT_DIR = Path("D:/00_작업장").resolve()
PORT = 8127

# ✅ 외부 JSON에서 불러오기
with open("users.json", "r", encoding="utf-8") as f:
    VALID_USERS = json.load(f)
logging.basicConfig(level=logging.INFO, stream=sys.stdout, encoding="utf-8",
                    format="%(asctime)s | %(levelname)s | %(message)s")

app = FastAPI(title="PSID Dropbox Secure")
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# ─────────────────────────────────────────────
def human_readable_size(size_bytes):
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024**2:
        return f"{size_bytes/1024:.2f} KB"
    elif size_bytes < 1024**3:
        return f"{size_bytes/1024**2:.2f} MB"
    else:
        return f"{size_bytes/1024**3:.2f} GB"

def datetimeformat(value):
    try:
        return datetime.fromtimestamp(value).strftime("%Y-%m-%d %H:%M")
    except Exception:
        return "-"
templates.env.filters["datetimeformat"] = datetimeformat

def safe_join(base: Path, target: str) -> Path:
    base = base.resolve()
    target_path = (base / unquote(target)).resolve(strict=False)
    if not str(PureWindowsPath(target_path)).startswith(str(PureWindowsPath(base))):
        raise PermissionError("상위 경로 접근 차단됨")
    return target_path

# ─────────────────────────────────────────────
@app.middleware("http")
async def add_headers(request, call_next):
    response = await call_next(request)
    response.headers["ngrok-skip-browser-warning"] = "true"
    return response

# ✅ 세션 흉내 (간단히 cookie 기반)
from fastapi import Cookie

@app.get("/", response_class=HTMLResponse)
async def root(request: Request, auth: str = Cookie(default=None)):
    if auth not in VALID_USERS:
        return RedirectResponse("/login")
    return RedirectResponse("/browse")

@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request, "error": None})

@app.post("/login", response_class=HTMLResponse)
async def login(request: Request, username: str = Form(...), password: str = Form(...)):
    if username in VALID_USERS and VALID_USERS[username] == password:
        response = RedirectResponse("/browse", status_code=303)
        response.set_cookie("auth", username, httponly=True)
        return response
    return templates.TemplateResponse("login.html", {"request": request, "error": "❌ 아이디 또는 비밀번호가 틀렸습니다."})

@app.get("/logout")
async def logout():
    response = RedirectResponse("/login")
    response.delete_cookie("auth")
    return response

# ─────────────────────────────────────────────
@app.get("/browse", response_class=HTMLResponse)
async def browse(request: Request, path: str = "", auth: str = Cookie(default=None)):
    if auth not in VALID_USERS:
        return RedirectResponse("/login")

    abs_path = safe_join(ROOT_DIR, path)
    entries = []
    for item in sorted(abs_path.iterdir(), key=lambda x: (not x.is_dir(), x.name.lower())):
        rel = os.path.relpath(item, ROOT_DIR)
        ext = item.suffix.lower().lstrip(".") if item.is_file() else ""
        entries.append({
            "name": item.name,
            "path": rel.replace("\\", "/"),
            "is_dir": item.is_dir(),
            "ext": ext,
            "size": "-" if item.is_dir() else human_readable_size(item.stat().st_size),
            "mtime": item.stat().st_mtime,
        })

    breadcrumb = path.split("/") if path else []
    return templates.TemplateResponse("browse.html", {
        "request": request,
        "entries": entries,
        "breadcrumb": breadcrumb,
        "abs_path": abs_path,
        "path": path,
        "user": auth
    })

@app.get("/download")
async def download(path: str, auth: str = Cookie(default=None)):
    if auth not in VALID_USERS:
        return RedirectResponse("/login")
    file_path = safe_join(ROOT_DIR, path)
    return FileResponse(file_path, filename=file_path.name)

@app.post("/upload")
async def upload(path: str = "", file: UploadFile = File(...), auth: str = Cookie(default=None)):
    if auth not in VALID_USERS:
        return RedirectResponse("/login")
    folder_path = safe_join(ROOT_DIR, path)
    with open(folder_path / file.filename, "wb") as f:
        f.write(await file.read())
    return RedirectResponse(f"/browse?path={quote(path)}", 303)

if __name__ == "__main__":
    import uvicorn
    logging.info(f"🚀 Running on http://127.0.0.1:{PORT}")
    uvicorn.run(app, host="0.0.0.0", port=PORT)
