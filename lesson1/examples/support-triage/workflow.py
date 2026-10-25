"""Only pre-answer input fields reach this router. Start with all-model baseline."""
def choose_route(item):
    return 'model'


def cheap_answer(item):
    return item['cache']['answer']
