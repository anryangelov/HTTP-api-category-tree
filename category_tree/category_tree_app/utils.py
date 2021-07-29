from collections import defaultdict
from collections import deque


def make_tree_for_category_list(categories: list, field_name):

    if not categories:
        return {}

    categ_by_parent = defaultdict(list)
    for c in categories:
        categ_by_parent[c['parent_category']].append(c)

    root = categories[0]
    root[field_name] = categ_by_parent.pop(root['category_id'], [])
    deq = deque(root[field_name])

    while deq:
        cat = deq.popleft()
        children = categ_by_parent.pop(cat['category_id'], [])
        cat[field_name] = children
        deq.extend(children)

    return root


def get_graph(similarities):
    graph = defaultdict(list)
    for p1, p2 in similarities:
        graph[p1].append(p2)
    return graph


def get_visited(graph, category_id):
    '''bfs'''
    visited = set()
    queue = deque()
    queue.append(category_id)
    while queue:
        category_id = queue.popleft()
        if category_id not in visited:
            visited.add(category_id)
            new_categories = graph.get(category_id, [])
            queue.extend(new_categories)
    return visited


def get_islands_categories(similarities):
    islands = []
    graph = get_graph(similarities)
    searched = set()
    for category_id in graph.keys():
        if category_id not in searched:
            categories = get_visited(graph, category_id)
            islands.append(categories)
            searched.update(categories)
    return islands


def all_shortest_paths_for_category(graph, category_id):
    '''essensally bread first search'''
    paths = []
    path = (category_id,)
    visited = set([category_id])
    queue = deque()
    queue.append((path, graph.get(category_id, [])))
    while queue:
        path, category_ids = queue.popleft()
        category_ids = [c for c in category_ids if c not in visited]
        if not category_ids:
            paths.append(path)
        for category_id in category_ids:
            new_path = path + (category_id,)
            #new_path.append(category_id)
            visited.add(category_id)
            queue.append((new_path, graph.get(category_id, [])))

    return paths


def get_longest_lists(lists):
    max_len = len(max(lists, key=len))
    return [l for l in lists if len(l) == max_len]


def remove_reverse_paths(paths):
    result = set()
    for path in paths:
        if path[0] > path[-1]:
            path = tuple(reversed(path))
        result.add(path)
    return result


def get_longest_rabbit_holes(similarities):
    graph = get_graph(similarities)
    longest_paths = []
    for category_id in graph.keys():
        paths = all_shortest_paths_for_category(graph, category_id)
        paths = get_longest_lists(paths)
        longest_paths.extend(paths)
    return remove_reverse_paths(get_longest_lists(longest_paths))

