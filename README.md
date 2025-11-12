좋아요 ✅ 아래는 그대로 **복사해서 GitHub의 `README.md`에 붙여넣으면 완벽히 렌더링되는 전체 마크다운 코드 스니펫**입니다.
(이미 Markdown 문법에 맞춰 포맷팅되어 있음.)

---

````markdown
# 🌀 PSID SANDBOX – FastAPI File Browser + Cloudflare Tunnel

## 📘 개요
이 프로젝트는 **로컬 디렉터리 탐색·업로드·다운로드가 가능한 웹 파일 브라우저**입니다.  
외부에서도 안전하게 접속할 수 있도록 **Cloudflare Tunnel (Cloudflared)** 을 이용해 로컬 서버를 공개합니다.

- **기술 스택:** FastAPI + Jinja2 + Bootstrap5  
- **주요 기능:**  
  - 폴더/파일 탐색, 업로드, 다운로드  
  - 검색 및 정렬  
  - 반응형 모바일 UI  
  - 폴더 항상 위 정렬  
  - Cloudflare Tunnel을 통한 외부 공개  

---

## ⚙️ 1. Python FastAPI 서버 설정

### 🧩 필수 패키지 설치
```bash
pip install fastapi uvicorn jinja2
````

### ▶️ 서버 실행

```bash
python sandbox_file_browser.py
```

> ✅ 기본 포트: `http://localhost:8127`
> 브라우저에서 접속 시 로컬 탐색기 웹 UI가 표시됩니다.

---

## 🌐 2. Cloudflare Tunnel 설치 (Windows 기준)

### 🧰 ① Cloudflared 다운로드

1. 아래 공식 링크에서 **Windows용 cloudflared.exe** 다운로드
   👉 [Cloudflare 공식 설치 페이지](https://developers.cloudflare.com/cloudflare-one/connections/connect-apps/install-and-setup/installation/)

2. 다운로드한 `cloudflared.exe` 파일을 다음 경로로 이동 (PATH 추가를 위함)

   ```
   C:\Windows\System32\
   ```

   또는, 프로젝트 폴더 내에 두고 경로를 직접 지정해 실행해도 됩니다.

3. 정상 설치 확인:

   ```bash
   cloudflared --version
   ```

   예시 출력:

   ```
   cloudflared version 2025.8.1 (built 2025-08-15-1427)
   ```

---

## 🚀 3. Cloudflare Tunnel 빠른 실행 (Quick Tunnel)

로그인 없이 임시 URL을 발급받아 사용할 수 있습니다.

### ① FastAPI 서버 실행

```bash
python sandbox_file_browser.py
```

### ② Cloudflare 터널 실행

```bash
cloudflared tunnel --url http://localhost:8127
```

실행 후 콘솔에 다음 메시지가 표시됩니다 👇

```
Your quick Tunnel has been created! Visit it at (it may take some time to be reachable):
https://friendly-mouse-tunnel.trycloudflare.com
```

📲 이제 외부 네트워크(휴대폰 등)에서도 아래 주소로 접속 가능합니다:
`https://friendly-mouse-tunnel.trycloudflare.com`

---

## 🔐 4. Cloudflare Tunnel 고급 설정 (선택)

### ① Cloudflare 계정 로그인

```bash
cloudflared tunnel login
```

→ 브라우저가 열리며 Cloudflare 계정 로그인 창이 뜹니다.
→ 로그인 완료 시 인증서(`cert.pem`)가 자동 생성됩니다.

### ② Named Tunnel 생성

```bash
cloudflared tunnel create psid-sandbox
```

### ③ DNS 도메인 연결 (예: `sandbox.mydomain.com`)

```bash
cloudflared tunnel route dns psid-sandbox sandbox.mydomain.com
```

### ④ 실행

```bash
cloudflared tunnel run psid-sandbox
```

> 이렇게 하면 `https://sandbox.mydomain.com` 형태의 고정 URL로 접속 가능!

---

## 🖥️ 5. 자동 실행 설정 (Windows 서비스 등록)

Cloudflare Tunnel을 부팅 시 자동 실행하려면:

```bash
cloudflared service install
```

또는 서비스 관리 도구(`services.msc`)에서 수동 등록할 수도 있습니다.
이후 Windows 부팅 시 자동으로 FastAPI 서버를 외부에 노출시킬 수 있습니다.
