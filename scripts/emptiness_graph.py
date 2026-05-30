"""
emptiness_graph.py

Load, validate, and query the emptiness knowledge graph.
Requires: pip install networkx pyvis pandas

Usage:
    python emptiness_graph.py              # load + print stats
    python emptiness_graph.py --query      # run example philosophical queries
    python emptiness_graph.py --viz        # generate HTML visualisation
"""

import json
import argparse
from pathlib import Path
import networkx as nx

DATA_DIR = Path(__file__).parent.parent / "data"

# ── loaders ────────────────────────────────────────────────────────────────

def load_jsonl(path):
    records = []
    with open(path) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#"):
                records.append(json.loads(line))
    return records

def build_graph():
    concepts = load_jsonl(DATA_DIR / "concepts.jsonl")
    texts    = load_jsonl(DATA_DIR / "corpus_manifest.jsonl")
    edges    = load_jsonl(DATA_DIR / "edges.jsonl")

    G = nx.MultiDiGraph()

    # concept nodes
    for c in concepts:
        G.add_node(c["id"],
                   kind="concept",
                   label=c["label"],
                   tradition=c.get("tradition", []),
                   category=c.get("category", ""),
                   definition=c.get("definition", ""),
                   sanskrit=c.get("sanskrit", ""),
                   tibetan=c.get("tibetan", ""))

    # text nodes
    for t in texts:
        G.add_node(t["id"],
                   kind="text",
                   label=t["title"],
                   tradition=t["tradition"],
                   vehicle=t.get("vehicle", ""),
                   author=t.get("author", ""),
                   century=t.get("century", ""),
                   emptiness_type=t.get("emptiness_type", ""),
                   emptiness_moves=t.get("emptiness_moves", []))

    # edges
    for e in edges:
        G.add_edge(e["source"], e["target"],
                   key=e["id"],
                   relation=e["relation"],
                   tradition=e.get("tradition", ""),
                   weight=e.get("weight", 0.5),
                   notes=e.get("notes", ""))

    return G, concepts, texts, edges

# ── stats ───────────────────────────────────────────────────────────────────

def print_stats(G):
    concept_nodes = [n for n, d in G.nodes(data=True) if d.get("kind") == "concept"]
    text_nodes    = [n for n, d in G.nodes(data=True) if d.get("kind") == "text"]

    print(f"\n{'='*60}")
    print(f"  EMPTINESS KNOWLEDGE GRAPH — STATISTICS")
    print(f"{'='*60}")
    print(f"  Total nodes  : {G.number_of_nodes()}")
    print(f"    Concepts   : {len(concept_nodes)}")
    print(f"    Texts      : {len(text_nodes)}")
    print(f"  Total edges  : {G.number_of_edges()}")

    relation_types = {}
    for u, v, data in G.edges(data=True):
        r = data["relation"]
        relation_types[r] = relation_types.get(r, 0) + 1
    print(f"\n  Relation types ({len(relation_types)}):")
    for r, count in sorted(relation_types.items(), key=lambda x: -x[1]):
        print(f"    {r:<40} {count}")

    print(f"\n  Most connected concept nodes:")
    degrees = {n: G.degree(n) for n in concept_nodes}
    for n, d in sorted(degrees.items(), key=lambda x: -x[1])[:8]:
        label = G.nodes[n]["label"]
        print(f"    {label:<35} degree={d}")

# ── philosophical queries ────────────────────────────────────────────────────

def query_what_does_text_negate(G, text_id):
    """Which concepts does a given text negate or deconstruct?"""
    label = G.nodes[text_id]["label"]
    print(f"\n  [{label}] negates / deconstructs:")
    for u, v, data in G.edges(data=True):
        if u == text_id and data["relation"] in ("negates", "deconstructs", "refutes"):
            target_label = G.nodes[v]["label"]
            print(f"    -> {target_label}  [{data['relation']}]")
            print(f"       {data['notes'][:100]}...")

def query_what_implies_sunyata(G):
    """What concepts and texts directly imply or are identical to sunyata?"""
    print(f"\n  What implies / is_identical_to / is_precursor_of SUNYATA:")
    for u, v, data in G.edges(data=True):
        if v == "sunyata" and data["relation"] in (
            "implies", "is_identical_to", "is_precursor_of", "is_coextensive_with"
        ):
            source_label = G.nodes[u]["label"]
            print(f"    {source_label:<35} --[{data['relation']}]--> Sunyata")
            print(f"    tradition: {data['tradition']}")

def query_tensions(G):
    """Show all doctrinal tensions in the graph."""
    print(f"\n  DOCTRINAL TENSIONS:")
    for u, v, data in G.edges(data=True):
        if data["relation"] == "tensions_with":
            ul = G.nodes[u]["label"]
            vl = G.nodes[v]["label"]
            print(f"    {ul} <--[tension]--> {vl}")
            print(f"    {data['notes'][:120]}...")

def query_path_to_sunyata(G, start_id):
    """Find shortest path from a concept to sunyata."""
    try:
        # Use simple graph for path finding
        simple = nx.DiGraph()
        for u, v, data in G.edges(data=True):
            if not simple.has_edge(u, v):
                simple.add_edge(u, v, relation=data["relation"])
        path = nx.shortest_path(simple, start_id, "sunyata")
        print(f"\n  Shortest path from '{start_id}' to Sunyata:")
        for i, node in enumerate(path):
            label = G.nodes[node]["label"]
            if i < len(path) - 1:
                next_node = path[i + 1]
                edge_data = simple[node][next_node]
                print(f"    {label}  --[{edge_data['relation']}]-->")
            else:
                print(f"    {label}")
    except nx.NetworkXNoPath:
        print(f"  No path found from {start_id} to sunyata")
    except nx.NodeNotFound as e:
        print(f"  Node not found: {e}")

def query_tradition_subgraph(G, tradition):
    """Extract edges belonging to a specific tradition."""
    print(f"\n  TRADITION: {tradition.upper()}")
    found = []
    for u, v, data in G.edges(data=True):
        if tradition in data.get("tradition", ""):
            ul = G.nodes[u]["label"]
            vl = G.nodes[v]["label"]
            found.append((ul, data["relation"], vl, data["weight"]))
    found.sort(key=lambda x: -x[3])
    for ul, rel, vl, w in found:
        print(f"    {ul:<30} --[{rel}]--> {vl}  (w={w})")

def query_comparative_emptiness(G):
    """
    The document's key idea: show how each tradition handles 
    the same concepts differently.
    """
    print(f"\n  COMPARATIVE EMPTINESS — how traditions differ:")
    traditions = ["theravada", "madhyamaka", "yogacara", "dzogchen", "prasangika"]
    target_concepts = ["sunyata", "anatta", "svabhava", "nonduality"]
    
    for concept in target_concepts:
        if concept not in G.nodes:
            continue
        label = G.nodes[concept]["label"]
        print(f"\n  [{label}]:")
        for u, v, data in G.edges(data=True):
            if v == concept or u == concept:
                trad = data.get("tradition", "")
                rel = data["relation"]
                other = v if u == concept else u
                other_label = G.nodes[other]["label"]
                direction = "->" if u == concept else "<-"
                print(f"    [{trad:<20}] {label} {direction} {other_label} [{rel}]")

# ── visualisation ─────────────────────────────────────────────────────────

def visualise(G):
    try:
        from pyvis.network import Network
    except ImportError:
        print("  Install pyvis: pip install pyvis")
        return

    TRADITION_COLORS = {
        "theravada":   "#4CAF50",
        "madhyamaka":  "#2196F3",
        "yogacara":    "#FF9800",
        "dzogchen":    "#9C27B0",
        "prasangika":  "#00BCD4",
        "mahayana":    "#607D8B",
        "mixed":       "#795548",
    }

    RELATION_COLORS = {
        "negates":      "#F44336",
        "refutes":      "#E91E63",
        "deconstructs": "#FF5722",
        "tensions_with":"#FF9800",
        "is_identical_to": "#4CAF50",
        "is_precursor_of": "#8BC34A",
        "implies":      "#2196F3",
        "enables":      "#00BCD4",
        "presupposes":  "#9E9E9E",
    }

    net = Network(height="900px", width="100%",
                  directed=True, notebook=False,
                  heading="Emptiness Knowledge Graph")
    net.toggle_physics(True)
    net.set_options("""
    {
      "physics": {
        "forceAtlas2Based": {
          "gravitationalConstant": -50,
          "springLength": 200
        },
        "solver": "forceAtlas2Based"
      }
    }
    """)

    for node, data in G.nodes(data=True):
        tradition = data.get("tradition", "")
        if isinstance(tradition, list):
            tradition = tradition[0] if tradition else "mixed"
        color = TRADITION_COLORS.get(tradition, "#9E9E9E")
        size = 25 if data["kind"] == "concept" else 15
        shape = "ellipse" if data["kind"] == "concept" else "box"
        title = data.get("definition", data.get("notes", ""))[:200]
        net.add_node(node,
                     label=data["label"],
                     color=color,
                     size=size,
                     shape=shape,
                     title=title)

    for u, v, data in G.edges(data=True):
        rel = data["relation"]
        color = RELATION_COLORS.get(rel, "#AAAAAA")
        net.add_edge(u, v,
                     label=rel,
                     color=color,
                     title=data.get("notes", "")[:200],
                     width=max(1, data.get("weight", 0.5) * 4))

    out = Path("emptiness_graph.html")
    net.save_graph(str(out))
    print(f"\n  Visualisation saved to: {out.resolve()}")

# ── main ─────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--query", action="store_true")
    parser.add_argument("--viz",   action="store_true")
    args = parser.parse_args()

    G, concepts, texts, edges = build_graph()
    print_stats(G)

    if args.query or True:  # always run queries for now
        print(f"\n{'='*60}")
        print(f"  PHILOSOPHICAL QUERIES")
        print(f"{'='*60}")

        query_what_does_text_negate(G, "heart_sutra")
        query_what_does_text_negate(G, "bodhicharyavatara_ch9")
        query_what_implies_sunyata(G)
        query_tensions(G)
        query_path_to_sunyata(G, "anatta")
        query_path_to_sunyata(G, "abhidharma_realism")
        query_tradition_subgraph(G, "dzogchen")
        query_comparative_emptiness(G)

    if args.viz:
        visualise(G)

if __name__ == "__main__":
    main()
