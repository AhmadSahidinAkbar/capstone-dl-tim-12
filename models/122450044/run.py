"""Kerangka run.py anggota - Ahmad Sahidin Akbar (122450044)
Jalur: CNN dari Nol (Modul 05)
Kasus: Perintah Suara Pengendali Meja (10 kata)
Input: Log-mel spektrogram 64 pita frekuensi, durasi 1 detik (16 kHz)
"""
from __future__ import annotations

import argparse
import os
import subprocess
import sys
import time
from pathlib import Path

import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F

AKAR = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(AKAR))
from src.protokol import data  # noqa: E402

NIM = Path(__file__).resolve().parent.name
JALUR = "cnn"


class AudioCNN(nn.Module):
    """Arsitektur CNN 2D dari Nol untuk klasifikasi 10 kata perintah suara.
    Menerima input spektrogram Log-mel berdimensi [Batch, 1, 64, Waktu].
    """
    def __init__(self, n_kelas: int = 10, dropout: float = 0.3):
        super().__init__()
        # Blok Konvolusi 1
        self.conv1 = nn.Conv2d(1, 16, kernel_size=3, padding=1)
        self.bn1 = nn.BatchNorm2d(16)
        self.pool1 = nn.MaxPool2d(2, 2)  # [16, 32, Waktu/2]

        # Blok Konvolusi 2
        self.conv2 = nn.Conv2d(16, 32, kernel_size=3, padding=1)
        self.bn2 = nn.BatchNorm2d(32)
        self.pool2 = nn.MaxPool2d(2, 2)  # [32, 16, Waktu/4]

        # Blok Konvolusi 3
        self.conv3 = nn.Conv2d(32, 64, kernel_size=3, padding=1)
        self.bn3 = nn.BatchNorm2d(64)
        self.pool3 = nn.AdaptiveAvgPool2d((4, 4))  # Menjaga dimensi output adaptif [64, 4, 4]

        # Classifier Head
        self.dropout1 = nn.Dropout(dropout)
        self.fc1 = nn.Linear(64 * 4 * 4, 64)
        self.dropout2 = nn.Dropout(0.2)
        self.fc2 = nn.Linear(64, n_kelas)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        # x: [Batch, 1, 64, Waktu]
        x = self.pool1(F.relu(self.bn1(self.conv1(x))))
        x = self.pool2(F.relu(self.bn2(self.conv2(x))))
        x = self.pool3(F.relu(self.bn3(self.conv3(x))))
        x = torch.flatten(x, 1)
        x = self.dropout1(x)
        x = F.relu(self.fc1(x))
        x = self.dropout2(x)
        return self.fc2(x)


def ke_tensor_4d(X: np.ndarray | None) -> torch.Tensor | None:
    """Mengubah matriks input spektrogram menjadi tensor 4D [Batch, Channel, Freq, Time]."""
    if X is None:
        return None
    arr = np.asarray(X, dtype=np.float32)
    if arr.ndim == 3:
        arr = np.expand_dims(arr, axis=1)  # [N, 1, 64, Waktu]
    elif arr.ndim == 2:
        arr = arr.reshape(len(arr), 1, 64, -1)
    return torch.tensor(arr)


def latih_dan_prediksi(seed: int, final: bool) -> tuple[np.ndarray, np.ndarray | None]:
    """Melatih CNN dari nol pada spektrogram Log-mel dan mengembalikan prediksi validasi."""
    torch.manual_seed(seed)
    np.random.seed(seed)

    Xtr, ytr, Xva, _, Xte, _ = data.muat()
    X_train = ke_tensor_4d(Xtr)
    y_train = torch.tensor(np.asarray(ytr, dtype=np.int64))
    X_val = ke_tensor_4d(Xva)

    model = AudioCNN(n_kelas=10, dropout=0.3)
    optimizer = torch.optim.AdamW(model.parameters(), lr=1e-3, weight_decay=1e-4)
    kriteria = nn.CrossEntropyLoss()

    # Pelatihan mini-batch
    batch_size = 32
    epochs = 20
    model.train()
    dataset_size = len(X_train)

    for epoch in range(epochs):
        indices = torch.randperm(dataset_size)
        for i in range(0, dataset_size, batch_size):
            batch_idx = indices[i:i + batch_size]
            bx, by = X_train[batch_idx], y_train[batch_idx]

            optimizer.zero_grad()
            out = model(bx)
            loss = kriteria(out, by)
            loss.backward()
            optimizer.step()

    # Evaluasi
    model.eval()
    with torch.no_grad():
        out_val = model(X_val)
        pred_val = out_val.argmax(dim=1).cpu().numpy()

        pred_test = None
        if final and Xte is not None:
            X_test = ke_tensor_4d(Xte)
            out_test = model(X_test)
            pred_test = out_test.argmax(dim=1).cpu().numpy()

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

    perintah = [
        sys.executable, "-m", "src.common.evaluate",
        "--nim", NIM,
        "--model", JALUR,
        "--seed", str(a.seed),
        "--pred-val", str(out / "pred_val.npy"),
        "--durasi", f"{durasi:.1f}",
        "--perangkat", a.perangkat
    ]
    if pred_test is not None:
        np.save(out / "pred_test.npy", np.asarray(pred_test))
        perintah += ["--pred-test", str(out / "pred_test.npy")]

    env = os.environ.copy()
    env["PYTHONUTF8"] = "1"
    subprocess.run(perintah, check=True, cwd=AKAR, env=env)


if __name__ == "__main__":
    main()
