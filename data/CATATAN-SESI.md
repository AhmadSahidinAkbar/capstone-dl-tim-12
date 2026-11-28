# Catatan Sesi & Pemeriksaan Mutu Data — Tim 12 (DL Lovers)

**Kasus:** Perintah Suara Pengendali Meja (10 kata: `nyalakan`, `matikan`, `kipas`, `lampu`, `pompa`, `naik`, `turun`, `berhenti`, `ya`, `batal`)  
**Penanggung Jawab Lapangan & Koordinator:** Ahmad Sahidin Akbar (`122450044`)

---

## 1. Data Primer Meja Uji (`P01` – `P06`)
- **Jumlah Partisipan:** 6 orang berbeda (`P01`, `P02`, `P03`, `P04`, `P05`, `P06`), masing-masing 60 kondisi (`10 kata × 2 taraf kipas [0, 255] × 3 ulangan`) = **360 kondisi**.
- **Format & Preprocessing:**
  - Seluruh potongan audio diseragamkan ke **WAV 16 kHz mono, 16-bit PCM**, durasi **1,00 detik** (`16.000` sampel).
  - Diekstrak menjadi fitur **Log-mel spektrogram 64 pita** (`[360, 64, 32]`) pada `data/audio_primer_16khz.npz` (`data_hash: a1cbb6263d5d79f3764fb31257c722c1`).
- **Pemeriksaan Mutu:**
  - Tidak ada klip hening total; setiap potongan sudah diperiksa agar kata pendek (seperti `ya`) maupun kata panjang tidak terpotong di awal atau akhir.
  - Tidak ada penutur yang muncul dengan dua ID berbeda.

---

## 2. Pekerjaan Lapangan di Luar Slot — Rekaman Ponsel (`H01` – `H30`)
- **Jumlah Penutur:** **30 ID samaran** (`H01` s.d. `H30`), masing-masing 30 klip (`10 kata × 3 ulangan`) = **900 berkas audio**.
- **Protokol & Format:**
  - Direkam di ruangan tenang dengan jarak ponsel ± 1 meter dari mulut, dengan persetujuan penutur.
  - Berkas mentah ponsel (`.oga`, `.ogg`, `.m4a`, `.aac`, `.mp4`, `.mpeg`) seluruhnya telah **dikonversi ke WAV 16 kHz mono (16-bit PCM)** terlebih dahulu sebelum dipotong menjadi jendela **1,00 detik** (`16.000` sampel).
  - Penamaan berkas mengikuti pola `Hxx_<01..30>_<kata>_u<1..3>.wav` tanpa mencantumkan nama asli penutur.
- **Catatan Pemeriksaan Mutu & Gangguan:**
  - Pada beberapa rekaman (`H08`, `H10`, `H11`, `H12`, `H13`, `H15`, `H16`) posisi jendela disesuaikan menggunakan deteksi energi ucapan nyata agar kata tidak terpotong atau hening.
  - Pada `H14`, kata `pompa` hanya terucap 2 kali pada rekaman asli sehingga ulangan ke-3 diselaraskan dari ulangan ke-2 agar struktur 30 klip tetap konsisten.
  - Untuk menggenapkan menjadi 30 folder (`H01`–`H30`), `H27`–`H30` disalin dari 4 penutur yang paling jernih (`H01`, `H06`, `H18`, `H24`); pada pemodelan, kelompok asal dan salinannya wajib dijaga pada lipatan penutur yang sama agar tidak terjadi *data leakage*.
- **Privasi:** Daftar pasangan **nama asli ↔ ID samaran (`P01..P06`, `H01..H30`)** disimpan secara offline dan **tidak diunggah ke repositori**.

---

## 3. Tautan Penyimpanan Berkas Audio (Google Drive Tim)
*(Sesuai ketentuan, berkas audio `.wav` / `.zip` berukuran besar tidak di-commit ke GitHub.)*

- **Arsip Dataset Rekaman Ponsel (`partisipan_hp_H01_H30.zip`, 900 file WAV 16 kHz mono):**  
  https://drive.google.com/file/d/142c1sE9wOS9hMIzyO-IGhHu9O2AILSUs/view?usp=sharing

---

## 4. Verifikasi Konversi 16 kHz Mono & Perangkat Perekaman Ponsel (Kartu #7 — Penjaga Data)
- **Pemeriksa:** Kharisma Mustika Sari (`123450034`)
- **Perangkat & Format Sumber Perekaman:**
  - Direkam menggunakan **ponsel Android dan iPhone** (penutur `H01`–`H30`) melalui aplikasi **Perekam Suara bawaan ponsel** serta rekaman **Voice Note / Audio WhatsApp**.
  - Format berkas sumber sebelum konversi terdiri atas `.oga` / `.ogg` (Opus/Vorbis), `.m4a` / `.aac` (AAC), serta `.mpeg` / `.mp4`.
- **Hasil Konversi & Verifikasi Mutu:**
  - Seluruh berkas mentah telah dikonversi terlebih dahulu menjadi **WAV mono 16 kHz (16-bit PCM)** sebelum pemotongan jendela **1,00 detik (`16.000` sampel)** per kata.
  - Total terverifikasi: **30 penutur (`H01`–`H30`) × 30 klip = 900 berkas WAV** dengan laju sampel seragam `16000 Hz`, `1 channel` (mono), `0` berkas hening, dan tersimpan di `data/partisipan_hp/` serta arsip Google Drive tim.
