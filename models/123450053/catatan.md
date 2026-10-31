# Catatan Model 
# 123450053 — Khazanatil Ilmi

**Jalur Model**: RNN -> LSTM/GRU atas Baris Citra (Modul 07–08)  
**Kasus**: Klasifikasi 10 Perintah Suara Pengendali Meja (Log-mel 64 pita, 1 detik)  
**Tugas Sampingan**: Integrator Sistem

## Alasan Optimizer
- Menggunakan **Adam** dengan learning rate $1 \times 10^{-3}$ dikombinasikan dengan teknik **Gradient Clipping** (`max_norm=5.0`).
- Alasan: Model keluarga RNN rentan terhadap permasalahan gradien meledak (*exploding gradient*) saat memproses sekuens rentang waktu frame audio. Adam dengan gradient clipping menjaga pembaharuan parameter recurrent tetap stabil tanpa osilasi loss.

## Regularisasi
- Recurrent Dropout ($0.2$) antar-layer GRU.
- Feed-forward Dropout ($0.3$) pada lapisan Fully Connected sebelum klasifikasi akhir.
- Weight decay $1 \times 10^{-4}$ untuk mencegah ko-dependensi antar-state memori tersembunyi (*hidden state*).

## Pencarian Hyperparameter (Tabel)
*(Akan dieksplorasi pada Sprint 1: perbandingan GRU vs LSTM, hidden unit 32 vs 64 vs 128, serta arah unidirectional vs bidirectional)*

| Percobaan | Arsitektur | Hidden Units | Layers | Val Acc | Val Macro-F1 |
|---|---|---|---|---|---|
| Init Sprint 0 | Bi-GRU | 64 | 2 | - | - |

## Ablation (>= 2)
*(Akan diuji pada Sprint 2)*:
1. Variasi tipe sel sekuensial: Bi-GRU vs Bi-LSTM terhadap latensi inferensi ONNX di CPU meja uji.
2. Pengaruh Temporal Mean Pooling vs Mengambil hidden state terakhir (`last step`).

## Hasil 3 Seed Konfigurasi Akhir
*(Akan dilengkapi pada Sprint 2 dengan seed 1, 2)*
