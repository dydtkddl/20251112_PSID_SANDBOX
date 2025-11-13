
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


```bash
conda create -n PSID_SANDBOX python=3.10 --yes
conda activate PSID_SANDBOX 
pip install pathlib  fastapi uvicorn jinja2
pip install python-multipart

winget install cloudflare.cloudflare
cloudflared tunnel --url http://localhsot:8127


https://maryland-gale-consistent-gospel.trycloudflare.com/
```
## 🖥️ 5. 자동 실행 설정 (Windows 서비스 등록)

Cloudflare Tunnel을 부팅 시 자동 실행하려면:

```bash
cloudflared service install
```

또는 서비스 관리 도구(`services.msc`)에서 수동 등록할 수도 있습니다.
이후 Windows 부팅 시 자동으로 FastAPI 서버를 외부에 노출시킬 수 있습니다.
