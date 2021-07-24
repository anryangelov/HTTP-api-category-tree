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
