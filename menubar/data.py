#!/usr/bin/env -S PATH=/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin python3
"""Data menu bar clint dalam JSON, dibaca aplikasi menubar (ClintBar) setiap beberapa detik. Membaca file lokal
saja, tanpa jaringan dan tanpa token: ~/Library/Logs/clint/terakhir.json (laporan), kerja/<sid>.json (kemajuan
develop per sesi), ~/.config/clint/sesi/ (sesi Claude Code). Juga menjalankan sapaan pagi dan cek status MR."""
import datetime, json, os, re, subprocess, sys, time

HOME = os.path.expanduser("~")
ROOT = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
LOG = os.path.join(HOME, "Library/Logs/clint")
CFG = os.path.join(HOME, ".config/clint")


def sapa():
    j = datetime.datetime.now().hour
    return "Selamat pagi" if j < 11 else "Selamat siang" if j < 15 else "Selamat sore" if j < 18 else "Selamat malam"


def durasi(dt):
    m = int(dt // 60)
    return "baru saja" if m < 1 else f"{m} mnt" if m < 60 else f"{m // 60} j {m % 60} mnt"


def nama_proyek(d):
    base, induk = os.path.basename(d), os.path.basename(os.path.dirname(d))
    return f"{induk} · {base}" if len(base) < 12 and induk not in ("Desktop", "Documents", os.path.basename(HOME)) else base


def giliran_selesai(path):
    """True bila baris bermakna terakhir transkrip menunjukkan jawaban sudah tuntas (end_turn atau
    ringkasan hook Stop). Pengaman bila hook status tidak tercatat dengan benar."""
    try:
        with open(path, "rb") as fh:
            fh.seek(0, 2); fh.seek(max(0, fh.tell() - 65536))
            baris = fh.read().decode("utf-8", "ignore").splitlines()[1:]
    except (OSError, TypeError):
        return False
    for b in reversed(baris):
        try:
            r = json.loads(b)
        except ValueError:
            continue
        t = r.get("type")
        if t == "system" and r.get("subtype") == "stop_hook_summary":
            return True
        if t == "assistant":
            return (r.get("message") or {}).get("stop_reason") == "end_turn"
        if t == "user":
            return False
    return False


def baca():
    lap, waktu = None, None
    p = os.path.join(LOG, "terakhir.json")
    if os.path.exists(p):
        try:
            lap = json.load(open(p, encoding="utf-8"))
            # Waktu laporan DIBUAT, bukan waktu file terakhir disentuh (pengecekan MR / tandai selesai).
            waktu = kapan(lap.get("_dibuat") or os.path.getmtime(p))
        except Exception:
            lap = None
    return lap, waktu, baca_kerja(), baca_sesi()


def kapan(ts):
    t = datetime.datetime.fromtimestamp(ts)
    selisih = (datetime.date.today() - t.date()).days
    return t.strftime("%H.%M") if selisih == 0 else t.strftime("kemarin %H.%M") if selisih == 1 else t.strftime("%d/%m %H.%M")


def hidup(path):
    """Klaim kerja/<sid>.json hidup bila < 3 jam dan sesinya masih ada; cek-<pid>.json bila prosesnya masih jalan."""
    if time.time() - os.path.getmtime(path) >= 3 * 3600:
        return False
    nama = os.path.basename(path)[:-5]
    if nama.startswith("cek-"):
        try:
            os.kill(int(nama[4:]), 0); return True
        except (ValueError, OSError):
            return False
    return os.path.exists(os.path.join(CFG, "sesi", nama + ".json"))


def baca_kerja():
    """Semua kemajuan kerja yang hidup: klaim per sesi (kerja/<sid>.json) dan cek-<pid>.json."""
    kerja, kd = [], os.path.join(LOG, "kerja")
    fs = [os.path.join(kd, f) for f in sorted(os.listdir(kd)) if f.endswith(".json")] if os.path.isdir(kd) else []
    for k in fs:
        try:
            if hidup(k):
                kerja.append(dict(json.load(open(k, encoding="utf-8")), _sid=os.path.basename(k)[:-5]))
        except Exception:
            pass
    return kerja


tugas_selesai = set()


def baca_sesi():
    sesi, sd = [], os.path.join(CFG, "sesi")
    tugas_selesai.clear()
    for fn in (os.listdir(sd) if os.path.isdir(sd) else []):
        try:
            f = os.path.join(sd, fn); x = json.load(open(f, encoding="utf-8")); umur = time.time() - os.path.getmtime(f)
        except Exception:
            continue
        x["_sid"] = fn[:-5]
        st = x.get("status")
        if st == "latar":               # format lama; kini Stop selalu menulis "selesai"
            st = x["status"] = "selesai"
        if st == "bekerja" and giliran_selesai(x.get("transkrip")):
            st = x["status"] = "selesai"
        # "menunggu" dicatat hook Notification (izin/pertanyaan). Transkrip yang bertambah sesudahnya berarti
        # sudah dijawab dan sesi bekerja lagi, juga bila hook versi lama belum mengembalikan statusnya.
        if st == "menunggu":
            try:
                if os.path.getmtime(x.get("transkrip") or "") > (x.get("update") or 0) + 5:
                    st = x["status"] = "bekerja"
            except OSError:
                pass
        if st == "selesai" and x.get("agents") and umur < 1800:
            st = x["status"] = "latar"   # turn selesai, tapi agent latar masih berjalan
        # Esc/interupsi tidak memicu hook Stop: status bisa tertahan "bekerja". Pakai aktivitas terakhir
        # (hook atau transkrip). > 10 mnt tanpa aktivitas dan tanpa agent jalan → dianggap diam.
        if st in ("bekerja", "latar"):
            akt = umur
            try:
                akt = min(akt, time.time() - os.path.getmtime(x.get("transkrip") or ""))
            except OSError:
                pass
            if akt > 600 and not x.get("agents"):
                x["status"], st, x["diam"] = "diam", "diam", akt
        if st == "selesai" and x.get("tugas") and umur < 12 * 3600:
            tugas_selesai.add(x["tugas"])
        if (st in ("bekerja", "latar") and umur < 3 * 3600) or (st == "menunggu" and umur < 3600) \
                or (st in ("selesai", "diam") and umur < 1800 if st == "diam" else st == "selesai" and umur < 600):
            x["umur"] = umur; sesi.append(x)
    sesi.sort(key=lambda x: x.get("mulai", 0))
    return sesi


def proyek_aktif():
    """Hasil active-projects.sh disimpan 5 menit: find di ~/.claude/projects lambat bila dipanggil tiap render."""
    cache = os.path.join(CFG, "proyek-aktif.txt")
    try:
        if time.time() - os.path.getmtime(cache) < 300:
            return [x for x in open(cache, encoding="utf-8").read().split("\n") if x.strip()]
    except OSError:
        pass
    try:
        out = subprocess.run(["bash", os.path.join(ROOT, "scripts/active-projects.sh"), "3"],
                             capture_output=True, text=True, timeout=10).stdout
        open(cache, "w", encoding="utf-8").write(out)
    except Exception:
        out = ""
    return [x for x in out.split("\n") if x.strip()]


def tugas_pendek(t):
    return re.sub(r"^/clint:\w+\s+", "", t or "").strip()


def sapaan_cfg():
    try:
        c = json.load(open(os.path.join(CFG, "sapaan.json"), encoding="utf-8"))
    except Exception:
        c = {}
    return {"aktif": c.get("aktif", True), "jam": int(c.get("jam", 8)), "menit": int(c.get("menit", 0)),
            "sampai": int(c.get("sampai", 13))}


def sapaan_pagi():
    """Jadwal sapaan pagi dijalankan dari sini (aplikasi menu bar punya izin folder Desktop; launchd tidak).
    Senin–Jumat, mulai jam yang diatur sampai sebelum jam `sampai`, sekali per hari. Laptop tidur →
    jalan saat bangun selama masih di rentang itu."""
    c = sapaan_cfg(); now = datetime.datetime.now()
    if not c["aktif"] or now.weekday() > 4 or (now.hour, now.minute) < (c["jam"], c["menit"]) or now.hour >= c["sampai"]:
        return
    tanda_hari = os.path.join(CFG, f"sapaan-{now:%Y-%m-%d}")
    if os.path.exists(tanda_hari):
        return
    for f in os.listdir(CFG):            # bersihkan penanda hari lain
        if f.startswith("sapaan-20") and f != os.path.basename(tanda_hari):
            os.remove(os.path.join(CFG, f))
    open(tanda_hari, "w").close()
    subprocess.Popen(["bash", os.path.join(ROOT, "scripts/morning-greeting.sh")],
                     stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, start_new_session=True)

def ribu(n):
    return f"{n / 1000:.1f}k" if n >= 1000 else str(n)


def detik(ts):
    return datetime.datetime.fromisoformat(ts.replace("Z", "+00:00")).timestamp()


def lama(dt):
    return f"{int(dt // 3600)}j {int(dt % 3600 // 60)}m" if dt >= 3600 else f"{int(dt // 60)}m {int(dt % 60):02d}s"


def token_terakhir(baris):
    """Token konteks dari usage pesan assistant terakhir (input + cache + output), seperti Agent map."""
    for b in reversed(baris):
        if '"usage"' not in b:
            continue
        try:
            u = (json.loads(b).get("message") or {}).get("usage")
        except ValueError:
            continue
        if u:
            return sum(u.get(k) or 0 for k in ("input_tokens", "cache_read_input_tokens",
                                                "cache_creation_input_tokens", "output_tokens"))
    return 0


def nama_model(m):
    x = re.match(r"claude-([a-z]+)-(\d+)-(\d+)", m or "")
    return f"{x.group(1).title()} {x.group(2)}.{x.group(3)}" if x else (m or "")


def rincian_agent(transkrip):
    """Sesi utama dan semua agent sebuah sesi, seperti Agent map di Claude Code. Sumbernya file lokal Claude Code:
    transkrip utama (model, token konteks, <task-notification> saat agent latar selesai beserta token dan
    durasinya) dan subagents/agent-<id>.{meta.json,jsonl}. Catatan hook tidak dipakai di sini karena SubagentStop
    tidak selalu terpanggil untuk agent latar. Tanpa token."""
    try:
        teks = open(transkrip, encoding="utf-8", errors="ignore").read()
    except (OSError, TypeError):
        return None, []
    ekor = teks[-262144:].splitlines()[1:]
    model = next((json.loads(b)["message"].get("model") for b in reversed(ekor)
                  if '"type":"assistant"' in b and '"model"' in b), "")
    konteks = token_terakhir(ekor)
    utama = {"model": nama_model(model), "token": ribu(konteks), "besar": konteks > 150000}
    selesai = {}
    for blok in re.findall(r"<task-notification>.*?</task-notification>", teks):
        aid = re.search(r"<task-id>(\w+)</task-id>", blok)
        if aid:
            angka = [re.search(rf"<{t}>(\d+)</{t}>", blok) for t in ("subagent_tokens", "duration_ms")]
            selesai[aid.group(1)] = tuple(x.group(1) if x else None for x in angka)
    hasil, folder = [], os.path.join(transkrip[:-6], "subagents")
    for fn in (os.listdir(folder) if os.path.isdir(folder) else []):
        if not fn.endswith(".meta.json"):
            continue
        aid, dasar = fn[6:-10], os.path.join(folder, fn[:-10])
        try:
            meta = json.load(open(dasar + ".meta.json", encoding="utf-8"))
            with open(dasar + ".jsonl", encoding="utf-8", errors="ignore") as fh:
                pertama = json.loads(fh.readline())
                fh.seek(0, 2); fh.seek(max(0, fh.tell() - 65536))
                baris = fh.read().splitlines()[1:]
        except (OSError, ValueError):
            continue
        mulai = detik(pertama.get("timestamp"))
        if meta.get("requestShape") == "background":
            jalan = aid not in selesai
        else:                              # agent biasa selesai saat hasil tool-nya masuk ke transkrip utama
            jalan = f'"tool_use_id":"{meta.get("toolUseId")}"' not in teks
        tok, ms = selesai.get(aid, (None, None))
        if jalan:
            dt, token = time.time() - mulai, token_terakhir(baris)
        else:
            akhir = next((json.loads(b).get("timestamp") for b in reversed(baris) if '"timestamp"' in b), None)
            dt = int(ms) / 1000 if ms else (detik(akhir) - mulai if akhir else 0)
            token = int(tok) if tok else token_terakhir(baris)
        hasil.append({"deskripsi": meta.get("description") or "", "tipe": (meta.get("agentType") or "").split(":")[-1],
                      "jalan": jalan, "lama": lama(dt), "token": ribu(token) if token else "", "_mulai": mulai})
    hasil.sort(key=lambda a: (not a["jalan"], -a["_mulai"]))
    for a in hasil:
        del a["_mulai"]
    return utama, hasil


def data():
    lap, waktu, semua_kerja, sesi = baca()
    L = lambda key: (lap or {}).get(key) or []
    gagal, kerjakan = L("gagal"), L("kerjakan")
    klaim = {k["_sid"]: k for k in semua_kerja}
    for x in sesi:
        x["_utama"], x["_agents"] = rincian_agent(x.get("transkrip"))
        if x["status"] == "latar" and not any(a["jalan"] for a in x["_agents"]):
            x["status"] = "selesai"
    sesi = [x for x in sesi if x["status"] != "selesai" or x["umur"] < 600]
    aktif = [x for x in sesi if x["status"] in ("bekerja", "latar")]
    cek_jalan = [k for k in semua_kerja if k["_sid"].startswith("cek-")]
    bekerja = bool(aktif or cek_jalan)
    # Perintah yang sedang dipegang sesi (tugas yang diketik, atau `perintah` di klaimnya): butir laporan yang sama
    # tampil di baris sesi itu, bukan di "Perlu dikerjakan". Butir yang tugasnya baru selesai diberi tanda ✓.
    dipegang = {p for x in sesi if x["status"] in ("bekerja", "latar", "menunggu")
                for p in (x.get("tugas"), (klaim.get(x["_sid"]) or {}).get("perintah")) if p}
    sama = lambda cmd, ps: bool(cmd) and any(cmd[:90] == p[:90] for p in ps)
    gagal, kerjakan = [[x for x in xs if not sama(x.get("perintah"), dipegang)] for xs in (gagal, kerjakan)]
    # Satu butir paling mendesak per project (yang gagal lebih dulu). Rincian lain ada di laporan HTML.
    urgen = {}
    for x in gagal + kerjakan:
        urgen.setdefault(x.get("proyek") or "", dict(x, jenis="gagal" if x in gagal else "kerjakan"))
    for x in urgen.values():
        if sama(x.get("perintah"), tugas_selesai):
            x["jenis"] = "tadi"

    if bekerja:
        n = len(aktif) + len(cek_jalan)
        tahap = next((x["tahap"].split(" · ")[0] for x in aktif if x.get("tahap")), "" if aktif else "cek")
        status, label = "bekerja", f"{n} · {tahap or 'bekerja'}"
        kepala = {"judul": "clint", "sub": f"{n} berjalan"}
    elif gagal:
        status, label = "gagal", "!"
        kepala = {"judul": sapa(), "sub": f"cek terakhir {waktu}", "gagal": gagal[0].get("teks") or ""}
    elif lap is None:
        status, label = "kosong", ""
        kepala = {"judul": sapa(), "sub": "Belum ada laporan"}
    else:
        status, label = ("ada", str(len(urgen))) if urgen else ("aman", "✓")
        kepala = {"judul": sapa(), "sub": f"cek terakhir {waktu}"}

    daftar = []
    for x in sesi:
        st, cwd, k = x["status"], x.get("cwd", ""), klaim.get(x["_sid"]) or {}
        ekor = {"bekerja": durasi(time.time() - x.get("mulai", time.time())), "latar": "di latar",
                "menunggu": "perlu jawaban",
                "selesai": "baru saja selesai" if x["umur"] < 60 else f"selesai {durasi(x['umur'])} lalu",
                "diam": f"diam {durasi(x.get('diam', 0))}"}[st]
        daftar.append({
            "status": st, "nama": k.get("judul") or tugas_pendek(x.get("tugas")) or "sesi",
            "proyek": nama_proyek(cwd), "buka": k.get("path") or cwd, "ekor": ekor,
            "langkah": x.get("langkah") if isinstance(x.get("langkah"), int) else None,
            "pr": f"PR {k['pr']}/{k['total']}" if k.get("pr") and k.get("total") and k["total"] > 1 else "",
            "agent": ", ".join(sorted({a["tipe"] for a in x["_agents"] if a["jalan"]})) or x.get("tahap") or "",
            "utama": x["_utama"], "agents": [a for a in x["_agents"] if a["jalan"]],
        })

    sp = sapaan_cfg()
    return {
        "status": status, "label": label, "kepala": kepala,
        "cek": [{"judul": k.get("judul") or "Cek project", "mulai": k.get("mulai", ""), "tahap": k.get("tahap", "")}
                for k in cek_jalan],
        "sesi": daftar,
        "urgen": [{"proyek": p, "teks": x.get("teks") or "", "jenis": x["jenis"]} for p, x in urgen.items()],
        "proyek_aktif": [{"nama": nama_proyek(d), "dir": d} for d in proyek_aktif()],
        "pengaturan": {"suara": not os.path.exists(os.path.join(CFG, "diam")),
                       "bisu": os.path.exists(os.path.join(CFG, "bisu-sampai")),
                       "sapaan": sp["aktif"], "sapaan_jam": f"{sp['jam']:02d}.{sp['menit']:02d}"},
        "laporan_ada": lap is not None,
    }


def periksa_mr():
    """Status MR dicek tiap 5 menit di latar (dan setiap giliran sesi selesai lewat hook Stop), via glab/gh."""
    cap = os.path.join(CFG, "mr-dicek")
    if os.path.exists(os.path.join(LOG, "terakhir.json")) and \
            (not os.path.exists(cap) or time.time() - os.path.getmtime(cap) > 300):
        open(cap, "w").close()
        subprocess.Popen(["python3", os.path.join(ROOT, "scripts/update-report.py"), "periksa-mr"],
                         stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, start_new_session=True)


if __name__ == "__main__":
    for tugas in (sapaan_pagi, periksa_mr):
        try:
            tugas()
        except Exception:
            pass
    json.dump(data(), sys.stdout, ensure_ascii=False)
