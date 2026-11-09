# Catatan Model 122450044 — Ahmad Sahidin Akbar

**Jalur Model**: CNN dari Nol (Modul 05)  
**Kasus**: Klasifikasi 10 Perintah Suara Pengendali Meja (Log-mel 64 pita, 1 detik)  
**Status Sprint 1**: Kerangka model teruji pada data simulasi (Seed 1)

---

## 1. Arsitektur Model (CNN 2D dari Nol)
Model menerima input spektrogram Log-mel berdimensi `[Batch, 1, 64, Waktu]`:
* **Blok Konvolusi 1**: `Conv2d(1, 16, kernel_size=3, padding=1)` $\rightarrow$ `BatchNorm2d(16)` $\rightarrow$ `ReLU` $\rightarrow$ `MaxPool2d(2, 2)` (output: `[16, 32, Waktu/2]`).
* **Blok Konvolusi 2**: `Conv2d(16, 32, kernel_size=3, padding=1)` $\rightarrow$ `BatchNorm2d(32)` $\rightarrow$ `ReLU` $\rightarrow$ `MaxPool2d(2, 2)` (output: `[32, 16, Waktu/4]`).
* **Blok Konvolusi 3**: `Conv2d(32, 64, kernel_size=3, padding=1)` $\rightarrow$ `BatchNorm2d(64)` $\rightarrow$ `ReLU` $\rightarrow$ `AdaptiveAvgPool2d((4, 4))` (output adaptif: `[64, 4, 4]`).
* **Classifier Head**:
  * `Dropout(0.3)`
  * `Linear(1024, 64)` $\rightarrow$ `ReLU`
  * `Dropout(0.2)`
  * `Linear(64, 10)` (output logits untuk 10 kata perintah suara).

---

## 2. Alasan Optimizer & Loss
* **Optimizer**: Menggunakan **AdamW** dengan learning rate awal $1 \times 10^{-3}$ dan `weight_decay = 1e-4`. AdamW dipilih karena memisahkan peluruhan bobot (*weight decay*) dari pembaruan momen gradien, menjaga stabilitas bobot konvolusi pada input matriks spektrogram audio.
* **Loss Function**: `CrossEntropyLoss()` untuk klasifikasi multi-kelas 10 perintah suara.

---

## 3. Regularisasi
* **Batch Normalization**: Dipasang setelah setiap lapisan konvolusi untuk menstabilkan distribusi aktivasi antar-batch.
* **Spatial/Adaptive Pooling**: `AdaptiveAvgPool2d((4, 4))` memastikan ukuran output tetap konsisten jika terjadi variasi durasi frame waktu.
* **Dropout**: Dropout ganda (0.3 pada flattened feature map dan 0.2 sebelum output layer) untuk mencegah ko-adaptasi fitur pada data penutur terbatas.

---

## 4. Hasil Awal Data Simulasi (Seed 1)
* **File Metrics**: `results/122450044/metrics.json`
* **Data Hash**: `edb46995414bfa955cbcb6c65c28927e`
* **Durasi Pelatihan**: ~4.9 detik (sangat cepat dan memenuhi batas komputasi $\le$ 20 menit di CPU laptop).
