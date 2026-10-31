# Catatan Model 123450034 — Kharisma Mustika Sari

**Jalur Model**: Transfer Learning / Fine-Tuning (Modul 06)  
**Kasus**: Klasifikasi 10 Perintah Suara Pengendali Meja (Log-mel 64 pita, 1 detik)  
**Tugas Sampingan**: Penjaga Data & Evaluasi

## Alasan Optimizer
- Menggunakan **AdamW** dengan learning rate rendah ($5 \times 10^{-4}$) dan penalti weight decay $1 \times 10^{-4}$.
- Alasan: Pada skema transfer learning, penggunaan learning rate yang terlalu besar berisiko merusak bobot representasi awal (*catastrophic forgetting*). AdamW menjaga stabilitas bobot pretrained sekaligus mempercepat konvergensi pada layer klasifikasi baru.

## Regularisasi
- Pemanfaatan Batch Normalization bawaan backbone untuk menjaga distribusi aktivasi.
- Dropout sebesar 0.3 pada layer classifier head sebelum proyeksi ke 10 kelas output.
- Weight decay pada pembaruan bobot untuk mencegah overfitting pada dataset suara meja yang terbatas.

## Pencarian Hyperparameter (Tabel)
*(Akan dieksplorasi pada Sprint 1: perbandingan unfreezing 2 blok teratas vs freeze seluruh backbone, serta learning rate 1e-3 vs 5e-4 vs 1e-4)*

| Percobaan | Strategi Backbone | Learning Rate | Batch Size | Val Acc | Val Macro-F1 |
|---|---|---|---|---|---|
| Init Sprint 0 | Feature Extraction | 5e-4 | 32 | - | - |

## Ablation (>= 2)
*(Akan diuji pada Sprint 2)*:
1. Variasi jumlah layer yang di-unfreeze (hanya classifier vs classifier + blok konvolusi terakhir).
2. Perbandingan input 1-channel replikasi 3-channel vs adaptasi conv layer pertama.

## Hasil 3 Seed Konfigurasi Akhir
*(Akan dilengkapi pada Sprint 2 dengan seed 1, 2, 3)*
