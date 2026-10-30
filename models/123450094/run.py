"""Kerangka run.py untuk Tantiy Widiyastuti (123450094)
Jalur: Autoencoder Representasi untuk Klasifikasi/Anomali
Kasus: Perintah Suara Pengendali Meja 10 Kata (Log-mel 64 pita, 1 detik)
Tugas Sampingan: Reproduksi & Demo
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

NIM = "123450094"
JALUR = "ae"


def latih_dan_prediksi(seed: int, final: bool) -> tuple[np.ndarray, np.ndarray | None]:
    """Convolutional Autoencoder yang mengekstrak ruang laten representasi untuk klasifikasi."""
    import torch
    import torch.nn as nn
    import torch.nn.functional as F

    torch.manual_seed(seed)
    np.random.seed(seed)

    Xtr, ytr, Xva, _, Xte, _ = data.muat()

    def ke_tensor_ae(X):
        # Format input menjadi citra 1-channel [Batch, 1, 64, T]
        arr = np.asarray(X, dtype=np.float32)
        if arr.ndim == 2:
            arr = arr.reshape(len(arr), 1, 64, -1)
        elif arr.ndim == 3:
            arr = arr[:, np.newaxis, :, :]
        return torch.tensor(arr)

    X_train, y_train = ke_tensor_ae(Xtr), torch.tensor(np.asarray(ytr, dtype=np.int64))
    X_val = ke_tensor_ae(Xva)
    X_test = ke_tensor_ae(Xte) if final and Xte is not None else None

    # Arsitektur Convolutional Autoencoder + Latent Classifier Head
    class AudioAutoencoderClassifier(nn.Module):
        def __init__(self, latent_dim=64, num_classes=10):
            super().__init__()
            # Encoder: mengompresi spektrogram Log-mel ke representasi bottleneck laten
            self.encoder = nn.Sequential(
                nn.Conv2d(1, 16, kernel_size=3, stride=2, padding=1),  # [B, 16, 32, T/2]
                nn.BatchNorm2d(16),
                nn.ReLU(inplace=True),
                nn.Conv2d(16, 32, kernel_size=3, stride=2, padding=1),  # [B, 32, 16, T/4]
                nn.BatchNorm2d(32),
                nn.ReLU(inplace=True),
                nn.AdaptiveAvgPool2d((4, 4))
            )
            # Proyeksi ke ruang laten kompak
            self.latent = nn.Linear(32 * 4 * 4, latent_dim)
            # Classifier Head dari representasi laten yang telah dikompresi
            self.classifier = nn.Sequential(
                nn.Linear(latent_dim, 64),
                nn.ReLU(inplace=True),
                nn.Dropout(0.3),
                nn.Linear(64, num_classes)
            )

        def forward(self, x):
            f = self.encoder(x)
            f = torch.flatten(f, 1)
            z = self.latent(f)
            return self.classifier(z)

    model = AudioAutoencoderClassifier(latent_dim=64, num_classes=10)
    optimizer = torch.optim.Adam(model.parameters(), lr=0.001, weight_decay=1e-4)

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
