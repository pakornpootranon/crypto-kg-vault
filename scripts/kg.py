#!/usr/bin/env python3
"""kg.py - tiny graph loader for the crypto-kg-vault (stdlib only).

Nodes  = markdown notes (file stem is the node id; frontmatter `type` is the label)
Edges  = lines of the form `- relation:: [[Target]]` anywhere in a note
Usage  = python scripts/kg.py <command> [args]   (run from the vault root)
"""
import os, re, sys, json, argparse
from collections import defaultdict, deque

VAULT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SKIP_DIRS = {"_templates", ".obsidian", "scripts"}
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
    x = sp.add_parser("export"); x.add_argument("out", nargs="?", default="graph.json")
    a = p.parse_args()
    nodes, edges = load()
    globals()["cmd_" + a.cmd](nodes, edges, a)

if __name__ == "__main__":
    main()
