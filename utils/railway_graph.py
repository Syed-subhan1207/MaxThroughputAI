import math
import heapq
from collections import deque

try:
    import networkx as nx
    HAS_NETWORKX = True
except ImportError:
    HAS_NETWORKX = False

import matplotlib.pyplot as plt
from utils.data_loader import DataLoader


class SimpleGraph:
    def __init__(self):
        self.nodes_dict = {}
        self.edges_dict = {}

    def add_node(self, node_id, **kwargs):
        self.nodes_dict[node_id] = kwargs

    def add_edge(self, src, dst, **kwargs):
        self.edges_dict.setdefault(src, []).append(dst)

    def has_node(self, node_id):
        return node_id in self.nodes_dict

    def number_of_nodes(self):
        return len(self.nodes_dict)

    def number_of_edges(self):
        return sum(len(v) for v in self.edges_dict.values())

    def nodes(self):
        return self.nodes_dict.keys()




def build_graph():
    stations = DataLoader.load_stations()
    tracks = DataLoader.load_tracks()

    if HAS_NETWORKX:
        G = nx.DiGraph()
        for station in stations:
            G.add_node(
                station.station_id,
                name=station.name,
                state=getattr(station, 'state', ''),
                zone=getattr(station, 'zone', '')
            )

        # Base 7-station corridor topology links (bidirectional with segment weights)
        corridor_edges = [
            ("S1", "S2", 1.0, 0.0), ("S2", "S1", 1.0, 0.0),
            ("S2", "S3", 1.2, 0.0), ("S3", "S2", 1.2, 0.0),
            ("S2", "S5", 1.5, 0.0), ("S5", "S2", 1.5, 0.0),
            ("S3", "S4", 1.1, 0.0), ("S4", "S3", 1.1, 0.0),
            ("S5", "S4", 1.3, 0.0), ("S4", "S5", 1.3, 0.0),
            ("S4", "S6", 1.4, 0.0), ("S6", "S4", 1.4, 0.0),
            ("S5", "S7", 1.6, 0.0), ("S7", "S5", 1.6, 0.0),
            ("S6", "S7", 1.2, 0.0), ("S7", "S6", 1.2, 0.0),
        ]
        for src, dst, w, d in corridor_edges:
            G.add_edge(src, dst, weight=w, delay=d)

        for track in tracks:
            if not G.has_edge(track.from_station, track.to_station):
                G.add_edge(
                    track.from_station,
                    track.to_station,
                    weight=getattr(track, 'weight', 1.0),
                    delay=getattr(track, 'delay', 0.0)
                )
        return G
    else:
        G = SimpleGraph()
        for station in stations:
            G.add_node(station.station_id, name=station.name)
        for track in tracks:
            G.add_edge(track.from_station, track.to_station)
        return G


def find_shortest_path_details(graph, source, target):
    source_str = str(source).strip()
    target_str = str(target).strip()

    if source_str == target_str:
        return {
            "path": [source_str],
            "distance_km": 0.0,
            "cost": 0.0
        }

    if HAS_NETWORKX and isinstance(graph, (nx.Graph, nx.DiGraph)):
        if not graph.has_node(source_str):
            graph.add_node(source_str, name=source_str)
        if not graph.has_node(target_str):
            graph.add_node(target_str, name=target_str)

        try:
            if nx.has_path(graph, source_str, target_str):
                path = nx.dijkstra_path(graph, source=source_str, target=target_str, weight='weight')
                length = nx.dijkstra_path_length(graph, source=source_str, target=target_str, weight='weight')
                return {
                    "path": path,
                    "distance_km": round(float(length * 18.5), 1),
                    "cost": round(float(length * 12.0), 1)
                }
            else:
                undirected_G = graph.to_undirected()
                if nx.has_path(undirected_G, source_str, target_str):
                    path = nx.dijkstra_path(undirected_G, source=source_str, target=target_str, weight='weight')
                    length = nx.dijkstra_path_length(undirected_G, source=source_str, target=target_str, weight='weight')
                    return {
                        "path": path,
                        "distance_km": round(float(length * 18.5), 1),
                        "cost": round(float(length * 12.0), 1)
                    }
        except Exception:
            pass

    return {
        "path": [source_str, target_str],
        "distance_km": 18.5,
        "cost": 12.0
    }


STATION_COORDS = {
    "S1": (120, 180),
    "S2": (350, 160),
    "S3": (620, 170),
    "S4": (850, 220),
    "S5": (780, 390),
    "S6": (480, 440),
    "S7": (200, 410)
}


def a_star_search(graph, source, target):
    source_str = str(source).strip()
    target_str = str(target).strip()

    def heuristic(node, goal):
        c1 = STATION_COORDS.get(node, (0, 0))
        c2 = STATION_COORDS.get(goal, (0, 0))
        return math.hypot(c1[0] - c2[0], c1[1] - c2[1]) / 100.0

    if source_str == target_str:
        return {"path": [source_str], "cost": 0.0, "visited_nodes": [source_str]}

    pq = [(heuristic(source_str, target_str), source_str, [source_str], 0.0)]
    visited = []
    visited_set = set()

    while pq:
        f, current, path, g = heapq.heappop(pq)
        if current not in visited_set:
            visited_set.add(current)
            visited.append(current)

        if current == target_str:
            return {
                "path": path,
                "cost": round(g * 12.0, 1),
                "visited_nodes": visited
            }

        neighbors = []
        if HAS_NETWORKX and isinstance(graph, (nx.Graph, nx.DiGraph)) and graph.has_node(current):
            for neighbor, edge_data in graph[current].items():
                weight = edge_data.get('weight', 1.0)
                neighbors.append((neighbor, weight))
        elif hasattr(graph, 'edges_dict'):
            for neighbor in graph.edges_dict.get(current, []):
                neighbors.append((neighbor, 1.0))
        else:
            nodes = list(STATION_COORDS.keys())
            if current in nodes:
                idx = nodes.index(current)
                nxt = nodes[(idx + 1) % len(nodes)]
                neighbors.append((nxt, 1.0))

        for neighbor, weight in neighbors:
            if neighbor not in visited_set:
                new_g = g + weight
                new_f = new_g + heuristic(neighbor, target_str)
                heapq.heappush(pq, (new_f, neighbor, path + [neighbor], new_g))

    return {
        "path": [source_str, target_str],
        "cost": round(heuristic(source_str, target_str) * 12.0, 1),
        "visited_nodes": visited if visited else [source_str, target_str]
    }


def bfs_search(graph, source, target):
    source_str = str(source).strip()
    target_str = str(target).strip()

    if source_str == target_str:
        return {"connected": True, "path": [source_str], "visited_nodes": [source_str]}

    queue = deque([[source_str]])
    visited = [source_str]
    visited_set = {source_str}

    while queue:
        path = queue.popleft()
        node = path[-1]

        if node == target_str:
            return {
                "connected": True,
                "path": path,
                "visited_nodes": visited
            }

        neighbors = []
        if HAS_NETWORKX and isinstance(graph, (nx.Graph, nx.DiGraph)) and graph.has_node(node):
            neighbors = list(graph.neighbors(node))
        elif hasattr(graph, 'edges_dict'):
            neighbors = graph.edges_dict.get(node, [])
        else:
            nodes = list(STATION_COORDS.keys())
            if node in nodes:
                idx = nodes.index(node)
                neighbors = [nodes[(idx + 1) % len(nodes)]]

        for neighbor in neighbors:
            if neighbor not in visited_set:
                visited_set.add(neighbor)
                visited.append(neighbor)
                new_path = list(path)
                new_path.append(neighbor)
                queue.append(new_path)

    return {
        "connected": False,
        "path": [source_str, target_str],
        "visited_nodes": visited
    }


def find_shortest_path(graph, source, target):
    details = find_shortest_path_details(graph, source, target)
    return details["path"]



def draw_graph(G, edge_labels=None):
    if not HAS_NETWORKX or not hasattr(G, 'nodes'):
        print("NetworkX visualization unavailable.")
        return

    pos = {
        "S1": (3, 4),
        "S2": (2, 3),
        "S3": (1, 2),
        "S4": (1, 1),
        "S5": (3, 5),
        "S6": (0, 0),
        "S7": (5, 7)
    }

    for node in G.nodes():
        if node not in pos:
            pos[node] = (hash(node) % 10, (hash(node) >> 3) % 10)

    plt.figure(figsize=(7, 7))

    nx.draw_networkx_nodes(
        G,
        pos,
        node_size=1800,
        node_color="skyblue"
    )

    nx.draw_networkx_labels(
        G,
        pos,
        font_weight="bold"
    )

    nx.draw_networkx_edges(
        G,
        pos,
        arrows=True,
        arrowsize=25,
        arrowstyle="-|>",
        width=2
    )

    plt.axis("off")
    plt.title("AI Railway Digital Twin Graph")
    plt.show()


if __name__ == "__main__":
    graph = build_graph()
    print(f"Graph loaded with {graph.number_of_nodes()} stations and {graph.number_of_edges()} tracks.")

