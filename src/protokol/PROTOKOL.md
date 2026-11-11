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

---

## Modul Pemotong Jendela Audio (Kartu #4)

Sesuai rancangan kasus tim, setiap kondisi rekaman meja berdurasi 2,5 detik (16 kHz). Sebelum diubah menjadi spektrogram Log-mel 64 pita, audio harus dipotong menjadi jendela tepat 1,0 detik (16.000 sampel).

### Letak Berkas
Fungsi pemotong diletakkan di:
`src/common/pemotong.py`

### Alur Pemotongan
1. **Pembuangan Awal**: Membuang 1,0 detik pertama rekaman (16.000 sampel) untuk mengeliminasi gangguan transisi alat/relay dan suara klik awal.
2. **Deteksi Ucapan Berbasis Energi**: Menggunakan *Short-Time Energy* (frame 25 ms, hop 10 ms) pada sisa sinyal (1,5 detik) untuk mendeteksi posisi energi tertinggi ucapan kata target.
3. **Penjendelaan 1 Detik**: Mengambil interval 1,0 detik di sekitar ucapan. Kata pendek seperti *"ya"* dijamin tidak terpotong karena jendela dipusatkan di sekitar puncak energi.
4. **Padding Otomatis**: Jika durasi sinyal kurang dari 1,0 detik, dilakukan *zero-padding* otomatis pada akhir sinyal.

### Contoh Pemanggilan Kode
```python
from src.common.pemotong import potong_jendela_audio, potong_batch

# Untuk sinyal tunggal 1D (misal dari berkas rekaman kondisi)
sinyal_1detik = potong_jendela_audio(sinyal_mentah, sr=16000, durasi_buang_awal=1.0, durasi_jendela=1.0)
assert len(sinyal_1detik) == 16000

# Untuk pemrosesan batch banyak rekaman
matriks_audio = potong_batch(daftar_sinyal, sr=16000)  # output: [N, 16000]
```
