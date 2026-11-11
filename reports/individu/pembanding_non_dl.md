# Laporan Model Pembanding Non-Deep Learning (Kartu #10)

**Tim**: 12 — Ruang Cerdas 5 Volt (Perintah Suara 10 Kata)  
**Penanggung Jawab**: Nadya Ratu Anjani (123450083) — Analis Utama  
**Metode**: Ekstraksi Rata-rata dan Simpangan Baku Koefisien Frekuensi Log-mel/MFCC + Random Forest & SVM  
**Tanggal Pengujian**: 11 November 2026 (Data Simulasi Tim)

---

## 1. Metodologi Ekstraksi Fitur Non-DL
Model deep learning menerima representasi spektrogram Log-mel berdimensi `[64, Waktu]`. Untuk pembanding non-DL:
1. **Rata-rata Temporal (64 fitur)**: Merangkum sebaran energi spektral rata-rata di tiap pita frekuensi.
2. **Simpangan Baku Temporal (64 fitur)**: Menangkap variabilitas dinamika perubahan energi saat kata diucapkan.
3. Total vektor fitur representasi per ucapan adalah **128 fitur**.

---

## 2. Tabel Performa Pembanding pada Data Validasi
| Algoritma Pembanding | Parameter Utama | Val Accuracy | Val Macro-F1 | Waktu Pelatihan |
|---|---|---|---|---|
| **Random Forest** | `n_estimators=100`, max_depth=None | 0.1111 (11.1%) | 0.1167 | < 1 detik |
| **SVM (RBF Kernel)** | `C=1.0`, `gamma='scale'`, StandardScaler | 0.0556 (5.6%) | 0.0286 | < 1 detik |

---

## 3. Catatan Batas Bawah (*Baseline Threshold*) untuk Tim
- Nilai performa pembanding non-DL terbaik saat ini adalah **Macro-F1 0.1167** (Random Forest).
- Nilai ini menjadi batas bawah (*benchmark*) yang wajib dilampaui oleh kelima arsitektur Deep Learning tim (CNN, TL, RNN, Transformer, AE) ketika dilatih menggunakan data primer meja uji.
