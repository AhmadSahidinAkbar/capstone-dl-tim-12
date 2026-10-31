# Catatan Model 
# 123450083 
# Nadya Ratu Anjani

**Jalur Model**: Transformer Encoder atas Patch (Modul 09)  
**Kasus**: Klasifikasi 10 Perintah Suara Pengendali Meja (Log-mel 64 pita, 1 detik)  
**Tugas Sampingan**: Analis Utama

## Alasan Optimizer
- Menggunakan **AdamW** dengan learning rate $5 \times 10^{-4}$ dan weight decay $1 \times 10^{-3}$.
- Alasan: Arsitektur Transformer sangat sensitif terhadap pembaruan bobot attention. AdamW membantu mendisplinkan matriks attention weights agar tidak mengalami degenerasi fitur pada jumlah sampel data latih yang ringkas.

## Regularisasi
- Attention Dropout ($0.2$) pada layer multi-head self-attention.
- Layer Normalization sebelum dan sesudah modul feed-forward network.
- Projection Dropout ($0.3$) pada lapisan classifier output sebelum penentuan kelas.

## Pencarian Hyperparameter (Tabel)
*(Akan dieksplorasi pada Sprint 1: perbandingan jumlah attention head 2 vs 4 vs 8, ukuran patch frekuensi-waktu, dan dimensi embedding 32 vs 64)*

| Percobaan | Patch Size | Heads | Embed Dim | Val Acc | Val Macro-F1 |
|---|---|---|---|---|---|
| Init Sprint 0 | 16x8 | 4 | 64 | - | - |

## Ablation (>= 2)
*(Akan diuji pada Sprint 2)*:
1. Pengaruh penambahan Positional Embedding vs tanpa Positional Embedding.
2. Pengaruh penggunaan token khusus [CLS] vs Global Average Pooling atas seluruh patch token.

## Hasil 3 Seed Konfigurasi Akhir
*(Akan dilengkapi pada Sprint 2 dengan seed 1, 2, 3)*
