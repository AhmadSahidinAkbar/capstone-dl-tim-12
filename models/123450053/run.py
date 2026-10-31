"""Kerangka run.py Khazanatl Ilmi (123450053)
Jalur: RNN -> LSTM/GRU atas Baris Citra (Modul 07-08)
Kasus: Perintah Suara Pengendali Meja 10 Kata (Log-mel 64 pita, 1 detik)
Tugas Sampingan: Integrator Sistem
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

NIM = "123450053"
JALUR = "rnn"


def latih_dan_prediksi(seed: int, final: bool) -> tuple[np.ndarray, np.ndarray | None]:
    """Model Sekuensial Bidirectional GRU memproses langkah waktu spektrogram Log-mel."""
    import torch
    import torch.nn as nn
    import torch.nn.functional as F

    torch.manual_seed(seed)
    np.random.seed(seed)

    Xtr, ytr, Xva, _, Xte, _ = data.muat()

    def ke_tensor_sekuensial(X):
        # Format input menjadi [Batch, Time_Steps, Mel_Features]
        arr = np.asarray(X, dtype=np.float32)
        if arr.ndim == 2:
            arr = arr.reshape(len(arr), 32, -1)
        elif arr.ndim == 3:
            # Jika [N, 64, T], lakukan transpose ke [N, T, 64]
            if arr.shape[1] == 64:
                arr = np.transpose(arr, (0, 2, 1))
        return torch.tensor(arr)

    X_train, y_train = ke_tensor_sekuensial(Xtr), torch.tensor(np.asarray(ytr, dtype=np.int64))
    X_val = ke_tensor_sekuensial(Xva)
    X_test = ke_tensor_sekuensial(Xte) if final and Xte is not None else None

    # Arsitektur Bi-GRU untuk Analisis Runtun Waktu Akustik
    class AudioBiGRU(nn.Module):
        def __init__(self, input_size=64, hidden_size=64, num_layers=2, num_classes=10):
            super().__init__()
            self.gru = nn.GRU(
                input_size=input_size,
                hidden_size=hidden_size,
                num_layers=num_layers,
                batch_first=True,
                bidirectional=True,
                dropout=0.2 if num_layers > 1 else 0.0
            )
            self.fc = nn.Sequential(
                nn.Linear(hidden_size * 2, 64),
                nn.ReLU(inplace=True),
                nn.Dropout(0.3),
                nn.Linear(64, num_classes)
            )

        def forward(self, x):
            # x: [Batch, Seq_Len, Features]
            out, _ = self.gru(x)
            # Pooling rata-rata temporal atas seluruh frame langkah waktu
            out = torch.mean(out, dim=1)
            return self.fc(out)

    input_dim = X_train.shape[-1]
    model = AudioBiGRU(input_size=input_dim, hidden_size=64, num_layers=2, num_classes=10)
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
            torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=5.0)
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
