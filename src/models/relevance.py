import pandas as pd
from tqdm import tqdm
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.schema import Document

from graph.global_state import State
from prompts.relevance_prompt import reason_prompt
from typing_extensions import Annotated
from pydantic import Field, BaseModel
from langchain_openai import ChatOpenAI

# 연관성 점수 계산 노드
def evaluate_relevance(state: State):
    
    df = state['search_df']

    targets = ['title', 'description', 'keyword']

    MAX_LENGTH = 2000

    dfs = {}

    for target in targets:
        print(f'\n[embedding_{target}]')
        
        df[target] = df[target].fillna('')
        df[target] = df[target].str.slice(0, MAX_LENGTH)

        texts = df[target].tolist()

        embeddings = OpenAIEmbeddings(model="text-embedding-3-small")

        docs = [Document(page_content=text, metadata={"ID": row.ID}) 
                for text, row in zip(texts, df.itertuples())]

        batch_size = 500
        stores = []
        for i in tqdm(range(0, len(docs), batch_size)):
            batch = docs[i:i+batch_size]
            store = FAISS.from_documents(batch, embeddings)
            stores.append(store)

        vectorstore = stores[0]
        for s in stores[1:]:
            vectorstore.merge_from(s)

        query = state[target]
        query_embedding = embeddings.embed_query(query)

        results_with_score = vectorstore.similarity_search_with_score_by_vector(query_embedding, k=20)
        
        dfs[f'df_{target}'] = pd.DataFrame([
            {
                "ID": r.metadata.get("ID"),
                "relevance": score,
                "target": target
            }
            for r, score in results_with_score
        ])
        
    merged_df = dfs['df_title'].merge(
        dfs['df_description'][["ID", "relevance"]], 
        on="ID",
        how="outer",
        suffixes=("_title", "_desc")
    ).merge(
        dfs['df_keyword'][["ID", "relevance"]].rename(columns={"relevance": "relevance_key"}), 
        on="ID",
        how="outer"
    )

    merged_df = merged_df.fillna(2.0)

    merged_df = merged_df.drop_duplicates(subset='ID')

    merged_df = merged_df[merged_df['ID'] != state['input_id']]

    # 2. 가중치 합산
    a, b, c = 10, 3, 1
    merged_df["relevance_raw"] = (
        merged_df["relevance_title"] * a + 
        merged_df["relevance_desc"] * b + 
        merged_df["relevance_key"] * c
    ) / (a + b + c)

    merged_df["relevance"] = 100 * (1 - merged_df["relevance_raw"] / 2)

    result_df = (merged_df[["ID", "relevance"]]
                .sort_values("relevance", ascending=False)
                .reset_index(drop=True)).head(5)

    return {'relevance_df': result_df}


# 선정사유 생성 노드
class IDRelevance(BaseModel):
    relevant_id: Annotated[
        list[str],
        Field(
            ..., 
            description=(
                "데이터의 ID 목록"
            ), 
        )
    ]
    reason: Annotated[
        list[str],
        Field(
            ..., 
            description="각 ID가 선정된 이유를 설명하는 문자열 목록. relevant_id와 인덱스가 일치해야 합니다.",
        )
    ]

def generate_reason(state: State):
    print('\ngenerating reasons...\n')
    df, title, description, keyword = state['search_df'], state['title'], state['description'], state['keyword']
    
    relevant_ids = state['relevance_df']['ID'].tolist()
    filtered_df = df[df['ID'].isin(relevant_ids)]

    prompt = reason_prompt.invoke(
        {
            'title': title, 
            'description': description,
            'keyword': keyword,
            'data': filtered_df[['ID', 'title', 'description', 'keyword']].to_dict(orient="records"),
        }
    )

    sllm = ChatOpenAI(model='gpt-4o-mini', temperature=0)

    structured_sllm = sllm.with_structured_output(IDRelevance)
    res = structured_sllm.invoke(prompt)
        
    tmp = pd.DataFrame({
        'ID': res.relevant_id,
        'reason': res.reason
    })
    
    relevance_df = pd.merge(
        state['relevance_df'][['ID', 'relevance']],
        tmp,
        on='ID',
        how='left'
    )

    return {'relevance_df': relevance_df}

# 결과 정리 노드
def summarize_results(state: State):
    
    merged_df = pd.merge(
        state['relevance_df'],
        state['search_df'][['ID','category', 'title', 'description', 'URL']],
        on='ID',
        how='left'
    )

    result_df = merged_df[['category', 'title', 'description', 'relevance', 'reason', 'URL']]
    result_df = result_df.rename(columns={
        'category': '구분',
        'title': '제목',
        'description': '설명',
        'relevance': '점수',
        'reason': '추천 사유',
    })

    return {'result_df': result_df}