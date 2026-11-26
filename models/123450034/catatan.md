# Catatan Model 123450034 — Kharisma Mustika Sari

## Identitas Model
- **Jalur Model:** Transfer Learning / Fine-Tuning
- **Arsitektur:** MobileNetV3 Small
- **Kasus:** Klasifikasi 10 kelas perintah suara pengendali meja
- **Input:** Log-mel spektrogram berukuran 64 × 32
- **Bobot awal:** Pretrained ImageNet
- **Perangkat:** CPU laptop

## Metode Transfer Learning
Model menggunakan MobileNetV3 Small dengan bobot pretrained ImageNet. Lapisan klasifikasi bawaan diganti dengan lapisan output untuk 10 kelas.

Sebagian besar layer fitur pretrained dibekukan (*frozen*), sedangkan dua blok fitur terakhir dibuka untuk proses *fine-tuning*. Input spektrogram diubah menjadi tiga channel dan diubah ukurannya menjadi 128 × 128 sebelum diproses oleh model.

## Konfigurasi Pelatihan

| Parameter | Nilai |
|---|---|
| Optimizer | AdamW |
| Learning rate | 0.0001 |
| Weight decay | 0.0001 |
| Batch size | 16 |
| Epoch | 10 |
| Loss function | Cross Entropy Loss |
| Seed | 2026 |
| Jumlah kelas | 10 |

AdamW digunakan dengan learning rate rendah untuk membantu menjaga kestabilan bobot pretrained selama proses fine-tuning.

## Hasil Pengujian Sprint 1

| Percobaan | Strategi Backbone | Learning Rate | Batch Size | Val Acc | Val Macro-F1 |
|---|---|---:|---:|---:|---:|
| MobileNetV3 Small | Fine-tuning 2 blok terakhir | 0.0001 | 16 | 0.527778 | 0.479719 |

- Jumlah data latih: 324 sampel.
- Jumlah data validasi: 36 sampel.
- Epoch terbaik: 5.
- Akurasi validasi terbaik: 52.78%.
- Macro F1 validasi: 47.97%.
- Durasi pelatihan: 74.42 detik.

## Regularisasi
- Menggunakan bobot pretrained ImageNet.
- Membekukan sebagian besar layer fitur backbone.
- Menggunakan weight decay sebesar 0.0001 pada optimizer AdamW.

## Catatan dan Keterbatasan
1. Label dataset masih berupa angka 0–9. Pemetaan angka ke nama perintah perlu dikonfirmasi kepada koordinator tim.
2. Pembagian data yang digunakan mengikuti fungsi `data.muat()` dari starter dengan validasi 10%. Pembagian ini belum menggunakan GroupKFold berdasarkan partisipan seperti yang disebutkan dalam protokol.
3. Pengujian ini menggunakan satu seed dan belum mencakup perbandingan beberapa hyperparameter.
4. Data uji belum dievaluasi karena protokol belum menyediakan data test.

## Rencana Pengembangan Sprint 2
1. Membandingkan strategi pembekuan dan pembukaan layer backbone.
2. Menguji variasi learning rate dan batch size.
3. Melakukan pengujian dengan tiga seed.
4. Melakukan evaluasi lanjutan sesuai protokol pembagian data tim.

## Ringkasan Hasil 3 Seed

| Seed | Val Accuracy | Val Macro-F1 | Durasi (detik) |
|---|---:|---:|---:|
| 1 | 0.638889 | 0.628131 | 57.14 |
| 2 | 0.638889 | 0.617020 | 47.10 |
| 3 | 0.638889 | 0.628571 | 46.27 |
| **Rata-rata** | **0.638889** | **0.624574** | **50.17** |

Seluruh percobaan menggunakan data_hash yang sama. Evaluasi hanya dilakukan pada data validasi sebanyak 36 sampel; data test belum dievaluasi.
