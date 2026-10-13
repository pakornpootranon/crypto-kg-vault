#!/usr/bin/env python3
"""kg.py - tiny graph loader for the crypto-kg-vault (stdlib only).

Nodes  = markdown notes (file stem is the node id; frontmatter `type` is the label)
Edges  = lines of the form `- relation:: [[Target]]` anywhere in a note
Usage  = python scripts/kg.py <command> [args]   (run from the vault root)
"""
import os, re, sys, json, argparse
from collections import defaultdict, deque

VAULT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SKIP_DIRS = {"_templates", ".obsidian", "scripts", "data", ".git"}
FM_RE = re.compile(r"^---\n(.*?)\n---", re.S)
EDGE_RE = re.compile(r"^\s*-\s*([a-z_]+)::\s*\[\[([^\]|#]+)(?:[|#][^\]]*)?\]\]", re.M)
LINK_RE = re.compile(r"\[\[([^\]|#]+)(?:[|#][^\]]*)?\]\]")
CODE_RE = re.compile(r"```.*?```|`[^`\n]*`", re.S)

def parse_frontmatter(text):
    m = FM_RE.match(text)
    if not m:
        return {}
    fm = {}
    key = None
    for line in m.group(1).splitlines():
        if re.match(r"^\s+-\s", line) and key:
            fm.setdefault(key, [])
            if not isinstance(fm[key], list):
                fm[key] = []
            fm[key].append(line.split("-", 1)[1].strip().strip('"'))
        elif ":" in line:
            key, _, val = line.partition(":")
            key = key.strip(); val = val.strip().strip('"')
            fm[key] = val
    return fm

def load():
    nodes, edges = {}, []
    for root, dirs, files in os.walk(VAULT):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
        for f in files:
            if not f.endswith(".md"):
                continue
            path = os.path.join(root, f)
            name = f[:-3]
            text = open(path, encoding="utf-8").read()
            fm = parse_frontmatter(text)
            nodes[name] = dict(id=name, type=fm.get("type", "note"), path=os.path.relpath(path, VAULT), fm=fm,
                               links=sorted(set(LINK_RE.findall(CODE_RE.sub("", text)))))
            for rel, tgt in EDGE_RE.findall(text):
                edges.append((name, rel, tgt.strip()))
    return nodes, edges

def adjacency(edges):
    out, inn = defaultdict(list), defaultdict(list)
    for s, r, t in edges:
        out[s].append((r, t)); inn[t].append((r, s))
    return out, inn

def cmd_stats(nodes, edges, a):
    by_type = defaultdict(int)
    for n in nodes.values():
        by_type[n["type"]] += 1
    rels = defaultdict(int)
    for _, r, _ in edges:
        rels[r] += 1
    print(f"nodes: {len(nodes)}  edges: {len(edges)}")
    print("by type:", dict(sorted(by_type.items())))
    print("relations:", dict(sorted(rels.items(), key=lambda x: -x[1])))

def cmd_node(nodes, edges, a):
    n = nodes.get(a.name)
    if not n:
        sys.exit(f"no node {a.name!r}")
    out, inn = adjacency(edges)
    print(f"{n['id']}  [{n['type']}]  {n['path']}")
    for k, v in n["fm"].items():
        if k not in ("type", "tags") and v not in ("", []):
            print(f"  {k}: {v}")
    print("out:")
    for r, t in out[n["id"]]:
        print(f"  -{r}-> {t}")
    print("in:")
    for r, s in inn[n["id"]]:
        print(f"  {s} -{r}->")

def cmd_neighbors(nodes, edges, a):
    out, inn = adjacency(edges)
    seen = {a.name: 0}; q = deque([a.name])
    while q:
        cur = q.popleft()
        if seen[cur] >= a.depth:
            continue
        nbrs = [(r, t) for r, t in out[cur]] + [(r, s) for r, s in inn[cur]]
        for r, t in nbrs:
            if a.rel and r != a.rel:
                continue
            if t not in seen:
                seen[t] = seen[cur] + 1; q.append(t)
    for n, d in sorted(seen.items(), key=lambda x: (x[1], x[0])):
        if d:
            print(f"{d}  {n}  [{nodes.get(n, {}).get('type', '?')}]")

def cmd_path(nodes, edges, a):
    out, inn = adjacency(edges)
    prev = {a.src: None}; q = deque([a.src])
    while q and a.dst not in prev:
        cur = q.popleft()
        for r, t in out[cur] + [(r, s) for r, s in inn[cur]]:
            if t not in prev:
                prev[t] = (cur, r); q.append(t)
    if a.dst not in prev:
        sys.exit("no path")
    path = []; cur = a.dst
    while prev[cur]:
        p, r = prev[cur]; path.append(f"{p} -{r}- {cur}"); cur = p
    print("\n".join(reversed(path)))

def cmd_find(nodes, edges, a):
    conds = dict(w.split("=", 1) for w in a.where)
    for n in sorted(nodes.values(), key=lambda x: x["id"]):
        if a.type and n["type"] != a.type:
            continue
        if all(str(n["fm"].get(k, "")) == v for k, v in conds.items()):
            print(n["id"])

def cmd_narrative(nodes, edges, a):
    out, inn = adjacency(edges)
    print(f"{a.name}")
    for r, t in out[a.name]:
        if r in ("beneficiary", "laggard", "threatens", "tailwind_for", "headwind_for"):
            print(f"  {r}: {t}")
    print("  rides it:")
    for r, s in inn[a.name]:
        if r == "rides_narrative":
            print(f"    {s} [{nodes.get(s,{}).get('type','?')}]")

def cmd_events(nodes, edges, a):
    rows = [n for n in nodes.values() if n["type"] == "event"]
    if a.upcoming:
        rows = [n for n in rows if n["fm"].get("status") == "upcoming"]
    for n in sorted(rows, key=lambda x: x["fm"].get("date", "")):
        print(f"{n['fm'].get('date','?')}  {n['id']}  impact={n['fm'].get('impact','')}  {n['fm'].get('direction','')}")

def cmd_check(nodes, edges, a):
    bad = 0
    for s, r, t in edges:
        if t not in nodes and not t.startswith("VERIFY"):
            print(f"dangling edge: {s} -{r}-> {t}"); bad += 1
    for n in nodes.values():
        for l in n["links"]:
            if l not in nodes and not l.startswith("VERIFY"):
                print(f"dangling link: {n['id']} -> {l}"); bad += 1
    print("ok" if not bad else f"{bad} problems")

def cmd_verify(nodes, edges, a):
    for n in sorted(nodes.values(), key=lambda x: x["id"]):
        for l in n["links"]:
            if l.startswith("VERIFY"):
                print(f"{n['id']}: {l}")

def cmd_export(nodes, edges, a):
    data = dict(nodes=[dict(id=n["id"], type=n["type"], **{k: v for k, v in n["fm"].items() if k != "type"}) for n in nodes.values()],
                edges=[dict(source=s, relation=r, target=t) for s, r, t in edges])
    json.dump(data, open(a.out, "w", encoding="utf-8"), indent=1, ensure_ascii=False)
    print(f"wrote {a.out}: {len(data['nodes'])} nodes, {len(data['edges'])} edges")


# ---------- horizon ranking (see 00_Schema/Schema - Horizon Scoring.md) ----------
def _num(v):
    try:
        return float(v)
    except (TypeError, ValueError):
        return None

def horizon_scores(fm, today):
    import datetime as _dt
    notes = []
    def pick(key, hint=None):
        v = _num(fm.get(key))
        if v is None and hint:
            h = _num(fm.get(hint))
            if h is not None:
                notes.append(f"{key.replace('score_','')}~hint")
                return h
        if v is None:
            notes.append(f"{key.replace('score_','')}?")
            return 0.0
        return v
    st_parts = [pick("score_momentum"), pick("score_flows"), pick("score_sentiment"), pick("score_catalysts")]
    lt_parts = [pick("score_fundamentals"), pick("score_adoption", "hint_adoption"),
                pick("score_tokenomics", "hint_tokenomics"), pick("score_narrative")]
    st, lt = sum(st_parts), sum(lt_parts)
    flags = []
    ud, up = fm.get("unlock_next_date", ""), _num(fm.get("unlock_pct_supply"))
    if ud:
        try:
            days = (_dt.date.fromisoformat(ud[:10]) - today).days
            if 0 <= days <= 14 and up is not None:
                pen = 3 if up >= 1 else 2 if up >= 0.3 else 0
                if pen:
                    st -= pen; flags.append(f"unlock {ud[:10]} {up}% (-{pen})")
        except ValueError:
            pass
    if fm.get("extended") == "true":
        st -= 1; flags.append("extended 30d>100% (-1)")
    if fm.get("risk_flag"):
        st -= 2; lt -= 2; flags.append(f"risk: {fm['risk_flag']} (-2)")
    illiquid = fm.get("liquidity_ok") == "false"
    if illiquid:
        flags.append("illiquid: no ST")
    sent, fund = _num(fm.get("score_sentiment")), _num(fm.get("score_fundamentals"))
    if not illiquid and st >= 13 and lt >= 13:
        bucket = "core (both horizons)"
    elif not illiquid and st >= 13:
        bucket = "short-term setup"
    elif lt >= 13:
        bucket = "long-term accumulate"
    elif sent is not None and fund is not None and sent >= 5 and fund <= 2:
        bucket = "narrative blow-off"
    elif sent is not None and fund is not None and fund >= 4 and sent <= 2:
        bucket = "quiet accumulation"
    elif st < 8 and lt < 8:
        bucket = "fade"
    else:
        bucket = "watch"
    return round(st, 1), round(lt, 1), bucket, flags, notes

def _prev_scores(today):
    d = os.path.join(VAULT, "90_Weekly", "data")
    if not os.path.isdir(d):
        return {}
    files = sorted(f for f in os.listdir(d) if f.startswith("scores-") and f < f"scores-{today}")
    return json.load(open(os.path.join(d, files[-1]), encoding="utf-8"))["tokens"] if files else {}

ST_KEYS = {'momentum', 'flows', 'sentiment', 'catalysts'}

def cmd_rank(nodes, edges, a):
    import datetime as _dt
    today = _dt.date.fromisoformat(a.date) if a.date else _dt.date.today()
    prev = _prev_scores(today.isoformat())
    rows = []
    for n in nodes.values():
        if n["type"] != "token" or n["fm"].get("status") == "dormant":
            continue
        st, lt, bucket, flags, notes = horizon_scores(n["fm"], today)
        p = prev.get(n["id"], {})
        rows.append(dict(id=n["id"], st=st, lt=lt, bucket=bucket, flags=flags, notes=notes, status=n["fm"].get("status", ""),
                         dst=None if "st" not in p else round(st - p["st"], 1), dlt=None if "lt" not in p else round(lt - p["lt"], 1),
                         new=n["id"] not in prev and bool(prev)))
    def fmt_d(x):
        return ("new" if prev else "-") if x is None else (f"+{x:g}" if x > 0 else f"{x:g}")
    print("### Short-term (1 to 4 weeks)")
    print("| # | Token | ST | dWk | Bucket | Flags | Gaps |\n|---|---|---|---|---|---|---|")
    for i, r in enumerate(sorted(rows, key=lambda r: -r["st"]), 1):
        print(f"| {i} | [[{r['id']}]] | {r['st']:g} | {fmt_d(r['dst'])} | {r['bucket']} | {'; '.join(r['flags'])} | {', '.join(n for n in r['notes'] if n.split('?')[0].split('~')[0] in ST_KEYS)} |")
    print("\n### Long-term (6 to 24 months)")
    print("| # | Token | LT | dWk | Bucket | Flags | Gaps |\n|---|---|---|---|---|---|---|")
    for i, r in enumerate(sorted(rows, key=lambda r: -r["lt"]), 1):
        print(f"| {i} | [[{r['id']}]] | {r['lt']:g} | {fmt_d(r['dlt'])} | {r['bucket']} | {'; '.join(r['flags'])} | {', '.join(n for n in r['notes'] if n.split('?')[0].split('~')[0] not in ST_KEYS)} |")
    if a.write:
        d = os.path.join(VAULT, "90_Weekly", "data"); os.makedirs(d, exist_ok=True)
        out = os.path.join(d, f"scores-{today.isoformat()}.json")
        json.dump(dict(date=today.isoformat(), tokens={r["id"]: dict(st=r["st"], lt=r["lt"], bucket=r["bucket"], flags=r["flags"]) for r in rows}),
                  open(out, "w", encoding="utf-8"), indent=1)
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        from market import set_fm
        for r in rows:
            path = os.path.join(VAULT, nodes[r["id"]]["path"])
            t = open(path, encoding="utf-8").read()
            open(path, "w", encoding="utf-8").write(set_fm(t, dict(st_score=r["st"], lt_score=r["lt"], bucket=r["bucket"])))
        print(f"\nwrote {os.path.relpath(out, VAULT)} and st_score/lt_score/bucket into {len(rows)} token notes")

def main():
    p = argparse.ArgumentParser(); sp = p.add_subparsers(dest="cmd", required=True)
    sp.add_parser("stats")
    x = sp.add_parser("node"); x.add_argument("name")
    x = sp.add_parser("neighbors"); x.add_argument("name"); x.add_argument("--depth", type=int, default=1); x.add_argument("--rel")
    x = sp.add_parser("path"); x.add_argument("src"); x.add_argument("dst")
    x = sp.add_parser("find"); x.add_argument("--type"); x.add_argument("--where", nargs="*", default=[])
    x = sp.add_parser("narrative"); x.add_argument("name")
    x = sp.add_parser("events"); x.add_argument("--upcoming", action="store_true")
    sp.add_parser("check"); sp.add_parser("verify")
    x = sp.add_parser("rank"); x.add_argument("--write", action="store_true"); x.add_argument("--date")
    x = sp.add_parser("export"); x.add_argument("out", nargs="?", default="graph.json")
    a = p.parse_args()
    nodes, edges = load()
    globals()["cmd_" + a.cmd](nodes, edges, a)

if __name__ == "__main__":
    main()
