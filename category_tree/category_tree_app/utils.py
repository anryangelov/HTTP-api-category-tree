from collections import defaultdict


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


def bfs(node):
    visited = set()
    queue = []
    visited.add(node)
    queue.append(node)

    while queue:
        s = queue.pop(0) 

        for neighbour in graph[s]:
            if neighbour not in visited:
                visited.add(neighbour)
                queue.append(neighbour)
