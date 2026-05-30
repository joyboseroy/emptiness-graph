"""
build_passage_index.py  v2
Improved passage splitting: verse-aware for Diamond Sutra, Sunyatasaptati, MMK
"""

import json
import re
from pathlib import Path

DATA_DIR  = Path(__file__).parent.parent / "data"
TEXTS_DIR = Path(__file__).parent.parent / "texts"

CONCEPT_KEYWORDS = {
    "svabhava": ["svabhava","inherent existence","intrinsic existence","own-being","own being","self-nature","inherently exist","exist inherently","exists inherently","true existence","truly exist","truly exists","independent existence","exist from its own side"],
    "sunyata": ["emptiness","empty","voidness","void","sunyata","shunyata","śūnyatā","devoid of inherent","empty of inherent","lack of inherent","stong pa","openness"],
    "anatta": ["not-self","no-self","non-self","anatta","anatman","no self","selflessness","without self","absence of self","no permanent individuality"],
    "anatta_of_persons": ["no permanent individuality","no soul","personal selflessness","pudgala","nairatmya","no nagasena","chariot","designation in common use","there is no nagasena"],
    "anatta_of_dharmas": ["dharma-nairatmya","no-self of phenomena","selflessness of phenomena","all dharmas are empty","dharmas lack","no eye no ear","no form no sound","aggregates are empty","phenomena are not self"],
    "pratityasamutpada": ["dependent origination","dependent arising","dependent co-arising","pratityasamutpada","interdependence","in dependence on","arises in dependence","conditioned by","twelve links","twelve nidanas","conditionally arisen","dependently arisen","dependently imputed"],
    "two_truths": ["two truths","conventional truth","ultimate truth","relative truth","worldly convention","ultimate reality","conventional reality","sammuti","paramattha","samvrti","paramartha"],
    "prasanga": ["prasanga","consequence","reductio","it follows that","would follow","contradiction","untenable","not tenable","cannot be tenable","would not be possible"],
    "dependent_designation": ["mere designation","mere imputation","merely designated","conventional designation","prajnapti","imputed by","name only","designation in common use","dependent designation"],
    "emptiness_of_emptiness": ["emptiness of emptiness","empty of emptiness","emptiness itself is empty","voidness is void","not to be apprehended","not apprehend emptiness","emptiness is not a thing"],
    "alayavijnana": ["alaya","storehouse consciousness","all-ground consciousness","base consciousness","alayavijnana","store consciousness"],
    "three_natures": ["three natures","trisvabhava","parikalpita","paratantra","parinishpanna","imagined nature","dependent nature","perfected nature","three own-natures","three characteristics"],
    "tathagatagarbha": ["tathagatagarbha","buddha-nature","buddha nature","buddha-embryo","buddha essence","sugatagarbha"],
    "five_aggregates": ["five aggregates","five skandhas","skandhas","rupa vedana","form is empty","aggregates are empty","form emptiness","feeling emptiness","consciousness emptiness","five heaps","pancaskandha","form feeling perception"],
    "twelve_nidanas": ["twelve links","twelve nidanas","ignorance formations consciousness","name and form","six sense","contact feeling craving","craving clinging becoming","birth old age death","ignorance ceases","compositional action"],
    "rigpa": ["rigpa","intrinsic awareness","pure awareness","naked awareness","self-knowing awareness","awareness itself","vidya","vidyā","knowing quality","cognizant emptiness"],
    "dharmadhatu": ["dharmadhatu","dharmadhātu","realm of phenomena","expanse of reality","dharmata","dharmatā","nature of phenomena","sphere of dharmas"],
    "nonduality": ["non-duality","nonduality","non-dual","nondual","advaya","not two","beyond duality","entrance into non-duality","neither nor","transcends duality"],
    "skillful_means": ["skillful means","upaya","upāya","expedient means","adapted teaching","one vehicle","ekayana","three vehicles","for the sake of beings"],
    "nihilism_extreme": ["nihilism","annihilationism","nothing exists","completely nonexistent","emptiness means nothing","uccheda","not nothing","denial of existence"],
    "eternalism_extreme": ["eternalism","permanent existence","sassata","permanent self","inherently permanent","unchanging existence"],
    "bodhichitta": ["bodhichitta","bodhicitta","awakening mind","mind of enlightenment","aspiration for enlightenment","for the sake of all beings","benefit all sentient beings"],
    "cittamatra": ["mind-only","mind only","cittamatra","yogacara","vijnanavada","only mind","consciousness only","no external objects","projection of mind"],
    "rangtong_shentong": ["rangtong","shentong","self-empty","other-empty","empty of its own nature","empty of other","buddha qualities"],
}

TEXT_ID_MAP = {
    "anattalakkhana.txt":         "anattalakkhana_sutta",
    "milinda_chariot.txt":        "milindapanha_chariot",
    "heart_sutra_english.txt":    "heart_sutra",
    "diamond_sutra.txt":          "diamond_sutra",
    "sunyatasaptati.txt":         "sunyatasaptati_nagarjuna",
    "mmk.txt":                    "mmk_nagarjuna",
    "bodhicharya_ch9.txt":        "bodhicharyavatara_ch9",
    "vimalakirti_ch9.txt":        "vimalakirti_sutra",
    "samdhinirmocana.txt":        "samdhinirmocana_sutra",
    "prajnaparamita_longer.txt":  "ashtasahasrika_prajnaparamita",
}

def clean_text(text):
    text = re.sub(r'\r\n', '\n', text)
    text = re.sub(r'\r', '\n', text)
    text = re.sub(r'\f', '\n', text)
    text = re.sub(r'\n{3,}', '\n\n', text)
    return text.strip()

def split_into_passages(text, text_id, min_chars=60, max_chars=1000):
    """Verse-aware splitting for texts with [N] markers; paragraph split for others."""
    text = clean_text(text)

    # Verse/stanza aware texts
    if re.search(r'\[\d+\]', text):
        # Split at verse markers like [1], [2] ...
        raw = re.split(r'\n(?=\[\d+\])', text)
        passages = []
        for chunk in raw:
            chunk = chunk.strip()
            if len(chunk) >= min_chars:
                passages.append(chunk)
        return passages

    # MMK-style: numbered chapters and verses like "1. (26)"
    if re.search(r'^\d+\. \(\d+\)', text, re.MULTILINE):
        raw = re.split(r'\n(?=\d+\. \(\d+\))', text)
        passages = []
        for chunk in raw:
            chunk = chunk.strip()
            if len(chunk) >= min_chars:
                passages.append(chunk)
        return passages

    # Standard paragraph splitting
    paragraphs = re.split(r'\n\n+', text)
    passages = []
    buffer = ""
    for para in paragraphs:
        para = para.strip()
        if not para or len(para) < 15:
            continue
        if re.match(r'^(Next|Previous|<|http|--|==|\[index\])', para):
            continue
        buffer = (buffer + " " + para).strip() if buffer else para
        if len(buffer) >= min_chars:
            if len(buffer) > max_chars:
                sentences = re.split(r'(?<=[.!?])\s+', buffer)
                chunk = ""
                for sent in sentences:
                    if len(chunk) + len(sent) > max_chars and chunk:
                        passages.append(chunk.strip())
                        chunk = sent
                    else:
                        chunk = (chunk + " " + sent).strip()
                if chunk:
                    passages.append(chunk.strip())
            else:
                passages.append(buffer)
            buffer = ""
    if buffer and len(buffer) >= min_chars:
        passages.append(buffer)
    return passages

def find_concepts(passage_lower):
    found = []
    for concept_id, keywords in CONCEPT_KEYWORDS.items():
        for kw in keywords:
            if kw in passage_lower:
                found.append(concept_id)
                break
    return found

def main():
    passages_out      = []
    passage_edges_out = []

    for fname, text_id in TEXT_ID_MAP.items():
        fpath = TEXTS_DIR / fname
        if not fpath.exists():
            print(f"  MISSING: {fname}")
            continue
        raw = fpath.read_text(encoding="utf-8", errors="replace")
        passages = split_into_passages(raw, text_id)
        print(f"  {fname:<40} {len(passages):>4} passages")

        for i, passage_text in enumerate(passages):
            passage_id = f"{text_id}_p{i:04d}"
            concepts = find_concepts(passage_text.lower())
            passages_out.append({
                "id": passage_id, "text_id": text_id,
                "passage_index": i, "text": passage_text,
                "char_count": len(passage_text),
                "concepts_mentioned": concepts,
            })
            for concept_id in concepts:
                passage_edges_out.append({
                    "source": passage_id, "target": concept_id,
                    "relation": "mentions", "text_id": text_id,
                })

    with open(DATA_DIR / "passages.jsonl", "w") as f:
        for r in passages_out:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    with open(DATA_DIR / "passage_edges.jsonl", "w") as f:
        for r in passage_edges_out:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")

    total = len(passages_out)
    total_m = len(passage_edges_out)
    concept_counts = {}
    for e in passage_edges_out:
        c = e["target"]
        concept_counts[c] = concept_counts.get(c, 0) + 1

    print(f"\n  Total passages : {total}")
    print(f"  Total mentions : {total_m}")
    print(f"\n  Concept frequency:")
    for c, n in sorted(concept_counts.items(), key=lambda x: -x[1]):
        print(f"    {c:<35} {n:>4}")

if __name__ == "__main__":
    main()
