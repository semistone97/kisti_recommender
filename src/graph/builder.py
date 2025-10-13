from langgraph.graph import START, END, StateGraph
from global_state import State
from router import input_router
from models.browse import DATA_browse, ARTI_browse
from models.search import generate_query, ARTI_search, DATA_search
from models.relevance import evaluate_relevance, generate_reason, summarize_results

def build_graph():
    builder = StateGraph(State)
    
    builder.add_node('DATA_browse', DATA_browse)
    builder.add_node('ARTI_browse', ARTI_browse)
    
    builder.add_conditional_edges(
        START,
        input_router,
        {
            'article': 'ARTI_browse',
            'dataset': 'DATA_browse'
        }
    )
    
    builder.add_edge('ARTI_browse', 'generate_query')
    builder.add_edge('DATA_browse', 'generate_query')
    
    builder.add_sequence([generate_query, ARTI_search, DATA_search, evaluate_relevance, generate_reason, summarize_results]) 
    
    builder.add_edge('summarize_results', END)
    
    return builder.compile()

graph = build_graph()