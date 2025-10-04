# proxy.py
from flask import Flask, request, jsonify
import os
import requests
from dotenv import load_dotenv
load_dotenv()

app = Flask(__name__)

SCIENCEON_BASE = "https://scienceon.kisti.re.kr/apigateway/api/way/service/arti/serviceArtiSearchApi.do"

CLIENT_ID = os.getenv("SCIENCEON_CLIENT_ID")   # 발급받은 클라이언트 ID (64자 영문/숫자)
TOKEN     = os.getenv("SCIENCEON_TOKEN")       # 발급받은 Access Token

# 간단 헬스체크
@app.route("/healthz")
def health():
    return {"ok": True}

# /api/arti/search?q=deep+learning&field=TI&start=1&rows=20&sort=RELEVANCE
@app.route("/api/arti/search")
def arti_search():
    if not CLIENT_ID or not TOKEN:
        return jsonify({"error": "SERVER_NOT_CONFIGURED", "detail": "Set SCIENCEON_CLIENT_ID and SCIENCEON_TOKEN env vars"}), 500

    # 쿼리 파라미터 받기
    q = request.args.get("q", "").strip()
    field = request.args.get("field", "TI").strip()   # 기본: 제목(TI) 검색 가정
    start = request.args.get("start", "1")
    rows  = request.args.get("rows", "20")
    sort  = request.args.get("sort", "RELEVANCE")     # 필요 시 문서 기준값으로 수정

    if not q:
        return jsonify({"error": "MISSING_QUERY", "detail": "q is required"}), 400

    # scienceON이 요구하는 searchQuery JSON 형태 구성
    # 예: {"TI":"deep learning"} 혹은 {"ALL":"keyword"} 같은 식으로 전달
    search_query = {field: q}

    # scienceON 요청 파라미터
    params = {
        "client_id": CLIENT_ID,
        "token": TOKEN,
        "target": "ARTI",              # 논문 검색 대상
        "searchQuery": str(search_query),  # 문서 가이드가 JSON 문자열 형태를 기대(보통)하므로 문자열화
        "startCount": start,           # 시작 위치(문서 용어에 따라 startCount/listCount)
        "listCount": rows,             # 조회 개수
        "sort": sort                   # 정렬 옵션 (필요 시 문서 값으로 조정)
        # displayFields 등 추가 노출 필드가 있으면 여기에 추가
    }

    # API 호출
    r = requests.get(SCIENCEON_BASE, params=params, timeout=15)

    # XML로 내려올 수 있으니, JSON 변환이 필요하면 별도 파싱 로직 추가
    # 일단은 원문을 그대로 중계
    return (r.text, r.status_code, {"Content-Type": r.headers.get("Content-Type", "text/xml; charset=UTF-8")})

if __name__ == "__main__":
    # 0.0.0.0 로 바인딩해서 외부에서도 접근 가능
    app.run(host="0.0.0.0", port=8080)