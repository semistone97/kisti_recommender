from dotenv import load_dotenv
from graph.builder import build_graph

load_dotenv(override=True)

def main():
    input_id = input('검색 데이터의 ID')
    input_category = input('article / dataset')
        
    graph = build_graph()
    
    res = graph.invoke({
        'input_id': input_id,
        'input_category': input_category,
    })

    print(res['result_df'])

if __name__ == "__main__":
    main()