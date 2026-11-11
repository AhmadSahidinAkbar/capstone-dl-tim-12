"""Kerangka run.py Khazanatil Ilmi (123450053)
Jalur: RNN -> Bidirectional GRU atas Runtun Waktu Spektrogram (Modul 07-08)
Kasus: Perintah Suara Pengendali Meja 10 Kata (Log-mel 64 pita, 1 detik)
Tugas Sampingan: Integrator Sistem
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
JALUR = "rnn"


class AudioBiGRU(nn.Module):
    """Arsitektur Bidirectional GRU untuk Analisis Runtun Waktu Akustik (Log-mel Spektrogram)."""

    def __init__(
        self,
        input_size: int = 64,
        hidden_size: int = 64,
        num_layers: int = 2,
        num_classes: int = 10,
        dropout: float = 0.2,
    ) -> None:
        super().__init__()
        self.gru = nn.GRU(
            input_size=input_size,
            hidden_size=hidden_size,
            num_layers=num_layers,
            batch_first=True,
            bidirectional=True,
            dropout=dropout if num_layers > 1 else 0.0,
        )
        self.fc = nn.Sequential(
            nn.Linear(hidden_size * 2, 64),
            nn.ReLU(inplace=True),
            nn.Dropout(0.3),
            nn.Linear(64, num_classes),
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        # Input shape: [Batch, Time_Steps, Mel_Features]
        out, _ = self.gru(x)
        # Temporal mean pooling atas seluruh frame waktu
        out = torch.mean(out, dim=1)
        return self.fc(out)


def ke_tensor_sekuensial(X: np.ndarray | None) -> torch.Tensor | None:
    """Format input menjadi tensor [Batch, Time_Steps, Mel_Features]."""
    if X is None:
        return None
    arr = np.asarray(X, dtype=np.float32)
    if arr.ndim == 2:
        # Jika bentuk pipih 2D, bentuk ulang ke [N, 32, 64] bila kelipatan 64
        if arr.shape[1] % 64 == 0:
            arr = arr.reshape(len(arr), -1, 64)
        else:
            arr = arr.reshape(len(arr), 32, -1)
    elif arr.ndim == 3:
        # Jika [N, 64, T], lakukan transpose ke urutan sekuensial [N, T, 64]
        if arr.shape[1] == 64:
            arr = np.transpose(arr, (0, 2, 1))
    return torch.tensor(arr)


def latih_dan_prediksi(seed: int, final: bool) -> tuple[np.ndarray, np.ndarray | None]:
    """Melatih model Bi-GRU dan mengembalikan tuple (pred_val, pred_test)."""
    torch.manual_seed(seed)
    np.random.seed(seed)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    Xtr, ytr, Xva, _, Xte, _ = data.muat()

    X_train_tensor = ke_tensor_sekuensial(Xtr)
    assert X_train_tensor is not None, "Data latih tidak boleh None"
    X_train = X_train_tensor.to(device)
    y_train = torch.tensor(np.asarray(ytr, dtype=np.int64), device=device)

    X_val_tensor = ke_tensor_sekuensial(Xva)
    assert X_val_tensor is not None, "Data validasi tidak boleh None"
    X_val = X_val_tensor.to(device)

    X_test_tensor = ke_tensor_sekuensial(Xte) if final and Xte is not None else None
    X_test = X_test_tensor.to(device) if X_test_tensor is not None else None

    input_dim = X_train.shape[-1]
    model = AudioBiGRU(input_size=input_dim, hidden_size=64, num_layers=2, num_classes=10).to(device)
    optimizer = torch.optim.Adam(model.parameters(), lr=0.001, weight_decay=1e-4)

    # Siklus pelatihan (anggaran CPU <= 20 menit)
    model.train()
    batch_size = 32
    n = len(X_train)
    epochs = 5

    for _ in range(epochs):
        perm = np.random.permutation(n)
        for i in range(0, n, batch_size):
            idx = perm[i : i + batch_size]
            optimizer.zero_grad()
            out = model(X_train[idx])
            loss = F.cross_entropy(out, y_train[idx])
            loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=5.0)
            optimizer.step()

    # Tahap evaluasi & inferensi
    model.eval()
    with torch.no_grad():
        pred_val = model(X_val).argmax(1).cpu().numpy()
        pred_test = model(X_test).argmax(1).cpu().numpy() if X_test is not None else None

    return pred_val, pred_test


def main() -> None:
    ap = argparse.ArgumentParser(description=f"Model {JALUR} {NIM}")
    ap.add_argument("--seed", type=int, required=True, help="Seed pengacakan pelatihan")
    ap.add_argument("--final", action="store_true", help="Evaluasi data uji sekali di sprint terakhir")
    ap.add_argument("--perangkat", default="cpu laptop", help="Keterangan perangkat eksekusi")
    a = ap.parse_args()

    t0 = time.time()
    pred_val, pred_test = latih_dan_prediksi(a.seed, a.final)
    durasi = time.time() - t0

    out = AKAR / "results" / NIM
    out.mkdir(parents=True, exist_ok=True)
    np.save(out / "pred_val.npy", np.asarray(pred_val))

    perintah = [
        sys.executable,
        "-m",
        "src.common.evaluate",
        "--nim",
        NIM,
        "--model",
        JALUR,
        "--seed",
        str(a.seed),
        "--pred-val",
        str(out / "pred_val.npy"),
        "--durasi",
        f"{durasi:.1f}",
        "--perangkat",
        a.perangkat,
    ]
    if pred_test is not None:
        np.save(out / "pred_test.npy", np.asarray(pred_test))
        perintah += ["--pred-test", str(out / "pred_test.npy")]

    env = os.environ.copy()
    env["PYTHONUTF8"] = "1"
    subprocess.run(perintah, check=True, cwd=AKAR, env=env)


if __name__ == "__main__":
    main()
