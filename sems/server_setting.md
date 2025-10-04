# 🧭 Oracle Cloud + ScienceON Proxy 서버 구성 노트

> 2025-10-04 기준  
> 작성자: 준석쿤  
> 목적: ScienceON 논문검색 API를 고정 IP 환경에서 안정적으로 호출하기 위한 Proxy 서버 구축

---

## 📍 1. Oracle Cloud 서버 정보

| 항목 | 내용 |
|------|------|
| **플랫폼** | Oracle Cloud Infrastructure (Always Free Tier) |
| **리전** | South Korea North (Chuncheon) |
| **운영체제** | Ubuntu 22.04 LTS |
| **인스턴스 이름** | `kisti_recommender` |
| **공인 IP (Reserved)** | `168.107.8.92` |
| **내부 IP** | `10.0.0.143` |
| **기본 사용자명 (SSH)** | `ubuntu` |
| **SSH 접속 명령** | `ssh -i "SSH Key Oct 4 2025.key" ubuntu@168.107.8.92` |
| **포트 오픈** | 22 (SSH), 8080 (Flask Proxy) |
| **보안 설정** | Security List에서 TCP 22, 8080 허용 |

---

## 🔐 2. SSH 관련 명령어

```bash
# 개인키 권한 수정 (필수)
chmod 400 "SSH Key Oct 4 2025.key"

# SSH 접속
ssh -i "SSH Key Oct 4 2025.key" ubuntu@168.107.8.92

# Flask 프로세스 확인
ps aux | grep proxy

# Flask 종료
kill <PID>
```


---

## 🌐 3. 네트워크 & 보안 설정
	•	Public Subnet 으로 인스턴스 생성
	•	Security List / NSG 설정

Source CIDR: 0.0.0.0/0
Protocol: TCP
Destination Port Range: 22,8080


	•	외부 접근을 위해 TCP 8080 반드시 열어두기
	•	ScienceON API 화이트리스트에 IP 168.107.8.92 등록

---

## ⚙️ 4. Proxy 서버 (proxy.py)

🧩 역할
	•	ScienceON API는 등록된 IP에서만 접근 가능 →
proxy.py가 중계 역할 수행

[팀원] → [Oracle 서버(168.107.8.92)] → [ScienceON API]



📄 코드 예시
```python
from flask import Flask, request, jsonify
import requests, os

app = Flask(__name__)

SCIENCEON_BASE = "https://scienceon.kisti.re.kr/apigateway/api/way/service/arti/serviceArtiSearchApi.do"
CLIENT_ID = os.getenv("SCIENCEON_CLIENT_ID")
TOKEN = os.getenv("SCIENCEON_TOKEN")

@app.route("/api/arti/search")
def arti_search():
    q = request.args.get("q", "")
    field = request.args.get("field", "TI")
    start = request.args.get("start", "1")
    rows = request.args.get("rows", "20")
    sort = request.args.get("sort", "RELEVANCE")

    params = {
        "client_id": CLIENT_ID,
        "token": TOKEN,
        "target": "ARTI",
        "searchQuery": str({field: q}),
        "startCount": start,
        "listCount": rows,
        "sort": sort,
    }

    r = requests.get(SCIENCEON_BASE, params=params)
    return (r.text, r.status_code, {"Content-Type": r.headers.get("Content-Type", "text/xml; charset=UTF-8")})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
```


---

⚡️ 실행 및 관리
```bash
# 의존성 설치
pip install flask requests

# 환경변수 설정 (ScienceON 인증용)
export SCIENCEON_CLIENT_ID="발급받은_client_id"
export SCIENCEON_TOKEN="발급받은_token"

# 백그라운드 실행
nohup python3 proxy.py > proxy.log 2>&1 &

# 로그 실시간 확인
tail -f proxy.log

# 상태 확인
curl http://localhost:8080/healthz
```


---

## 🧑‍🤝‍🧑 5. 팀원 사용 가이드

🔗 기본 사용 예시
```bash
curl "http://168.107.8.92:8080/api/arti/search?q=AI&field=ALL&rows=5"
```
Flask 서버가 ScienceON API를 대신 호출하고 결과(XML/JSON)를 그대로 반환.

🧩 파라미터 요약

파라미터	설명	예시
q	검색어	"AI"
field	검색 필드 (TI, AU, ALL)	ALL
rows	결과 문서 수	5
start	시작 인덱스	1
sort	정렬 기준	RELEVANCE


---

💻 Python 예시
```python
import requests

r = requests.get("http://168.107.8.92:8080/api/arti/search", params={"q": "AI", "field": "ALL", "rows": 5})
print(r.text)
```


---

## 🧰 6. 트러블슈팅 요약
```
문제	원인	해결
SSH 안 됨	포트 22 미허용	Security List 수정
Flask 접근 불가	포트 8080 미허용	Security List 수정
Permission denied (key)	키 권한 너무 넓음	chmod 400 key파일
Flask 종료됨	SSH 종료 후 nohup 안 사용	nohup python3 proxy.py & 다시 실행
API 호출 실패	ScienceON IP 미등록	168.107.8.92 등록 확인
```


---

## 🧠 7. 운영 팁
	•	서버 재부팅 후 proxy.py 자동 실행하려면 systemd 등록 고려
	•	nohup 은 임시 유지 방식이므로 장기 운영 시 서비스화 권장
	•	Flask 앞단에 Nginx 달면 HTTPS 가능
	•	ScienceON 응답(XML)을 JSON으로 변환하면 프론트엔드에서 처리 쉬워짐

---

📎 참고 링크
	•	ScienceON API 문서
👉 https://scienceon.kisti.re.kr/apigateway/api/way/service/arti/serviceArtiSearchApi.do
	•	Oracle Cloud 대시보드
👉 https://cloud.oracle.com

---

작성일: 2025-10-04
# 요약:

Oracle Cloud 무료 티어를 이용해 고정 IP 환경의 ScienceON API 프록시 서버를 구축.
Flask 기반 중계 서버를 백그라운드로 실행하여 팀원 공동 접근 환경 완성.
