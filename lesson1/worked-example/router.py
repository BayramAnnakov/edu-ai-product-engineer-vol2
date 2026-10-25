"""Only pre-answer input fields reach this router. Start with all-model baseline."""
def choose_route(item):
    if not isinstance(item, dict):
        return 'model'
    files = item.get('files')
    if not isinstance(files, list) or not files:
        return 'model'
    for path in files:
        if not isinstance(path, str) or not path or '\\' in path or ':' in path or '\x00' in path:
            return 'model'
        parts = path.split('/')
        if any(part in ('', '.', '..') for part in parts):
            return 'model'
        if path != 'README.md' and not (len(parts) > 1 and parts[0] == 'docs' and path.endswith('.md')):
            return 'model'
    return 'cheap'


def cheap_answer(item):
    return 'clear'
