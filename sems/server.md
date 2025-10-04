물론이지 🙌
지금까지 세팅한 내용을 깔끔하게 정리해서,
나중에 너나 팀원이 다시 봐도 한눈에 이해될 수 있도록 Markdown 설명서 형식으로 써줄게.

---

📘 ScienceON API Proxy Server Guide

1️⃣ 서버 정보 (Oracle Cloud)

항목	내용
플랫폼	Oracle Cloud Infrastructure (Always Free Tier)
리전	South Korea North (Chuncheon)
운영체제	Ubuntu 22.04 LTS
인스턴스 이름	kisti_recommender
공인 IP (Reserved)	168.107.8.92
내부 IP	10.0.0.143
기본 사용자명 (SSH)	ubuntu
접속 명령 예시	ssh -i "SSH Key Oct 4 2025.key" ubuntu@168.107.8.92
포트 오픈	22 (SSH), 8080 (Flask Proxy)
보안 그룹	Security List에서 TCP 8080 Ingress 허용


---

2️⃣ proxy.py 의 역할 및 구조

📄 파일 개요

proxy.py 는 ScienceON API를 중계(Proxy) 해주는 Flask 기반 서버입니다.
ScienceON API는 등록된 IP(168.107.8.92)에서만 접근 가능하므로,
이 서버를 통해 팀원들이 우회적으로 API를 사용할 수 있습니다.

[팀원 PC] → [Oracle 서버 (168.107.8.92)] → [ScienceON API]


---

⚙️ 주요 구성

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


---

🔑 환경 변수 설정

서버에서 ScienceON API 호출 시 필요한 인증 정보:

export SCIENCEON_CLIENT_ID="발급받은_client_id"
export SCIENCEON_TOKEN="발급받은_token"

이 두 값은 ScienceON API 신청 승인 후 발급됩니다.
안전을 위해 코드에 직접 쓰지 말고 환경 변수로 지정하세요.

---

🧠 실행 방법

서버 SSH 접속 후 프로젝트 폴더에서:

pip install flask requests
nohup python3 proxy.py > proxy.log 2>&1 &

	•	nohup : 터미널을 닫아도 백그라운드에서 계속 실행
	•	proxy.log : 로그 파일 (요청/에러 기록)
	•	실행 중인 프로세스 확인:

ps aux | grep proxy



---

3️⃣ 팀원 사용법

💡 기본 원리

팀원들은 직접 ScienceON API에 접근하지 않고,
이 서버의 /api/arti/search 엔드포인트를 사용합니다.

서버가 대신 ScienceON에 요청을 보내고 응답을 전달합니다.

---

🔗 요청 예시

curl "http://168.107.8.92:8080/api/arti/search?q=AI&field=ALL&rows=5"

	•	q : 검색어 (예: "AI", "Deep Learning")
	•	field : 검색 필드 (TI=제목, AU=저자, ALL=전체)
	•	rows : 반환할 문서 수
	•	기타 파라미터: start, sort 등 ScienceON 문서 기준

응답은 ScienceON 원본 XML 혹은 JSON 그대로 전달됩니다.

---

🧑‍💻 Python에서 사용 예시

import requests

r = requests.get("http://168.107.8.92:8080/api/arti/search", params={"q": "AI", "field": "ALL", "rows": 5})
print(r.text)


---

🧱 서버 상태 확인

서버가 잘 작동 중인지 확인하려면:

curl http://168.107.8.92:8080/healthz

정상일 경우:

{"ok": true}


---

🧰 로그 확인 (운영자용)

tail -f proxy.log

서버에서 모든 API 호출과 에러를 실시간으로 볼 수 있습니다.

---

✅ 추가 참고

항목	설명
Flask 서버 포트	8080
기본 URL	http://168.107.8.92:8080/api/arti/search
공개 범위	OCI Security List에서 8080포트 열림 (전 세계 접근 가능)
백엔드 언어	Python 3 (Flask + Requests)
ScienceON API 문서	https://scienceon.kisti.re.kr/apigateway/api/way/service/arti/serviceArtiSearchApi.do


---

⚠️ 주의사항
	•	IP 변경 금지: 현재 IP(168.107.8.92)는 ScienceON에 등록된 고정 IP입니다.
VM 삭제 후 새로 만들면 IP가 바뀌므로, 기존 인스턴스를 유지해야 합니다.
	•	보안: SSH Key는 개인만 보관하고 외부 공유 금지.
	•	중단 방지: 서버가 재부팅되면 nohup 프로세스는 사라질 수 있습니다.
재시작 시 nohup python3 proxy.py & 명령을 다시 실행해야 합니다.

---

이 문서만 깃헙 리포에 README_SERVER.md 같은 이름으로 올려두면
팀원들이 바로 따라 할 수 있을 거야 🚀