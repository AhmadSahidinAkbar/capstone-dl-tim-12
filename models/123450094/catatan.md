# Catatan Model 123450094 — Tanty Widiyastuti

**Jalur Model**: Autoencoder Representasi untuk Klasifikasi/Anomali  
**Kasus**: Klasifikasi 10 Perintah Suara Pengendali Meja (Log-mel 64 pita, 1 detik)  
**Tugas Sampingan**: Reproduksi & Demo

## Alasan Optimizer
- Menggunakan **Adam** dengan learning rate $1 \times 10^{-3}$ dan penalti bobot weight decay $1 \times 10^{-4}$.
- Alasan: Kompresi representasi fitur laten melalui convolutional bottleneck membutuhkan optimizer dengan momen adaptif yang cepat menemukan manifold data berdimensi rendah tanpa terjebak pada plateaus konvergensi awal.

## Regularisasi
- Batch Normalization pada setiap blok konvolusi encoder untuk menstabilkan pemadatan representasi fitur.
- Dropout sebesar 0.3 pada lapisan classifier head untuk mencegah memorisasi berlebih atas ruang laten.
- Weight decay untuk membatasi magnitudo bobot proyeksi laten.

## Pencarian Hyperparameter (Tabel)
*(Akan dieksplorasi pada Sprint 1: variasi dimensi ruang laten 32 vs 64 vs 128, perbandingan fungsi aktivasi ReLU vs LeakyReLU, serta learning rate 1e-3 vs 5e-4)*

| Percobaan | Dimensi Laten | Encoder Blocks | Activation | Val Acc | Val Macro-F1 |
|---|---|---|---|---|---|
| Init Sprint 0 | 64 | 2 Conv Blocks | ReLU | - | - |

## Ablation (>= 2)
*(Akan diuji pada Sprint 2)*:
1. Variasi dimensi bottleneck ruang laten: latent_dim=32 vs latent_dim=64 terhadap separabilitas 10 kelas.
2. Pengaruh penambahan rekonstruksi un-supervised pre-training vs end-to-end classifier training.

## Hasil 3 Seed Konfigurasi Akhir
*(Akan dilengkapi pada Sprint 2 dengan seed 1, 2, 3)*
