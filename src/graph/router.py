def input_router(state):

    if state['input_category'] == 'article':
        return 'article'
    
    if state['input_category'] == 'dataset':
        return 'dataset'

    return 'END'