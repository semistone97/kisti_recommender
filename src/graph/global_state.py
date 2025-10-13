from langgraph.graph import MessagesState
import pandas as pd
from dataclasses import field

class State(MessagesState):
    
    # 입력된 데이터
    input_id: str = ''  
    input_category: str = ''
    
    # 메타데이터 검색을 통해 확인한 제목과 설명
    title: str = ''   
    description: str = ''
    keyword: str = ''
    
    # LLM이 생성한 검색어 리스트
    query : list[str] = []
    
    # 검색어를 통해 검색한 전체 데이터
    search_df: pd.DataFrame = field(default_factory=pd.DataFrame)

    # 연관성 검색을 통해 확인한 topK 데이터
    relevance_df: pd.DataFrame = field(default_factory=pd.DataFrame)
    
    # 결과
    result_df: pd.DataFrame = field(default_factory=pd.DataFrame)
