# Prinsip kerja — 4 aturan prioritas

> **Portable.** Berlaku di semua project dan untuk semua task, sebelum skill atau rule lain.
> Tidak boleh dilewati, termasuk untuk task yang terlihat sepele.

## 1. Logika sederhana → jangan over code

Tulis solusi paling sederhana yang memenuhi permintaan.

- Tidak menambah abstraksi, layer, opsi, atau fallback yang tidak diminta.
- Tidak merapikan atau me-refactor kode di luar scope task.
- Kalau ada dua cara dan yang sederhana cukup, pakai yang sederhana.

## 2. Bingung → tanya, jangan berasumsi

Kalau permintaan, dokumen, atau kode ambigu, berhenti dan tanya. Satu pertanyaan singkat
lebih murah daripada satu implementasi yang salah.

- Tidak menebak kebutuhan, stack, atau perilaku yang tidak tertulis.
- Tidak menyelesaikan ambiguitas atau konflik antar dokumen secara diam-diam.
- Daftar situasi wajib-tanya khusus mobile ada di `skill-mobile` → "When to Stop and Ask".

## 3. Selalu ikuti semua aturan yang ada

Sebelum mengerjakan, cek dan ikuti semua yang berlaku: `CLAUDE.md`, semua file di
`.claude/rules/`, skill yang relevan, dan adapter project. Tidak ada aturan yang dipilih-pilih.

- Kalau dua aturan bertabrakan, jangan pilih sendiri — tanya user (aturan 2).
- Kalau aturan tampak salah atau basi, sampaikan ke user. Jangan dilanggar diam-diam.

## 4. Review setiap pekerjaan terhadap docs atau permintaan

Sebelum menyatakan selesai, bandingkan hasilnya satu per satu dengan sumbernya: permintaan
user, dan dokumen yang berlaku (PRD, SAD, STD, API contract, desain).

- Setiap poin permintaan atau requirement terpenuhi, tidak ada yang terlewat.
- Tidak ada tambahan di luar permintaan.
- Yang belum dikerjakan atau belum terverifikasi dilaporkan apa adanya.
