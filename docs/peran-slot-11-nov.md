# Penetapan Peran Slot Meja Uji (11 Nov 2026) dan Kesiapan Partisipan

Dokumen ini disusun untuk memenuhi kelengkapan tugas **#2 (Peran slot meja 11 Nov dan partisipan)** pada proyek Capstone Deep Learning: Ruang Cerdas 5 Volt.

* **Tim**: 12
* **Kasus**: Perintah suara pengendali meja (10 kata)
* **Pilar**: Suara
* **Pembimbing**: Ardika Satria
* **Jadwal Slot Meja**: Rabu, 11 November 2026, pukul 08.00–09.00 WIB
* **Tempat**: Meja Uji Ruang Cerdas 5V, Lab Sains Data ITERA

---

## 1. Pembagian Peran Anggota Tim (Slot Meja)

Mengacu pada Buku Panduan Metode Eksperimen Lapangan Bagian 4, seluruh 5 anggota tim telah ditetapkan perannya masing-masing selama sesi slot meja berlangsung:

| Peran Slot | Anggota Bertugas | NIM | Tanggung Jawab Operasional di Meja |
|---|---|---|---|
| **Operator Perekam** | Ahmad Sahidin Akbar | 122450044 | Berada di laptop meja, menjalankan skrip `meja.py`, memastikan masukan audio 16 kHz aktif, dan menekan tombol *Enter* di awal setiap blok saat partisipan telah siap. |
| **Operator Alat** | Tanty Widiyastuti | 123450094 | Mengawasi aktuator kipas 5V di meja uji, memastikan tidak ada benda asing yang menghalangi kisi kipas, dan memastikan posisi fisik meja tetap sesuai foto acuan. |
| **Koordinator Partisipan** | Kharisma Mustika Sari | 123450034 | Menyambut partisipan, memastikan formulir persetujuan (*informed consent*) ditandatangani sebelum rekaman, dan mengarahkan partisipan duduk tepat di tanda selotip menghadap mikrofon. |
| **Pencatat Kejadian** | Nadya Ratu Anjani | 123450083 | Memegang lembar sesi fisik dan pulpen untuk mencatat setiap kondisi yang terganggu (misal: batuk, salah ucap kata, tawa, atau bunyi pintu/suara luar) beserta nomor kondisinya. |
| **Penjaga Suara & Bingkai** | Khazanatil Ilmi | 123450053 | Memastikan pintu ruangan lab tertutup rapat, ponsel seluruh orang dalam mode hening (*silent*), dan menjaga ruangan dalam keadaan hening total selama sesi rekam berlangsung. |

---

## 2. Kesiapan Partisipan Manusia (P01 – P06)

Rencana eksperimen tim (`rencana/t12-perintah-suara.yaml`) membutuhkan 6 orang partisipan berbeda yang membentuk 6 blok eksperimen:

1. **Sumber Partisipan**: Seluruh 6 orang partisipan berasal dari **luar anggota tim** (mahasiswa lintas kelompok / kawan sekelas) untuk menjamin objektivitas pengujian variasi vokal penutur baru.
2. **Jadwal Kehadiran**: Seluruh partisipan dijadwalkan hadir di lab pada pukul **07.50 WIB** (10 menit sebelum slot dimulai) untuk pengarahan singkat dan penandatanganan formulir persetujuan.
3. **Kerahasiaan Data (Privasi)**:
   * Sesuai ketentuan, daftar pasangan Nama Asli dan ID Samaran (`P01`, `P02`, `P03`, `P04`, `P05`, `P06`) disimpan terpisah di catatan pribadi Koordinator tim dan **tidak diunggah ke repositori GitHub**.
   * Di dalam lembar sesi, berkas rekaman, dan analisis hanya digunakan kode ID samaran tersebut.

---

## 3. Protokol Pelaksanaan Sesi Perekaman

* **Total Kondisi**: 360 kondisi (6 partisipan $\times$ 60 kondisi).
* **Rincian per Partisipan**: 10 kata target $\times$ 2 taraf bising kipas (0 dan 255) $\times$ 3 ulangan.
* **10 Kata Perintah**: `nyalakan`, `matikan`, `kipas`, `lampu`, `pompa`, `naik`, `turun`, `berhenti`, `ya`, `batal`.
* **Siklus per Kondisi**:
  1. Layar menampilkan kata selama 2,5 detik $\rightarrow$ Partisipan mengucapkan kata tepat satu kali secara jelas dengan intonasi wajar.
  2. Kipas meja otomatis menyala (PWM 255) atau mati (PWM 0) sebagai variasi bising latar.
  3. Jeda hening 0,5 detik $\rightarrow$ Partisipan diam, layar menampilkan jeda.
* **Penanganan Gangguan**:
  * Sesi **tidak diulang di tempat** jika terjadi gangguan (batuk/salah kata) agar alur waktu dan konsistensi skrip terjaga.
  * Pencatat kejadian langsung menuliskan nomor kondisi terkait di lembar sesi fisik (misalnya: `[45/360] - Batuk pada kata 'naik'`). Data kondisi tersebut nantinya akan dikeluarkan saat pemotongan jendela audio.

---

## 4. Lembar Kerja Fisik (Tercetak)

Sebelum slot berlangsung, Koordinator menyiapkan 2 dokumen fisik:
1. **Formulir Persetujuan Partisipan (*Informed Consent*)**: Lembar pernyataan kesediaan direkam suaranya untuk keperluan penelitian akademik Capstone Deep Learning ITERA.
2. **Lembar Sesi Fisik**: Tabel pencatatan manual untuk diisi oleh Pencatat Kejadian selama 360 kondisi berjalan.

Dokumen lembar sesi fisik yang telah diisi saat slot meja akan difoto setelah sesi selesai dan dijadikan bukti autentik saat pemeriksaan keaslian data oleh pembimbing.
