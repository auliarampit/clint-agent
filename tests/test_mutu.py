"""Test skrip mutu: outcome-mr.py (hasil MR dari data GitLab), pelajaran.py (kategori temuan berulang),
golden-check.py (cacat yang ditanam harus ditemukan), dan kelengkapan kasus di tests/golden.
Jalankan: python3 -m unittest discover -s tests"""
import glob, importlib.util, json, os, shutil, subprocess, tempfile, unittest

AKAR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SKRIP = os.path.join(AKAR, "scripts")
GOLDEN = os.path.join(AKAR, "tests", "golden")

TEMUAN = """VERDICT: Needs Fix
TEMUAN:
- [Major] src/upload/uploadProof.ts:8 · best-practice · bug · catch kosong menelan galat unggah
  sekarang: } catch (e) {}
  usulan: lempar ulang galatnya
- [Low] src/upload/uploadProof.ts:3 · best-practice · penamaan · nama form terlalu umum
  sekarang: const form
  usulan: const proofForm
"""


def muat(nama):
    spek = importlib.util.spec_from_file_location(nama.replace("-", "_"), os.path.join(SKRIP, nama))
    mod = importlib.util.module_from_spec(spek)
    spek.loader.exec_module(mod)
    return mod


def tulis(path, isi):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    open(path, "w", encoding="utf-8").write(isi)


class OutcomeMr(unittest.TestCase):
    def setUp(self):
        self.o = muat("outcome-mr.py")

    def test_susun_memisahkan_manusia_bot_dan_push(self):
        mr = {"state": "merged", "created_at": "2026-11-10T10:00:00.000+07:00",
              "merged_at": "2026-11-10T12:30:00.000+07:00"}
        notes = [
            {"system": False, "author": {"bot": False}, "body": "tolong cek null", "created_at": "2026-11-10T11:00:00.000+07:00"},
            {"system": False, "author": {"bot": True}, "body": "[Major] ...", "created_at": "2026-11-10T10:05:00.000+07:00"},
            {"system": True, "author": {}, "body": "added 2 commits", "created_at": "2026-11-10T11:30:00.000+07:00"},
            {"system": True, "author": {}, "body": "changed the description", "created_at": "2026-11-10T10:01:00.000+07:00"},
        ]
        self.assertEqual(self.o.susun(mr, notes),
                         {"state": "merged", "komentar_manusia": 1, "push_susulan": 1, "jam_ke_merge": 2.5})

    def test_susun_mr_open_tanpa_waktu_merge(self):
        r = self.o.susun({"state": "opened", "created_at": "2026-11-10T10:00:00+07:00", "merged_at": None}, [])
        self.assertIsNone(r["jam_ke_merge"])

    def test_ringkasan_menghitung_lolos_dan_mendaftar_yang_dikomentari(self):
        rows = [
            {"repo": "/x/app", "mr": 1, "branch": "feat/a", "state": "merged", "komentar_manusia": 0,
             "push_susulan": 0, "jam_ke_merge": 1.0, "tinjau": None},
            {"repo": "/x/app", "mr": 2, "branch": "fix/b", "state": "merged", "komentar_manusia": 3,
             "push_susulan": 1, "jam_ke_merge": 5.0, "tinjau": {"berat": 0, "putaran": 1}},
            {"repo": "/x/app", "mr": 3, "branch": "feat/c", "tinjau": None},
        ]
        out = self.o.ringkasan(rows, "(uji)")
        self.assertIn("MR dikirim: 3 · terbaca 2", out)
        self.assertIn("tidak terbaca 1", out)
        self.assertIn("Lolos tanpa komentar manusia: 1 dari 2 MR selesai (50%)", out)
        self.assertIn("!2 fix/b · 3 komentar · clint 1 putaran, 0 Major di putaran 1", out)


class Pelajaran(unittest.TestCase):
    def setUp(self):
        self.d = tempfile.mkdtemp()
        self.p = muat("pelajaran.py")
        self.mf = self.p.muat_parser()

    def tearDown(self):
        shutil.rmtree(self.d)

    def test_kategori_dihitung_sekali_per_pr(self):
        for branch in ("feat/a", "feat/b", "fix/c"):
            tulis(os.path.join(self.d, ".git", "clint", branch, "temuan-code-reviewer.md"), TEMUAN)
        tulis(os.path.join(self.d, ".git", "clint", "feat/a", "temuan-conformance-reviewer.md"), TEMUAN)
        hasil = self.p.kandidat(self.d, self.mf, 3)
        self.assertEqual(sorted(hasil), ["bug", "penamaan"])
        self.assertEqual(len(hasil["bug"]["pr"]), 3)
        self.assertEqual(self.mf.TINGKAT[hasil["bug"]["tingkat"]], "Major")

    def test_di_bawah_ambang_tidak_muncul(self):
        tulis(os.path.join(self.d, ".git", "clint", "feat/a", "temuan-code-reviewer.md"), TEMUAN)
        self.assertEqual(self.p.kandidat(self.d, self.mf, 3), {})


class GoldenCheck(unittest.TestCase):
    def setUp(self):
        self.d = tempfile.mkdtemp()
        self.kasus = os.path.join(GOLDEN, "galat-ditelan")

    def tearDown(self):
        shutil.rmtree(self.d)

    def jalankan(self, isi):
        tulis(os.path.join(self.d, "temuan-code-reviewer.md"), isi)
        return subprocess.run(["python3", os.path.join(SKRIP, "golden-check.py"), self.kasus, self.d],
                              capture_output=True, text=True)

    def test_cacat_ditemukan(self):
        r = self.jalankan(TEMUAN)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("hilang=0", r.stdout)

    def test_tingkat_terlalu_rendah_dianggap_hilang(self):
        r = self.jalankan(TEMUAN.replace("[Major]", "[Low]"))
        self.assertEqual(r.returncode, 1)
        self.assertIn("HILANG  src/upload/uploadProof.ts", r.stdout)

    def test_tanpa_temuan_dianggap_hilang(self):
        r = self.jalankan("VERDICT: LGTM\nTEMUAN: -\n")
        self.assertEqual(r.returncode, 1)

    def test_setiap_kasus_lengkap(self):
        kasus = sorted(glob.glob(os.path.join(GOLDEN, "*", "")))
        self.assertTrue(kasus)
        for k in kasus:
            diff = open(os.path.join(k, "diff.patch"), encoding="utf-8").read()
            for w in json.load(open(os.path.join(k, "ekspektasi.json"), encoding="utf-8"))["wajib"]:
                self.assertIn(w["file"], diff, k)
                self.assertIn(w["tingkat_min"], ("Critical", "Major", "Minor", "Low"), k)
                self.assertTrue(w["kata"], k)


if __name__ == "__main__":
    unittest.main()
