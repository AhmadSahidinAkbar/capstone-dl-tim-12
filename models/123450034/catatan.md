# Catatan Model 123450034 — Kharisma Mustika Sari

**Jalur Model**: Transfer Learning / Fine-Tuning (Modul 06)  
**Kasus**: Klasifikasi 10 Perintah Suara Pengendali Meja (Log-mel 64 pita, 1 detik)  
**Tugas Sampingan**: Penjaga Data & Evaluasi  
**Status Sprint 1**: Kerangka model teruji pada data simulasi (Seed 1)

---

## 1. Arsitektur Model (Transfer Learning Feature Extractor)
- Spektrogram Log-mel input 1-kanal berdimensi `[Batch, 1, 64, Waktu]` direplikasi menjadi pseudo-3-kanal `[Batch, 3, 64, Waktu]` agar kompatibel dengan topologi konvolusi transfer learning.
- **Backbone Feature Extractor**:
  - `Conv2d(3, 32, kernel_size=3, padding=1)` $\rightarrow$ `BatchNorm2d(32)` $\rightarrow$ `ReLU` $\rightarrow$ `MaxPool2d(2, 2)`
  - `Conv2d(32, 64, kernel_size=3, padding=1)` $\rightarrow$ `BatchNorm2d(64)` $\rightarrow$ `ReLU` $\rightarrow$ `AdaptiveAvgPool2d((4, 4))`
- **Classification Head (Fine-tuned)**:
  - `Linear(64 * 4 * 4, 128)` $\rightarrow$ `ReLU`
  - `Dropout(0.3)`
  - `Linear(128, 10)` (output logits untuk 10 kata perintah suara).

---

## 2. Alasan Optimizer & Loss
- Menggunakan **AdamW** dengan learning rate rendah ($5 \times 10^{-4}$) dan penalti `weight_decay = 1e-4`.
- **Alasan**: Pada skema transfer learning, learning rate yang terlalu tinggi berisiko menyebabkan *catastrophic forgetting* pada representasi fitur umum. AdamW memisahkan peluruhan bobot (*weight decay*) dari pembaruan momen gradien sehingga bobot backbone tetap stabil saat lapisan classifier beradaptasi.
- **Loss Function**: `CrossEntropyLoss()` untuk klasifikasi multi-kelas 10 kata target.

---

## 3. Regularisasi
- Pemanfaatan **Batch Normalization** pada setiap blok konvolusi untuk menstabilkan distribusi aktivasi.
- **Dropout (0.3)** pada classification head sebelum proyeksi ke 10 kelas output guna mencegah *co-adaptation* fitur.
- **Weight decay** pada optimizer untuk mencegah overfitting pada jumlah sampel terbatas.

---

## 4. Hasil Awal Data Simulasi (Seed 1) — Sprint 1 (Kartu #15)
- **File Metrics**: `results/123450034/metrics.json`
- **Data Hash**: `edb46995414bfa955cbcb6c65c28927e`
- **Metrik Validasi**:
  - `val_acc`: 0.1667 (16.67%)
  - `val_macro_f1`: 0.0286
- **Durasi Pelatihan**: ~9.3 detik (sangat cepat, jauh di bawah anggaran $\le$ 20 menit CPU laptop).
- **Status Selesai**: Skrip `python models/123450034/run.py --seed 1` berjalan tanpa error sampai akhir, dan dimensi output sesuai 10 kelas target.

---

## 5. Rencana Eksplorasi (Sprint 2)
- Pencarian hyperparameter: unfreezing blok akhir vs freeze penuh, variasi learning rate (1e-3 vs 5e-4 vs 1e-4).
- Ablation study: adaptasi conv layer pertama vs replikasi 3-kanal.
