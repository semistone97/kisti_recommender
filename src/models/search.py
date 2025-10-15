import os, requests
import pandas as pd
from langchain_openai import ChatOpenAI
from typing_extensions import Annotated
from pydantic import Field, BaseModel

from graph.global_state import State
from utils.func import xml_to_df, transform_query
from utils.sciecneon_api import call_access_token
from utils.config_loader import config
from prompts.query_prompt import query_prompt

# 쿼리 생성 노드
class QueryResult(BaseModel):
    query: Annotated[
        list[str],
        Field(
            ..., 
            max_length=int(config['search']['query_length']), 
            min_length=int(config['search']['query_length']),
            description=f"가장 적절한 검색어들의 리스트, 총 {int(config['search']['query_length'])}개", 
        )
    ]
    
def generate_query(state: State):

    prompt = query_prompt.invoke(
        {
            'title': state['title'], 
            'description': state['description'],
            'keyword': state['keyword'],
        }
    )

    # sLLM
    sllm = ChatOpenAI(model='gpt-4o-mini', temperature=0)

    structured_sllm = sllm.with_structured_output(QueryResult)
    res = structured_sllm.invoke(prompt)
    query = res.query
    
    print('\n[query]\n', query)

    return {'query': query}


# 논문 검색 노드
def ARTI_search(state: State):
    
    CLIENT_ID = os.getenv("SCIENCEON_CLIENT_ID")
    ARTI_KEY = os.getenv("SCIENCEON_API_KEY")
    MAC_ADDRESS = os.getenv("MAC_ADDRESS")

    access_token = call_access_token(MAC_ADDRESS, ARTI_KEY, CLIENT_ID)

    url = "https://apigateway.kisti.re.kr/openapicall.do"
    df = pd.DataFrame()
    
    for query in state['query']:
        params = {
            "client_id": CLIENT_ID,
            "token": access_token,
            "version": 1.0,
            "action": "search",
            "target": "ARTI",
            "searchQuery": transform_query(query),
            'curPage': 1, # 현재페이지 번호
            'rowCount': int(config['search']['search_length']), # 디스플레이 건수(기본값 10, 최대값 100)
        }

        res = requests.get(url, params=params, timeout=20)
        xml = res.text
        tmp = xml_to_df(xml)
        tmp["query"] = query
        df = pd.concat([df, tmp], ignore_index=True)
        
    df = df.drop_duplicates(subset='CN')
    print('\n[total article length]\n', len(df))

    cleaned_df = (
        df[
            ['CN', 'Title', 'Abstract', 'Pubyear', 'Keyword', 'Author', 'ContentURL', 'query']
        ]
        .rename(
            columns={
                'CN': 'ID',
                'Title': 'title',
                'Abstract': 'description',
                'Pubyear': 'pubyear',
                'Keyword': 'keyword',
                'Author': 'author',
                'ContentURL': 'URL'
            }
        )
    )

    cleaned_df['category'] = 'article'

    search_df = state.get('search_df')
    
    if search_df is not None and not search_df.empty:
        return {'search_df': pd.concat([search_df, cleaned_df], ignore_index=True)}
    else:
        return {'search_df': cleaned_df}

# 데이터셋 검색 노드
def DATA_search(state: State):
    
    API_KEY = os.getenv("DATAON_SEARCH_API_KEY")
    assert API_KEY and API_KEY.strip(), "환경변수(DATAON_API_KEY)가 비어있어요!"

    url = "https://dataon.kisti.re.kr/rest/api/search/dataset/"
    df = pd.DataFrame()
    for query in state['query']:
        params = {"key": API_KEY, "query": query, "from": 0, "size": int(config['search']['search_length'])}
        # key / CHAR / 필수 / API_KEY
        # query / CHAR / 필수 / 검색키워드
        # from / CHAR / 옵션 / 페이지시작위치
        # size / CHAR / 옵션 / 페이지사이즈

        res = requests.get(url, params=params, timeout=20)
        data = res.json()
        
        if "records" in data:
            tmp = pd.DataFrame(data["records"])
            tmp["query"] = query
            df = pd.concat([df, tmp], ignore_index=True)

    df = df.drop_duplicates(subset='svc_id')
    print('\n[total dataset length]\n', len(df))
    
    cleaned_df = (
        df[
            ['svc_id', 'dataset_title_etc_main', 'dataset_expl_etc_main','dataset_pub_dt_pc', 'dataset_kywd_etc_main', 'dataset_creator_etc_main', 'dataset_lndgpg', 'query']
        ]
        .rename(
            columns={
                'svc_id': 'ID',
                'dataset_title_etc_main': 'title',
                'dataset_expl_etc_main': 'description',
                'dataset_pub_dt_pc': 'pubyear',
                'dataset_kywd_etc_main': 'keyword',
                'dataset_creator_etc_main': 'author',
                'dataset_lndgpg': 'URL',
            }
        )
    )

    cleaned_df['category'] = 'dataset'
    
    search_df = state.get('search_df')
    
    if search_df is not None and not search_df.empty:
        return {'search_df': pd.concat([search_df, cleaned_df], ignore_index=True)}
    else:
        return {'search_df': cleaned_df}
