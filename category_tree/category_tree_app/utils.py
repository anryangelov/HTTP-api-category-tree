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


def is_vertex_part_of_island(new_vertex, island):
    for vertex in island:
        if set(new_vertex).intersection(vertex):
            return True
    return False


def is_vertex_part_of_any_island(new_vertex, islands):
    if not islands:
        return False
    for island in islands:
        if is_vertex_part_of_island(new_vertex, island):
            island.add(new_vertex)
            return True
    return False


def get_islands_vertexes(similarities):
    islands = []
    for new_vertex in sorted(list(similarities)):
        if not is_vertex_part_of_any_island(new_vertex, islands):
            new_island = {new_vertex}
            islands.append(new_island)
    return islands


def get_islands_categories(islands_vertexes):
    islands = []
    for island_vertexes in islands_vertexes:
        categories = set()
        for vertex in island_vertexes:
            categories.update(vertex)
        islands.append(categories)
    return islands


def get_graph(island_vertexes):
    graph = defaultdict(list)
    for p1, p2 in sorted(list(island_vertexes)):
        graph[p1].append(p2)
    return graph


def all_shortest_paths_for_category_in_island(graph, category_id):
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
    islands_longest_paths = []
    islands_vertexes = get_islands_vertexes(similarities)
    for island_vertexes in islands_vertexes:
        graph = get_graph(island_vertexes)
        for category_id in graph.keys():
            paths = all_shortest_paths_for_category_in_island(graph, category_id)
            longest_paths = get_longest_lists(paths)
            islands_longest_paths.extend(longest_paths)

    return remove_reverse_paths(get_longest_lists(islands_longest_paths))
