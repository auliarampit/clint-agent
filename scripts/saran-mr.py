#!/usr/bin/env python3
"""Pasang saran tinjauan ke MR/PR supaya bisa divalidasi langsung di kode (tanpa token).

- Saran pada baris yang berubah di MR → komentar *suggestion* di baris itu (bisa "Apply suggestion").
- Saran lain → bagian "Saran tinjauan" untuk deskripsi MR (dicetak ke stdout): tautan file#baris,
  cuplikan kode sekarang, usulan dalam bentuk diff, alasan, dan agent sumbernya.

Pakai (dari dalam repo project):
  saran-mr.py <nomor MR/PR> <saran.json> [--uji]
saran.json: [{"path":"src/a.ts","line":42,"sekarang":"kode lama (1..n baris)","usulan":"kode baru",
              "alasan":"kenapa","agent":"reviewer-senior","lintas":false}]
  "lintas": true = perbaikan butuh perubahan di luar baris itu (mis. konstanta baru) → tidak dijadikan
  suggestion (Apply akan merusak build), masuk ke deskripsi saja.
--uji: tampilkan apa yang akan diposting, tanpa mengirim apa pun.
"""
import json, re, subprocess, sys


def sh(*a, inp=None):
    return subprocess.run(a, capture_output=True, text=True, input=inp, timeout=30)


def baris_berubah(base, head, path):
    """Nomor baris (versi baru) yang ditambah/diubah di MR untuk satu file."""
    out = sh("git", "diff", "-U0", f"{base}..{head}", "--", path).stdout
    hasil = set()
    for m in re.finditer(r"^@@ -\d+(?:,\d+)? \+(\d+)(?:,(\d+))? @@", out, re.M):
        mulai, n = int(m.group(1)), int(m.group(2) or 1)
        hasil.update(range(mulai, mulai + n))
    return hasil


def blok_saran(s, n):
    return (f"**Saran {s.get('agent', 'peninjau')}:** {s.get('alasan', '')}\n\n"
            f"```suggestion:-0+{n - 1}\n{s.get('usulan', '').rstrip()}\n```")


def main():
    if len(sys.argv) < 3:
        print(__doc__); sys.exit(1)
    nomor, berkas, uji = sys.argv[1].lstrip("!#"), sys.argv[2], "--uji" in sys.argv
    saran = json.load(open(berkas, encoding="utf-8"))
    github = "github.com" in sh("git", "remote", "get-url", "origin").stdout

    if github:
        pr = json.loads(sh("gh", "pr", "view", nomor, "--json", "url,headRefName,baseRefOid,headRefOid").stdout)
        base, head, cabang, url = pr["baseRefOid"], pr["headRefOid"], pr["headRefName"], pr["url"]
        repo_url = url.split("/pull/")[0]
        blob = lambda p, l: f"{repo_url}/blob/{cabang}/{p}#L{l}"
    else:
        mr = json.loads(sh("glab", "mr", "view", nomor, "-F", "json").stdout)
        ref, cabang, url = mr["diff_refs"], mr["source_branch"], mr["web_url"]
        base, head = ref["base_sha"], ref["head_sha"]
        repo_url = url.split("/-/merge_requests/")[0]
        blob = lambda p, l: f"{repo_url}/-/blob/{cabang}/{p}#L{l}"
    sh("git", "fetch", "-q", "origin", head)

    deskripsi, terpasang = [], 0
    for s in saran:
        path, line = s["path"], int(s["line"])
        n = max(1, len((s.get("sekarang") or "").rstrip("\n").splitlines()))
        if not s.get("lintas") and line in baris_berubah(base, head, path):
            body = blok_saran(s, n)
            if github:
                args = ["gh", "api", f"repos/{{owner}}/{{repo}}/pulls/{nomor}/comments", "-f", f"body={body}",
                        "-f", f"commit_id={head}", "-f", f"path={path}", "-F", f"line={line + n - 1}", "-f", "side=RIGHT"]
                if n > 1:
                    args += ["-F", f"start_line={line}", "-f", "start_side=RIGHT"]
            else:
                pos = {"position_type": "text", "base_sha": base, "start_sha": ref["start_sha"], "head_sha": head,
                       "new_path": path, "old_path": path, "new_line": line}
                args = ["glab", "api", "-X", "POST", f"projects/:id/merge_requests/{nomor}/discussions",
                        "--input", "-", "-H", "Content-Type: application/json"]
            if uji:
                print(f"[uji] komentar saran di {path}:{line} ({n} baris)\n{body}\n", file=sys.stderr)
            else:
                r = sh(*args, inp=None if github else json.dumps({"body": body, "position": pos}))
                if r.returncode == 0:
                    terpasang += 1
                    continue
                print(f"gagal memasang komentar di {path}:{line}: {r.stderr.strip()[:200]}", file=sys.stderr)
            if uji:
                terpasang += 1
                continue
        diff = "\n".join(["-" + x for x in (s.get("sekarang") or "").rstrip("\n").splitlines()] +
                         ["+" + x for x in (s.get("usulan") or "").rstrip("\n").splitlines()])
        deskripsi.append(f"- **[{path}:{line}]({blob(path, line)})** — {s.get('alasan', '')} "
                         f"_({s.get('agent', 'peninjau')})_\n\n  ```diff\n  " + diff.replace("\n", "\n  ") + "\n  ```")

    print(f"{terpasang} saran dipasang di baris kode; {len(deskripsi)} saran untuk deskripsi.", file=sys.stderr)
    if deskripsi:
        print("<details>\n<summary>Saran tinjauan (tidak menahan MR) — " + str(len(deskripsi)) +
              "</summary>\n\n" + "\n\n".join(deskripsi) + "\n\n</details>")


if __name__ == "__main__":
    main()
