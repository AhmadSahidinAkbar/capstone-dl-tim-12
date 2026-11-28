# Catatan Model 123450094 — Tanty Widiyastuti

**Jalur Model**: Autoencoder Representasi untuk Klasifikasi/Anomali (Modul 09)  
**Kasus**: Klasifikasi 10 Perintah Suara Pengendali Meja (Log-mel 64 pita, 1 detik)  
**Tugas Sampingan**: Reproduksi & Demo  
**Status Sprint 1**: Kerangka model teruji pada data simulasi (Seed 1)

---

## 1. Arsitektur Model (Convolutional Autoencoder + Latent Classifier)
Model menerima input spektrogram Log-mel berdimensi `[Batch, 1, 64, Waktu]`:
* **Encoder Konvolusi**:
  * `Conv2d(1, 16, kernel_size=3, stride=2, padding=1)` $\rightarrow$ `BatchNorm2d(16)` $\rightarrow$ `ReLU` (downsampling spasial $32 \times T/2$).
  * `Conv2d(16, 32, kernel_size=3, stride=2, padding=1)` $\rightarrow$ `BatchNorm2d(32)` $\rightarrow$ `ReLU` $\rightarrow$ `AdaptiveAvgPool2d((4, 4))` (fitur: `[32, 4, 4]`).
* **Bottleneck Proyeksi Laten**:
  * `Linear(32 * 4 * 4, latent_dim=64)` $\rightarrow$ mengekstrak representasi manifold laten kompak 64-dimensi.
* **Classifier Head**:
  * `Linear(64, 64)` $\rightarrow$ `ReLU`
  * `Dropout(0.3)`
  * `Linear(64, 10)` (output logits untuk 10 kata target suara).

---

## 2. Alasan Optimizer & Loss
* **Optimizer**: Menggunakan **Adam** dengan learning rate awal $1 \times 10^{-3}$ dan `weight_decay = 1e-4`.
* **Alasan**: Pemadatan fitur spektrogram ke dalam ruang laten berdimensi rendah membutuhkan pembaruan momen adaptif agar gradien tidak terjebak pada plateaus awal.
* **Loss Function**: `CrossEntropyLoss()` untuk klasifikasi multi-kelas 10 kata target.

---

## 3. Regularisasi
* **Batch Normalization**: Dipasang setelah setiap lapisan konvolusi encoder untuk menstabilkan distribusi aktivasi.
* **Adaptive Pooling**: `AdaptiveAvgPool2d((4, 4))` menjamin representasi spasial tetap konsisten terlepas dari variasi durasi waktu frame audio.
* **Dropout (0.3)**: Mencegah *co-adaptation* fitur laten pada klasifikasi 10 perintah meja.

---

## 4. Hasil Awal Data Simulasi (Seed 1) — Sprint 1 (Kartu #21)
* **File Metrics**: `results/123450094/metrics.json`
* **Data Hash**: `edb46995414bfa955cbcb6c65c28927e`
* **Metrik Validasi**:
  * `val_acc`: 0.1667 (16.67%)
  * `val_macro_f1`: 0.0316
* **Durasi Pelatihan**: ~7.4 detik (sangat cepat dan memenuhi batas komputasi $\le$ 20 menit di CPU laptop).
* **Status Selesai**: Skrip `python models/123450094/run.py --seed 1` berjalan sukses tanpa error sampai akhir, dan keluaran sesuai 10 kelas target.

---

## 5. Rencana Eksplorasi (Sprint 2)
* Eksplorasi dimensi ruang laten: 32 vs 64 vs 128 terhadap separabilitas kelas dan skor anomali.
* Penambahan fungsi rekonstruksi Mean Squared Error (MSE) jika digabungkan dengan unsupervised pre-training.
