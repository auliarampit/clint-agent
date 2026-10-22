"""Test sumber tugas (tugas-saya.py), saringan laporan (update-report.py saring), dan deteksi adapter
(deteksi-tugas.py) terhadap fixture tiga jenis project: sprint tracker berkolom PIC, tabel feedback tanpa PIC,
dan checklist rencana. Jalankan: python3 -m unittest discover -s tests"""
import json, os, shutil, subprocess, sys, tempfile, unittest

AKAR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SKRIP = os.path.join(AKAR, "scripts")
FIXTURE = os.path.join(AKAR, "tests", "fixtures")


def tulis(p, data):
    with open(p, "w", encoding="utf-8") as fh:
        json.dump(data, fh, ensure_ascii=False)


def baca(p):
    with open(p, encoding="utf-8") as fh:
        return fh.read()


def git(d, *a):
    return subprocess.run(["git", "-C", d, *a], capture_output=True, text=True, check=True).stdout.strip()


def jadikan_repo(d, commit=()):
    """Repo git dengan branch dev dan origin/dev; `commit` = pesan commit tambahan (file kosong per commit)."""
    git(d, "init", "-q", "-b", "dev")
    git(d, "-c", "user.name=t", "-c", "user.email=t@t", "add", "-A")
    git(d, "-c", "user.name=t", "-c", "user.email=t@t", "commit", "-q", "-m", "awal")
    for i, pesan in enumerate(commit):
        open(os.path.join(d, f".c{i}"), "w").close()
        git(d, "add", "-A")
        git(d, "-c", "user.name=t", "-c", "user.email=t@t", "commit", "-q", "-m", pesan)
    git(d, "update-ref", "refs/remotes/origin/dev", "HEAD")


class Dasar(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix="clint-test-")
        self.home = os.path.join(self.tmp, "home")
        os.makedirs(os.path.join(self.home, ".config/clint"))
        os.makedirs(os.path.join(self.home, "Library/Logs/clint"))
        tulis(os.path.join(self.home, ".config/clint/user.json"), {"name": ["Aulia"], "language": "id"})
        self.env = dict(os.environ, HOME=self.home, PYTHONDONTWRITEBYTECODE="1")

    def tearDown(self):
        shutil.rmtree(self.tmp)

    def salin(self, nama):
        d = os.path.join(self.tmp, nama)
        shutil.copytree(os.path.join(FIXTURE, nama), d)
        return d

    def jalan(self, skrip, *a):
        return subprocess.run([sys.executable, os.path.join(SKRIP, skrip), *a], capture_output=True, text=True,
                              env=self.env, check=True).stdout

    def tugas(self, d):
        return json.loads(self.jalan("tugas-saya.py", d, "--json"))

    def ids(self, r, kelas):
        return sorted(x["id"] for x in r[kelas])

    def sprint(self):
        d = self.salin("sprint-pic")
        jadikan_repo(d, ["fix(auth): tombol daftar (BUG-1)", "docs(pm): BUG-1 ke QA", "feat(home): kartu (ENH-2a)"])
        return d

    def jadwal(self):
        d = self.salin("jadwal")
        jadikan_repo(os.path.join(d, "docs"))
        jadikan_repo(os.path.join(d, "mobile"))
        return os.path.join(d, "mobile")

    def feedback(self):
        d = self.salin("feedback")
        jadikan_repo(os.path.join(d, "docs"))
        jadikan_repo(os.path.join(d, "mobile"))
        return os.path.join(d, "mobile")


class TugasSaya(Dasar):
    def test_sprint_hanya_butir_user_di_sprint_aktif(self):
        r = self.tugas(self.sprint())
        self.assertEqual(self.ids(r, "kerjakan"), ["BUG-1", "MOD-A-02 (mobile)"])
        self.assertEqual(self.ids(r, "diserahkan"), ["ENH-2a"])
        self.assertIn("BUG-4", self.ids(r, "selesai"))
        self.assertIn("MOD-A-01 (mobile)", self.ids(r, "selesai"), "Code ✅ meski QA 🐞: gerbang modul bukan tugas")
        semua = [x["id"] for k in ("kerjakan", "diserahkan", "selesai", "tidak_dikenal") for x in r[k]]
        self.assertNotIn("BUG-3", semua, "butir milik Budi")
        self.assertNotIn("BUG-9", semua, "sprint s01 sudah Closed")
        self.assertEqual(self.ids(r, "tidak_dikenal"), ["BUG-5"], "status 🤷 tidak ditebak")

    def test_commit_kode_dari_seluruh_histori_bukan_commit_docs(self):
        r = self.tugas(self.sprint())
        bug1 = next(x for x in r["kerjakan"] if x["id"] == "BUG-1")
        self.assertIn("fix(auth): tombol daftar (BUG-1)", bug1["commit"])

    def test_feedback_tanpa_pic_status_beranotasi(self):
        r = self.tugas(self.feedback())
        self.assertEqual(self.ids(r, "kerjakan"), ["feedback-mobile #1", "feedback-mobile #5"])
        self.assertEqual(self.ids(r, "diserahkan"), ["feedback-mobile #3"])
        self.assertEqual(self.ids(r, "selesai"), ["feedback-mobile #2", "feedback-mobile #4"],
                         "Diverifikasi beranotasi dan 'Belum berlaku' (bukan 'Belum')")
        self.assertEqual(self.ids(r, "tidak_dikenal"), ["MOM-M-20", "feedback-mobile #6"])
        self.assertNotIn("feedback-web #1", [x["id"] for x in r["kerjakan"]], "file web bukan surface ini")

    def test_checklist_diringkas_per_rencana(self):
        r = self.tugas(self.salin("checklist"))
        self.assertEqual(self.ids(r, "kerjakan"), ["PLAN-02"])
        self.assertEqual(r["kerjakan"][0]["status"], "2 terbuka / 3")
        self.assertIn("Fase 1", r["kerjakan"][0]["judul"])
        self.assertEqual(self.ids(r, "selesai"), ["PLAN-01"])

    def test_jadwal_modul_sprint_berjalan_tanpa_rencana(self):
        r = self.tugas(self.jadwal())
        self.assertEqual(self.ids(r, "kerjakan"), ["MR-MOB-08", "MR-MOB-10"], "awalan MR- disamakan, WEB dan sprint lalu tidak")
        self.assertEqual({x["status"] for x in r["kerjakan"]}, {"belum direncanakan"})

    def test_tanpa_adapter_tidak_ada_tugas(self):
        d = self.salin("tanpa-sumber")
        self.assertFalse(self.tugas(d)["adapter"])
        self.assertIn("sumber_tugas=tidak ada", self.jalan("tugas-saya.py", d))


class Saring(Dasar):
    def laporan(self, proyek, **grup):
        lap = {"judul": "x", "kalimat": "x", "proyek": proyek, "gagal": [], "kerjakan": [], "cek": [], "tunggu": []}
        lap.update(grup)
        p = os.path.join(self.tmp, "lap.json")
        tulis(p, lap)
        self.jalan("update-report.py", "saring", p)
        return json.loads(baca(p))

    def test_kartu_halu_dibuang_yang_terbukti_lolos(self):
        d = self.sprint()
        commit = git(d, "rev-parse", "--short", "HEAD~1")
        commit_enh = git(d, "rev-parse", "--short", "HEAD")
        b = lambda s, t="x": {"proyek": "sp", "sumber": s, "teks": t}
        hasil = self.laporan(
            [{"nama": "sp", "dir": d}],
            kerjakan=[b("BUG-1"), b("ENH-2a", "belum ada commit"), b(f"ENH-2a {commit_enh}"), b("QA retest"),
                      b(f"api {commit}"),
                      b("migrasi 0028_paket.sql"), b("src/.../register.ts:1"), b("MR !12")],
            cek=[b("BUG-4", "cek apakah masih duplikat")],
            berikutnya=[{"proyek": "sp", "langkah": ["[siap] /clint:develop ENH-2a x", "[siap] /clint:develop BUG-1"]}])
        self.assertEqual([x["sumber"] for x in hasil["kerjakan"]],
                         ["BUG-1", f"api {commit}", "src/.../register.ts:1", "MR !12", "MOD-A-02 (mobile)"],
                         "MOD-A-02 tidak ditulis agent, dilengkapi dari sumber tugas")
        self.assertEqual(hasil["cek"], [], "BUG-4 sudah selesai")
        self.assertEqual(hasil["berikutnya"][0]["langkah"], ["[siap] /clint:develop BUG-1"])
        log = baca(os.path.join(self.home, "Library/Logs/clint/ditolak.log"))
        self.assertIn(f"ENH-2a {commit_enh}\tENH-2a sudah diserahkan", log, "status tracker menang atas commit")
        self.assertIn("QA retest\ttanpa bukti", log)
        self.assertIn("0028_paket.sql\ttanpa bukti", log)
        self.assertIn("BUG-4\tBUG-4 sudah diserahkan/selesai", log)

    def test_tunggu_harus_tertulis_di_dokumen(self):
        m = self.feedback()
        b = lambda s: {"proyek": "mr", "sumber": s, "teks": "x"}
        hasil = self.laporan([{"nama": "mr", "dir": m}], tunggu=[b("MOM-M-20"), b("FB-UI-MOB bag.34")])
        self.assertEqual([x["sumber"] for x in hasil["tunggu"]], ["MOM-M-20"])

    def test_semua_terbuang_berarti_tidak_ada_tugas(self):
        d = self.salin("tanpa-sumber")
        jadikan_repo(d)
        hasil = self.laporan([{"nama": "ts", "dir": d}], kerjakan=[{"proyek": "ts", "sumber": "QA retest", "teks": "x"}])
        self.assertEqual(hasil["judul"], "Tidak ada tugas lagi.")

    def test_tugas_yang_tidak_ditulis_agent_dilengkapi(self):
        m = self.jadwal()
        hasil = self.laporan([{"nama": "mr", "dir": m}])
        self.assertEqual([(x["sumber"], x["perintah"]) for x in hasil["kerjakan"]],
                         [("MR-MOB-08", "/clint:develop MR-MOB-08"), ("MR-MOB-10", "/clint:develop MR-MOB-10")])
        self.assertEqual(hasil["judul"], "2 tugas siap dikerjakan.")

    def test_kartu_gabungan_agent_tidak_digandakan(self):
        m = self.jadwal()
        kartu = {"proyek": "mr", "sumber": "../docs/overview.md", "teks": "Belum direncanakan: MR-MOB-08, MR-MOB-10"}
        hasil = self.laporan([{"nama": "mr", "dir": m}], kerjakan=[kartu])
        self.assertEqual(len(hasil["kerjakan"]), 1)

    def test_lengkapi_dibatasi_lima_sisanya_di_rincian(self):
        d = self.salin("checklist")
        for i in range(3, 10):
            with open(os.path.join(d, f"docs/plans/PLAN-0{i}-x.md"), "w") as fh:
                fh.write("- [ ] satu\n")
        jadikan_repo(d)
        hasil = self.laporan([{"nama": "ck", "dir": d}])
        self.assertEqual(len(hasil["kerjakan"]), 5)
        self.assertIn("3 tugas lain", hasil["rincian"][0]["butir"][0])
        p = os.path.join(self.tmp, "lap.json")
        self.jalan("update-report.py", "saring", p)
        ulang = json.loads(baca(p))
        self.assertEqual(len(ulang["kerjakan"]), 5, "saring dua kali tidak menambah butir")
        self.assertEqual(len(ulang["rincian"][0]["butir"]), 1)


class Deteksi(Dasar):
    def tanpa_tugas(self, d):
        p = os.path.join(d, ".claude/clint.json")
        c = json.loads(baca(p))
        c.pop("tugas")
        tulis(p, c)

    def usulan(self, keluaran):
        i = keluaran.index("{")
        j = min(k for k in (keluaran.find("STATUS BELUM"), keluaran.find("uji coba")) if k > 0)
        return json.loads(keluaran[i:j])["tugas"][0]

    def test_sprint_seri_aktif_dan_status_tak_dikenal_ditanyakan(self):
        d = self.sprint()
        self.tanpa_tugas(d)
        out = self.jalan("deteksi-tugas.py", d)
        u = self.usulan(out)
        self.assertEqual((u["file"], u.get("pilih"), u["kolom"]["pic"]), ("docs/sprints/s*.md", "aktif", "PIC"))
        self.assertIn("'🤷'", out)
        self.jalan("deteksi-tugas.py", d, "--status", "🤷=selesai", "--tulis")
        r = self.tugas(d)
        self.assertEqual(r["tidak_dikenal"], [])
        self.assertIn("BUG-1", self.ids(r, "kerjakan"))

    def test_feedback_disaring_nama_surface(self):
        m = self.feedback()
        self.tanpa_tugas(m)
        u = self.usulan(self.jalan("deteksi-tugas.py", m))
        self.assertEqual((u["file"], u["pemilik"]), ("../docs/qa/feedback/**/*mobile*.md", "semua"))

    def test_koreksi_cocok_berdasarkan_awalan(self):
        m = self.feedback()
        self.tanpa_tugas(m)
        out = self.jalan("deteksi-tugas.py", m, "--status", "menunggu=diserahkan", "info=selesai")
        self.assertNotIn("STATUS BELUM", out)
        self.assertIn("menunggu", self.usulan(out)["status"]["diserahkan"])

    def test_checklist_dengan_id_pola(self):
        d = self.salin("checklist")
        self.tanpa_tugas(d)
        u = self.usulan(self.jalan("deteksi-tugas.py", d))
        self.assertEqual((u["jenis"], u["file"]), ("checklist", "docs/plans/PLAN-*.md"))

    def test_jadwal_terdeteksi_dengan_awalan_dari_nama_rencana(self):
        m = self.jadwal()
        self.tanpa_tugas(m)
        out = self.jalan("deteksi-tugas.py", m)
        i = out.index("{")
        j = out.index("uji coba")
        u = json.loads(out[i:j])["tugas"][-1]
        self.assertEqual((u["jenis"], u["idAwalan"], u["kolom"]["tanggal"]), ("jadwal", "MR-", "Target"))
        self.assertIn("kerjakan 2", out)

    def test_tanpa_sumber_tidak_mengusulkan(self):
        self.assertIn("usulan=tidak ada", self.jalan("deteksi-tugas.py", self.salin("tanpa-sumber")))


if __name__ == "__main__":
    unittest.main()
