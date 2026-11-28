# Catatan Model 123450053 — Khazanatil Ilmi

**Jalur Model**: RNN (Bi-GRU atas Runtun Waktu Spektrogram) (Modul 07)  
**Kasus**: Klasifikasi 10 Perintah Suara Pengendali Meja (Log-mel 64 pita, 1 detik)  
**Tugas Sampingan**: Integrator Sistem  
**Status Sprint 1**: Teruji pada data simulasi dan data primer meja uji fisik (Seed 1)

---

## 1. Arsitektur Model (Bidirectional GRU)
Model memproses urutan langkah waktu frame spektrogram Log-mel berdimensi `[Batch, Time_Steps, Mel_Features=64]`:
* **Recurrent Core**:
  * `nn.GRU(input_size=64, hidden_size=64, num_layers=2, batch_first=True, bidirectional=True, dropout=0.2)`
  * Memproses dependensi temporal maju dan mundur (*bidirectional*) dengan total representasi 128 fitur ($64 \times 2$).
* **Temporal Mean Pooling**:
  * Merata-ratakan *hidden state* atas seluruh langkah waktu audio untuk merangkum konteks ucapan secara utuh dan tahan terhadap variasi jeda kata.
* **Classifier Head**:
  * `Linear(128, 64)` $\rightarrow$ `ReLU`
  * `Dropout(0.3)`
  * `Linear(64, 10)` (output logits untuk 10 kata perintah suara).

---

## 2. Alasan Optimizer & Loss
* **Optimizer**: Menggunakan **Adam** dengan learning rate $1 \times 10^{-3}$ dikombinasikan dengan teknik **Gradient Clipping** (`max_norm = 5.0`) dan `weight_decay = 1e-4`.
* **Alasan**: Jaringan berulang (RNN) sangat rentan terhadap ledakan gradien (*exploding gradient*) saat merambatkan gradien mundur sepanjang runtunan langkah waktu. Penggunaan gradient clipping dan Adam menjamin konvergensi yang cepat dan stabil tanpa lonjakan loss.
* **Loss Function**: `CrossEntropyLoss()` untuk klasifikasi multi-kelas 10 kata target.

---

## 3. Regularisasi
* **Recurrent Dropout (0.2)**: Dipasang antar-lapisan GRU untuk mencegah ko-adaptasi representasi transisi antar-state.
* **Feed-forward Dropout (0.3)**: Dipasang sebelum lapisan klasifikasi akhir untuk menghindari overfitting pada data penutur terbatas.
* **Weight Decay ($1 \times 10^{-4}$)**: Membatasi magnitudo bobot matriks rekuren.

---

## 4. Hasil Awal Data Simulasi (Seed 1) — Sprint 1 (Kartu #17)
* **File Metrics**: `results/123450053/metrics.json`
* **Data Hash**: `edb46995414bfa955cbcb6c65c28927e`
* **Metrik Validasi**:
  * `val_acc`: 0.1667 (16.67%)
  * `val_macro_f1`: 0.0300
* **Durasi Pelatihan**: ~11.3 detik (sangat efisien di CPU laptop).
* **Status Selesai**: Skrip `python models/123450053/run.py --seed 1` berjalan sukses tanpa error sampai akhir, dan keluaran sesuai 10 kelas target.

---

## 5. Hasil Data Primer Meja Uji (Seed 1) — Sprint 1 (Kartu #18)
* **File Metrics**: `results/123450053/metrics.json`
* **Data Hash**: `a1cbb6263d5d79f3764fb31257c722c1` (`n_sampel = 360`, `n_val = 36`)
* **Metrik Validasi Keseluruhan**:
  * `val_acc`: `0.3889` (38.89%)
  * `val_macro_f1`: `0.3375`
* **Akurasi per Penutur (`partisipan` pada split validasi)**:
  * `P01` ($n=7$): `0.5714` (57.14%)
  * `P02` ($n=6$): `0.6667` (66.67%)
  * `P03` ($n=4$): `0.0000` (0.00%)
  * `P04` ($n=6$): `0.3333` (33.33%)
  * `P05` ($n=5$): `0.4000` (40.00%)
  * `P06` ($n=8$): `0.2500` (25.00%)
* **Perbandingan dengan Pembanding Non-DL Tim (`results/baseline_non_dl/metrics.json`)**:
  * Random Forest: `val_acc = 0.0556`, `val_macro_f1 = 0.0364`
  * SVM (RBF): `val_acc = 0.0556`, `val_macro_f1 = 0.0174`
  * Model Bi-GRU (`0.3889` akurasi, `0.3375` macro-F1) melampaui pembanding non-DL terbaik secara signifikan (+33.33% akurasi, +0.3011 macro-F1) dengan konfigurasi awal 5 epoch.

---

## 6. Rencana Eksplorasi (Sprint 2)
* Eksplorasi sel sekuensial: Bi-GRU vs Bi-LSTM terhadap latensi inferensi di meja uji.
* Variasi pooling: Temporal Mean Pooling vs Attention Pooling vs Last Step hidden state.
* Penambahan epoch, penjadwalan *learning rate*, serta evaluasi 3 seed (`1, 2, 3`) dan 2 eksperimen ablasi.
