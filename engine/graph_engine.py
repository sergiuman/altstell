"""
AltStell Multi-Agent Graph Engine (NetworkX + Local Ollama gemma2:latest).

Implements TWO interconnected graphs:
1. Knowledge Graph (nx.MultiDiGraph):
   - Nodes: Books (17), Developmental Values (25+), 11yo Dilemmas (17+), Short-Video Episodes (24+)
   - Edges: TEACHES_VALUE, SYNERGIZES_WITH, CONTRASTS_TENSION, SOLVES_DILEMMA, DRAMATIZES, LEARNED_FUSION
   - Algorithms: PageRank Value Importance, Under-Explored Bridge Scoring, Value-Path Recommendation.

2. Agent Execution StateGraph (Directed Graph with Conditional Feedback Loops):
   [CuratorNode] -> [ValueDiscoveryNode] -> [AltStoryArchitectNode] -> [ChildPsychGuardNode]
        ^                                          ^                            |
        |                                          +---- (revise if < 86) ------+
        |                                                                       v (pass)
   [UpdateGraphWeights] <--- [GitHubPublisherNode] <--- [QABenchmarkNode] <--- [MediaSynthesizerNode]
"""
import json
import math
import os
import re
import time
from datetime import datetime, timezone
from typing import Any, Callable, Dict, List, Optional, Tuple

import networkx as nx

from engine import ollama_client


BASE_DIR = "/Users/sergiuman/Desktop/Gemini/Books"
GRAPH_PATH = os.path.join(BASE_DIR, "data", "knowledge_graph.json")
SEED_GRAPH_PATH = os.path.join(BASE_DIR, "data", "seed_knowledge_graph.json")
FEED_PATH = os.path.join(BASE_DIR, "data", "feed.json")
PRINCIPLES_PATH = os.path.join(BASE_DIR, "data", "storytelling_principles.json")


DEFAULT_PRINCIPLES = {
    "version": 1,
    "target_age": 11,
    "core_philosophy": "Alternative Storytelling that sparks curiosity, metacognition, empathy, and real-world agency without addictive dark patterns.",
    "rules": [
        "Hook within 3 seconds using a relatable 11-year-old cognitive puzzle, friend dilemma, or surprising perspective shift.",
        "Maintain middle-grade readability (Flesch-Kincaid Grade 5.0–7.2): vivid verbs, concrete sensory imagery, zero baby-talk, zero corporate buzzwords.",
        "Always present a Dual-Perspective Flip so the viewer practices empathy and sees past System-1 snap judgments.",
        "Include an interactive 'What Would You Do?' dilemma where neither choice shames the child, and the growth choice models emotional regulation and agency.",
        "End every episode with a concrete 2-minute Offline Real-World Quest so digital stories transfer into real-world competence and play.",
        "Ensure full bilingual parity between English and natural, idiomatic Romanian with accurate diacritics (ă, â, î, ș, ț)."
    ],
    "learned_heuristics": [
        "11-year-olds respond far better to inner-voice contrast ('My fast brain shouted X, my wise brain noticed Y') than adult lectures.",
        "Pairing two complementary values from different books (e.g., Quiet Observation + Deep Listening) creates novel 'superpower combinations'."
    ]
}


class KnowledgeGraphManager:
    """Manages the NetworkX MultiDiGraph of Books, Psychological Values, Dilemmas, and Episodes."""

    def __init__(self, graph_path: str = GRAPH_PATH):
        self.graph_path = graph_path
        self.G = nx.MultiDiGraph()
        self.raw_data: Dict[str, Any] = {"nodes": [], "edges": [], "learned_bridges": [], "meta": {}}

    def load(self) -> nx.MultiDiGraph:
        source = self.graph_path if os.path.exists(self.graph_path) else SEED_GRAPH_PATH
        if os.path.exists(source):
            with open(source, "r", encoding="utf-8") as f:
                self.raw_data = json.load(f)
        self._rebuild_nx()
        return self.G

    def _rebuild_nx(self) -> None:
        self.G.clear()
        for node in self.raw_data.get("nodes", []):
            nid = node["id"]
            self.G.add_node(nid, **node)
        for edge in self.raw_data.get("edges", []):
            src = edge.get("source")
            dst = edge.get("target")
            rel = edge.get("relation") or edge.get("type") or "RELATED_TO"
            edge["relation"] = rel
            edge["type"] = rel
            if src in self.G and dst in self.G:
                self.G.add_edge(src, dst, key=rel, **edge)

    def sync_episodes_into_graph(self, episodes: List[Dict[str, Any]]) -> None:
        """Integrates all episodes as first-class graph nodes & links them to books, values, and dilemmas."""
        existing_non_ep = [n for n in self.raw_data.get("nodes", []) if n.get("type") != "episode"]
        existing_edges = [
            e for e in self.raw_data.get("edges", [])
            if (e.get("relation") or e.get("type")) not in ("DRAMATIZES_BOOK", "ACTIVATE_VALUE", "EXPLORES_DILEMMA", "NEXT_SPARK")
        ]

        ep_nodes = []
        ep_edges = []
        for ep in episodes:
            eid = ep["id"]
            ep_nodes.append({
                "id": eid,
                "type": "episode",
                "label_en": ep["title"]["en"],
                "label_ro": ep["title"]["ro"],
                "alt_format": ep.get("alt_format", "PERSPECTIVE_FLIP"),
                "category": ep.get("category", "brain_systems"),
                "is_graph_fusion": bool(ep.get("is_graph_fusion", len(ep.get("book_ids", [])) > 1)),
                "accent_color": ep.get("accent_color", "#6366f1"),
            })
            for bid in ep.get("book_ids", []):
                ep_edges.append({
                    "source": eid,
                    "target": bid,
                    "relation": "DRAMATIZES_BOOK",
                    "weight": 0.95,
                })
            for vid in ep.get("value_ids", []):
                ep_edges.append({
                    "source": eid,
                    "target": vid,
                    "relation": "ACTIVATE_VALUE",
                    "weight": 0.92,
                })
            did = ep.get("dilemma_id")
            if did:
                ep_edges.append({
                    "source": eid,
                    "target": did,
                    "relation": "EXPLORES_DILEMMA",
                    "weight": 0.88,
                })

        self.raw_data["nodes"] = existing_non_ep + ep_nodes
        self.raw_data["edges"] = existing_edges + ep_edges
        self._rebuild_nx()

        # Compute developmental NEXT_SPARK edges between episodes sharing complementary values
        next_edges = self._compute_developmental_recommendations(episodes)
        self.raw_data["edges"].extend(next_edges)
        self._rebuild_nx()

    def _compute_developmental_recommendations(self, episodes: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Links each episode to 2 developmentally complementary next episodes via shared/synergistic values."""
        synergy_pairs = set()
        for u, v, data in self.G.edges(data=True):
            if data.get("relation") in ("SYNERGIZES_WITH", "CONTRASTS_TENSION"):
                synergy_pairs.add((u, v))
                synergy_pairs.add((v, u))

        rec_edges = []
        for ep_a in episodes:
            scores: List[Tuple[float, str]] = []
            vals_a = set(ep_a.get("value_ids", []))
            books_a = set(ep_a.get("book_ids", []))
            for ep_b in episodes:
                if ep_a["id"] == ep_b["id"]:
                    continue
                vals_b = set(ep_b.get("value_ids", []))
                books_b = set(ep_b.get("book_ids", []))
                overlap = len(vals_a & vals_b) * 0.45
                synergy = sum(0.4 for va in vals_a for vb in vals_b if (va, vb) in synergy_pairs)
                novel_book_bonus = 0.25 if not (books_a & books_b) else 0.0
                format_variety = 0.15 if ep_a.get("alt_format") != ep_b.get("alt_format") else 0.0
                total = overlap + synergy + novel_book_bonus + format_variety
                if total > 0:
                    scores.append((total, ep_b["id"]))
            scores.sort(reverse=True)
            for sc, target_ep in scores[:2]:
                rec_edges.append({
                    "source": ep_a["id"],
                    "target": target_ep,
                    "relation": "NEXT_SPARK",
                    "weight": round(min(0.99, sc), 3),
                })
        return rec_edges

    def compute_graph_metrics(self) -> Dict[str, Any]:
        """Computes PageRank centrality, node/edge counts, connected components, and value coverage."""
        if len(self.G) == 0:
            return {"nodes": 0, "edges": 0, "density": 0.0, "largest_wcc_ratio": 0.0}

        simple_di = nx.DiGraph()
        for n, d in self.G.nodes(data=True):
            simple_di.add_node(n, **d)
        for u, v, d in self.G.edges(data=True):
            w = float(d.get("weight", 0.7))
            if simple_di.has_edge(u, v):
                simple_di[u][v]["weight"] = max(simple_di[u][v]["weight"], w)
            else:
                simple_di.add_edge(u, v, weight=w)

        # Undirected projection for centrality across bidirectional wisdom web
        undir = simple_di.to_undirected()
        try:
            pr = nx.pagerank(undir, weight="weight")
        except Exception:
            # Pure-Python weighted PageRank power iteration (damping=0.85, 60 iterations)
            nodes_list = list(undir.nodes())
            n_cnt = max(1, len(nodes_list))
            pr = {n: 1.0 / n_cnt for n in nodes_list}
            out_w = {
                u: sum(float(undir[u][v].get("weight", 1.0)) for v in undir.neighbors(u))
                for u in nodes_list
            }
            alpha = 0.85
            for _ in range(60):
                nxt = {n: (1.0 - alpha) / n_cnt for n in nodes_list}
                dangling = sum(pr[u] for u in nodes_list if out_w[u] == 0.0)
                for u in nodes_list:
                    nxt[u] += alpha * dangling / n_cnt
                    if out_w[u] > 0:
                        for v in undir.neighbors(u):
                            w = float(undir[u][v].get("weight", 1.0))
                            nxt[v] += alpha * pr[u] * (w / out_w[u])
                pr = nxt

        for nid, score in pr.items():
            if nid in self.G.nodes:
                self.G.nodes[nid]["centrality"] = round(score, 5)
        for node_obj in self.raw_data.get("nodes", []):
            node_obj["centrality"] = round(pr.get(node_obj["id"], 0.0), 5)

        wccs = list(nx.connected_components(undir))
        largest_wcc = max((len(c) for c in wccs), default=0)
        value_nodes = [n for n, d in self.G.nodes(data=True) if d.get("type") == "value"]
        covered_values = [
            v for v in value_nodes
            if any(self.G.nodes[p].get("type") == "episode" for p in self.G.predecessors(v))
        ]
        fusion_eps = [
            n for n, d in self.G.nodes(data=True)
            if d.get("type") == "episode" and d.get("is_graph_fusion")
        ]

        top_values = sorted(
            [(v, pr.get(v, 0.0)) for v in value_nodes],
            key=lambda x: x[1],
            reverse=True,
        )[:6]

        metrics = {
            "total_nodes": self.G.number_of_nodes(),
            "total_edges": self.G.number_of_edges(),
            "book_count": sum(1 for _, d in self.G.nodes(data=True) if d.get("type") == "book"),
            "value_count": len(value_nodes),
            "dilemma_count": sum(1 for _, d in self.G.nodes(data=True) if d.get("type") == "dilemma"),
            "episode_count": sum(1 for _, d in self.G.nodes(data=True) if d.get("type") == "episode"),
            "fusion_episode_count": len(fusion_eps),
            "value_coverage_ratio": round(len(covered_values) / max(1, len(value_nodes)), 4),
            "largest_wcc_ratio": round(largest_wcc / max(1, self.G.number_of_nodes()), 4),
            "avg_degree": round(
                sum(dict(undir.degree()).values()) / max(1, undir.number_of_nodes()), 2
            ),
            "top_central_values": [
                {"id": vid, "label_en": self.G.nodes[vid].get("label_en", vid), "pagerank": round(sc, 5)}
                for vid, sc in top_values
            ],
            "updated_at": datetime.now(timezone.utc).isoformat(),
        }
        self.raw_data["meta"] = metrics
        return metrics

    def discover_next_value_bridge(self, existing_episodes: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Finds the highest-potential pair of values from DIFFERENT books that have NOT yet been
        combined in an episode, ranking by (centrality_a + centrality_b + synergy_bonus).
        """
        used_pairs = set()
        for ep in existing_episodes:
            vids = sorted(ep.get("value_ids", []))
            for i in range(len(vids)):
                for j in range(i + 1, len(vids)):
                    used_pairs.add((vids[i], vids[j]))

        # First check curated learned_bridges not yet turned into an episode
        for bridge in self.raw_data.get("learned_bridges", []):
            va = bridge.get("value_a")
            vb = bridge.get("value_b")
            if va and vb and tuple(sorted([va, vb])) not in used_pairs:
                if va in self.G and vb in self.G:
                    return bridge

        # Otherwise discover dynamically from NetworkX graph topology!
        value_nodes = [n for n, d in self.G.nodes(data=True) if d.get("type") == "value"]
        value_to_books: Dict[str, List[str]] = {v: [] for v in value_nodes}
        for u, v, d in self.G.edges(data=True):
            if d.get("relation") == "TEACHES_VALUE" and v in value_to_books:
                value_to_books[v].append(u)

        best_score = -1.0
        best_pair: Optional[Tuple[str, str]] = None
        for i, va in enumerate(value_nodes):
            for vb in value_nodes[i + 1:]:
                pair = tuple(sorted([va, vb]))
                if pair in used_pairs:
                    continue
                books_a = set(value_to_books.get(va, []))
                books_b = set(value_to_books.get(vb, []))
                cross_book = 0.5 if (books_a and books_b and not (books_a & books_b)) else 0.1
                ca = float(self.G.nodes[va].get("centrality", 0.02))
                cb = float(self.G.nodes[vb].get("centrality", 0.02))
                has_synergy = 0.35 if (self.G.has_edge(va, vb) or self.G.has_edge(vb, va)) else 0.15
                dom_a = self.G.nodes[va].get("domain", "")
                dom_b = self.G.nodes[vb].get("domain", "")
                cross_domain = 0.25 if dom_a != dom_b else 0.05
                score = (ca + cb) * 10.0 + cross_book + has_synergy + cross_domain
                if score > best_score:
                    best_score = score
                    best_pair = (va, vb)

        if not best_pair:
            best_pair = (value_nodes[0], value_nodes[-1])

        va, vb = best_pair
        ba = (value_to_books.get(va) or ["book_01"])[0]
        bb = (value_to_books.get(vb) or ["book_08"])[0]
        na = self.G.nodes[va]
        nb = self.G.nodes[vb]
        return {
            "bridge_id": f"bridge_{va}_{vb}",
            "value_a": va,
            "value_b": vb,
            "book_a": ba,
            "book_b": bb,
            "label_a_en": na.get("label_en", va),
            "label_b_en": nb.get("label_en", vb),
            "label_a_ro": na.get("label_ro", va),
            "label_b_ro": nb.get("label_ro", vb),
            "emergent_principle_en": f"Combining {na.get('label_en', va)} with {nb.get('label_en', vb)} unlocks deeper self-mastery for 11-year-olds.",
            "emergent_principle_ro": f"Îmbinarea dintre {na.get('label_ro', va)} și {nb.get('label_ro', vb)} deschide o nouă putere interioară la 11 ani.",
        }

    def save(self) -> None:
        os.makedirs(os.path.dirname(self.graph_path), exist_ok=True)
        with open(self.graph_path, "w", encoding="utf-8") as f:
            json.dump(self.raw_data, f, ensure_ascii=False, indent=2)


class AgentExecutionGraph:
    """
    Directed Graph State Machine with conditional edges & revision loops for multi-agent execution.
    """

    def __init__(self):
        self.workflow = nx.DiGraph()
        self.handlers: Dict[str, Callable[[Dict[str, Any]], Dict[str, Any]]] = {}
        self.routers: Dict[str, Callable[[Dict[str, Any]], str]] = {}

    def add_agent_node(self, name: str, handler: Callable[[Dict[str, Any]], Dict[str, Any]]) -> None:
        self.workflow.add_node(name)
        self.handlers[name] = handler

    def add_edge(self, src: str, dst: str) -> None:
        self.workflow.add_edge(src, dst)

    def add_conditional_edges(self, src: str, router: Callable[[Dict[str, Any]], str], targets: List[str]) -> None:
        for t in targets:
            self.workflow.add_edge(src, t, conditional=True)
        self.routers[src] = router

    def run(self, entry_node: str, initial_state: Dict[str, Any], max_steps: int = 20) -> Dict[str, Any]:
        state = dict(initial_state)
        state.setdefault("trace", [])
        curr: Optional[str] = entry_node
        steps = 0

        while curr and curr != "END" and steps < max_steps:
            steps += 1
            t0 = time.time()
            handler = self.handlers[curr]
            state = handler(state)
            elapsed_ms = int((time.time() - t0) * 1000)
            state["trace"].append({"step": steps, "agent": curr, "elapsed_ms": elapsed_ms})

            if curr in self.routers:
                curr = self.routers[curr](state)
            else:
                succ = list(self.workflow.successors(curr))
                curr = succ[0] if succ else "END"

        return state
