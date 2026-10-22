"""Test rujukan skrip di skill/agent (setiap `$R/scripts/...` benar-benar ada, tanpa path keras atau cache plugin
basi) dan sync-repos.sh (menarik repo kerja + relatedRepos, cache 2 menit, working tree kotor hanya di-fetch).
Jalankan: python3 -m unittest discover -s tests"""
import glob, json, os, re, shutil, subprocess, tempfile, unittest

AKAR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SKRIP = os.path.join(AKAR, "scripts")
TEKS = sorted(glob.glob(os.path.join(AKAR, "skills", "*", "SKILL.md")) + glob.glob(os.path.join(AKAR, "agents", "*.md")))


def git(*args, cwd):
    subprocess.run(["git", *args], cwd=cwd, check=True, capture_output=True,
                   env=dict(os.environ, GIT_AUTHOR_NAME="t", GIT_AUTHOR_EMAIL="t@t", GIT_COMMITTER_NAME="t",
                            GIT_COMMITTER_EMAIL="t@t"))


class RujukanSkrip(unittest.TestCase):
    def test_skrip_yang_dirujuk_ada(self):
        hilang = []
        for p in TEKS:
            for nama in re.findall(r"\$R/scripts/([\w.-]+)", open(p, encoding="utf-8").read()):
                if not os.path.exists(os.path.join(SKRIP, nama)):
                    hilang.append(f"{os.path.relpath(p, AKAR)}: {nama}")
        self.assertEqual(hilang, [])

    def test_tanpa_path_keras_atau_cache_basi(self):
        salah = [os.path.relpath(p, AKAR) for p in TEKS
                 if re.search(r"/Users/|plugins/cache/clint", open(p, encoding="utf-8").read())]
        self.assertEqual(salah, [])

    def test_skill_yang_memakai_R_mendefinisikannya(self):
        kurang = [os.path.relpath(p, AKAR) for p in glob.glob(os.path.join(AKAR, "skills", "*", "SKILL.md"))
                  if "$R/" in open(p, encoding="utf-8").read()
                  and "~/.config/clint/root" not in open(p, encoding="utf-8").read()]
        self.assertEqual(kurang, [])


class SyncRepos(unittest.TestCase):
    def setUp(self):
        self.d = tempfile.mkdtemp()
        for nama, branch in (("kerja", "dev"), ("docs", "main")):
            asal = os.path.join(self.d, f"{nama}.git")
            git("init", "-q", "--bare", "-b", branch, asal, cwd=self.d)
            git("clone", "-q", asal, nama, cwd=self.d)
            p = os.path.join(self.d, nama)
            git("checkout", "-q", "-b", branch, cwd=p)
            open(os.path.join(p, "a.txt"), "w").write("1")
            git("add", ".", cwd=p); git("commit", "-q", "-m", "awal", cwd=p); git("push", "-q", "-u", "origin", branch, cwd=p)
        kerja = os.path.join(self.d, "kerja")
        os.makedirs(os.path.join(kerja, ".claude"))
        json.dump({"baseBranch": "dev", "relatedRepos": [{"name": "docs", "path": "../docs", "branch": "main"}]},
                  open(os.path.join(kerja, ".claude", "clint.json"), "w"))
        git("add", ".", cwd=kerja); git("commit", "-q", "-m", "clint", cwd=kerja); git("push", "-q", cwd=kerja)
        # Commit baru di origin docs dari clone lain: sync harus menariknya.
        git("clone", "-q", "-b", "main", os.path.join(self.d, "docs.git"), "docs2", cwd=self.d)
        p = os.path.join(self.d, "docs2")
        open(os.path.join(p, "b.txt"), "w").write("2")
        git("add", ".", cwd=p); git("commit", "-q", "-m", "prd baru", cwd=p); git("push", "-q", cwd=p)

    def tearDown(self):
        shutil.rmtree(self.d)

    def jalan(self):
        return subprocess.run(["bash", os.path.join(SKRIP, "sync-repos.sh"), os.path.join(self.d, "kerja")],
                              capture_output=True, text=True).stdout

    def test_menarik_related_lalu_cache(self):
        out = self.jalan()
        self.assertIn("repo=docs status=terbaru", out)
        self.assertIn("repo=kerja status=terbaru", out)
        self.assertTrue(os.path.exists(os.path.join(self.d, "docs", "b.txt")))
        os.remove(os.path.join(self.d, "docs", "b.txt"))      # dari cache: tidak menyentuh repo lagi
        self.assertEqual(self.jalan(), out)
        self.assertFalse(os.path.exists(os.path.join(self.d, "docs", "b.txt")))

    def test_working_tree_kotor_hanya_fetch(self):
        open(os.path.join(self.d, "docs", "catatan.md"), "w").write("draf")
        out = self.jalan()
        self.assertIn("repo=docs status=fetch-saja alasan=working-tree-kotor", out)
        self.assertFalse(os.path.exists(os.path.join(self.d, "docs", "b.txt")))


if __name__ == "__main__":
    unittest.main()
