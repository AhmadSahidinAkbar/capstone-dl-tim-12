# Protokol evaluasi tim — Tim 12 (SmartDesk)

Diisi Penjaga Data & Evaluasi pada Sprint 0, digabung ke `main` lewat *pull request* yang
disetujui pembimbing, lalu **dibekukan**. Perubahan setelah itu hanya lewat *pull request*
baru yang disetujui pembimbing.

| Butir | Isi |
|---|---|
| Kasus (dari kartu Kasus tim) | Perintah suara pengendali meja (10 kata) |
| Sumber dataset | Rekaman data primer meja uji (mikrofon 16 kHz) & https://github.com/sains-data/capstone-dl-2026-starter |
| Jenis tugas (`TUGAS`) | klasifikasi |
| Target / label | 10 kata (`nyalakan`, `matikan`, `kipas`, `lampu`, `pompa`, `naik`, `turun`, `berhenti`, `ya`, `batal`) + diam/bising latar |
| Ukuran data latih / validasi / uji | 6 partisipan manual (P01–P06), 3 ulangan per kondisi, durasi 2.5 detik (1 detik awal dibuang) |
| Cara split | GroupKFold berbasis identitas penutur/partisipan (P01–P06) |
| Metrik utama untuk komparasi | macro-F1 dan akurasi per penutur |
| Praproses yang sama untuk semua model | Pemotongan 1 detik pertama tiap rekaman, ekstraksi Log-mel spektrogram 64 pita frekuensi (1 detik, 16 kHz), normalisasi dihitung hanya dari data latih (tanpa data leakage) |
| Anggaran komputasi per run | ≤ 20 menit CPU laptop |
| Evaluasi data uji | Sekali, oleh Penjaga Data & Evaluasi, pada sprint terakhir (`--final`) |
| `data_hash` saat dibekukan | `edb46995414bfa955cbcb6c65c28927e` |

Disetujui pembimbing pada: (Menunggu konfirmasi Pull Request pembimbing)
