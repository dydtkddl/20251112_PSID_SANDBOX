# -*- coding: utf-8 -*-
"""
📁 PSID Dropbox Secure File Browser (FastAPI)
───────────────────────────────────────────────
• 로그인 기반 접근 (users.json)
• 업로드 / 다운로드 / 탐색
• Access / Error / Activity 로그 분리 (자동 회전)
• 업로드/다운로드 상세 기록 (파일명, 크기, IP, 수행시간)
"""

import os, sys, json, logging
from pathlib import Path, PureWindowsPath
from urllib.parse import quote, unquote
from datetime import datetime
from logging.handlers import TimedRotatingFileHandler

from fastapi import (
    FastAPI, Request, File, UploadFile, Response, Form, Cookie
)
from fastapi.responses import HTMLResponse, FileResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
ROOT_DIR = Path("C:/Users/KHU_PSID/Desktop/KHU_PSID").resolve()

# ─────────────────────────────────────────────
ROOT_DIR = Path("D:/00_작업장").resolve()
PORT = 8127

# ✅ 로그인 계정 로드
with open("users.json", "r", encoding="utf-8") as f:
    VALID_USERS = json.load(f)

# ─────────────────────────────────────────────
# 로그 디렉터리 및 설정
LOG_DIR = Path("logs")
LOG_DIR.mkdir(exist_ok=True)

def setup_logging():
    """access.log / error.log / activity.log 분리 + 자동 회전"""
    fmt = logging.Formatter("%(asctime)s | %(levelname)s | %(message)s")

    access_handler = TimedRotatingFileHandler(
        LOG_DIR / "access.log", when="H", interval=1, backupCount=48, encoding="utf-8"
    )
    access_handler.setLevel(logging.INFO)
    access_handler.setFormatter(fmt)

    error_handler = TimedRotatingFileHandler(
        LOG_DIR / "error.log", when="H", interval=1, backupCount=48, encoding="utf-8"
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(fmt)

    activity_handler = TimedRotatingFileHandler(
        LOG_DIR / "activity.log", when="H", interval=1, backupCount=48, encoding="utf-8"
    )
    activity_handler.setLevel(logging.INFO)
    activity_handler.setFormatter(fmt)

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(fmt)

    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    root_logger.addHandler(console_handler)
    root_logger.addHandler(access_handler)
    root_logger.addHandler(error_handler)

    activity_logger = logging.getLogger("activity")
    activity_logger.setLevel(logging.INFO)
    activity_logger.addHandler(activity_handler)

    uvicorn_access = logging.getLogger("uvicorn.access")
    uvicorn_access.handlers = [access_handler]
    uvicorn_access.propagate = False

    uvicorn_error = logging.getLogger("uvicorn.error")
    uvicorn_error.handlers = [error_handler]
    uvicorn_error.propagate = False

    logging.info("✅ Logging initialized (hourly rotation)")
    return activity_logger

activity_log = setup_logging()

# ─────────────────────────────────────────────
app = FastAPI(title="PSID Dropbox Secure")
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# ─────────────────────────────────────────────
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

# ─────────────────────────────────────────────
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
    client_ip = request.client.host
    if username in VALID_USERS and VALID_USERS[username] == password:
        response = RedirectResponse("/browse", status_code=303)
        response.set_cookie("auth", username, httponly=True)
        activity_log.info(f"✅ LOGIN | user={username} | ip={client_ip}")
        return response
    activity_log.warning(f"❌ LOGIN FAILED | user={username} | ip={client_ip}")
    return templates.TemplateResponse(
        "login.html",
        {"request": request, "error": "❌ 아이디 또는 비밀번호가 틀렸습니다."},
    )

@app.get("/logout")
async def logout(auth: str = Cookie(default=None)):
    activity_log.info(f"👋 LOGOUT | user={auth}")
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
    return templates.TemplateResponse(
        "browse.html",
        {
            "request": request,
            "entries": entries,
            "breadcrumb": breadcrumb,
            "abs_path": abs_path,
            "path": path,
            "user": auth,
        },
    )

# ─────────────────────────────────────────────
@app.get("/download")
async def download(path: str, auth: str = Cookie(default=None), request: Request = None):
    if auth not in VALID_USERS:
        return RedirectResponse("/login")

    start_time = datetime.now()
    file_path = safe_join(ROOT_DIR, path)

    if not file_path.exists() or not file_path.is_file():
        logging.error(f"❌ DOWNLOAD FAILED | path={path} (not found)")
        return HTMLResponse("<h3>❌ 파일 없음</h3>", status_code=404)

    elapsed = (datetime.now() - start_time).total_seconds() * 1000
    activity_log.info(
        f"⬇️ DOWNLOAD | user={auth} | ip={request.client.host} | file={file_path.name} "
        f"| size={os.path.getsize(file_path)} bytes | took={elapsed:.2f}ms"
    )
    return FileResponse(file_path, filename=file_path.name)

# ─────────────────────────────────────────────
@app.post("/upload")
async def upload(
    path: str = "",
    file: UploadFile = File(...),
    auth: str = Cookie(default=None),
    request: Request = None,
):
    if auth not in VALID_USERS:
        return RedirectResponse("/login")

    start_time = datetime.now()
    folder_path = safe_join(ROOT_DIR, path)
    dest = folder_path / file.filename

    content = await file.read()
    with open(dest, "wb") as f:
        f.write(content)

    elapsed = (datetime.now() - start_time).total_seconds() * 1000
    activity_log.info(
        f"📤 UPLOAD | user={auth} | ip={request.client.host} | file={file.filename} "
        f"| size={len(content)} bytes | dest={dest} | took={elapsed:.2f}ms"
    )
    return RedirectResponse(f"/browse?path={quote(path)}", status_code=303)

# ─────────────────────────────────────────────
if __name__ == "__main__":
    import uvicorn
    logging.info(f"🚀 Running on http://127.0.0.1:{PORT}")
    uvicorn.run(app, host="0.0.0.0", port=PORT)