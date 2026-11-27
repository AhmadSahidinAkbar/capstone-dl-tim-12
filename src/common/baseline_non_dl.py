"""Skrip Baseline Pembanding Non-Deep Learning - Tim 12
Penanggung Jawab: Nadya Ratu Anjani (123450083) - Analis Utama
Tugas: Kartu #10 (Pembanding non-DL: MFCC rata-rata dan simpangan + Random Forest/SVM)

Metode:
1. Memuat masukan representasi akustik (Log-mel / MFCC 64 pita frekuensi) dari `src.protokol.data.muat()`.
2. Mengekstrak ringkasan statistik per frame waktu:
   - Rata-rata koefisien frekuensi sepanjang waktu (mean)
   - Simpangan baku koefisien frekuensi sepanjang waktu (std)
   - Menggabungkannya menjadi vektor fitur 128-dimensi per sampel ucapan.
3. Melatih model Random Forest dan SVM (RBF kernel) dari Scikit-Learn.
4. Menghasilkan metrik validasi (Accuracy & Macro-F1) sebagai patokan performa minimum
   (lower bound) yang wajib dilampaui oleh model-model deep learning tim.
5. Menyimpan output ke `results/baseline_non_dl/metrics.json` dan `reports/pembanding_non_dl.md`.
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, f1_score
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC

AKAR = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(AKAR))
from src.protokol import data  # noqa: E402


def ekstraksi_fitur_statistik(X: np.ndarray) -> np.ndarray:
    """Mengekstrak rata-rata dan simpangan baku sepanjang sumbu waktu (frame).
    
    Input: [N, 64, T] atau [N, fitur]
    Output: [N, 128] jika 3D, atau [N, fitur]
    """
    arr = np.asarray(X, dtype=np.float32)
    if arr.ndim == 2:
        # Jika bentuk [N, 64*T]
        arr = arr.reshape(len(arr), 64, -1)

    if arr.ndim == 3:
        # arr: [N, freq_bins=64, time_frames]
        fitur_mean = np.mean(arr, axis=2)  # [N, 64]
        fitur_std = np.std(arr, axis=2)    # [N, 64]
        return np.concatenate([fitur_mean, fitur_std], axis=1)  # [N, 128]

    return arr.reshape(len(arr), -1)


def main():
    parser = argparse.ArgumentParser(description="Baseline Pembanding Non-DL Tim 12")
    parser.add_argument("--seed", type=int, default=1, help="Seed pengacakan model")
    args = parser.parse_args()

    print("======================================================================")
    print("      EVALUASI BASELINE PEMBANDING NON-DL (RANDOM FOREST & SVM)       ")
    print("======================================================================")

    t0 = time.time()
    Xtr, ytr, Xva, yva, Xte, yte = data.muat()

    # 1. Ekstraksi fitur statistik rata-rata & simpangan
    Xtr_feat = ekstraksi_fitur_statistik(Xtr)
    Xva_feat = ekstraksi_fitur_statistik(Xva)

    print(f"Bentuk data mentah latih   : {Xtr.shape}")
    print(f"Bentuk fitur statistik     : {Xtr_feat.shape} (64 rata-rata + 64 simpangan)")

    # Standardisasi fitur untuk SVM
    scaler = StandardScaler()
    Xtr_scaled = scaler.fit_transform(Xtr_feat)
    Xva_scaled = scaler.transform(Xva_feat)

    # 2. Model A: Random Forest Classifier
    rf = RandomForestClassifier(n_estimators=100, random_state=args.seed, n_jobs=-1)
    rf.fit(Xtr_feat, ytr)
    pred_va_rf = rf.predict(Xva_feat)
    acc_rf = accuracy_score(yva, pred_va_rf)
    f1_rf = f1_score(yva, pred_va_rf, average="macro", zero_division=0)

    # 3. Model B: Support Vector Machine (RBF)
    svm = SVC(kernel="rbf", C=1.0, random_state=args.seed)
    svm.fit(Xtr_scaled, ytr)
    pred_va_svm = svm.predict(Xva_scaled)
    acc_svm = accuracy_score(yva, pred_va_svm)
    f1_svm = f1_score(yva, pred_va_svm, average="macro", zero_division=0)

    durasi = time.time() - t0

    print("\n--- HASIL EVALUASI PEMBANDING NON-DL ---")
    print(f"Random Forest  -> Val Accuracy: {acc_rf:.4f} ({acc_rf*100:.2f}%), Val Macro-F1: {f1_rf:.4f}")
    print(f"SVM (RBF)      -> Val Accuracy: {acc_svm:.4f} ({acc_svm*100:.2f}%), Val Macro-F1: {f1_svm:.4f}")
    print(f"Durasi Komputasi : {durasi:.2f} detik")

    # Pilih model non-DL terbaik
    terbaik = "Random Forest" if f1_rf >= f1_svm else "SVM (RBF)"
    best_acc = max(acc_rf, acc_svm)
    best_f1 = max(f1_rf, f1_svm)
    print(f"\nModel Pembanding Terbaik : {terbaik} (Macro-F1: {best_f1:.4f})")

    # 4. Simpan metrik ke results/baseline_non_dl/metrics.json
    out_dir = AKAR / "results" / "baseline_non_dl"
    out_dir.mkdir(parents=True, exist_ok=True)
    hasil_json = {
        "model": "non_dl_baseline",
        "seed": args.seed,
        "metrik": {
            "random_forest": {
                "val_acc": round(float(acc_rf), 6),
                "val_macro_f1": round(float(f1_rf), 6)
            },
            "svm": {
                "val_acc": round(float(acc_svm), 6),
                "val_macro_f1": round(float(f1_svm), 6)
            },
            "best_val_acc": round(float(best_acc), 6),
            "best_val_macro_f1": round(float(best_f1), 6)
        },
        "best_model": terbaik,
        "n_fitur": Xtr_feat.shape[1],
        "n_train": len(Xtr),
        "n_val": len(Xva),
        "durasi_detik": round(durasi, 2)
    }

    out_file = out_dir / "metrics.json"
    out_file.write_text(json.dumps(hasil_json, indent=2), encoding="utf-8")
    print(f"[OK] Metrik JSON tersimpan di: {out_file.relative_to(AKAR)}")

    # 5. Buat laporan komparasi di reports/pembanding_non_dl.md
    rep_dir = AKAR / "reports"
    rep_dir.mkdir(parents=True, exist_ok=True)
    rep_file = rep_dir / "pembanding_non_dl.md"

    laporan_md = f"""# Laporan Model Pembanding Non-Deep Learning (Kartu #10)

**Tim**: 12 — Ruang Cerdas 5 Volt (Perintah Suara 10 Kata)  
**Penanggung Jawab**: Nadya Ratu Anjani (123450083) — Analis Utama  
**Metode**: Ekstraksi Rata-rata dan Simpangan Baku Koefisien Frekuensi Log-mel/MFCC + Random Forest & SVM  
**Tanggal Pengujian**: 11 November 2026 (Data Simulasi Tim)

---

## 1. Metodologi Ekstraksi Fitur Non-DL
Model deep learning menerima representasi spektrogram Log-mel berdimensi `[64, Waktu]`. Untuk pembanding non-DL:
1. **Rata-rata Temporal (64 fitur)**: Merangkum sebaran energi spektral rata-rata di tiap pita frekuensi.
2. **Simpangan Baku Temporal (64 fitur)**: Menangkap variabilitas dinamika perubahan energi saat kata diucapkan.
3. Total vektor fitur representasi per ucapan adalah **128 fitur**.

---

## 2. Tabel Performa Pembanding pada Data Validasi
| Algoritma Pembanding | Parameter Utama | Val Accuracy | Val Macro-F1 | Waktu Pelatihan |
|---|---|---|---|---|
| **Random Forest** | `n_estimators=100`, max_depth=None | {acc_rf:.4f} ({acc_rf*100:.1f}%) | {f1_rf:.4f} | < 1 detik |
| **SVM (RBF Kernel)** | `C=1.0`, `gamma='scale'`, StandardScaler | {acc_svm:.4f} ({acc_svm*100:.1f}%) | {f1_svm:.4f} | < 1 detik |

---

## 3. Catatan Batas Bawah (*Baseline Threshold*) untuk Tim
- Nilai performa pembanding non-DL terbaik saat ini adalah **Macro-F1 {best_f1:.4f}** ({terbaik}).
- Nilai ini menjadi batas bawah (*benchmark*) yang wajib dilampaui oleh kelima arsitektur Deep Learning tim (CNN, TL, RNN, Transformer, AE) ketika dilatih menggunakan data primer meja uji.
"""
    rep_file.write_text(laporan_md, encoding="utf-8")
    print(f"[OK] Laporan pembanding tersimpan di: {rep_file.relative_to(AKAR)}")
    print("======================================================================")


if __name__ == "__main__":
    main()
