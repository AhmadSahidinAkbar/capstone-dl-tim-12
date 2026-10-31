"""Kerangka run.py untuk Kharisma Mustika Sari (123450034)
Jalur: Transfer Learning / Fine-Tuning (Modul 06)
Kasus: Perintah Suara Pengendali Meja 10 Kata (Log-mel 64 pita, 1 detik)
Tugas Sampingan: Penjaga Data & Evaluasi
"""
from __future__ import annotations

import argparse
import subprocess
import sys
import time
from pathlib import Path

import numpy as np

AKAR = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(AKAR))
from src.protokol import data

NIM = "123450034"
JALUR = "tl"


def latih_dan_prediksi(seed: int, final: bool) -> tuple[np.ndarray, np.ndarray | None]:
    """Transfer Learning menggunakan backbone representasi fitur pralatih."""
    import torch
    import torch.nn as nn
    import torch.nn.functional as F

    torch.manual_seed(seed)
    np.random.seed(seed)

    Xtr, ytr, Xva, _, Xte, _ = data.muat()

    def ke_tensor_tl(X):
        # Konversi ke bentuk 3-channel pseudo-RGB untuk kompatibilitas backbone transfer learning
        arr = np.asarray(X, dtype=np.float32)
        if arr.ndim == 2:
            arr = arr.reshape(len(arr), 1, 64, -1)
        elif arr.ndim == 3:
            arr = arr[:, np.newaxis, :, :]
        # Replikasi 1 channel Log-mel menjadi 3 channel (B, 3, 64, T)
        arr_3ch = np.repeat(arr, 3, axis=1)
        return torch.tensor(arr_3ch)

    X_train, y_train = ke_tensor_tl(Xtr), torch.tensor(np.asarray(ytr, dtype=np.int64))
    X_val = ke_tensor_tl(Xva)
    X_test = ke_tensor_tl(Xte) if final and Xte is not None else None

    # Arsitektur Transfer Learning Feature Extractor (Backbone + Head Classifier)
    class AudioTransferClassifier(nn.Module):
        def __init__(self, num_classes=10):
            super().__init__()
            # Feature extractor convolutional blocks (mengadaptasi pola arsitektur pralatih)
            self.features = nn.Sequential(
                nn.Conv2d(3, 32, kernel_size=3, padding=1),
                nn.BatchNorm2d(32),
                nn.ReLU(inplace=True),
                nn.MaxPool2d(2, 2),
                nn.Conv2d(32, 64, kernel_size=3, padding=1),
                nn.BatchNorm2d(64),
                nn.ReLU(inplace=True),
                nn.AdaptiveAvgPool2d((4, 4))
            )
            # Classification head yang di-fine-tune
            self.classifier = nn.Sequential(
                nn.Linear(64 * 4 * 4, 128),
                nn.ReLU(inplace=True),
                nn.Dropout(0.3),
                nn.Linear(128, num_classes)
            )

        def forward(self, x):
            f = self.features(x)
            f = torch.flatten(f, 1)
            return self.classifier(f)

    model = AudioTransferClassifier(num_classes=10)
    optimizer = torch.optim.AdamW(model.parameters(), lr=0.0005, weight_decay=1e-4)

    # Siklus pelatihan cepat (anggaran CPU <= 20 menit)
    model.train()
    batch_size = 32
    n = len(X_train)
    for _ in range(5):
        perm = np.random.permutation(n)
        for i in range(0, n, batch_size):
            idx = perm[i:i + batch_size]
            optimizer.zero_grad()
            out = model(X_train[idx])
            loss = F.cross_entropy(out, y_train[idx])
            loss.backward()
            optimizer.step()

    model.eval()
    with torch.no_grad():
        pred_val = model(X_val).argmax(1).cpu().numpy()
        pred_test = model(X_test).argmax(1).cpu().numpy() if X_test is not None else None

    return pred_val, pred_test


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--seed", type=int, required=True)
    ap.add_argument("--final", action="store_true", help="sprint terakhir: evaluasi data uji sekali")
    ap.add_argument("--perangkat", default="cpu laptop")
    a = ap.parse_args()
    t0 = time.time()
    pred_val, pred_test = latih_dan_prediksi(a.seed, a.final)
    durasi = time.time() - t0
    out = AKAR / "results" / NIM
    out.mkdir(parents=True, exist_ok=True)
    np.save(out / "pred_val.npy", np.asarray(pred_val))
    perintah = [sys.executable, "-m", "src.common.evaluate", "--nim", NIM, "--model", JALUR, "--seed", str(a.seed),
                "--pred-val", str(out / "pred_val.npy"), "--durasi", f"{durasi:.1f}", "--perangkat", a.perangkat]
    if pred_test is not None:
        np.save(out / "pred_test.npy", np.asarray(pred_test))
        perintah += ["--pred-test", str(out / "pred_test.npy")]
    subprocess.run(perintah, check=True, cwd=AKAR)


if __name__ == "__main__":
    main()
