"""
embedding_engine.py — Real vector embeddings for papers
Uses sentence-transformers (SPECTER2 or all-MiniLM) for paper embeddings,
HDBSCAN for clustering, UMAP for 2D projection.
"""

import json
import numpy as np
from pathlib import Path
from typing import Optional

import sys
sys.path.insert(0, str(Path(__file__).parent))
from utils import log, save_json

# ── Embedding ────────────────────────────────────────────────────────────────

class PaperEmbedder:
    """Embed papers using sentence-transformers."""

    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        """
        Models ranked by quality for academic papers:
          1. 'allenai/specter2'       — best for papers (trained on citations)
          2. 'all-mpnet-base-v2'      — strong general-purpose
          3. 'all-MiniLM-L6-v2'      — fast, good enough for clustering
        Falls back gracefully if preferred model unavailable.
        """
        try:
            from sentence_transformers import SentenceTransformer
            # Try SPECTER2 first (best for academic papers)
            try:
                self.model = SentenceTransformer("allenai/specter2")
                self.model_name = "allenai/specter2"
                log.info(f"Loaded embedding model: allenai/specter2")
            except Exception:
                self.model = SentenceTransformer(model_name)
                self.model_name = model_name
                log.info(f"Loaded embedding model: {model_name}")
        except ImportError:
            raise ImportError(
                "sentence-transformers required. Run: pip install sentence-transformers"
            )

    def _paper_to_text(self, paper: dict) -> str:
        """Convert a paper record to a text string for embedding."""
        parts = []
        # Title (most important)
        title = paper.get("title", "")
        if title:
            parts.append(title)

        # Problem statement
        problem = paper.get("problem", {})
        if isinstance(problem, dict):
            stmt = problem.get("statement", "")
            if stmt:
                parts.append(stmt)
        elif isinstance(problem, str) and problem:
            parts.append(problem)

        # Method
        method = paper.get("method", {})
        if isinstance(method, dict):
            name = method.get("name", "")
            mechanism = method.get("mechanism", "")
            novelty = method.get("novelty_claim", "")
            for m in [name, mechanism, novelty]:
                if m:
                    parts.append(m)

        # Claims
        for claim in paper.get("claims", [])[:3]:
            if isinstance(claim, dict):
                c = claim.get("claim", "")
                if c:
                    parts.append(c)

        return " ".join(parts)

    def embed_papers(self, papers: list[dict]) -> np.ndarray:
        """Embed a list of paper records. Returns (N, dim) array."""
        texts = [self._paper_to_text(p) for p in papers]
        log.info(f"Embedding {len(texts)} papers with {self.model_name}...")
        embeddings = self.model.encode(
            texts,
            show_progress_bar=True,
            batch_size=32,
            normalize_embeddings=True,
        )
        log.info(f"Embeddings shape: {embeddings.shape}")
        return embeddings

    def compute_similarity_matrix(self, embeddings: np.ndarray) -> np.ndarray:
        """Compute cosine similarity matrix (embeddings should be normalized)."""
        return embeddings @ embeddings.T


# ── Clustering ───────────────────────────────────────────────────────────────

def cluster_embeddings(
    embeddings: np.ndarray,
    min_cluster_size: int = 3,
    min_samples: int = 2,
) -> dict:
    """
    Cluster embeddings using HDBSCAN.
    Returns dict with labels, probabilities, and cluster info.
    """
    try:
        import hdbscan
        clusterer = hdbscan.HDBSCAN(
            min_cluster_size=min_cluster_size,
            min_samples=min_samples,
            metric="euclidean",
            cluster_selection_method="eom",
        )
    except ImportError:
        # Fallback to sklearn KMeans
        log.warning("hdbscan not available, falling back to KMeans")
        from sklearn.cluster import KMeans
        n_clusters = max(3, len(embeddings) // 8)
        n_clusters = min(n_clusters, 15)
        clusterer = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)

    labels = clusterer.fit_predict(embeddings)
    n_clusters = len(set(labels)) - (1 if -1 in labels else 0)
    n_noise = list(labels).count(-1)

    log.info(f"Clustering: {n_clusters} clusters found, {n_noise} noise points")

    # Get probabilities if available (HDBSCAN)
    probs = getattr(clusterer, "probabilities_", np.ones(len(labels)))

    return {
        "labels": labels.tolist(),
        "probabilities": probs.tolist(),
        "n_clusters": n_clusters,
        "n_noise": n_noise,
    }


# ── Dimensionality Reduction ─────────────────────────────────────────────────

def reduce_to_2d(embeddings: np.ndarray, method: str = "umap") -> np.ndarray:
    """Reduce embeddings to 2D for visualization."""
    if method == "umap":
        try:
            import umap
            reducer = umap.UMAP(
                n_components=2,
                n_neighbors=min(15, len(embeddings) - 1),
                min_dist=0.1,
                metric="cosine",
                random_state=42,
            )
            coords = reducer.fit_transform(embeddings)
            log.info("2D reduction: UMAP")
            return coords
        except ImportError:
            log.warning("umap-learn not available, falling back to t-SNE")

    # Fallback: t-SNE
    from sklearn.manifold import TSNE
    perplexity = min(30, max(5, len(embeddings) // 4))
    reducer = TSNE(
        n_components=2,
        perplexity=perplexity,
        random_state=42,
        init="pca",
    )
    coords = reducer.fit_transform(embeddings)
    log.info("2D reduction: t-SNE")
    return coords


# ── Paper Similarity ─────────────────────────────────────────────────────────

def find_nearest_neighbors(
    embeddings: np.ndarray,
    paper_ids: list[str],
    k: int = 5,
) -> dict:
    """Find k nearest neighbors for each paper."""
    sim_matrix = embeddings @ embeddings.T
    neighbors = {}
    for i, pid in enumerate(paper_ids):
        sims = sim_matrix[i]
        # Exclude self
        sims[i] = -1
        top_k_idx = np.argsort(sims)[-k:][::-1]
        neighbors[pid] = [
            {"paper_id": paper_ids[j], "similarity": float(sims[j])}
            for j in top_k_idx
        ]
    return neighbors


# ── Full Embedding Pipeline ──────────────────────────────────────────────────

def run_embedding_pipeline(papers: list[dict], output_dir: str) -> dict:
    """
    Full embedding pipeline:
    1. Embed papers
    2. Cluster with HDBSCAN
    3. Reduce to 2D
    4. Find nearest neighbors
    5. Save everything
    """
    # Filter valid papers
    valid = [p for p in papers if "_error" not in p and p.get("title")]
    paper_ids = [p.get("paper_id", f"paper-{i}") for i, p in enumerate(valid)]

    if len(valid) < 3:
        log.warning("Too few papers for embedding pipeline (need >= 3)")
        return {"status": "skipped", "reason": "too_few_papers"}

    # 1. Embed
    embedder = PaperEmbedder()
    embeddings = embedder.embed_papers(valid)

    # 2. Cluster
    min_size = max(2, len(valid) // 10)
    cluster_result = cluster_embeddings(embeddings, min_cluster_size=min_size)

    # 3. 2D projection
    coords_2d = reduce_to_2d(embeddings)

    # 4. Nearest neighbors
    neighbors = find_nearest_neighbors(embeddings, paper_ids, k=5)

    # 5. Build output
    paper_embeddings_data = []
    for i, paper in enumerate(valid):
        paper_embeddings_data.append({
            "paper_id": paper_ids[i],
            "title": paper.get("title", ""),
            "cluster_label": cluster_result["labels"][i],
            "cluster_probability": round(cluster_result["probabilities"][i], 3),
            "x_2d": round(float(coords_2d[i][0]), 4),
            "y_2d": round(float(coords_2d[i][1]), 4),
            "nearest_neighbors": neighbors[paper_ids[i]][:3],
        })

    # Cluster summaries
    cluster_summaries = {}
    for i, label in enumerate(cluster_result["labels"]):
        if label == -1:
            continue
        key = f"cluster_{label}"
        if key not in cluster_summaries:
            cluster_summaries[key] = {
                "cluster_id": label,
                "papers": [],
                "centroid_x": 0,
                "centroid_y": 0,
            }
        cluster_summaries[key]["papers"].append({
            "paper_id": paper_ids[i],
            "title": valid[i].get("title", ""),
        })
        cluster_summaries[key]["centroid_x"] += coords_2d[i][0]
        cluster_summaries[key]["centroid_y"] += coords_2d[i][1]

    for cs in cluster_summaries.values():
        n = len(cs["papers"])
        cs["centroid_x"] = round(cs["centroid_x"] / n, 4)
        cs["centroid_y"] = round(cs["centroid_y"] / n, 4)
        cs["paper_count"] = n

    result = {
        "model": embedder.model_name,
        "n_papers": len(valid),
        "n_clusters": cluster_result["n_clusters"],
        "n_noise": cluster_result["n_noise"],
        "papers": paper_embeddings_data,
        "cluster_summaries": list(cluster_summaries.values()),
        "embedding_dim": int(embeddings.shape[1]),
    }

    # Save
    save_json(result, f"{output_dir}/embeddings.json")

    # Save raw embeddings as numpy (for downstream use)
    np.save(f"{output_dir}/embeddings.npy", embeddings)
    log.info(f"Saved raw embeddings: {output_dir}/embeddings.npy")

    return result
