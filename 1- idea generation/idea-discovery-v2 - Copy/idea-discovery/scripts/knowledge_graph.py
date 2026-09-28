"""
knowledge_graph.py — Research Knowledge Graph
Builds a typed graph of papers, methods, problems, datasets, claims, conflicts.
Gap detection becomes graph queries instead of LLM guessing.
"""

import json
from pathlib import Path
from collections import defaultdict
from typing import Optional

import sys
sys.path.insert(0, str(Path(__file__).parent))
from utils import log, save_json

try:
    import networkx as nx
except ImportError:
    raise ImportError("networkx required. Run: pip install networkx")


class ResearchGraph:
    """
    Knowledge graph for research papers.

    Node types: paper, method, problem, dataset, metric, claim
    Edge types: uses_method, addresses_problem, evaluates_on, measures_with,
                claims, cites, conflicts_with, extends, competes_with
    """

    def __init__(self):
        self.G = nx.DiGraph()
        self._stats = defaultdict(int)

    # ── Building ────────────────────────────────────────────────────────────

    def add_paper(self, paper: dict):
        """Add a paper and all its entities + relationships to the graph."""
        pid = paper.get("paper_id", "unknown")
        if "_error" in paper:
            return

        # Paper node
        self.G.add_node(pid, type="paper",
                        title=paper.get("title", ""),
                        year=paper.get("year"),
                        venue=paper.get("venue", ""))
        self._stats["papers"] += 1

        # Method node + edge
        method = paper.get("method", {})
        if isinstance(method, dict) and method.get("name"):
            method_id = f"method:{method['name'].lower().strip()}"
            category = method.get("category", "unknown")
            self.G.add_node(method_id, type="method",
                            name=method.get("name", ""),
                            category=category,
                            mechanism=method.get("mechanism", ""))
            self.G.add_edge(pid, method_id, type="uses_method")
            self._stats["methods"] += 1

            # Method category node (higher level)
            if category and category != "unknown":
                cat_id = f"category:{category}"
                self.G.add_node(cat_id, type="method_category", name=category)
                self.G.add_edge(method_id, cat_id, type="belongs_to_category")

        # Problem node + edge
        problem = paper.get("problem", {})
        if isinstance(problem, dict) and problem.get("statement"):
            # Normalize problem — use first 80 chars as key
            prob_text = problem["statement"][:80].lower().strip()
            prob_id = f"problem:{prob_text}"
            self.G.add_node(prob_id, type="problem",
                            statement=problem.get("statement", ""),
                            motivation=problem.get("motivation", ""))
            self.G.add_edge(pid, prob_id, type="addresses_problem")
            self._stats["problems"] += 1

        # Dataset nodes + edges
        for ds in paper.get("datasets", []):
            if isinstance(ds, dict) and ds.get("name"):
                ds_id = f"dataset:{ds['name'].lower().strip()}"
                self.G.add_node(ds_id, type="dataset",
                                name=ds.get("name", ""),
                                domain=ds.get("domain", ""),
                                public=ds.get("public", True))
                self.G.add_edge(pid, ds_id, type="evaluates_on")
                self._stats["datasets"] += 1

        # Metric nodes + edges
        for mt in paper.get("metrics", []):
            if isinstance(mt, dict) and mt.get("name"):
                mt_id = f"metric:{mt['name'].lower().strip()}"
                self.G.add_node(mt_id, type="metric",
                                name=mt.get("name", ""))
                self.G.add_edge(pid, mt_id, type="measures_with",
                               value=mt.get("value", ""),
                               baseline=mt.get("baseline_comparison", ""))
                self._stats["metrics"] += 1

        # Claim nodes + edges
        for i, claim in enumerate(paper.get("claims", [])):
            if isinstance(claim, dict) and claim.get("claim"):
                claim_id = f"claim:{pid}:{i}"
                self.G.add_node(claim_id, type="claim",
                                text=claim.get("claim", ""),
                                evidence_type=claim.get("evidence_type", ""),
                                strength=claim.get("strength", ""))
                self.G.add_edge(pid, claim_id, type="claims")
                self._stats["claims"] += 1

        # Related work edges
        rw = paper.get("related_work_positioning", {})
        if isinstance(rw, dict):
            for ref in rw.get("builds_on", []):
                if ref:
                    self.G.add_edge(pid, str(ref), type="extends")
            for ref in rw.get("competes_with", []):
                if ref:
                    self.G.add_edge(pid, str(ref), type="competes_with")

    def add_conflict(self, conflict: dict):
        """Add a conflict edge between two papers."""
        pa = conflict.get("paper_a", {}).get("paper_id", "")
        pb = conflict.get("paper_b", {}).get("paper_id", "")
        if pa and pb and self.G.has_node(pa) and self.G.has_node(pb):
            self.G.add_edge(pa, pb,
                           type="conflicts_with",
                           conflict_id=conflict.get("conflict_id", ""),
                           conflict_type=conflict.get("type", ""),
                           severity=conflict.get("severity", ""))
            self._stats["conflicts"] += 1

    def build_from_corpus(self, corpus: dict, conflicts: Optional[dict] = None):
        """Build the full graph from corpus + optional conflicts."""
        for paper in corpus.get("papers", []):
            self.add_paper(paper)

        if conflicts:
            for conflict in conflicts.get("conflicts", []):
                self.add_conflict(conflict)

        log.info(f"Knowledge graph built: {self.G.number_of_nodes()} nodes, "
                 f"{self.G.number_of_edges()} edges")
        log.info(f"  Papers: {self._stats['papers']}, "
                 f"Methods: {self._stats['methods']}, "
                 f"Problems: {self._stats['problems']}, "
                 f"Datasets: {self._stats['datasets']}")

    # ── Querying ────────────────────────────────────────────────────────────

    def get_nodes_by_type(self, node_type: str) -> list[dict]:
        """Get all nodes of a given type."""
        return [
            {"id": n, **self.G.nodes[n]}
            for n in self.G.nodes
            if self.G.nodes[n].get("type") == node_type
        ]

    def get_method_problem_matrix(self) -> dict:
        """Build Method × Problem matrix from graph edges."""
        matrix = {}
        papers = self.get_nodes_by_type("paper")

        for paper in papers:
            pid = paper["id"]
            # Find methods and problems this paper connects to
            methods = [
                self.G.nodes[t].get("name", t)
                for _, t, d in self.G.out_edges(pid, data=True)
                if d.get("type") == "uses_method"
            ]
            problems = [
                self.G.nodes[t].get("statement", t)[:60]
                for _, t, d in self.G.out_edges(pid, data=True)
                if d.get("type") == "addresses_problem"
            ]

            for m in methods:
                for p in problems:
                    key = f"{m}|||{p}"
                    if key not in matrix:
                        matrix[key] = {"method": m, "problem": p, "papers": [], "count": 0}
                    matrix[key]["papers"].append(pid)
                    matrix[key]["count"] += 1

        return matrix

    def get_method_dataset_matrix(self) -> dict:
        """Build Method × Dataset matrix."""
        matrix = {}
        papers = self.get_nodes_by_type("paper")

        for paper in papers:
            pid = paper["id"]
            methods = [
                self.G.nodes[t].get("name", t)
                for _, t, d in self.G.out_edges(pid, data=True)
                if d.get("type") == "uses_method"
            ]
            datasets = [
                self.G.nodes[t].get("name", t)
                for _, t, d in self.G.out_edges(pid, data=True)
                if d.get("type") == "evaluates_on"
            ]

            for m in methods:
                for ds in datasets:
                    key = f"{m}|||{ds}"
                    if key not in matrix:
                        matrix[key] = {"method": m, "dataset": ds, "papers": [], "count": 0}
                    matrix[key]["papers"].append(pid)
                    matrix[key]["count"] += 1

        return matrix

    def find_structural_gaps(self) -> list[dict]:
        """
        Find gaps using graph structure:
        - Methods never applied to certain problems
        - Problems never evaluated on certain datasets
        - Methods never measured with certain metrics
        """
        gaps = []

        # Get unique methods and problems
        methods = set()
        problems = set()
        datasets = set()

        papers = self.get_nodes_by_type("paper")
        for paper in papers:
            pid = paper["id"]
            for _, t, d in self.G.out_edges(pid, data=True):
                if d.get("type") == "uses_method":
                    methods.add(t)
                elif d.get("type") == "addresses_problem":
                    problems.add(t)
                elif d.get("type") == "evaluates_on":
                    datasets.add(t)

        # Method × Problem gaps
        mp_matrix = self.get_method_problem_matrix()
        used_pairs = set(mp_matrix.keys())

        for m_node in methods:
            m_name = self.G.nodes[m_node].get("name", m_node)
            for p_node in problems:
                p_stmt = self.G.nodes[p_node].get("statement", p_node)[:60]
                key = f"{m_name}|||{p_stmt}"
                if key not in used_pairs:
                    gaps.append({
                        "type": "method_problem_void",
                        "method": m_name,
                        "method_node": m_node,
                        "problem": p_stmt,
                        "problem_node": p_node,
                        "description": f"Method '{m_name}' has never been applied to problem '{p_stmt}'",
                    })

        # Dataset monocultures: problems where all papers use same dataset
        problem_datasets = defaultdict(set)
        for paper in papers:
            pid = paper["id"]
            paper_problems = [
                t for _, t, d in self.G.out_edges(pid, data=True)
                if d.get("type") == "addresses_problem"
            ]
            paper_datasets = [
                self.G.nodes[t].get("name", t)
                for _, t, d in self.G.out_edges(pid, data=True)
                if d.get("type") == "evaluates_on"
            ]
            for prob in paper_problems:
                for ds in paper_datasets:
                    problem_datasets[prob].add(ds)

        for prob_node, ds_set in problem_datasets.items():
            if len(ds_set) == 1:
                p_stmt = self.G.nodes[prob_node].get("statement", prob_node)[:60]
                gaps.append({
                    "type": "dataset_monoculture",
                    "problem": p_stmt,
                    "problem_node": prob_node,
                    "dataset": list(ds_set)[0],
                    "description": f"Problem '{p_stmt}' evaluated on only one dataset: {list(ds_set)[0]}",
                })

        # Orphan methods (used in only 1 problem)
        method_problems = defaultdict(set)
        for paper in papers:
            pid = paper["id"]
            paper_methods = [t for _, t, d in self.G.out_edges(pid, data=True)
                             if d.get("type") == "uses_method"]
            paper_problems = [t for _, t, d in self.G.out_edges(pid, data=True)
                              if d.get("type") == "addresses_problem"]
            for m in paper_methods:
                for p in paper_problems:
                    method_problems[m].add(p)

        for m_node, p_set in method_problems.items():
            if len(p_set) == 1:
                m_name = self.G.nodes[m_node].get("name", m_node)
                gaps.append({
                    "type": "orphan_method",
                    "method": m_name,
                    "method_node": m_node,
                    "description": f"Method '{m_name}' applied to only 1 problem domain",
                })

        log.info(f"Graph-based gap detection: {len(gaps)} structural gaps found")
        return gaps

    def get_conflict_subgraph(self) -> list[dict]:
        """Extract all conflict edges and their context."""
        conflicts = []
        for u, v, data in self.G.edges(data=True):
            if data.get("type") == "conflicts_with":
                u_data = self.G.nodes.get(u, {})
                v_data = self.G.nodes.get(v, {})
                conflicts.append({
                    "paper_a": {"id": u, "title": u_data.get("title", "")},
                    "paper_b": {"id": v, "title": v_data.get("title", "")},
                    "conflict_id": data.get("conflict_id", ""),
                    "conflict_type": data.get("conflict_type", ""),
                    "severity": data.get("severity", ""),
                })
        return conflicts

    def get_paper_neighborhood(self, paper_id: str, depth: int = 1) -> dict:
        """Get the local neighborhood of a paper (entities it connects to)."""
        if not self.G.has_node(paper_id):
            return {"error": f"Paper {paper_id} not in graph"}

        neighbors = {"paper_id": paper_id}
        for _, target, data in self.G.out_edges(paper_id, data=True):
            edge_type = data.get("type", "unknown")
            target_data = self.G.nodes.get(target, {})
            if edge_type not in neighbors:
                neighbors[edge_type] = []
            neighbors[edge_type].append({
                "id": target,
                "name": target_data.get("name", target_data.get("title", target)),
                "type": target_data.get("type", "unknown"),
            })
        return neighbors

    # ── Analytics ───────────────────────────────────────────────────────────

    def get_stats(self) -> dict:
        """Graph statistics."""
        type_counts = defaultdict(int)
        for n in self.G.nodes:
            type_counts[self.G.nodes[n].get("type", "unknown")] += 1

        edge_type_counts = defaultdict(int)
        for _, _, d in self.G.edges(data=True):
            edge_type_counts[d.get("type", "unknown")] += 1

        return {
            "total_nodes": self.G.number_of_nodes(),
            "total_edges": self.G.number_of_edges(),
            "node_types": dict(type_counts),
            "edge_types": dict(edge_type_counts),
            "density": round(nx.density(self.G), 6),
            "connected_components": nx.number_weakly_connected_components(self.G),
        }

    def get_most_connected(self, node_type: str, top_k: int = 10) -> list[dict]:
        """Find the most connected nodes of a given type (by degree)."""
        nodes = [
            (n, self.G.degree(n))
            for n in self.G.nodes
            if self.G.nodes[n].get("type") == node_type
        ]
        nodes.sort(key=lambda x: x[1], reverse=True)
        return [
            {"id": n, "degree": d, **self.G.nodes[n]}
            for n, d in nodes[:top_k]
        ]

    # ── Export ──────────────────────────────────────────────────────────────

    def export_for_visualization(self) -> dict:
        """Export graph as nodes + edges for D3/vis.js visualization."""
        nodes = []
        for n in self.G.nodes:
            data = dict(self.G.nodes[n])
            data["id"] = n
            # Truncate long text fields
            for key in ["statement", "mechanism", "text"]:
                if key in data and len(str(data[key])) > 100:
                    data[key] = str(data[key])[:100] + "..."
            nodes.append(data)

        edges = []
        for u, v, data in self.G.edges(data=True):
            edge = {"source": u, "target": v}
            edge.update(data)
            edges.append(edge)

        return {"nodes": nodes, "edges": edges}

    def save(self, output_dir: str):
        """Save the graph to files."""
        # Save graph stats
        save_json(self.get_stats(), f"{output_dir}/graph_stats.json")

        # Save visualization export
        viz_data = self.export_for_visualization()
        save_json(viz_data, f"{output_dir}/graph_data.json")

        # Save structural gaps
        gaps = self.find_structural_gaps()
        save_json(gaps, f"{output_dir}/graph_gaps.json")

        # Save matrices
        mp_matrix = self.get_method_problem_matrix()
        save_json(list(mp_matrix.values()), f"{output_dir}/method_problem_matrix.json")

        md_matrix = self.get_method_dataset_matrix()
        save_json(list(md_matrix.values()), f"{output_dir}/method_dataset_matrix.json")

        log.info(f"Knowledge graph saved to {output_dir}/")
