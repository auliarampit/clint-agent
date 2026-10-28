#!/usr/bin/env python3
"""Audit pemakaian clint dari transkrip sesi + log PR, tanpa token: token, waktu per PR/modul, agent, cek lokal.

  audit-usage.py [--sejak YYYY-MM-DD] [--sampai YYYY-MM-DD] [--proyek <kata>] [--json <file>]

Default 7 hari terakhir. Sumber:
- ~/.claude/projects/*/<sid>.jsonl (+ <sid>/subagents/*.jsonl): token per panggilan model (pesan ganda per id
  dihitung sekali), waktu, perintah clint, durasi tool;
- ~/Library/Logs/clint/pr.jsonl: `mulai` (prepare-branch.sh, membawa sid), `tinjau` (merge-findings.py),
  `kirim` (ship-pr.py). PR dihitung dari pasangan mulai → kirim per repo + branch.
Token PR = token sesi utama di jendela mulai→kirim (dibagi rata bila beberapa PR berjalan bersamaan) + subagent
yang prompt-nya menyebut branch atau worktree PR itu. Menit aktif = jumlah jeda < 10 menit antar kejadian.
"""
import argparse, glob, json, os, re, statistics
from collections import Counter, defaultdict
from datetime import datetime, timedelta, timezone

PROJ = os.path.expanduser("~/.claude/projects")
LOG = os.path.expanduser("~/Library/Logs/clint/pr.jsonl")
CMD = re.compile(r"<command-name>/?(clint:[a-z-]+)</command-name>")
CEK = [("run-checks", r"run-checks\.py"), ("lint", r"\beslint\b|run lint"), ("typecheck", r"\btsc\b|typecheck"),
       ("test", r"\bjest\b|vitest|run test"), ("e2e", r"maestro|playwright")]
JEDA = 600


def waktu(s):
    t = datetime.fromisoformat(s.replace("Z", "+00:00"))
    return t if t.tzinfo else t.astimezone()


def baca(path):
    for baris in open(path, errors="ignore"):
        try:
            yield json.loads(baris)
        except ValueError:
            continue


def transkrip(path):
    """Titik panggilan model [(waktu, token dict)], waktu kejadian, perintah, durasi cek, prompt pertama."""
    pakai, kejadian, perintah, cek, pending, prompt = {}, [], [], Counter(), {}, None
    for d in baca(path):
        t = d.get("timestamp")
        if not t:
            continue
        t = waktu(t)
        kejadian.append(t)
        m = d.get("message") or {}
        isi = m.get("content")
        if d.get("type") == "user" and prompt is None:
            prompt = isi if isinstance(isi, str) else json.dumps(isi)[:4000]
        if isinstance(isi, str):
            perintah += CMD.findall(isi)
        if d.get("type") == "assistant" and m.get("usage") and m.get("id"):
            u = m["usage"]
            pakai[m["id"]] = (t, {"in": u.get("input_tokens", 0), "cw": u.get("cache_creation_input_tokens", 0),
                                  "cr": u.get("cache_read_input_tokens", 0), "out": u.get("output_tokens", 0)})
        for c in isi if isinstance(isi, list) else []:
            if not isinstance(c, dict):
                continue
            if c.get("type") == "tool_use":
                inp = c.get("input") or {}
                if c.get("name") == "Skill" and str(inp.get("skill", "")).startswith("clint:"):
                    perintah.append(inp["skill"])
                if c.get("name") == "Bash":
                    jenis = next((n for n, p in CEK if re.search(p, str(inp.get("command", "")))), None)
                    if jenis:
                        pending[c["id"]] = (jenis, t)
            if c.get("type") == "tool_result" and c.get("tool_use_id") in pending:
                jenis, t0 = pending.pop(c["tool_use_id"])
                cek[jenis] += (t - t0).total_seconds()
    return sorted(pakai.values(), key=lambda x: x[0]), sorted(kejadian), perintah, cek, prompt or ""


def jumlah(titik, dari=None, sampai=None):
    tot = Counter()
    for t, u in titik:
        if (dari is None or t >= dari) and (sampai is None or t <= sampai):
            tot.update(u)
    return tot


def aktif(kejadian):
    return sum(d for d in ((b - a).total_seconds() for a, b in zip(kejadian, kejadian[1:])) if d < JEDA) / 60


def total(c):
    return sum(c.get(k, 0) for k in ("in", "cw", "cr", "out"))


def jt(x):
    return f"{x / 1e6:.1f} jt"


def ringkas(xs, fmt="{:.1f}"):
    if not xs:
        return "-"
    xs = sorted(xs)
    n = len(xs)
    return (f"median {fmt.format(statistics.median(xs))} · p25 {fmt.format(xs[n // 4])} · "
            f"p75 {fmt.format(xs[(3 * n) // 4])} · rata2 {fmt.format(statistics.mean(xs))}")


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--sejak")
    ap.add_argument("--sampai")
    ap.add_argument("--proyek")
    ap.add_argument("--json")
    a = ap.parse_args()
    lokal = datetime.now().astimezone().tzinfo
    sejak = (datetime.fromisoformat(a.sejak).replace(tzinfo=lokal) if a.sejak
             else datetime.now(lokal) - timedelta(days=7))
    sampai = (datetime.fromisoformat(a.sampai).replace(tzinfo=lokal) + timedelta(days=1) if a.sampai
              else datetime.now(lokal) + timedelta(minutes=1))

    sesi = {}
    for f in glob.glob(f"{PROJ}/*/*.jsonl"):
        proyek = os.path.basename(os.path.dirname(f))
        if a.proyek and a.proyek not in proyek:
            continue
        if datetime.fromtimestamp(os.path.getmtime(f), timezone.utc) < sejak:
            continue
        titik, kejadian, perintah, cek, _ = transkrip(f)
        if not kejadian or not (sejak <= kejadian[0] < sampai):
            continue
        subs = []
        for sf in glob.glob(f[:-6] + "/subagents/*.jsonl"):
            meta = sf[:-6] + ".meta.json"
            jenis = json.load(open(meta)).get("agentType", "?") if os.path.exists(meta) else "?"
            st, sk, _, scek, sprompt = transkrip(sf)
            if sk:
                subs.append({"jenis": jenis, "titik": st, "kejadian": sk, "cek": scek, "prompt": sprompt})
                cek.update(scek)
        semua = sorted(kejadian + [t for s in subs for t in s["kejadian"]])
        sesi[os.path.basename(f)[:-6]] = {"proyek": proyek.replace("-Users-", "").split("-Desktop-")[-1],
                                         "mulai": kejadian[0], "titik": titik, "subs": subs, "cek": cek,
                                         "perintah": sorted(set(perintah)), "aktif": aktif(semua)}

    # Pasangan mulai → kirim dari log PR.
    pr, buka = [], {}
    for d in (baca(LOG) if os.path.exists(LOG) else []):
        t = waktu(d["t"])
        if not (sejak <= t < sampai):
            continue
        kunci = (d.get("repo"), d.get("branch"))
        if d["jadi"] == "mulai":
            buka[kunci] = {"sid": d.get("sid"), "mulai": t, "repo": kunci[0], "branch": kunci[1], "putaran": 0,
                           "hanya_low": 0}
        elif d["jadi"] == "tinjau" and kunci in buka:
            buka[kunci]["putaran"] = max(buka[kunci]["putaran"], d.get("putaran", 1))
            buka[kunci]["hanya_low"] += int(any(d.get("jumlah", {}).values()) and not d.get("ulang"))
        elif d["jadi"] == "kirim" and kunci in buka:
            p = buka.pop(kunci)
            p.update(kirim=t, mr=d.get("mr"), plan=d.get("plan"), pr=d.get("pr"), draft=d.get("draft"))
            pr.append(p)

    for p in pr:
        s = sesi.get(p["sid"])
        p["menit"] = (p["kirim"] - p["mulai"]).total_seconds() / 60
        if not s:
            p.update(token=None, aktif=None)
            continue
        bersama = [q for q in pr if q["sid"] == p["sid"] and q["mulai"] < p["kirim"] and q["kirim"] > p["mulai"]]
        tanda = (p["branch"], p["branch"].replace("/", "-"))
        milik = [x for x in s["subs"] if any(k in x["prompt"] for k in tanda)]
        utama = Counter({k: v / len(bersama) for k, v in jumlah(s["titik"], p["mulai"], p["kirim"]).items()})
        for x in milik:
            utama.update(jumlah(x["titik"]))
        p["token"] = dict(utama)
        p["subagent"] = Counter(x["jenis"] for x in milik)
        kej = [t for t in sorted(t for x in milik for t in x["kejadian"]) if t <= p["kirim"]]
        p["aktif"] = aktif(sorted(kej + [t for t, _ in s["titik"] if p["mulai"] <= t <= p["kirim"]]))
        p["cek"] = sum((x["cek"] for x in milik), Counter())

    akhir = sampai - timedelta(days=1) if a.sampai else datetime.now(lokal)
    out = [f"# Audit clint {sejak:%d %b} – {akhir:%d %b %Y}", ""]
    semua = Counter()
    for s in sesi.values():
        semua.update(jumlah(s["titik"]))
        for x in s["subs"]:
            semua.update(jumlah(x["titik"]))
    out += [f"Sesi: {len(sesi)} · token {jt(total(semua))} (cache read {jt(semua['cr'])}, cache write "
            f"{jt(semua['cw'])}, output {jt(semua['out'])}, input {jt(semua['in'])})", ""]

    out += ["## Per perintah (sesi yang memakai perintah itu)"]
    per = defaultdict(lambda: [0, Counter(), 0.0])
    for s in sesi.values():
        tot = jumlah(s["titik"]) + sum((jumlah(x["titik"]) for x in s["subs"]), Counter())
        for c in s["perintah"] or ["(tanpa clint)"]:
            per[c][0] += 1
            per[c][1].update(tot)
            per[c][2] += s["aktif"]
    for c, (n, tot, akt) in sorted(per.items(), key=lambda x: -total(x[1][1])):
        out.append(f"- {c}: {n} sesi · {jt(total(tot))} · {akt / n:.0f} mnt aktif/sesi")

    out += ["", "## Per agent"]
    agen = defaultdict(list)
    for s in sesi.values():
        agen["(sesi utama)"].append(s["titik"])
        for x in s["subs"]:
            agen[x["jenis"]].append(x["titik"])
    for j, daftar in sorted(agen.items(), key=lambda x: -sum(total(jumlah(t)) for t in x[1])):
        daftar = [t for t in daftar if t]
        if not daftar:
            continue
        konteks = [statistics.mean(u["in"] + u["cw"] + u["cr"] for _, u in t) for t in daftar]
        awal = [t[0][1]["in"] + t[0][1]["cw"] + t[0][1]["cr"] for t in daftar]
        out.append(f"- {j}: {len(daftar)}× · {jt(sum(total(jumlah(t)) for t in daftar) / len(daftar))}/run · "
                   f"{statistics.mean(len(t) for t in daftar):.0f} panggilan · konteks awal "
                   f"{statistics.median(awal) / 1e3:.0f}k → rata2 {statistics.median(konteks) / 1e3:.0f}k")

    out += ["", f"## Per PR ({len(pr)} PR tercatat mulai → kirim)"]
    ada = [p for p in pr if p.get("token") is not None]
    if ada:
        out += [f"- Menit aktif: {ringkas([p['aktif'] for p in ada])}",
                f"- Menit kalender mulai→kirim: {ringkas([p['menit'] for p in pr], '{:.0f}')}",
                f"- Token: {ringkas([total(p['token']) / 1e6 for p in ada])} jt",
                f"- Putaran tinjauan: {ringkas([p['putaran'] for p in ada])} · putaran hanya-Low "
                f"{sum(p['hanya_low'] for p in ada)}",
                f"- Subagent per PR: " + ", ".join(f"{j} {n / len(ada):.1f}" for j, n in
                                                   sum((p["subagent"] for p in ada), Counter()).most_common()),
                f"- Waktu cek per PR (detik): " + ", ".join(f"{j} {v / len(ada):.0f}" for j, v in
                                                          sum((p["cek"] for p in ada), Counter()).most_common())]
        for p in sorted(ada, key=lambda p: p["mulai"]):
            out.append(f"  - {p['mulai']:%d/%m %H:%M} {os.path.basename(p['repo'] or '')} "
                       f"{('!' + str(p['mr'])) if p['mr'] else 'push'} {p['pr'] or p['branch']} · {p['aktif']:.0f} mnt · "
                       f"{jt(total(p['token']))} · putaran {p['putaran']}" + (" · draft" if p["draft"] else ""))
    if len(ada) < len(pr):
        out.append(f"- {len(pr) - len(ada)} PR tanpa transkrip sesi (sid kosong atau di luar rentang)")

    modul = defaultdict(list)
    for p in ada:
        if p.get("plan"):
            modul[os.path.basename(p["plan"])].append(p)
    if modul:
        out += ["", "## Per modul (rencana)"]
        for m, ps in modul.items():
            out.append(f"- {m}: {len(ps)} PR · {sum(p['aktif'] for p in ps) / 60:.1f} jam aktif · "
                       f"{min(p['mulai'] for p in ps):%d/%m %H:%M} → {max(p['kirim'] for p in ps):%d/%m %H:%M} · "
                       f"{jt(sum(total(p['token']) for p in ps))}")

    cek = sum((s["cek"] for s in sesi.values()), Counter())
    out += ["", "## Waktu cek lokal (semua sesi, menit)", "- " + ", ".join(f"{j} {v / 60:.0f}" for j, v in
                                                                          cek.most_common())]
    print("\n".join(out))
    if a.json:
        bersih = [{k: (v.isoformat() if isinstance(v, datetime) else v) for k, v in p.items()} for p in pr]
        json.dump({"sesi": len(sesi), "token": dict(semua), "pr": bersih}, open(a.json, "w"), indent=1, default=str)


if __name__ == "__main__":
    main()
