#!/usr/bin/env python3
"""Bahan tinjauan satu PR tanpa token: pr.diff di folder kerja PR, ukuran, area sensitif, kandidat auditor.

  review-prep.py <path kerja> <base-ref> [--design] [--json]

--design: project punya prototype (`docs.design` bukan TIDAK ADA), jadi design-auditor bisa jadi kandidat.
Kandidat hanya titik awal: orkestrator tetap memilih maksimal 2 dan boleh menambah auditor dari isi diff.
"""
import json, os, re, subprocess, sys

LOCK = re.compile(r"(^|/)(bun\.lockb?|package-lock\.json|yarn\.lock|pnpm-lock\.yaml|Podfile\.lock)$")
TEST = re.compile(r"(__tests__|\.test\.|\.spec\.|/tests?/|\.maestro/|e2e/)")
UI = re.compile(r"\.(tsx|jsx|vue|svelte|html|css|scss)$")
ABAIKAN = re.compile(r"(^|/)(locales?|i18n|translations?)/|(^|/)(eslint|prettier|jest|babel|tsconfig)[^/]*$")

AUDITOR = {
    "security-auditor": (
        r"auth|login|session|token|secur|crypt|permission|role|guard|middleware|storage|keychain|webview|"
        r"deeplink|linking|upload|\.env|package\.json|dockerfile|nginx",
        r"token|password|secret|jwt|bearer|authorization|cookie|securestore|asyncstorage|localstorage|keychain|"
        r"crypto|eval\(|dangerouslysetinnerhtml|webview|linking\.|http://|owner|userid|businessid|tenant|"
        r"signedurl|presign|upload|deleteobject|sql\.raw|\.raw\(|\.execute\(|\$\{[^}]+\}.*\b(where|from|and)\b"),
    "database-auditor": (
        r"migration|schema|\.sql$|prisma|drizzle|repositor|entity|seed",
        r"\bselect\b.*\bfrom\b|insert into|\bupdate\s+\w+\s+set\b|delete from|\.transaction\(|for update|"
        r"forupdate|innerjoin|leftjoin|createtable|altertable|\.index\(|findmany|\.query\(|sql`"),
    "api-contract-auditor": (
        r"controller|router|dto|openapi|swagger|contract|endpoint|(?<!apps)/api/|(^|/)services?/api",
        r"@(get|post|put|patch|delete)\(|router\.(get|post|put|patch|delete)|app\.(get|post|put|patch|delete)|"
        r"z\.object|@is[a-z]+\(|res\.status|httpstatus|statuscode"),
    "accessibility-auditor": (
        UI.pattern,
        r"onpress|onclick|<button|<input|textinput|pressable|touchable|accessibility|aria-|modal|dialog|"
        r"color|navigation|<form|label"),
    "performance-auditor": (
        r"package\.json",
        r"flatlist|flashlist|scrollview|\.map\(|useeffect|usememo|usecallback|<image|<img|usequery|findmany|"
        r"for .* await|promise\.all|setinterval|animated|reanimated|export|csv|cache"),
}
SENSITIF = re.compile(r"auth|login|session|token|migration|schema|contract|openapi|payment|pembayaran|bayar|billing|"
                      r"checkout|invoice", re.I)
AREA_SENSITIF = ("security-auditor", "database-auditor", "api-contract-auditor")


def git(cwd, *args):
    return subprocess.run(["git", "-C", cwd, *args], capture_output=True, text=True, check=True).stdout


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    if len(args) < 2:
        sys.exit(__doc__)
    kerja, base = os.path.abspath(args[0]), args[1]
    common = git(kerja, "rev-parse", "--path-format=absolute", "--git-common-dir").strip()
    branch = git(kerja, "branch", "--show-current").strip() or "HEAD"
    folder = os.path.join(common, "clint", branch)
    os.makedirs(folder, exist_ok=True)
    diff = git(kerja, "diff", base)
    with open(os.path.join(folder, "pr.diff"), "w") as f:
        f.write(diff)

    files, tambah, kurang = {}, 0, 0
    cur = None
    for line in diff.splitlines():
        if line.startswith("diff --git"):
            cur = line.split(" b/", 1)[1]
            files[cur] = []
        elif cur and not LOCK.search(cur) and line[:1] in "+-" and not line.startswith(("+++", "---")):
            if line[0] == "+":
                tambah += 1
                files[cur].append(line[1:].lower())
            else:
                kurang += 1
    kode = [p for p in files if not LOCK.search(p) and not ABAIKAN.search(p)]
    sensitif = sorted({p for p in kode if SENSITIF.search(p)})
    baris = tambah + kurang

    kandidat = {}
    for nama, (pola_path, pola_isi) in AUDITOR.items():
        rp, ri = re.compile(pola_path, re.I), re.compile(pola_isi, re.I)
        bukti = []
        for p in kode:
            if TEST.search(p):
                continue
            if nama in ("accessibility-auditor",) and not UI.search(p):
                continue
            hit_path = bool(rp.search(p))
            hit_isi = sum(1 for l in files[p] if ri.search(l))
            if hit_path or hit_isi:
                bukti.append((p, hit_path, hit_isi))
        if bukti:
            skor = sum(3 * hp + hi for _, hp, hi in bukti)
            kandidat[nama] = {"skor": skor, "bukti": [f"{p}{' (path)' if hp else ''}{f' {hi} baris' if hi else ''}"
                                                      for p, hp, hi in sorted(bukti, key=lambda b: -(3 * b[1] + b[2]))[:4]]}
    sensitif += sorted({b.split(" ")[0] for n in AREA_SENSITIF for b in kandidat.get(n, {}).get("bukti", [])}
                       - set(sensitif))
    if sensitif or baris > 150:
        ukuran = "Sedang"
    elif baris <= 30 and len(kode) <= 2:
        ukuran = "Mikro"
    else:
        ukuran = "Kecil"
    if "--design" in sys.argv:
        ui = [p for p in kode if UI.search(p) and not TEST.search(p)]
        if ui:
            kandidat["design-auditor"] = {"skor": 3 * len(ui), "bukti": ui[:4]}

    hasil = {"folder": folder, "diff": os.path.join(folder, "pr.diff"), "branch": branch, "file": len(kode),
             "baris": baris, "tambah": tambah, "kurang": kurang, "ukuran": ukuran, "sensitif": sensitif,
             "kandidat": dict(sorted(kandidat.items(), key=lambda k: -k[1]["skor"]))}
    with open(os.path.join(folder, "prep.json"), "w") as f:
        json.dump(hasil, f, indent=1)
    if "--json" in sys.argv:
        print(json.dumps(hasil, indent=1))
        return
    print(f"folder={folder}\nukuran={ukuran} file={len(kode)} baris=+{tambah}/-{kurang}")
    print("sensitif=" + (", ".join(sensitif) or "-"))
    for nama, k in hasil["kandidat"].items():
        print(f"kandidat {nama} skor={k['skor']}: " + "; ".join(k["bukti"]))


if __name__ == "__main__":
    main()
