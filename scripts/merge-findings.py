#!/usr/bin/env python3
"""Gabungkan blok temuan semua peninjau satu putaran ke findings.md, tanpa token.

  merge-findings.py <folder kerja PR> [--putaran N]

Masukan: <folder>/temuan-<agent>.md, masing-masing berisi blok `VERDICT:` + `TEMUAN:` (format seragam peninjau).
Temuan ganda hanya digabung bila path, baris, dan kategori sama persis; selain itu semua temuan tetap ada.
Keluaran: <folder>/findings.md dan ringkasan di stdout (verdict per agent, jumlah per tingkat, agent yang
perlu ikut putaran ulang).
"""
import glob, os, re, sys

TINGKAT = ["Critical", "Major", "Minor", "Low"]
ITEM = re.compile(r"^\s*- \[(Critical|Major|Minor|Low)\]\s+(.+)$")


def parse(path):
    agent = os.path.basename(path)[len("temuan-"):-len(".md")]
    verdict, items, cur = "?", [], None
    for line in open(path, encoding="utf-8").read().splitlines():
        m = re.match(r"^\s*VERDICT:\s*(.+)$", line)
        if m:
            verdict = m.group(1).strip()
            continue
        m = ITEM.match(line)
        if m:
            kepala = m.group(2)
            bagian = [b.strip() for b in kepala.split(" · ")]
            lokasi = bagian[0]
            kategori = bagian[2] if len(bagian) > 3 else (bagian[1] if len(bagian) > 1 else "")
            cur = {"tingkat": m.group(1), "kepala": kepala, "lokasi": lokasi, "kategori": kategori.lower(),
                   "isi": [], "agents": [agent], "luar": False}
            items.append(cur)
        elif cur and line.startswith((" ", "\t")) and line.strip():
            if line.strip() == "(luar cakupan)":
                cur["luar"] = True
            else:
                cur["isi"].append(line.rstrip())
        elif not line.strip() or line.startswith("TEMUAN"):
            continue
        else:
            cur = None
    return agent, verdict, items


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    if not args:
        sys.exit(__doc__)
    folder = args[0]
    putaran = sys.argv[sys.argv.index("--putaran") + 1] if "--putaran" in sys.argv else "1"
    berkas = sorted(glob.glob(os.path.join(folder, "temuan-*.md")))
    if not berkas:
        sys.exit(f"tidak ada temuan-*.md di {folder}")

    verdicts, semua, kunci = {}, [], {}
    for b in berkas:
        agent, verdict, items = parse(b)
        verdicts[agent] = (verdict, len(items))
        for it in items:
            k = (it["lokasi"], it["kategori"])
            if k in kunci:
                lama = kunci[k]
                lama["agents"].append(agent)
                if TINGKAT.index(it["tingkat"]) < TINGKAT.index(lama["tingkat"]):
                    lama["tingkat"] = it["tingkat"]
                continue
            kunci[k] = it
            semua.append(it)

    dalam = [i for i in semua if not i["luar"]]
    luar = [i for i in semua if i["luar"]]
    out = [f"# Temuan putaran {putaran}", "",
           "Verdict: " + ", ".join(f"{a} {v}" for a, (v, _) in verdicts.items()) + ".", ""]
    n = 0
    for t in TINGKAT:
        grup = [i for i in dalam if i["tingkat"] == t]
        if not grup:
            continue
        out += [f"## {t}"]
        for i in grup:
            n += 1
            out += [f"{n}. [{t}] {i['kepala']} ({', '.join(i['agents'])})"] + i["isi"]
        out += [""]
    if luar:
        out += ["## Luar cakupan (masuk deskripsi MR)"]
        for i in luar:
            n += 1
            out += [f"{n}. [{i['tingkat']}] {i['kepala']} ({', '.join(i['agents'])})"] + i["isi"]
        out += [""]
    with open(os.path.join(folder, "findings.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(out))

    hitung = {t: sum(1 for i in dalam if i["tingkat"] == t) for t in TINGKAT}
    ulang = sorted({a for i in dalam for a in i["agents"]})
    print(f"findings={os.path.join(folder, 'findings.md')}")
    for a, (v, k) in verdicts.items():
        print(f"verdict {a}={v} temuan={k}")
    print("jumlah " + " ".join(f"{t}={c}" for t, c in hitung.items()) + f" luar_cakupan={len(luar)}"
          + f" digabung={sum(len(i['agents']) - 1 for i in semua)}")
    print("putaran_ulang=" + (",".join(ulang) or "-"))


if __name__ == "__main__":
    main()
