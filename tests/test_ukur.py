"""Test skrip hemat token dan pengukuran: plan-slice.py, run-checks.py, merge-findings.py (Low tanpa putaran
ulang), dan audit-usage.py (pasangan mulai → kirim di pr.jsonl dengan token dari transkrip).
Jalankan: python3 -m unittest discover -s tests"""
import json, os, shutil, subprocess, tempfile, unittest

AKAR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SKRIP = os.path.join(AKAR, "scripts")

RENCANA = """# Implementation Plan — MOB-1

## 1. Lingkup

Fitur contoh untuk PR-1 s/d PR-3.

## 5. Urutan pekerjaan

| PR    | Branch          | Isi |
| ----- | --------------- | --- |
| PR-1  | feat/fondasi    | data |
| PR-1b | feat/fondasi-b  | tiruan |
| PR-2  | feat/layar      | layar, setelah PR-1 |
| PR-3  | feat/lain       | lain |

## 6. Ketidakjelasan

| No | Isi |
| -- | --- |
| K1 | umum tanpa PR |
| K2 | khusus PR-3 |

## 7. Rincian per PR

### PR-1 Fondasi

- isi PR-1

### PR-2 Layar

- isi PR-2

## Status PR

- [ ] PR-1 · ⬜ belum mulai
"""


def git(*args, cwd):
    subprocess.run(["git", *args], cwd=cwd, check=True, capture_output=True,
                   env=dict(os.environ, GIT_AUTHOR_NAME="t", GIT_AUTHOR_EMAIL="t@t", GIT_COMMITTER_NAME="t",
                            GIT_COMMITTER_EMAIL="t@t"))


def skrip(nama, *args, home=None, cek=True):
    env = dict(os.environ, HOME=home) if home else None
    r = subprocess.run(["python3", os.path.join(SKRIP, nama), *args], capture_output=True, text=True, env=env)
    if cek and r.returncode != 0:
        raise AssertionError(r.stdout + r.stderr)
    return r


class PlanSlice(unittest.TestCase):
    def setUp(self):
        self.d = tempfile.mkdtemp()
        self.rencana = os.path.join(self.d, "mob-1.md")
        open(self.rencana, "w").write(RENCANA)

    def tearDown(self):
        shutil.rmtree(self.d)

    def test_hanya_pr_itu_dan_bagian_umum(self):
        out = skrip("plan-slice.py", self.rencana, "PR-2").stdout
        self.assertIn("Fitur contoh", out)
        self.assertIn("| PR-2  | feat/layar", out)
        self.assertIn("| PR    | Branch", out)
        self.assertIn("K1 | umum tanpa PR", out)
        self.assertIn("- isi PR-2", out)
        for dibuang in ("feat/lain", "K2 | khusus", "- isi PR-1", "## Status PR", "feat/fondasi-b"):
            self.assertNotIn(dibuang, out)

    def test_pr_1_tidak_mengambil_pr_1b(self):
        out = skrip("plan-slice.py", self.rencana, "PR-1").stdout
        self.assertIn("| PR-1  | feat/fondasi ", out)
        self.assertIn("layar, setelah PR-1", out)
        self.assertNotIn("feat/fondasi-b", out)


class RunChecks(unittest.TestCase):
    def setUp(self):
        self.d = tempfile.mkdtemp()
        asal, self.kerja = os.path.join(self.d, "asal.git"), os.path.join(self.d, "app")
        git("init", "-q", "--bare", "-b", "dev", asal, cwd=self.d)
        git("clone", "-q", asal, "app", cwd=self.d)
        git("checkout", "-q", "-b", "dev", cwd=self.kerja)
        os.makedirs(os.path.join(self.kerja, ".claude"))
        json.dump({"baseBranch": "dev", "surfaces": [{
            "name": "mobile", "root": ".", "lint": "echo PENUH", "lintRelated": "echo LINT",
            "typecheck": "true", "testRelated": "sh -c 'echo uji gagal; exit 1' --"}]},
            open(os.path.join(self.kerja, ".claude", "clint.json"), "w"))
        open(os.path.join(self.kerja, "a.ts"), "w").write("1")
        git("add", ".", cwd=self.kerja); git("commit", "-q", "-m", "a", cwd=self.kerja)
        git("push", "-q", "-u", "origin", "dev", cwd=self.kerja)
        git("checkout", "-q", "-b", "feat/x", cwd=self.kerja)
        open(os.path.join(self.kerja, "b.tsx"), "w").write("2")
        open(os.path.join(self.kerja, "c.md"), "w").write("3")

    def tearDown(self):
        shutil.rmtree(self.d)

    def test_file_berubah_paralel_dan_gagal_terlapor(self):
        r = skrip("run-checks.py", self.kerja, cek=False)
        self.assertEqual(r.returncode, 1)
        self.assertIn("mobile.lint=lulus", r.stdout)
        self.assertIn("mobile.test=gagal", r.stdout)
        self.assertIn("uji gagal", r.stdout)
        folder = os.path.join(self.kerja, ".git", "clint", "feat/x")
        log = open(os.path.join(folder, "checks", "mobile.lint.log")).read()
        self.assertIn("echo LINT b.tsx", log)
        self.assertNotIn("c.md", log)
        self.assertTrue(os.path.exists(os.path.join(folder, "checks.md")))

    def test_penuh_memakai_lint_seluruh_surface(self):
        r = skrip("run-checks.py", self.kerja, "--penuh", cek=False)
        log = open(os.path.join(self.kerja, ".git", "clint", "feat/x", "checks", "mobile.lint.log")).read()
        self.assertIn("PENUH", log)
        self.assertIn("mobile.lint=lulus", r.stdout)


class MergeFindingsLow(unittest.TestCase):
    def setUp(self):
        self.d = tempfile.mkdtemp()
        self.folder = os.path.join(self.d, "repo", ".git", "clint", "feat", "x")
        os.makedirs(self.folder)

    def tearDown(self):
        shutil.rmtree(self.d)

    def tulis(self, agent, *butir):
        isi = "VERDICT: Needs Fix\nTEMUAN:\n" + "".join(f"- [{t}] a.ts:{i} · clean · {k} · masalah\n"
                                                     for i, (t, k) in enumerate(butir))
        open(os.path.join(self.folder, f"temuan-{agent}.md"), "w").write(isi)

    def test_peninjau_hanya_low_tidak_diulang(self):
        self.tulis("code-reviewer", ("Low", "nama"))
        self.tulis("security-auditor", ("Major", "token"))
        out = skrip("merge-findings.py", self.folder, home=self.d).stdout
        self.assertIn("putaran_ulang=security-auditor", out)
        self.assertNotIn("hanya_low", out)

    def test_semua_low_tanpa_putaran_ulang_dan_tercatat(self):
        self.tulis("code-reviewer", ("Low", "nama"), ("Low", "format"))
        out = skrip("merge-findings.py", self.folder, "--putaran", "2", home=self.d).stdout
        self.assertIn("putaran_ulang=-", out)
        self.assertIn("hanya_low=ya", out)
        log = [json.loads(l) for l in open(os.path.join(self.d, "Library/Logs/clint/pr.jsonl"))]
        self.assertEqual((log[-1]["branch"], log[-1]["putaran"], log[-1]["ulang"]), ("feat/x", 2, []))
        self.assertEqual(log[-1]["repo"], os.path.join(self.d, "repo"))


class AuditUsage(unittest.TestCase):
    def setUp(self):
        self.d = tempfile.mkdtemp()
        proj = os.path.join(self.d, ".claude", "projects", "-Users-t-Desktop-app")
        os.makedirs(os.path.join(proj, "s1", "subagents"))

        def pesan(t, mid, cr, isi=None):
            return {"type": "assistant", "timestamp": t, "message": {
                "id": mid, "content": isi or [], "usage": {"input_tokens": 0, "cache_creation_input_tokens": 0,
                                                           "cache_read_input_tokens": cr, "output_tokens": 0}}}
        utama = [{"type": "user", "timestamp": "2026-10-28T09:00:00+07:00",
                  "message": {"content": "<command-name>/clint:develop</command-name>"}},
                 pesan("2026-10-28T09:01:00+07:00", "a", 1000),
                 pesan("2026-10-28T09:05:00+07:00", "b", 2000),
                 pesan("2026-10-28T09:05:00+07:00", "b", 2000),
                 pesan("2026-10-28T09:30:00+07:00", "c", 9999)]
        sub = [{"type": "user", "timestamp": "2026-10-28T09:02:00+07:00",
                "message": {"content": "Path kerja /x/app-worktrees/feat-x"}},
               pesan("2026-10-28T09:03:00+07:00", "d", 500)]
        for path, baris in ((os.path.join(proj, "s1.jsonl"), utama),
                            (os.path.join(proj, "s1", "subagents", "agent-1.jsonl"), sub)):
            open(path, "w").write("".join(json.dumps(b) + "\n" for b in baris))
        json.dump({"agentType": "clint:developer"}, open(os.path.join(proj, "s1", "subagents", "agent-1.meta.json"), "w"))
        log = os.path.join(self.d, "Library", "Logs", "clint")
        os.makedirs(log)
        open(os.path.join(log, "pr.jsonl"), "w").write("".join(json.dumps(b) + "\n" for b in [
            {"t": "2026-10-28T09:00:30+0700", "jadi": "mulai", "sid": "s1", "repo": "/x/app", "branch": "feat/x"},
            {"t": "2026-10-28T09:04:00+0700", "jadi": "tinjau", "repo": "/x/app", "branch": "feat/x", "putaran": 1,
             "jumlah": {"Low": 1}, "ulang": []},
            {"t": "2026-10-28T09:10:00+0700", "jadi": "kirim", "repo": "/x/app", "branch": "feat/x", "mr": 7,
             "plan": "docs/plans/mob-1.md", "pr": "PR-2", "draft": False}]))

    def tearDown(self):
        shutil.rmtree(self.d)

    def test_pr_dari_log_dan_token_transkrip(self):
        hasil = os.path.join(self.d, "hasil.json")
        out = skrip("audit-usage.py", "--sejak", "2026-10-28", "--sampai", "2026-10-28", "--json", hasil,
                    home=self.d).stdout
        self.assertIn("1 PR tercatat", out)
        self.assertIn("mob-1.md: 1 PR", out)
        self.assertIn("clint:develop: 1 sesi", out)
        pr = json.load(open(hasil))["pr"][0]
        self.assertEqual(pr["token"]["cr"], 1000 + 2000 + 500)   # pesan ganda "b" sekali, "c" di luar jendela
        self.assertEqual((pr["mr"], pr["putaran"], pr["hanya_low"]), (7, 1, 1))


if __name__ == "__main__":
    unittest.main()
