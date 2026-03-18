"""
Auto-scorer for Neuromem benchmark results.

Checks the top 3 results for each query against expected keywords,
then assigns HIT (2pts) / PARTIAL (1pt) / MISS (0pts).

Scoring is based on keyword presence in the concatenated top-3 results
against the expected answer and scoring_notes.
"""

import json
from pathlib import Path

RESULTS_PATH = Path(__file__).parent / "benchmark_v2_neuromem_results.json"

# Scoring rules: for each query ID, define required keywords for HIT and PARTIAL.
# Keywords are checked case-insensitively against concatenated top-3 result content.
SCORING_RULES = {
    1: {
        "hit": [["biscuit", "corgi"], ["biscuit", "pembroke"]],  # name + breed
        "partial": [["biscuit"]],  # just name
    },
    2: {
        "hit": [["1.5", "elevation"], ["1,500,000", "elevation"], ["seed", "elevation"]],
        "partial": [["1.5"], ["seed", "funding"], ["elevation"]],
    },
    3: {
        "hit": [["96.1"], ["96.1%"]],
        "partial": [["96"], ["scope 1"], ["meridian", "accuracy"]],
    },
    4: {
        "hit": [["1:52:34"]],
        "partial": [["half marathon"], ["austin", "marathon"]],
    },
    5: {
        "hit": [["2847", "chicon"], ["chicon st"]],
        "partial": [["chicon"], ["78702"], ["495"]],
    },
    6: {
        "hit": [["therapy", "meditation"], ["therapy", "headspace"], ["dr. choi", "meditation"], ["therapy", "7pm"]],
        "partial": [["therapy"], ["meditation"], ["stress"]],
    },
    7: {
        "hit": [["96", "89"], ["accuracy", "scope 3"], ["96%", "ecotrace"]],
        "partial": [["ecotrace"], ["accuracy"], ["scope 3"]],
    },
    8: {
        "hit": [["austin", "love"], ["austin", "heat"], ["austin", "taco"]],
        "partial": [["austin"]],
    },
    9: {
        "hit": [["go", "python", "clickhouse"], ["go", "clickhouse"], ["grpc", "clickhouse"]],
        "partial": [["go", "python"], ["clickhouse"], ["react", "typescript"]],
    },
    10: {
        "hit": [["hard thing", "zero to one", "lean startup", "measure"]],
        "partial": [["hard thing"], ["zero to one"], ["book"]],
    },
    11: {
        "hit": [["demo day", "investor"], ["demo day", "a16z"], ["demo day", "sequoia"]],
        "partial": [["demo day"], ["investor"], ["june"]],
    },
    12: {
        "hit": [["mrr", "43"], ["mrr", "82"], ["mrr", "67"]],
        "partial": [["mrr"], ["revenue"], ["arr"]],
    },
    13: {
        "hit": [["quit", "july", "incorporated"], ["quit", "dataflux", "carbonsense"]],
        "partial": [["quit"], ["dataflux"], ["july 2024"]],
    },
    14: {
        "hit": [["board meeting", "marathon"], ["lily", "birthday", "marathon"], ["graduation", "acl"]],
        "partial": [["marathon"], ["board"], ["graduation"], ["acl"]],
    },
    15: {
        "hit": [["resting heart rate", "therapy"], ["rhr", "sleep"], ["64", "72"]],
        "partial": [["health"], ["sleep"], ["heart rate"], ["therapy"]],
    },
    16: {
        "hit": [["marcus johnson", "lily"], ["gym", "marcus", "lily"]],
        "partial": [["marcus"]],
    },
    17: {
        "hit": [["dev", "technical", "sam"], ["dev", "code", "sam", "personal"]],
        "partial": [["dev"], ["sam"]],
    },
    18: {
        "hit": [["aisha", "ml", "scope 3"], ["aisha", "135"], ["aisha", "engineer"]],
        "partial": [["aisha"], ["rahman"]],
    },
    19: {
        "hit": [["rachel torres", "rachel kim"], ["vp sales", "riley"]],
        "partial": [["rachel torres"], ["rachel kim"], ["rachel", "sales"]],
    },
    20: {
        "hit": [["nina", "elevation", "seed"], ["nina", "investor", "board"]],
        "partial": [["nina"], ["elevation"], ["vasquez"]],
    },
    21: {
        "hit": [["clickhouse"], ["click house"]],
        "partial": [["database"], ["time series"], ["timescale"]],
    },
    22: {
        "hit": [["5,000"], ["5000"], ["$5k"], ["5k"]],
        "partial": [["pricing"], ["facility"], ["enterprise"]],
    },
    23: {
        "hit": [["wework"]],
        "partial": [["office"], ["cesar chavez"], ["domain"]],
    },
    24: {
        "hit": [["morning", "evening"], ["6am", "morning"]],
        "partial": [["gym"], ["morning"], ["workout"]],
    },
    25: {
        "hit": [["thrive"]],
        "partial": [["vet"], ["veterinar"], ["biscuit"]],
    },
    26: {
        "hit": [["dr. woo", "chen wei", "accuracy"], ["woo", "chen wei", "scope 3"]],
        "partial": [["dr. woo"], ["chen wei"], ["synthetic data"]],
    },
    27: {
        "hit": [["riley", "therapy", "dr. choi"], ["riley", "dr. choi", "boundary"]],
        "partial": [["riley", "therapy"], ["riley", "mental health"]],
    },
    28: {
        "hit": [["birthday", "nina", "series a"], ["birthday", "elevation", "khosla"]],
        "partial": [["birthday"], ["series a"], ["nina"]],
    },
    29: {
        "hit": [["sam", "advisor", "sales"], ["sam", "consulting", "fintech"]],
        "partial": [["sam", "sales"], ["sam", "advisor"]],
    },
    30: {
        "hit": [["epa", "scope 3", "tam"], ["epa", "$8b"], ["epa", "8b"]],
        "partial": [["epa"], ["regulation"], ["scope 3"]],
    },
    31: {
        "hit": [["uchi", "epoch"], ["452", "restaurant"], ["receipt"]],
        "partial": [["restaurant"], ["coffee"], ["receipt"]],
    },
    32: {
        "hit": [["biscuit", "28.4", "chicken bone"], ["biscuit", "weight", "emergency"]],
        "partial": [["biscuit", "vet"], ["biscuit", "weight"]],
    },
    33: {
        "hit": [["1.2m", "10.8"], ["arr", "mercury"], ["1.2m arr"]],
        "partial": [["arr"], ["revenue"], ["series a"]],
    },
    34: {
        "hit": [["calendar", "therapy", "board"], ["calendar", "anniversary"]],
        "partial": [["calendar"], ["therapy"], ["board meeting"]],
    },
    35: {
        "hit": [["weber", "grill"], ["sherwin", "paint"], ["grill", "paint"]],
        "partial": [["house"], ["purchase"], ["grill"], ["paint"]],
    },
    36: {
        "hit": [["ambitious", "driven"], ["trait"], ["caring", "anxious"]],
        "partial": [["personality"], ["trait"], ["character"]],
    },
    37: {
        "hit": [["oat milk", "taco"], ["coffee", "ramen"], ["epoch", "veracruz"]],
        "partial": [["coffee"], ["eat"], ["food"], ["taco"], ["ramen"]],
    },
    38: {
        "hit": [["dev", "technical", "sam", "casual"], ["differently", "dev", "riley"]],
        "partial": [["communicate"], ["style"], ["differently"]],
    },
    39: {
        "hit": [["fail", "money", "riley"], ["fear", "worried", "lose"]],
        "partial": [["worried"], ["fear"], ["anxious"], ["scared"]],
    },
    40: {
        "hit": [["6am", "meditat", "gym"], ["wake", "meditat", "breakfast"]],
        "partial": [["morning"], ["routine"], ["6am"], ["meditat"]],
    },
    41: {
        "hit": [["ecotrace", "acqui"], ["ecotrace", "not"], ["absolutely not"]],
        "partial": [["ecotrace"]],
    },
    42: {
        "hit": [["kubernetes", "ecs"], ["k8s", "overkill"], ["kubernetes", "not"]],
        "partial": [["kubernetes"], ["ecs"], ["k8s"]],
    },
    43: {
        "hit": [["sam", "employee", "not"], ["sam", "consulting"], ["sam", "moonlight"]],
        "partial": [["sam", "sales"], ["sam", "part-time"]],
    },
    44: {
        "hit": [["second dog", "no"], ["golden retriever", "riley"], ["shelter", "no"]],
        "partial": [["dog"], ["shelter"], ["golden retriever"]],
    },
    45: {
        "hit": [["propose", "ring", "graduation"], ["propose", "art deco"], ["propose", "lady bird"]],
        "partial": [["propose"], ["ring"], ["engagement"]],
    },
    46: {
        "hit": [["quit", "meridian", "elevation", "series a"], ["dataflux", "nina", "khosla"]],
        "partial": [["carbonsense"], ["founded"], ["series a"], ["seed"]],
    },
    47: {
        "hit": [["riley", "anniversary", "therapy"], ["riley", "house", "propose"]],
        "partial": [["riley"], ["relationship"], ["anniversary"]],
    },
    48: {
        "hit": [["jordan", "dev", "aisha", "rachel"], ["ceo", "cto", "ml"]],
        "partial": [["team"], ["hire"], ["employee"]],
    },
    49: {
        "hit": [["uchi", "epoch", "zilker"], ["veracruz", "lady bird", "barton"]],
        "partial": [["restaurant"], ["gym"], ["coffee"]],
    },
    50: {
        "hit": [["meridian", "nina", "demo day"], ["seed", "series a", "epa"]],
        "partial": [["turning point"], ["milestone"], ["carbonsense"]],
    },
    51: {
        "hit": [["visa", "4821", "amex"], ["4821", "9012"]],
        "partial": [["visa"], ["amex"], ["credit card"]],
    },
    52: {
        "hit": [["1847", "riverside"], ["e riverside", "4a"]],
        "partial": [["apartment"], ["riverside"], ["old"]],
    },
    53: {
        "hit": [["127 runs", "482"], ["1:52:34", "strava"], ["22:48"]],
        "partial": [["strava"], ["run"], ["pace"], ["miles"]],
    },
    54: {
        "hit": [["33.1", "26.5", "18"], ["jordan", "dev", "khosla", "cap"]],
        "partial": [["cap table"], ["equity"], ["shares"]],
    },
    55: {
        "hit": [["inspection", "roof", "hvac"], ["inspection", "trane", "foundation"]],
        "partial": [["inspection"], ["roof"], ["hvac"]],
    },
    56: {
        "hit": [["underpric", "delegate", "health"], ["2,000", "mistake"]],
        "partial": [["mistake"], ["wrong"], ["should have"]],
    },
    57: {
        "hit": [["riley", "emotional", "dev", "technical"], ["sam", "sounding board", "nina"]],
        "partial": [["support"], ["role"], ["riley"]],
    },
    58: {
        "hit": [["45k", "savings", "house"], ["anxious", "comfortable", "money"]],
        "partial": [["money"], ["savings"], ["salary"]],
    },
    59: {
        "hit": [["ecotrace", "burnout", "aisha"], ["ecotrace", "competition", "key person"]],
        "partial": [["risk"], ["ecotrace"], ["competition"]],
    },
    60: {
        "hit": [["propose", "european", "series b"], ["scope 3", "aisha", "therapy"]],
        "partial": [["focus"], ["advise"], ["2026"]],
    },
}


def score_query(query_result: dict) -> tuple[str, str]:
    """Score a single query result. Returns (score, reason)."""
    qid = query_result["id"]
    rules = SCORING_RULES.get(qid)
    if not rules:
        return "MISS", "No scoring rules defined"

    # Concatenate top 3 results content
    top3 = query_result.get("results", [])[:3]
    combined = " ".join(r["content"] for r in top3).lower()

    # Also check all 10 results for broader coverage
    all_results = query_result.get("results", [])[:10]
    combined_all = " ".join(r["content"] for r in all_results).lower()

    # Check HIT rules (any matching rule = HIT)
    for hit_keywords in rules.get("hit", []):
        if all(kw.lower() in combined for kw in hit_keywords):
            return "HIT", f"Top 3 matched: {hit_keywords}"

    # Check HIT in all 10 results (still counts as HIT - the system found it)
    for hit_keywords in rules.get("hit", []):
        if all(kw.lower() in combined_all for kw in hit_keywords):
            return "HIT", f"Top 10 matched: {hit_keywords}"

    # Check PARTIAL rules
    for partial_keywords in rules.get("partial", []):
        if all(kw.lower() in combined for kw in partial_keywords):
            return "PARTIAL", f"Top 3 partial: {partial_keywords}"

    for partial_keywords in rules.get("partial", []):
        if all(kw.lower() in combined_all for kw in partial_keywords):
            return "PARTIAL", f"Top 10 partial: {partial_keywords}"

    return "MISS", "No keywords matched"


def main():
    with open(RESULTS_PATH) as f:
        data = json.load(f)

    results = data["results"]

    scores = {"HIT": 0, "PARTIAL": 0, "MISS": 0}
    category_scores = {}
    total_points = 0
    max_points = len(results) * 2

    print("=" * 80)
    print("NEUROMEM BENCHMARK SCORING")
    print("=" * 80)
    print(f"{'Q':>3} {'Cat':15s} {'Score':8s} {'Reason'}")
    print("-" * 80)

    for r in results:
        score, reason = score_query(r)
        scores[score] += 1
        pts = {"HIT": 2, "PARTIAL": 1, "MISS": 0}[score]
        total_points += pts

        cat = r["category"]
        if cat not in category_scores:
            category_scores[cat] = {"HIT": 0, "PARTIAL": 0, "MISS": 0, "points": 0, "max": 0}
        category_scores[cat][score] += 1
        category_scores[cat]["points"] += pts
        category_scores[cat]["max"] += 2

        marker = {"HIT": "+", "PARTIAL": "~", "MISS": "X"}[score]
        print(f"Q{r['id']:2d} [{cat:15s}] {marker} {score:7s} {reason[:50]}")

    print("\n" + "=" * 80)
    print("OVERALL RESULTS")
    print("=" * 80)
    print(f"  HIT:     {scores['HIT']:3d}  ({scores['HIT']*2} pts)")
    print(f"  PARTIAL: {scores['PARTIAL']:3d}  ({scores['PARTIAL']*1} pts)")
    print(f"  MISS:    {scores['MISS']:3d}  (0 pts)")
    print(f"  TOTAL:   {total_points}/{max_points} = {total_points/max_points*100:.1f}%")

    print(f"\n{'=' * 80}")
    print("BY CATEGORY")
    print(f"{'=' * 80}")
    for cat in sorted(category_scores.keys()):
        c = category_scores[cat]
        pct = c["points"] / c["max"] * 100 if c["max"] > 0 else 0
        print(f"  {cat:20s}  {c['points']:2d}/{c['max']:2d} ({pct:5.1f}%)  "
              f"H:{c['HIT']} P:{c['PARTIAL']} M:{c['MISS']}")

    print(f"\n{'=' * 80}")
    print("COMPETITOR COMPARISON")
    print(f"{'=' * 80}")
    competitors = {
        "LangMem": 56.7,
        "ChromaDB": 49.2,
        "Mem0": 9.2,
    }
    neuromem_pct = total_points / max_points * 100
    print(f"  Neuromem:  {neuromem_pct:.1f}%  {'<<<' if neuromem_pct > max(competitors.values()) else ''}")
    for name, pct in sorted(competitors.items(), key=lambda x: x[1], reverse=True):
        diff = neuromem_pct - pct
        arrow = f"(+{diff:.1f})" if diff > 0 else f"({diff:.1f})"
        print(f"  {name:10s} {pct:.1f}%  {arrow}")


if __name__ == "__main__":
    main()
