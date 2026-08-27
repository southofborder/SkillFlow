"""Port of src/analyzer/fcg-builder.js — the graph container + id assignment.

FunctionCallGraph mirrors the JS class: nodes is an insertion-ordered dict
(node_id -> node), edges is a list, adjacency_list is node_id -> [neighbor_ids].
build_fcg assigns `node_NNN` ids in tool order (the M1 acceptance unit). Keys are
mirrored verbatim (id, source, target, confidence, ...).
"""


class FunctionCallGraph:
    """Port of the FunctionCallGraph class (fcg-builder.js:6-80)."""

    def __init__(self):
        self.nodes = {}          # node_id -> node (insertion-ordered dict == JS Map)
        self.edges = []          # [{source, target, confidence, ...}]
        self.adjacency_list = {}  # node_id -> [neighbor_ids]

    # Port of addNode (fcg-builder.js:17-22)
    def add_node(self, node):
        self.nodes[node["id"]] = node
        if node["id"] not in self.adjacency_list:
            self.adjacency_list[node["id"]] = []

    # Port of addEdge (fcg-builder.js:28-34)
    def add_edge(self, edge):
        self.edges.append(edge)
        if edge["source"] not in self.adjacency_list:
            self.adjacency_list[edge["source"]] = []
        self.adjacency_list[edge["source"]].append(edge["target"])

    # Port of getAllNodes (fcg-builder.js:40-42)
    def get_all_nodes(self):
        return list(self.nodes.values())

    # Port of getAllEdges (fcg-builder.js:48-50)
    def get_all_edges(self):
        return self.edges

    # Port of getNeighbors (fcg-builder.js:57-59)
    def get_neighbors(self, node_id):
        return self.adjacency_list.get(node_id, [])

    # Port of getNode (fcg-builder.js:66-68)
    def get_node(self, node_id):
        return self.nodes.get(node_id)

    # Port of getStatistics (fcg-builder.js:74-79)
    def get_statistics(self):
        return {"total_nodes": len(self.nodes), "total_edges": len(self.edges)}


# Port of buildFCG (fcg-builder.js:88-107)
def build_fcg(tools, validated_edges):
    graph = FunctionCallGraph()
    for i, tool in enumerate(tools):
        node = {**tool, "id": f"node_{str(i + 1).rjust(3, '0')}"}
        graph.add_node(node)
    for edge in validated_edges:
        graph.add_edge(edge)
    return graph


# Port of removeDuplicateEdges (fcg-builder.js:115-145)
def remove_duplicate_edges(graph):
    edge_map = {}
    for edge in graph.edges:
        key = f"{edge['source']}->{edge['target']}:{edge.get('type') or 'data_dependency'}"
        if key not in edge_map:
            edge_map[key] = edge
        else:
            existing = edge_map[key]
            # JS `edge.confidence > existing.confidence`: any undefined/NaN operand
            # makes the comparison false, so only replace when both are numbers.
            ec = edge.get("confidence")
            xc = existing.get("confidence")
            if isinstance(ec, (int, float)) and isinstance(xc, (int, float)) and ec > xc:
                edge_map[key] = edge

    graph.edges = list(edge_map.values())
    graph.adjacency_list = {}
    for node_id in graph.nodes.keys():
        graph.adjacency_list[node_id] = []
    for edge in graph.edges:
        graph.adjacency_list[edge["source"]].append(edge["target"])
    return graph
