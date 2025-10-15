from dotenv import load_dotenv
from graph.builder import build_graph
import pandas as pd
import json, argparse

load_dotenv(override=True)

def main():
    
    parser = argparse.ArgumentParser(description="에이전트 실행")
    parser.add_argument("--id", required=True, help="검색 데이터의 ID")
    parser.add_argument("--category", required=True, choices=['article', 'dataset'], help="article 또는 dataset 선택")
    args = parser.parse_args()

    id = args.id
    category = args.category
        
    graph = build_graph()
    
    res = graph.invoke({
        'input_id': id,
        'input_category': category,
    })

    print(res['result_df'])
    df = res['result_df']
    
    data = df.to_dict(orient='records')

    with open('./results/analysis_result.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

    print('saved to results/analysis_result.json')
if __name__ == "__main__":
    main()