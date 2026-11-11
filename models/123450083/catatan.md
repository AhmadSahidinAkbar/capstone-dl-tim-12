# Catatan Model 123450083 — Nadya Ratu Anjani

**Jalur Model**: Transformer Encoder atas Patch Spektrogram (Modul 08)  
**Kasus**: Klasifikasi 10 Perintah Suara Pengendali Meja (Log-mel 64 pita, 1 detik)  
**Tugas Sampingan**: Analis Utama  
**Status Sprint 1**: Kerangka model teruji pada data simulasi (Seed 1)

---

## 1. Arsitektur Model (Audio Spectrogram Transformer)
Model memproses input spektrogram Log-mel berdimensi `[Batch, 1, 64, Waktu]`:
* **Patch Embedding**:
  * Menggunakan `Conv2d(1, embed_dim=64, kernel_size=(16, 8), stride=(16, 8))` untuk memotong spektrogram menjadi patch token frekuensi-waktu dan memproyeksikannya ke embedding 64-dimensi.
* **Transformer Encoder**:
  * `d_model = 64`, `nhead = 4`, `dim_feedforward = 128`, `dropout = 0.2`, `num_layers = 2`.
  * Pembelajaran representasi kontekstual antar-patch via mekanisme *Multi-Head Self-Attention*.
* **Token Klasifikasi [CLS] & Output Head**:
  * Penambahan parameter `cls_token` pada urutan sequence awal.
  * Classifier Head: `LayerNorm(64)` $\rightarrow$ `Dropout(0.3)` $\rightarrow$ `Linear(64, 10)` (output logits 10 kata target suara).

---

## 2. Alasan Optimizer & Loss
* **Optimizer**: Menggunakan **AdamW** dengan learning rate $5 \times 10^{-4}$ dan `weight_decay = 1e-3`.
* **Alasan**: Mekanisme self-attention pada Transformer sangat rentan mengalami *attention weight collapse* bila regularisasi bobot tidak terpisah dari momentum pembaruan gradien. AdamW menjaga bobot proyeksi query-key-value tetap stabil pada sampel data berdurasi singkat.
* **Loss Function**: `CrossEntropyLoss()` untuk klasifikasi multi-kelas 10 kata target.

---

## 3. Regularisasi
* **Attention Dropout (0.2)**: Mengacak matriks attention weights untuk mencegah ketergantungan hanya pada satu patch frekuensi tertentu.
* **Layer Normalization**: Menjaga kestabilan dinamika aktivasi antar-lapisan feedforward encoder.
* **Projection Dropout (0.3)**: Mencegah overfitting pada classifier head sebelum menghasilkan prediksi 10 kelas.

---

## 4. Hasil Awal Data Simulasi (Seed 1) — Sprint 1 (Kartu #19)
* **File Metrics**: `results/123450083/metrics.json`
* **Data Hash**: `edb46995414bfa955cbcb6c65c28927e`
* **Metrik Validasi**:
  * `val_acc`: 0.0556 (5.56%)
  * `val_macro_f1`: 0.0286
* **Durasi Pelatihan**: ~5.7 detik (sangat efisien di CPU laptop).
* **Status Selesai**: Skrip `python models/123450083/run.py --seed 1` berjalan sukses tanpa error sampai akhir, dan keluaran sesuai 10 kelas target.

---

## 5. Rencana Eksplorasi (Sprint 2)
* Eksplorasi patch size: (16, 8) vs (8, 4) untuk menangkap detail temporal yang lebih rapat.
* Pengujian penambahan 1D sinusoidal Positional Encoding vs tanpa positional encoding.
* Komparasi representasi CLS Token vs Global Average Pooling atas token patch.
