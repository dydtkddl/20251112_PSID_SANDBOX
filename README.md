# 20251112_PSID_SANDBOX  

## 📂 개요  
본 프로젝트는 로컬 Windows 데스크탑 상의 특정 폴더를 웹 브라우저로 탐색/업로드/다운로드할 수 있도록 구현된 파일 브라우저 시스템입니다.  
- 사용 기술: FastAPI + Jinja2 + Bootstrap  
- 목적: 지정된 루트 폴더 이하만 접근 가능하도록 샌드박스 형태로 구현됨  
- 기능: 폴더/파일 탐색, 업로드, 다운로드, 검색, 정렬, 반응형 UI  
- 배포 방식: 외부에서도 접속 가능하도록 Cloudflared(Cloudflare Tunnel) 을 활용  

---

## ✅ 사전준비  
1. Python 환경 설치 (권장: Python 3.9 이상)  
2. 프로젝트 클론 또는 다운로드  
   ```bash
   git clone https://github.com/dydtkddl/20251112_PSID_SANDBOX.git
   cd 20251112_PSID_SANDBOX
