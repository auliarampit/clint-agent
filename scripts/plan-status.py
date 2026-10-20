#!/usr/bin/env python3
"""Status setiap PR di file rencana dan langkah berikutnya (paralel/urutan). Tanpa token.

  plan-status.py [PLAN ...] [--repo DIR] [--session SID] [--set PR-n=STATE[:catatan]] [--write] [--json]

Tanpa PLAN: semua rencana di `docs.plans` yang punya tabel *Urutan pekerjaan*.
Fakta: MR (glab/gh per branch), trailer `Plan: <rencana> PR-n` di base, branch lokal/remote, klaim sesi lain
(~/Library/Logs/clint/kerja/*.json), dan bagian `## Status PR` di file rencana.
STATE untuk --set: done, review, draft, held, blocked, todo. Status "unknown" (push-base tanpa bukti) tidak ditulis.
"""
import argparse, glob, json, os, re, subprocess, sys, time
from concurrent.futures import ThreadPoolExecutor

HOME = os.path.expanduser("~")
KERJA = os.path.join(HOME, "Library/Logs/clint/kerja")
SESI = os.path.join(HOME, ".config/clint/sesi")
LABEL = {"done": "✅ selesai", "review": "🔍 menunggu review", "draft": "🧪 Draft, E2E tertunda",
         "held": "⏸️ tertahan", "blocked": "🚫 terblokir", "todo": "⬜ belum mulai", "unknown": "❔ belum tercatat"}
EMOJI = {"✅": "done", "🔍": "review", "🧪": "draft", "⏸": "held", "🚫": "blocked", "⬜": "todo"}
HEAD_STATUS = "## Status PR"


def run(args, cwd, timeout=20):
    try:
        r = subprocess.run(args, cwd=cwd, capture_output=True, text=True, timeout=timeout)
        return r.stdout if r.returncode == 0 else None
    except (OSError, subprocess.TimeoutExpired):
        return None


def main_repo(path):
    common = run(["git", "rev-parse", "--path-format=absolute", "--git-common-dir"], path)
    if not common:
        sys.exit(f"{path} bukan repo git")
    common = common.strip()
    return os.path.dirname(common) if os.path.basename(common) == ".git" else common


def parse_table(lines):
    start = next((i for i, l in enumerate(lines) if re.match(r"#+ .*Urutan pekerjaan", l)), None)
    if start is None:
        return []
    rows = [l for l in lines[start + 1:start + 80] if l.startswith("|")]
    if len(rows) < 2:
        return []
    head = [c.strip().lower() for c in rows[0].strip("|").split("|")]
    col = lambda name: next((i for i, h in enumerate(head) if h.startswith(name)), None)
    i_pr, i_br, i_dep = col("pr"), col("branch"), col("bergantung")
    prs = []
    for r in rows[2:]:
        cells = [c.strip() for c in r.strip().strip("|").split("|")]
        m = re.search(r"PR-\d+", cells[i_pr] if i_pr is not None and i_pr < len(cells) else "")
        if not m:
            continue
        dep = cells[i_dep] if i_dep is not None and i_dep < len(cells) else ""
        local = dep.split(";")[0]
        deps = [p for mod, p in re.findall(r"(?:([A-Z][A-Z0-9]*(?:-[A-Z0-9]+)*-\d+)\s+)?(PR-\d+)", local) if not mod]
        prs.append({"id": m.group(0),
                    "branch": (cells[i_br].strip("` ") if i_br is not None and i_br < len(cells) else "") or None,
                    "deps": list(dict.fromkeys(deps)),
                    "lintas": re.sub(r"\*+|\blintas:\s*", "", ";".join(dep.split(";")[1:])).strip(" ;") or None})
    return prs


def parse_status(lines):
    out, inside = {}, False
    for l in lines:
        if l.startswith("## "):
            inside = l.strip() == HEAD_STATUS
            continue
        m = inside and re.match(r"- \[[ xX]\] (PR-\d+) · (\S+)[^·]*(?:· (.*))?$", l.strip())
        if m:
            st = next((v for k, v in EMOJI.items() if m.group(2).startswith(k)), "todo")
            note = (m.group(3) or "").strip()
            if st in ("held", "blocked") and ":" in l.split("·")[1]:
                note = l.split("·")[1].split(":", 1)[1].strip() + (f" · {note}" if note else "")
            out[m.group(1)] = (st, note)
    return out


def mr_of(branch, cli, cwd):
    if not branch or cli not in ("glab", "gh"):
        return None
    if cli == "gh":
        o = run(["gh", "pr", "list", "--head", branch, "--state", "all", "--json", "number,state,isDraft,url"], cwd)
        xs = json.loads(o) if o else []
        return xs and {"n": xs[0]["number"], "state": xs[0]["state"].lower().replace("open", "opened"),
                       "draft": xs[0]["isDraft"], "url": xs[0]["url"]}
    o = run(["glab", "mr", "list", "--all", "--source-branch", branch, "-F", "json"], cwd)
    xs = json.loads(o) if o else []
    return xs and {"n": xs[0]["iid"], "state": xs[0]["state"], "draft": xs[0].get("draft"), "url": xs[0]["web_url"]}


def claims(repo, slug, own):
    out = {}
    for f in glob.glob(os.path.join(KERJA, "*.json")):
        sid = os.path.basename(f)[:-5]
        try:
            k = json.load(open(f, encoding="utf-8"))
        except (OSError, ValueError):
            continue
        alive = time.time() - os.path.getmtime(f) < 3 * 3600 and os.path.exists(os.path.join(SESI, f"{sid}.json"))
        if not alive or os.path.realpath(k.get("dir") or "") != os.path.realpath(repo):
            continue
        if os.path.splitext(os.path.basename(k.get("rencana") or ""))[0] != slug:
            continue
        for p in k.get("prs") or []:
            out[p] = {"self": sid == own, "tahap": k.get("tahap") or "", "path": k.get("path") or ""}
    return out


def evaluate(plan, repo, cfg, own, overrides):
    lines = open(plan, encoding="utf-8").read().splitlines()
    prs = parse_table(lines)
    if not prs:
        return None
    slug = os.path.splitext(os.path.basename(plan))[0]
    base = f"origin/{cfg.get('baseBranch') or 'main'}"
    cli = None if (cfg.get("mr") or {}).get("mode") == "push-base" else (cfg.get("mr") or {}).get("cli") or "glab"
    written = parse_status(lines)
    log = run(["git", "log", base, "--format=%h%x00%B%x1e", f"--grep=Plan: {slug} PR-"], repo) or ""
    on_base = {}
    for rec in log.split("\x1e"):
        if "\x00" in rec:
            h, body = rec.strip().split("\x00", 1)
            for p in re.findall(rf"^Plan: {re.escape(slug)} (PR-\d+)\s*$", body, re.M):
                on_base.setdefault(p, h)
    with ThreadPoolExecutor(8) as ex:
        mrs = dict(zip([p["id"] for p in prs], ex.map(lambda p: mr_of(p["branch"], cli, repo), prs)))
    held_by = claims(repo, slug, own)
    for p in prs:
        st, note = written.get(p["id"], ("todo", ""))
        mr, b = mrs.get(p["id"]), p["branch"]
        local = b and run(["git", "show-ref", "--verify", "-q", f"refs/heads/{b}"], repo) is not None
        remote = b and run(["git", "show-ref", "--verify", "-q", f"refs/remotes/origin/{b}"], repo) is not None
        if st == "done":
            pass
        elif (mr and mr["state"] == "merged") or p["id"] in on_base:
            st, note = "done", f"MR !{mr['n']}" if mr and mr["state"] == "merged" else f"commit {on_base[p['id']]}"
        elif st == "blocked":
            pass
        elif mr and mr["state"] == "opened":
            st, note = ("draft" if mr["draft"] else "review"), f"MR !{mr['n']}"
        elif local or remote:
            subj = (run(["git", "log", "-1", "--format=%s", b if local else f"origin/{b}"], repo) or "").strip()
            st = "held"
            note = re.sub(r"^tertahan,\s*", "", subj.split(":", 1)[1].strip()) if subj.startswith("wip(") and ":" in subj \
                else f"setengah jalan, branch `{b}` ada tanpa MR"
        elif mr and mr["state"] == "closed":
            st, note = "todo", f"MR !{mr['n']} ditutup tanpa merge"
        elif cli is None and not written:
            st = "unknown"
        if p["id"] in overrides:
            st, note = overrides[p["id"]][0], overrides[p["id"]][1] or note
        p.update(state=st, note=note, mr=mr, claim=held_by.get(p["id"]))
    return {"path": os.path.relpath(plan, repo), "slug": slug, "prs": prs}


def plan_steps(r):
    prs = {p["id"]: p for p in r["prs"]}
    cmd = lambda ids: f"/clint:develop {r['path']} {','.join(ids)}"
    free = lambda p: not p["claim"]
    done = {i for i, p in prs.items() if p["state"] == "done"}
    landed = done | {i for i, p in prs.items() if p["state"] in ("review", "draft")}
    steps, info = [], []
    unknown = [i for i, p in prs.items() if p["state"] == "unknown"]
    others = [p for p in prs.values() if p["claim"] and not p["claim"]["self"]]
    if others:
        info.append("Sedang dikerjakan sesi lain: " + ", ".join(f"{p['id']} ({p['claim']['tahap'] or 'berjalan'})" for p in others))
    for p in prs.values():
        if p["state"] == "held" and free(p):
            steps.append(f"[lanjutkan] {cmd([p['id']])} · tertahan: {p['note']}")
    for p in prs.values():
        if p["state"] == "draft" and p["mr"]:
            steps.append(f"[E2E] /clint:test e2e !{p['mr']['n']} · {p['id']}")
    todo = [] if unknown else [p for p in prs.values() if p["state"] == "todo" and free(p)]
    ready = [p for p in todo if set(p["deps"]) <= done]
    stacked = [p for p in todo if p not in ready and set(p["deps"]) <= landed]
    if ready:
        ids = [p["id"] for p in ready[:3]]
        steps.append(f"[{'paralel' if len(ids) > 1 else 'siap'}] {cmd(ids)}")
    if stacked and len(ready) < 3:
        ids = [p["id"] for p in stacked[:3 - len(ready)]]
        on = sorted({d for p in stacked for d in p["deps"] if d not in done})
        steps.append(f"[{'paralel' if len(ids) > 1 else 'siap'}, di atas {','.join(on)} yang belum merge] {cmd(ids)}")
    assumed = landed | {p["id"] for p in ready + stacked} | {p["id"] for p in prs.values() if p["claim"] or p["state"] == "held"}
    rest = [p for p in todo if p not in ready and p not in stacked]
    for _ in range(3):
        wave = [p for p in rest if set(p["deps"]) <= assumed]
        if not wave:
            break
        need = sorted({d for p in wave for d in p["deps"] if d not in done}, key=lambda x: int(x[3:]))
        lintas = "; ".join(f"{p['id']}: {p['lintas']}" for p in wave if p["lintas"])
        steps.append(f"[urutan, setelah {','.join(need)}] {cmd([p['id'] for p in wave])}" + (f" · lintas: {lintas}" if lintas else ""))
        assumed |= {p["id"] for p in wave}
        rest = [p for p in rest if p not in wave]
    if unknown:
        steps.insert(0, f"[catat status] {len(unknown)} PR tanpa bukti (push-base tanpa trailer Plan:) · "
                        f"/clint:docs perbarui Status PR di {r['path']} dari git log")
    for p in prs.values():
        if p["state"] == "blocked":
            steps.append(f"[terblokir] {p['id']}: {p['note'] or 'lihat rencana'}")
    review = [f"!{p['mr']['n']} ({p['id']})" for p in prs.values() if p["state"] == "review" and p["mr"]]
    if review:
        info.append("Menunggu review/merge: " + ", ".join(review))
    return steps, info


def write_status(plan, r):
    text = open(plan, encoding="utf-8").read()
    old = parse_status(text.splitlines())
    items = []
    for p in r["prs"]:
        st, note = p["state"], p["note"]
        if p["claim"]:
            st, note = old.get(p["id"], ("todo", ""))
        label = LABEL[st] + (f": {note}" if st in ("held", "blocked") and note else "")
        tail = f" · {note}" if note and st not in ("held", "blocked") else ""
        items.append(f"- [{'x' if st == 'done' else ' '}] {p['id']} · {label}{tail}")
    block = HEAD_STATUS + "\n\n" + "\n\n".join(items) + "\n"
    pat = re.compile(rf"^{re.escape(HEAD_STATUS)}\n.*?(?=^## |\Z)", re.M | re.S)
    if pat.search(text):
        new = pat.sub(lambda _: block + ("\n" if re.search(rf"^{re.escape(HEAD_STATUS)}\n.*?^## ", text, re.M | re.S) else ""), text, count=1)
    else:
        new = text.rstrip("\n") + "\n\n" + block
    if new != text:
        open(plan, "w", encoding="utf-8").write(new)
        return True
    return False


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("plans", nargs="*")
    ap.add_argument("--repo", default=os.getcwd())
    ap.add_argument("--session", default="")
    ap.add_argument("--set", action="append", default=[])
    ap.add_argument("--write", action="store_true")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()

    work = (run(["git", "rev-parse", "--show-toplevel"], a.repo) or a.repo).strip()
    repo = main_repo(work)
    cfg_path = os.path.join(work, ".claude/clint.json")
    cfg = json.load(open(cfg_path, encoding="utf-8")) if os.path.exists(cfg_path) else {}
    overrides = {}
    for s in a.set:
        pr, _, v = s.partition("=")
        st, _, note = v.partition(":")
        if st not in LABEL:
            sys.exit(f"--set {s}: STATE harus salah satu dari {', '.join(LABEL)}")
        overrides[pr] = (st, note.strip())
    plans = [os.path.abspath(p) for p in a.plans]
    if not plans:
        d = (cfg.get("docs") or {}).get("plans")
        if not d or d == "TIDAK ADA":
            sys.exit("docs.plans tidak diatur di .claude/clint.json")
        plans = sorted(glob.glob(os.path.join(work, d, "*.md")))
    results, skipped = [], []
    for p in plans:
        r = evaluate(p, work, cfg, a.session, overrides)
        if r is None:
            skipped.append(os.path.relpath(p, work))
            continue
        r["steps"], r["info"] = plan_steps(r)
        r["done"] = sum(p["state"] == "done" for p in r["prs"])
        if a.write and any(x["state"] == "unknown" for x in r["prs"]):
            r["written"] = False
        elif a.write:
            r["written"] = write_status(p, r)
        results.append(r)

    if a.json:
        print(json.dumps({"repo": repo, "plans": results, "skipped": skipped}, ensure_ascii=False, indent=1))
        return
    finished = [r["slug"] for r in results if r["done"] == len(r["prs"])]
    for r in results:
        if len(plans) > 1 and r["slug"] in finished:
            continue
        print(f"{r['path']}: {r['done']}/{len(r['prs'])} selesai" + (" (status ditulis)" if r.get("written") else ""))
        for p in r["prs"]:
            if p["claim"]:
                c = p["claim"]
                print(f"  {p['id']} 🔄 dikerjakan {'sesi ini' if c['self'] else 'sesi lain'}" + (f" · {c['tahap']}" if c["tahap"] else ""))
                continue
            dep = f" · butuh {','.join(p['deps'])}" if p["deps"] and p["state"] == "todo" else ""
            print(f"  {p['id']} {LABEL[p['state']]}{(' · ' + p['note']) if p['note'] else ''}{dep}")
        for i in r["info"]:
            print(f"  {i}")
        if r["steps"]:
            print("  Berikutnya:")
            for s in r["steps"]:
                print(f"    {s}")
        print()
    if finished and len(plans) > 1:
        print("Selesai semua: " + ", ".join(finished))
    if skipped:
        print(f"{len(skipped)} file tanpa tabel Urutan pekerjaan dilewati" + (f": {', '.join(skipped)}" if len(skipped) <= 5 else ""))


if __name__ == "__main__":
    main()
