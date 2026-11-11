# Catatan Pemeriksaan Mutu Data Sesi Meja (11 Nov) — Tim 12

**Penjaga Data**: Kharisma Mustika Sari (NIM: 123450034)  
**Kasus**: Pengendali Meja Cerdas Berbasis Suara (SmartDesk Voice Control)  
**Tanggal Verifikasi**: 11 November 2026

---

## 1. Identifikasi Sesi & Kondisi Data
- **Jumlah Partisipan**: 6 partisipan (P01 - P06).
- **Target Kelas**: 10 kata perintah suara (`maju`, `mundur`, `naik`, `turun`, `stop`, `buka`, `tutup`, `cepat`, `lambat`, `reset`).
- **Variasi Kondisi**: 2 taraf bising kipas (Kipas Off / Low & Kipas High) × 3 ulangan per kondisi.
- **Total Kondisi Terverifikasi**: $6 \text{ partisipan} \times 10 \text{ kata} \times 2 \text{ taraf} \times 3 \text{ ulangan} = 360 \text{ kondisi}$ (Lengkap 100%, selisih 0).

---

## 2. Hasil Pemeriksaan Mutu (Quality Control)
1. **Pemeriksaan Energi & Pemotong Audio**:
   - Sampel kata pendek (seperti `stop`, `naik`) telah diverifikasi menggunakan `src/common/pemotong.py`. 
   - Hasil pemotongan jendela berbasis energi tidak memotong bagian fonem awal maupun akhir kata.
2. **Pemeriksaan Identitas Penutur**:
   - Seluruh ID penutur unik (P01 hingga P06). Tidak ditemukan penutur ganda atau penamaan ID ganda.
3. **Pemeriksaan Konsistensi Manifest**:
   - Berkas `data/MANIFEST.json` telah dikonfigurasi untuk merujuk pada dataset `data/audio_primer_16khz.npz`.
   - `data_hash` seragam untuk seluruh anggota Tim 12.
