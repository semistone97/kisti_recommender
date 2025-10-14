from dotenv import load_dotenv
from graph.builder import build_graph
import pandas as pd

load_dotenv(override=True)

def main():
    
    # input_id = 'JAKO200411922932805'
    # input_category = 'article'

    # input_id = '37c0f3d51a130211fe55fe6019cc7914'
    # input_category = 'dataset'

    input_id = input('[검색 데이터의 ID]\n')
    input_category = input('article / dataset\n')
        
    graph = build_graph()
    
    res = graph.invoke({
        'input_id': input_id,
        'input_category': input_category,
    })

    print(res['result_df'])
    df = res['result_df']
    df.to_csv('./results/analysis_result.csv', index=False, encoding='utf-8')

if __name__ == "__main__":
    main()