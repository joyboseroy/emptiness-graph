# Emptiness Graph

**A typed philosophical knowledge graph of Buddhist emptiness teachings**  
spanning Theravada, Prajnaparamita, Madhyamaka, and Yogacara

`joyboseroy/emptiness-graph` · GitHub | HuggingFace Dataset

---

## What This Is

This is not a Buddhist chatbot dataset.

It is a **structured philosophical graph** encoding the conceptual architecture
of *sunyata* (emptiness) across the major Buddhist traditions — from the Pali
Canon's *anatta* through Nagarjuna's Madhyamaka, Shantideva's dialectics,
Yogacara's three-natures, and the Prajnaparamita sutras.

The core insight:

> Nagarjuna's arguments are essentially dependency analysis.  
> A thing exists because of other things.  
> Remove independent existence.  
> What remains is a network.

Emptiness (*sunyata*) is not a fact to be retrieved. It is a **relational
structure** to be traversed. This graph makes that structure explicit and
queryable.

---

## Is This Enough to Use?

**Yes, as a graph dataset.** The five files are self-contained. Load them with
Python (NetworkX, igraph, FalkorDB, Neo4j) and run traversal queries without
any other dependencies.

**Current status:**
- 10 of 16 planned texts are ingested as passages
- All 16 texts are represented in the philosophical graph via hand-authored
  concept and edge nodes
- 6 texts are in `corpus_manifest.jsonl` as planned but not yet ingested:
  Lotus Sutra Ch.2, Lankavatara Sutra, Vigrahavyavartani, Ratnavali,
  Ratnaguna-samcaya-gatha, Madhyamakavatara Ch.6

---

## Files

| File | Records | Description |
|------|---------|-------------|
| `corpus_manifest.jsonl` | 16 | All planned source texts with metadata, sources, and ingestion status |
| `concepts.jsonl` | 25 | Philosophical concept nodes with multilingual terms |
| `edges.jsonl` | 38 | Hand-authored typed philosophical relations |
| `passages.jsonl` | 1,126 | Text passages from 10 ingested sources |
| `passage_edges.jsonl` | 416 | Passage to concept mention links |

There are **two layers** to this graph, explained in detail below.

---

## How the Graph Was Built — Layer 1: The Philosophical Graph

**This layer is entirely hand-authored.** It was not produced by NLP,
entity extraction, or any automated process. Every concept node and every
edge was written individually with explicit philosophical reasoning.

### Step 1: Corpus selection

16 texts were selected based on direct philosophical relevance to emptiness
across four traditions. The criterion: does this text make a philosophically
distinct argument about sunyata, anatta, or dependent origination? Texts that
merely mention emptiness in passing were excluded.

### Step 2: Concept nodes (`concepts.jsonl`)

25 philosophical concepts were defined by hand. Each record contains:

- `id` — unique key used throughout as the graph node identifier
- `label`, `label_alt` — English names
- `sanskrit`, `pali`, `tibetan` — terms in original languages where applicable
- `tradition` — which Buddhist school(s) use this concept
- `definition` — philosophically precise description
- `category` — `ontological_concept` / `logical_method` / `soteriological_concept` / etc.
- `key_texts` — which corpus texts most directly instantiate this concept

Example:
```json
{
  "id": "pratityasamutpada",
  "label": "Pratityasamutpada",
  "sanskrit": "pratītyasamutpāda",
  "pali": "paticca-samuppāda",
  "tradition": ["theravada", "mahayana", "madhyamaka"],
  "definition": "All phenomena arise in dependence upon causes, conditions,
    and designations. For Nagarjuna, dependent origination IS emptiness —
    they are coextensive, not two different things.",
  "nagarjuna_claim": "identical_to_sunyata",
  "category": "ontological_concept"
}
```

### Step 3: Edge taxonomy

17 typed relation types were defined before any edges were written:

**Ontological:** `negates` · `presupposes` · `implies` · `is_identical_to` ·
`is_coextensive_with` · `depends_on` · `is_ground_of`

**Logical/Dialectical:** `refutes` · `extends` · `applies_method_of` ·
`deconstructs`

**Doctrinal:** `tensions_with` · `reframes_as` · `is_conventional_expression_of` ·
`is_ultimate_level_of` · `is_precursor_of`

**Practice:** `enables` · `is_obstacle_to` · `is_antidote_to`

The distinction between `negates` and `refutes` is deliberate: `negates` is
an ontological claim (sunyata negates svabhava as a mode of existence);
`refutes` is a dialectical move (Shantideva Ch.9 refutes the Abhidharma
position using the diamond-splinter argument).

### Step 4: Edges (`edges.jsonl`)

38 edges were written by hand, each containing:

- `source`, `target` — concept_id or text_id
- `relation` — one of the 17 typed relations above
- `tradition` — which tradition asserts this edge
- `weight` — 0.0–1.0, centrality to understanding emptiness
- `source_texts` — which corpus texts ground this claim
- `notes` — a paragraph of philosophical commentary explaining the edge

Example:
```json
{
  "id": "e001",
  "source": "pratityasamutpada",
  "target": "sunyata",
  "relation": "is_identical_to",
  "tradition": "madhyamaka",
  "weight": 1.0,
  "source_texts": ["mmk_nagarjuna", "sunyatasaptati_nagarjuna"],
  "notes": "Nagarjuna's master thesis, MMK Ch.24.18: whatever is dependently
    co-arisen is explained to be emptiness. Not two doctrines — one."
}
```

**Key design decisions:**

- Emptiness of emptiness is encoded as a self-loop: `sunyata --[negates]--> sunyata`.
  This prevents sunyata from becoming a new reified absolute — Nagarjuna's
  own move in the Vigrahavyavartani.
- `tensions_with` edges encode unresolved disputes rather than harmonising
  traditions. The tension between tathagatagarbha and sunyata is philosophically
  real and is kept as such.
- Text nodes (sutras, treatises) are first-class nodes in the graph alongside
  concept nodes, allowing edges like `heart_sutra --[refutes]--> abhidharma_realism`.

---

## How the Graph Was Built — Layer 2: The Passage Index

**This layer is automated.** The script `build_passage_index.py` processes
source text files and produces `passages.jsonl` and `passage_edges.jsonl`.

### Step 1: Text acquisition

All 10 ingested texts were sourced from openly available web versions of
these sutras and treatises — public domain translations and openly licensed
academic translations available online. See `corpus_manifest.jsonl` for the
exact URL and translator for each text.

Texts provided as PDFs were extracted using `pdftotext`. The Heart Sutra
file contained Tibetan script and Wylie transliteration interleaved with
English — these were filtered to English-only lines using Unicode range
detection (Tibetan script occupies U+0F00–U+0FFF).

### Step 2: Passage splitting

Two strategies depending on text structure:

- **Verse-aware splitting** for texts with numbered verse markers (`[1]`, `[2]`
  etc.) — each verse becomes one passage. Used for Diamond Sutra,
  Sunyatasaptati, and MMK.
- **Paragraph splitting** for prose texts, with a 60–1000 character window.
  Short paragraphs are merged with their successor; long ones are split at
  sentence boundaries.

### Step 3: Concept matching

Each passage is matched against a manually defined keyword list per concept.
For example, `svabhava` matches: `svabhava`, `inherent existence`, `intrinsic
existence`, `own-being`, `exist inherently`, `true existence`, etc.

This is intentionally precision-oriented — a keyword match means the passage
explicitly uses the concept's vocabulary, not just that the concept is
philosophically present.

### Step 4: Outputs

`passages.jsonl`:
```json
{
  "id": "mmk_nagarjuna_p0045",
  "text_id": "mmk_nagarjuna",
  "passage_index": 45,
  "text": "That which is dependently arisen is explained to be emptiness...",
  "char_count": 312,
  "concepts_mentioned": ["pratityasamutpada", "sunyata", "two_truths"]
}
```

`passage_edges.jsonl`:
```json
{
  "source": "mmk_nagarjuna_p0045",
  "target": "sunyata",
  "relation": "mentions",
  "text_id": "mmk_nagarjuna"
}
```

To reproduce from scratch:
```bash
# place source text files in texts/
python build_passage_index.py
# outputs data/passages.jsonl and data/passage_edges.jsonl
```

---

## The Corpus

### Ingested (10 texts, 1,126 passages)

| Text | Translator | Passages | Source |
|------|-----------|---------|--------|
| Anattalakkhana Sutta (SN 22.59) | Bhikkhu Sujato | 20 | accesstoinsight.org |
| Milindapanha — Chariot Argument | T.W. Rhys Davids | 23 | accesstoinsight.org |
| Heart Sutra | Nyingma Monlam / multiple | 90 | lotsawahouse.org |
| Diamond Sutra | Public domain | 30 | accesstoinsight.org |
| Ashtasahasrika Prajnaparamita | 84000 Translation Project | 119 | 84000.co |
| Vimalakirti Sutra Ch.9 | Robert Thurman | 41 | openly available web text |
| Samdhinirmocana Sutra | 84000 Translation Project | 570 | 84000.co |
| Mulamadhyamakakarika (Ch.1,18,22,23,24,26) | Geshe Kelsang Wangmo | 120 | openly available PDF |
| Sunyatasaptati | Christian Lindtner | 73 | landofenlightenedwisdom.org |
| Bodhicharyavatara Ch.9 | Padmakara Translation Group | 40 | openly available PDF |

### Planned but not yet ingested (6 texts)

These texts are represented in the philosophical graph (concepts.jsonl,
edges.jsonl) via hand-authored nodes, but their passages have not yet been
extracted:

- Ratnaguna-samcaya-gatha (Conze tr.)
- Vigrahavyavartani — Nagarjuna
- Ratnavali — Nagarjuna
- Lankavatara Sutra
- Lotus Sutra Ch.2
- Madhyamakavatara Ch.6 — Chandrakirti

---

## Concept Nodes (25)

`svabhava` · `sunyata` · `anatta` · `anatta_of_persons` · `anatta_of_dharmas`
`pratityasamutpada` · `two_truths` · `two_truths_theravada` · `prasanga`
`dependent_designation` · `emptiness_of_emptiness` · `alayavijnana`
`three_natures` · `tathagatagarbha` · `five_aggregates` · `twelve_nidanas`
`dharmadhatu` · `nonduality` · `skillful_means` · `nihilism_extreme`
`eternalism_extreme` · `abhidharma_realism` · `cittamatra` · `bodhichitta`
`three_kayas`

**Not included:** Rigpa, kadag, lhundrub, rangtong/shentong. These are
Dzogchen-specific concepts that require Longchenpa texts to be properly
grounded. Reserved for a future Dzogchen extension.

---

## How to Use It

### Load the philosophical graph

```python
import json, networkx as nx

def load_jsonl(path):
    return [json.loads(l) for l in open(path)
            if l.strip() and not l.startswith('#')]

G = nx.MultiDiGraph()
for c in load_jsonl("concepts.jsonl"):
    G.add_node(c["id"], kind="concept", **c)
for t in load_jsonl("corpus_manifest.jsonl"):
    G.add_node(t["id"], kind="text", **t)
for e in load_jsonl("edges.jsonl"):
    G.add_edge(e["source"], e["target"], **e)
```

### Query: what does a text negate or refute?

```python
for u, v, data in G.edges(data=True):
    if u == "heart_sutra" and data["relation"] in ("refutes", "deconstructs"):
        print(f"  {G.nodes[v]['label']} [{data['relation']}]")
# Five Aggregates   [deconstructs]
# Abhidharma Realism [refutes]
```

### Query: what implies sunyata, and from which tradition?

```python
for u, v, data in G.edges(data=True):
    if v == "sunyata" and data["relation"] in (
            "is_identical_to", "is_precursor_of", "is_coextensive_with"):
        print(f"  {G.nodes[u]['label']} --[{data['relation']}] ({data['tradition']})")
# Pratityasamutpada --[is_identical_to] (madhyamaka)
# Anatta            --[is_precursor_of] (mahayana)
```

### Query: all doctrinal tensions

```python
for u, v, data in G.edges(data=True):
    if data["relation"] == "tensions_with":
        print(f"  {G.nodes[u]['label']} <--> {G.nodes[v]['label']}")
# Tathagatagarbha <--> Sunyata
# Cittamatra      <--> Sunyata
```

### Query: how do traditions differ on one concept?

```python
for u, v, data in G.edges(data=True):
    if v == "sunyata" or u == "sunyata":
        other = v if u == "sunyata" else u
        direction = "->" if u == "sunyata" else "<-"
        print(f"  [{data['tradition']:<20}] sunyata {direction} "
              f"{other} [{data['relation']}]")
```

### Query: find passages for a concept

```python
passages = load_jsonl("passages.jsonl")
pedges   = load_jsonl("passage_edges.jsonl")

def passages_for_concept(concept_id):
    pids = {e["source"] for e in pedges if e["target"] == concept_id}
    return [p for p in passages if p["id"] in pids]

for p in passages_for_concept("emptiness_of_emptiness"):
    print(f"[{p['text_id']}]\n{p['text'][:200]}\n")
```

### Shortest path between concepts

```python
simple = nx.DiGraph()
for u, v, data in G.edges(data=True):
    simple.add_edge(u, v, relation=data["relation"])

path = nx.shortest_path(simple, "anatta", "sunyata")
for i, node in enumerate(path):
    if i < len(path) - 1:
        rel = simple[node][path[i+1]]["relation"]
        print(f"  {G.nodes[node]['label']} --[{rel}]-->")
    else:
        print(f"  {G.nodes[node]['label']}")
# Anatta --[is_precursor_of]--> Sunyata
```

### Visualise (requires pyvis)

```bash
pip install networkx pyvis
python emptiness_graph.py --viz
# saves emptiness_graph.html
```

### Load from HuggingFace

```python
from datasets import load_dataset
ds = load_dataset("joyboseroy/emptiness-graph")
```

---

## Sample Query Results

**What does the Heart Sutra deconstruct/refute?**
```
Five Aggregates      [deconstructs]
Abhidharma Realism   [refutes]
```

**What implies Sunyata?**
```
Pratityasamutpada  --[is_identical_to]  (madhyamaka)
Anatta             --[is_precursor_of]  (mahayana)
```

**Doctrinal tensions:**
```
Tathagatagarbha  <--> Sunyata
Cittamatra       <--> Sunyata
```

**Tradition comparison on Sunyata:**
```
Theravada   : Anatta            [is_precursor_of]
Madhyamaka  : Pratityasamutpada [is_identical_to]
Yogacara    : Three Natures     [reframes_as]
Mahayana    : Bodhichitta       [enables]
```

---

## What Is Not Included

**Longchenpa / Dzogchen** — The Choying Dzod and Trilogy of Rest require
Dzogchen-specific concepts (rigpa, kadag, lhundrub) that sit in a different
ontological register. They are reserved for a future `dzogchen-extension`.

**Tibetan commentarial literature** — Tsongkhapa, Mipham, Patrul Rinpoche
etc. are deliberately excluded. This dataset focuses on Indian root texts
and their direct translations.

**6 planned texts not yet ingested** — see corpus table above.

**Embeddings, audio, images** — text and graph structure only.

---

## Citation

```bibtex
@dataset{bose2026emptiness,
  title   = {Emptiness Graph: A Typed Philosophical Knowledge Graph
             of Buddhist Sunyata},
  author  = {Bose, Joy},
  year    = {2026},
  url     = {https://huggingface.co/datasets/joyboseroy/emptiness-graph},
  note    = {Hand-authored concept graph and automated passage index
             spanning Theravada, Prajnaparamita, Madhyamaka, and Yogacara.
             All source texts sourced from openly available web translations.}
}
```

---

## License

`concepts.jsonl`, `edges.jsonl`, `corpus_manifest.jsonl`: **CC BY 4.0**

`passages.jsonl`, `passage_edges.jsonl`: passages from public domain
translations are CC BY 4.0. The 84000 translations (Ashtasahasrika,
Samdhinirmocana) are CC BY-NC-ND 4.0 — non-commercial research use only.
See the `license` field in `corpus_manifest.jsonl` for per-text details.

---

## Contributing

The highest-value contributions are additional edges in `edges.jsonl` with
proper `notes` commentary. Keyword lists in `build_passage_index.py` can
also be extended per concept. Please do not add edges without the `notes`
field — that field is what distinguishes this from automated triple extraction
and is the primary scholarly contribution of the dataset.
