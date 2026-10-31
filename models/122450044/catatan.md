# Catatan Model 122450044 — Ahmad Sahidin Akbar

**Jalur Model**: CNN dari Nol (Modul 05)  
**Kasus**: Klasifikasi 10 Perintah Suara Pengendali Meja (Log-mel 64 pita, 1 detik)

## Alasan Optimizer
- Direncanakan menggunakan **Adam** atau **AdamW** dengan learning rate awal $1 \times 10^{-3}$, dengan alternatif SGD + momentum jika terjadi overfitting pada representasi spektrogram.

## Regularisasi
- Batch Normalization setelah layer konvolusi.
- Dropout (0.2 – 0.3) sebelum layer Fully Connected.
- Nilai dropout awal ditetapkan sebesar 0.3 pada layer classifier sebelum output 10 kelas.
- Weight decay (L2 regularization) pada optimizer.

## Pencarian Hyperparameter (Tabel)
*(Akan dilengkapi pada Sprint 1 & Sprint 2)*

## Ablation (>= 2)
*(Akan dilengkapi pada Sprint 2: variasi kernel size dan kedalaman layer konvolusi)*

## Hasil 3 Seed Konfigurasi Akhir
*(Akan dilengkapi pada Sprint 2 dengan seed 1, 2, 3)*