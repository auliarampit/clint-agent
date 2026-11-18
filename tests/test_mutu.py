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
                         {"v": 2, "state": "merged", "komentar_manusia": 1, "push_susulan": 1, "jam_ke_merge": 2.5,
                          "hermes": None})

    def test_susun_hermes_warden_dan_balasan_clint_bukan_manusia(self):
        mr = {"state": "merged", "created_at": "2026-11-16T10:00:00+07:00", "merged_at": "2026-11-16T11:00:00+07:00"}
        orang = {"bot": False, "username": "arya"}
        nf = ("<!-- hermes-mr-review --> <!-- verdict:NeedsFix sha:abc -->\n## AI Code Review\n### Temuan\n"
              "- **[Major] [Best practice]** `src/a/StoryViewer.tsx:93` - View kepala menelan ketukan.\n"
              "- **[Critical] [Requirement]** `eas.json:43`\n  buildArtifactPaths salah tempat.\n"
              "- **[Minor] [Standard]** `src/a/x.ts:1` - nama kurang jelas.\n")
        notes = [
            {"system": False, "author": orang, "body": nf, "created_at": "2026-11-16T10:05:00+07:00"},
            {"system": False, "author": orang, "body": "<!-- warden-report --> 0 findings",
             "created_at": "2026-11-16T10:06:00+07:00"},
            {"system": False, "author": {"bot": False, "username": "project_1479_bot_bfac93"},
             "body": "Tindak lanjut di 5288f4ca", "created_at": "2026-11-16T10:20:00+07:00"},
            {"system": False, "author": orang, "body": "<!-- hermes-mr-review --> <!-- verdict:LGTM sha:def -->",
             "created_at": "2026-11-16T10:30:00+07:00"},
        ]
        r = self.o.susun(mr, notes)
        self.assertEqual(r["komentar_manusia"], 0)
        self.assertEqual((r["hermes"]["pertama"], r["hermes"]["akhir"], r["hermes"]["jumlah"]), ("NeedsFix", "LGTM", 2))
        self.assertEqual(r["hermes"]["berat"], [
            {"tingkat": "Major", "lokasi": "src/a/StoryViewer.tsx:93", "teks": "View kepala menelan ketukan."},
            {"tingkat": "Critical", "lokasi": "eas.json:43", "teks": "buildArtifactPaths salah tempat."}])

    def test_ringkasan_memisahkan_needsfix_lolos_peninjau_dan_tanpa_peninjau(self):
        h = lambda v, berat=(): {"pertama": v, "akhir": "LGTM", "jumlah": 1, "berat": list(berat)}
        maj = {"tingkat": "Major", "lokasi": "src/a.ts:1", "teks": "state basi"}
        rows = [
            {"repo": "/x/app", "mr": 1, "branch": "feat/a", "state": "merged", "komentar_manusia": 0, "push_susulan": 0,
             "jam_ke_merge": 1.0, "hermes": h("LGTM"), "tinjau": {"berat": 0, "putaran": 1}},
            {"repo": "/x/app", "mr": 2, "branch": "feat/b", "state": "merged", "komentar_manusia": 0, "push_susulan": 1,
             "jam_ke_merge": 1.0, "hermes": h("NeedsFix", [maj]), "tinjau": {"berat": 0, "putaran": 1}},
            {"repo": "/x/app", "mr": 3, "branch": "chore/c", "state": "merged", "komentar_manusia": 0, "push_susulan": 0,
             "jam_ke_merge": 1.0, "hermes": h("NeedsFix"), "tinjau": None},
        ]
        out = self.o.ringkasan(rows, "(uji)")
        self.assertIn("Hermes: 3 MR ditinjau · LGTM sejak awal 1 (33%) · NeedsFix 2 "
                      "(lolos peninjau clint 1, tanpa peninjau clint 1)", out)
        self.assertIn("- !2 feat/b · lolos peninjau clint (1 putaran)", out)
        self.assertIn("[Major] src/a.ts:1 · state basi", out)
        self.assertIn("Lolos tanpa komentar manusia: 3 dari 3 MR selesai (100%)", out)

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


class UtangMutu(unittest.TestCase):
    def setUp(self):
        self.u = muat("utang-mutu.py")

    def test_e2e_tertunda_dibaca_dari_deskripsi_bukan_draft(self):
        self.assertEqual(self.u.e2e_tertunda("Ringkasan\nE2E: tertunda. iPhone uji tidak tersambung."),
                         "iPhone uji tidak tersambung.")
        self.assertEqual(self.u.e2e_tertunda("**E2E:** tertunda"), "tanpa alasan tertulis")
        self.assertIsNone(self.u.e2e_tertunda("E2E: tidak perlu; flow dikerjakan di PR-10."))
        self.assertIsNone(self.u.e2e_tertunda("E2E: tertunda, perangkat belum ada\n...\nE2E: lulus"))
        self.assertIsNone(self.u.e2e_tertunda("Tanpa baris status"))

    def test_susun_memisahkan_merged_tertunda_dan_feedback_tanpa_verifikasi(self):
        kirim = [
            {"mr": 1, "branch": "fix/fb-mob01-001-a", "verifikasi": "lulus", "draft": True},
            {"mr": 2, "branch": "fix/fb-mob01-002-b", "verifikasi": "belum", "draft": True},
            {"mr": 3, "branch": "feat/c", "verifikasi": None, "draft": True},
            {"mr": 4, "branch": "fix/fb-mob01-004-d", "verifikasi": None, "draft": False},
        ]
        info = {1: ("merged", "E2E: tertunda. butuh HP fisik"), 2: ("merged", "E2E: tidak perlu"),
                3: ("opened", "E2E: tertunda. belum"), 4: None}
        tertunda, feedback, gagal = self.u.susun(kirim, info)
        self.assertEqual(tertunda, ["!1 fix/fb-mob01-001-a · butuh HP fisik"])
        self.assertEqual(feedback, ["!2 fix/fb-mob01-002-b · verifikasi=belum",
                                    "!4 fix/fb-mob01-004-d · verifikasi=kosong"])
        self.assertEqual(gagal, 1)

    def test_daftar_terbaru_dulu_dan_dibatasi(self):
        out = self.u.daftar([f"!{i}" for i in range(1, 13)]).splitlines()
        self.assertEqual((out[0], out[9], out[-1]), ("!12", "!3", "(+2 lainnya)"))
        self.assertEqual(self.u.daftar([]), "(tidak ada)")


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
