import os, requests, json, xmltodict
from graph.global_state import State
from utils.func import xml_to_df
from utils.sciecneon_api import call_access_token

# 데이터셋 검색 노드
def DATA_browse(state: State):

    API_KEY = os.getenv("DATAON_META_API_KEY")
    assert API_KEY and API_KEY.strip(), "환경변수(DATAON_META_API_KEY)가 비어있어요!"

    url = "https://dataon.kisti.re.kr/rest/api/search/dataset/" + state["input_id"]
    params = {"key": API_KEY}

    res = requests.get(url, params=params, timeout=20)
    data = res.json()

    # json 저장
    with open("../data/input_data.json", "w", encoding="utf-8") as f:
        json.dump(data['records'], f, ensure_ascii=False, indent=4)

    title, description, keyword = data['records']['dataset_title_etc_main'], data['records']['dataset_expl_etc_main'], data['records']['dataset_kywd_etc_main']
    print('\n[title]\n', title)
    print('\n[description]\n', description)
    print('\n[keyword]\n', keyword)

    return {'title':title, 'description' : description, 'keyword': keyword} 

# 논문 검색 노드
def ARTI_browse(state: State):
    
    CLIENT_ID = os.getenv("SCIENCEON_CLIENT_ID")
    ARTI_KEY = os.getenv("SCIENCEON_API_KEY")
    MAC_ADDRESS = os.getenv("MAC_ADDRESS")

    # access token 생성
    access_token = call_access_token(MAC_ADDRESS, ARTI_KEY, CLIENT_ID)

    url = "https://apigateway.kisti.re.kr/openapicall.do"
    params = {
        "client_id": CLIENT_ID,
        "token": access_token,
        "version": 1.0,
        "action": "browse",
        "target": "ARTI",
        "cn": state['input_id'],
        "include": "",
        "exclude": None,
    }
    
    res = requests.get(url, params=params, timeout=20)
    xml = res.text
    dict_data = xmltodict.parse(xml)
    
    # 데이터를 json으로 저장
    with open("../data/input_data.json", "w", encoding="utf-8") as f:
        json.dump(dict_data, f, ensure_ascii=False, indent=4)

    df = xml_to_df(xml)
    
    title, description, keyword = df['Title'].iloc[0], df['Abstract'].iloc[0], df['Keyword'].iloc[0]
    
    print('\n[title]\n', title)
    print('\n[description]\n', description)
    print('\n[keyword]\n', keyword)    

    return {'title': title, 'description': description, 'keyword': keyword}