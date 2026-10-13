#!/usr/bin/env python3
"""market.py - free market + DeFi data for the crypto-kg-vault (stdlib only, Python 3.8+).

Sources (no API key): CoinGecko public API (prices, mcap, FDV, volume, 7d/30d change, trending)
and DefiLlama (protocol TVL, chain TVL, fees). Bigdata.com stays the primary source for news and
sentiment; this script only fills the mechanical market fields so the weekly run does not guess them.

Commands (run from the vault root):
  python3 scripts/market.py update            refresh mkt fields + score_momentum + hints in every 30_Tokens note
  python3 scripts/market.py discover          scan ALL chains for tokens not yet in the vault; writes 90_Weekly/data/discover-DATE.json
  python3 scripts/market.py add SYM cg_id "Name" [--tier 3]   scaffold a new token note from _templates/token.md

Frontmatter keys read:   coingecko_id, defillama_parent (e.g. parent#aave), defillama_slug, defillama_chain
Frontmatter keys written: price_usd, price_date, mcap_usd_m, fdv_usd_m, mc_fdv, vol24h_usd_m, chg_7d, chg_30d,
  rs_btc_7d, rs_btc_30d, ath_drawdown_pct, tvl_usd_m, tvl_chg_7d, fees_30d_usd_m, fees_chg_30d,
  liquidity_ok, extended, score_momentum, hint_tokenomics, hint_adoption, mkt_date
"""
import os, re, sys, json, time, argparse, datetime, urllib.request, urllib.error

VAULT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TOK_DIR = os.path.join(VAULT, "30_Tokens")
DATA_DIR = os.path.join(VAULT, "90_Weekly", "data")
CG = "https://api.coingecko.com/api/v3"
LL = "https://api.llama.fi"
TODAY = datetime.date.today().isoformat()
STABLE_HINTS = ("usd", "eur", "gold", "wrapped", "staked", "bridged", "restaked", "liquid staking", "wbtc", "steth", "weth", "paxg", "xaut")

# ---------- helpers ----------
def get(url, retries=3):
    for i in range(retries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "crypto-kg-vault/1.0", "Accept": "application/json"})
            with urllib.request.urlopen(req, timeout=45) as r:
                return json.loads(r.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            if e.code == 429 and i < retries - 1:
                time.sleep(20 * (i + 1)); continue
            raise
        except Exception:
            if i < retries - 1:
                time.sleep(5); continue
            raise

FM_RE = re.compile(r"^---\n(.*?)\n---", re.S)

def read_fm(text):
    m = FM_RE.match(text)
    fm = {}
    if not m:
        return fm
    for line in m.group(1).splitlines():
        if re.match(r"^[A-Za-z_][\w]*:", line):
            k, _, v = line.partition(":")
            fm[k.strip()] = v.strip().strip('"')
    return fm

def set_fm(text, updates):
    """Replace or insert top-level scalar keys inside the frontmatter, leaving everything else untouched."""
    m = FM_RE.match(text)
    if not m:
        return text
    lines = m.group(1).splitlines()
    for k, v in updates.items():
        v = "" if v is None else str(v)
        pat = re.compile(r"^" + re.escape(k) + r":")
        for i, line in enumerate(lines):
            if pat.match(line):
                lines[i] = f"{k}: {v}".rstrip(); break
        else:
            # insert before `tags:` if present so lists stay at the end
            idx = next((i for i, l in enumerate(lines) if l.startswith("tags:")), len(lines))
            lines.insert(idx, f"{k}: {v}".rstrip())
    return "---\n" + "\n".join(lines) + "\n---" + text[m.end():]

def r1(x):
    return None if x is None else round(float(x), 1)

def token_notes():
    out = []
    for f in sorted(os.listdir(TOK_DIR)):
        if f.endswith(".md"):
            p = os.path.join(TOK_DIR, f)
            t = open(p, encoding="utf-8").read()
            out.append((p, t, read_fm(t)))
    return out

# ---------- mechanical scores ----------
def momentum_score(rs7, rs30, vol, mcap):
    """0-5 relative strength vs BTC plus turnover. Pure price data; judgement lives elsewhere."""
    if rs7 is None or rs30 is None:
        return None
    s = 0
    s += 1 if rs30 > 0 else 0
    s += 1 if rs30 > 20 else 0
    s += 1 if rs7 > 0 else 0
    s += 1 if rs7 > 8 else 0
    s += 1 if (mcap and vol and vol / mcap >= 0.05) else 0
    return s

def tokenomics_hint(mc_fdv):
    if mc_fdv is None:
        return None
    return 5 if mc_fdv >= 0.9 else 4 if mc_fdv >= 0.75 else 3 if mc_fdv >= 0.55 else 2 if mc_fdv >= 0.35 else 1

def adoption_hint(tvl_chg, fees_chg):
    vals = [v for v in (tvl_chg, fees_chg) if v is not None]
    if not vals:
        return None
    v = sum(vals) / len(vals)
    return 5 if v >= 25 else 4 if v >= 10 else 3 if v >= 0 else 2 if v >= -15 else 1

# ---------- data pulls ----------
def cg_markets(ids):
    rows = []
    ids = list(ids)
    for i in range(0, len(ids), 100):
        chunk = ",".join(ids[i:i + 100])
        rows += get(f"{CG}/coins/markets?vs_currency=usd&ids={chunk}&per_page=250&price_change_percentage=7d,30d")
        time.sleep(2)
    return {r["id"]: r for r in rows}

def llama_protocols():
    try:
        return get(f"{LL}/protocols")
    except Exception as e:
        print("defillama protocols failed:", e); return []

def llama_fees():
    try:
        return get(f"{LL}/overview/fees?excludeTotalDataChart=true&excludeTotalDataChartBreakdown=true").get("protocols", [])
    except Exception as e:
        print("defillama fees failed:", e); return []

def llama_chain_tvl(chain):
    try:
        hist = get(f"{LL}/v2/historicalChainTvl/{urllib.request.quote(chain)}")
        if len(hist) >= 31:
            now, ago7 = hist[-1]["tvl"], hist[-8]["tvl"]
            return now, (now / ago7 - 1) * 100 if ago7 else None
    except Exception as e:
        print(f"chain tvl {chain} failed:", e)
    return None, None

def agg_protocol(protos, fees, parent=None, slug=None):
    def match(x):
        return (parent and x.get("parentProtocol") == parent) or (slug and x.get("slug") == slug)
    tvl = tvl7 = 0.0
    for x in protos:
        if match(x) and x.get("tvl"):
            t = float(x["tvl"]); tvl += t
            if x.get("change_7d") is not None:
                tvl7 += t / (1 + x["change_7d"] / 100)
            else:
                tvl7 += t
    f30 = f60 = 0.0
    for x in fees:
        if match(x):
            f30 += float(x.get("total30d") or 0); f60 += float(x.get("total60dto30d") or 0)
    tvl_chg = (tvl / tvl7 - 1) * 100 if tvl and tvl7 else None
    fees_chg = (f30 / f60 - 1) * 100 if f60 else None
    return (tvl or None), tvl_chg, (f30 or None), fees_chg

# ---------- commands ----------
def cmd_update(a):
    notes = token_notes()
    ids = {fm.get("coingecko_id") for _, _, fm in notes if fm.get("coingecko_id")}
    mk = cg_markets(ids | {"bitcoin"})
    btc = mk.get("bitcoin", {})
    b7 = btc.get("price_change_percentage_7d_in_currency") or 0
    b30 = btc.get("price_change_percentage_30d_in_currency") or 0
    need_llama = any(fm.get("defillama_parent") or fm.get("defillama_slug") for _, _, fm in notes)
    protos = llama_protocols() if need_llama else []
    fees = llama_fees() if need_llama else []
    snap = {"date": TODAY, "btc": {"price": btc.get("current_price"), "chg_7d": r1(b7), "chg_30d": r1(b30)}, "tokens": {}}
    for path, text, fm in notes:
        cid = fm.get("coingecko_id")
        sym = fm.get("symbol") or os.path.basename(path)[:-3]
        if not cid or cid not in mk:
            print(f"skip {sym}: no coingecko_id or not returned"); continue
        r = mk[cid]
        mcap = r.get("market_cap") or 0; fdv = r.get("fully_diluted_valuation") or mcap
        vol = r.get("total_volume") or 0
        c7 = r.get("price_change_percentage_7d_in_currency"); c30 = r.get("price_change_percentage_30d_in_currency")
        rs7 = None if c7 is None else c7 - b7
        rs30 = None if c30 is None else c30 - b30
        mc_fdv = round(mcap / fdv, 2) if fdv else None
        tvl = tvl_chg = f30 = fees_chg = None
        if fm.get("defillama_parent") or fm.get("defillama_slug"):
            tvl, tvl_chg, f30, fees_chg = agg_protocol(protos, fees, fm.get("defillama_parent") or None, fm.get("defillama_slug") or None)
        elif fm.get("defillama_chain"):
            tvl, tvl_chg = llama_chain_tvl(fm["defillama_chain"])
        upd = {
            "price_usd": r.get("current_price"), "price_date": TODAY,
            "mcap_usd_m": round(mcap / 1e6) if mcap else "", "fdv_usd_m": round(fdv / 1e6) if fdv else "",
            "mc_fdv": mc_fdv, "vol24h_usd_m": round(vol / 1e6, 1),
            "chg_7d": r1(c7), "chg_30d": r1(c30), "rs_btc_7d": r1(rs7), "rs_btc_30d": r1(rs30),
            "ath_drawdown_pct": r1(r.get("ath_change_percentage")),
            "tvl_usd_m": round(tvl / 1e6) if tvl else "", "tvl_chg_7d": r1(tvl_chg),
            "fees_30d_usd_m": round(f30 / 1e6, 1) if f30 else "", "fees_chg_30d": r1(fees_chg),
            "liquidity_ok": "true" if vol >= 5e6 else "false",
            "extended": "true" if (c30 or 0) >= 100 else "false",
            "score_momentum": momentum_score(rs7, rs30, vol, mcap),
            "hint_tokenomics": tokenomics_hint(mc_fdv),
            "hint_adoption": adoption_hint(tvl_chg, fees_chg),
            "mkt_date": TODAY,
        }
        open(path, "w", encoding="utf-8").write(set_fm(text, upd))
        snap["tokens"][sym] = upd
        print(f"{sym:7} ${r.get('current_price')}  7d {r1(c7)}%  30d {r1(c30)}%  rs30 {r1(rs30)}  mom {upd['score_momentum']}  mc/fdv {mc_fdv}  tvl7d {r1(tvl_chg)}  fees30 {r1(fees_chg)}")
    os.makedirs(DATA_DIR, exist_ok=True)
    out = os.path.join(DATA_DIR, f"market-{TODAY}.json")
    json.dump(snap, open(out, "w", encoding="utf-8"), indent=1)
    print(f"BTC 7d {r1(b7)}%  30d {r1(b30)}%\nwrote {os.path.relpath(out, VAULT)}")

def looks_stable(r):
    n = (r.get("name", "") + " " + r.get("symbol", "")).lower()
    p = r.get("current_price") or 0
    return any(h in n for h in STABLE_HINTS) or 0.97 <= p <= 1.03

def cmd_discover(a):
    have = {fm.get("coingecko_id") for _, _, fm in token_notes()}
    rows = []
    for page in (1, 2):
        rows += get(f"{CG}/coins/markets?vs_currency=usd&order=market_cap_desc&per_page=250&page={page}&price_change_percentage=7d,30d")
        time.sleep(3)
    btc = next((r for r in rows if r["id"] == "bitcoin"), {})
    b7 = btc.get("price_change_percentage_7d_in_currency") or 0
    b30 = btc.get("price_change_percentage_30d_in_currency") or 0
    pool = []
    for r in rows:
        if r["id"] in have or looks_stable(r):
            continue
        mcap = r.get("market_cap") or 0; vol = r.get("total_volume") or 0
        if mcap < a.min_mcap * 1e6 or vol < a.min_vol * 1e6:
            continue
        c7 = r.get("price_change_percentage_7d_in_currency") or 0
        c30 = r.get("price_change_percentage_30d_in_currency") or 0
        pool.append(dict(id=r["id"], symbol=r["symbol"].upper(), name=r["name"], rank=r.get("market_cap_rank"),
                         mcap_usd_m=round(mcap / 1e6), vol24h_usd_m=round(vol / 1e6, 1), chg_7d=r1(c7), chg_30d=r1(c30),
                         rs_btc_7d=r1(c7 - b7), rs_btc_30d=r1(c30 - b30),
                         mc_fdv=round(mcap / r["fully_diluted_valuation"], 2) if r.get("fully_diluted_valuation") else None,
                         momentum=momentum_score(c7 - b7, c30 - b30, vol, mcap)))
    leaders = sorted(pool, key=lambda x: (x["momentum"], x["rs_btc_30d"]), reverse=True)[:a.top]
    try:
        trending = [c["item"] for c in get(f"{CG}/search/trending").get("coins", [])]
    except Exception as e:
        print("trending failed:", e); trending = []
    trend = [dict(id=t["id"], symbol=t["symbol"].upper(), name=t["name"], rank=t.get("market_cap_rank"))
             for t in trending if t["id"] not in have]
    # DefiLlama: protocols with real fee growth (fundamental discovery, long-term lens)
    fees = llama_fees()
    fee_up = []
    for x in fees:
        f30 = float(x.get("total30d") or 0); f60 = float(x.get("total60dto30d") or 0)
        if f30 >= a.min_fees * 1e6 and f60 >= 0.5e6:
            fee_up.append(dict(name=x.get("displayName") or x.get("name"), slug=x.get("slug"), category=x.get("category"),
                               chains=(x.get("chains") or [])[:4], fees_30d_usd_m=round(f30 / 1e6, 1),
                               fees_chg_30d=r1((f30 / f60 - 1) * 100)))
    fee_up = sorted(fee_up, key=lambda x: x["fees_chg_30d"], reverse=True)[:a.top]
    out = dict(date=TODAY, btc_chg_7d=r1(b7), btc_chg_30d=r1(b30), momentum_leaders=leaders, trending=trend, fee_growth=fee_up)
    os.makedirs(DATA_DIR, exist_ok=True)
    path = os.path.join(DATA_DIR, f"discover-{TODAY}.json")
    json.dump(out, open(path, "w", encoding="utf-8"), indent=1)
    print(f"## Discovery {TODAY} (not yet in vault; BTC 30d {r1(b30)}%)\n### Momentum leaders (top 500 by mcap, rs vs BTC)")
    for x in leaders:
        print(f"- {x['symbol']} ({x['id']}) #{x['rank']} mcap ${x['mcap_usd_m']} m  7d {x['chg_7d']}%  30d {x['chg_30d']}%  mom {x['momentum']}  mc/fdv {x['mc_fdv']}")
    print("### CoinGecko trending")
    for x in trend:
        print(f"- {x['symbol']} ({x['id']}) rank {x['rank']}")
    print("### Fee growth leaders (DefiLlama, 30d vs prior 30d)")
    for x in fee_up:
        print(f"- {x['name']} [{x['category']}] fees30 ${x['fees_30d_usd_m']} m  {x['fees_chg_30d']}%  chains {x['chains']}")
    print(f"wrote {os.path.relpath(path, VAULT)}")

def cmd_add(a):
    path = os.path.join(TOK_DIR, f"{a.symbol}.md")
    if os.path.exists(path):
        sys.exit(f"{a.symbol} already exists")
    t = open(os.path.join(VAULT, "_templates", "token.md"), encoding="utf-8").read()
    t = set_fm(t, {"symbol": a.symbol, "name": a.name, "coingecko_id": a.cg_id, "tier": a.tier,
                   "status": "discovery", "snapshot_date": TODAY, "added_date": TODAY})
    t = t.replace("# SYMBOL (Name)", f"# {a.symbol} ({a.name})")
    open(path, "w", encoding="utf-8").write(t)
    print(f"created 30_Tokens/{a.symbol}.md; run `market.py update` to fill market fields")

def main():
    p = argparse.ArgumentParser(); sp = p.add_subparsers(dest="cmd", required=True)
    sp.add_parser("update")
    x = sp.add_parser("discover")
    x.add_argument("--min-mcap", type=float, default=150, help="USD m"); x.add_argument("--min-vol", type=float, default=10, help="USD m")
    x.add_argument("--min-fees", type=float, default=1, help="USD m per 30d"); x.add_argument("--top", type=int, default=15)
    x = sp.add_parser("add"); x.add_argument("symbol"); x.add_argument("cg_id"); x.add_argument("name"); x.add_argument("--tier", default="3")
    a = p.parse_args()
    globals()["cmd_" + a.cmd](a)

if __name__ == "__main__":
    main()
