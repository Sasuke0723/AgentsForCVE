"""计划功能：组装漏洞复现主流程图，串联 knowledge、build、poc、verify 四个阶段。"""
try:
    from langgraph.graph import StateGraph, END
except ImportError:
    END = "__end__"

    class _CompiledStateGraph:
        def __init__(self, entry_point, nodes, edges, conditional_edges):
            self.entry_point = entry_point
            self.nodes = nodes
            self.edges = edges
            self.conditional_edges = conditional_edges

        def invoke(self, initial_state):
            state = dict(initial_state)
            current = self.entry_point

            while current != END:
                updates = self.nodes[current](state) or {}
                state.update(updates)

                if current in self.conditional_edges:
                    router, mapping = self.conditional_edges[current]
                    route = router(state)
                    current = mapping[route]
                elif current in self.edges:
                    current = self.edges[current]
                else:
                    current = END
            return state

    class StateGraph:
        def __init__(self, _state_type):
            self.nodes = {}
            self.edges = {}
            self.conditional_edges = {}
            self.entry_point = None

        def add_node(self, name, node):
            self.nodes[name] = node

        def set_entry_point(self, name):
            self.entry_point = name

        def add_edge(self, start, end):
            self.edges[start] = end

        def add_conditional_edges(self, start, router, mapping):
            self.conditional_edges[start] = (router, mapping)

        def compile(self):
            return _CompiledStateGraph(
                entry_point=self.entry_point,
                nodes=self.nodes,
                edges=self.edges,
                conditional_edges=self.conditional_edges,
            )

from app.orchestrator.state import AppState
from app.orchestrator.routers import route_after_build, route_after_poc, route_after_verify
from app.nodes.knowledge_node import knowledge_node
from app.nodes.build_node import build_node
from app.nodes.poc_node import poc_node
from app.nodes.verify_node import verify_node


def build_app_graph():
    graph = StateGraph(AppState)

    graph.add_node("knowledge", knowledge_node)
    graph.add_node("build", build_node)
    graph.add_node("poc", poc_node)
    graph.add_node("verify", verify_node)

    graph.set_entry_point("knowledge")

    graph.add_edge("knowledge", "build")

    graph.add_conditional_edges(
        "build",
        route_after_build,
        {
            "poc": "poc",
            "build": "build",
            "failed": END,
        },
    )

    graph.add_conditional_edges(
        "poc",
        route_after_poc,
        {
            "verify": "verify",
            "poc": "poc",
            "failed": END,
        },
    )

    graph.add_conditional_edges(
        "verify",
        route_after_verify,
        {
            "success": END,
            "failed": END,
        },
    )

    return graph.compile()
