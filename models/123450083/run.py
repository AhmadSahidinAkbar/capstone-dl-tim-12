"""Kerangka run.py untuk Nadya Ratu Anjani (123450083)
Jalur: Transformer Encoder atas Patch (Modul 09)
Kasus: Perintah Suara Pengendali Meja 10 Kata (Log-mel 64 pita, 1 detik)
Tugas Sampingan: Analis Utama
"""
from __future__ import annotations

import argparse
import math
import subprocess
import sys
import time
from pathlib import Path

import numpy as np

AKAR = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(AKAR))
from src.protokol import data

NIM = "123450083"
JALUR = "trf"


def latih_dan_prediksi(seed: int, final: bool) -> tuple[np.ndarray, np.ndarray | None]:
    """Audio Spectrogram Transformer (AST) berbasis patch encoder dan self-attention."""
    import torch
    import torch.nn as nn
    import torch.nn.functional as F

    torch.manual_seed(seed)
    np.random.seed(seed)

    Xtr, ytr, Xva, _, Xte, _ = data.muat()

    def ke_tensor_ast(X):
        # Format input menjadi citra 1-channel [Batch, 1, 64, T]
        arr = np.asarray(X, dtype=np.float32)
        if arr.ndim == 2:
            arr = arr.reshape(len(arr), 1, 64, -1)
        elif arr.ndim == 3:
            arr = arr[:, np.newaxis, :, :]
        return torch.tensor(arr)

    X_train, y_train = ke_tensor_ast(Xtr), torch.tensor(np.asarray(ytr, dtype=np.int64))
    X_val = ke_tensor_ast(Xva)
    X_test = ke_tensor_ast(Xte) if final and Xte is not None else None

    # Arsitektur Audio Transformer Mini (Patch Embedding + Transformer Encoder)
    class AudioTransformerClassifier(nn.Module):
        def __init__(self, embed_dim=64, num_heads=4, num_layers=2, num_classes=10):
            super().__init__()
            # Proyeksi patch spektrogram (misal kernel 16x16 atau 8x8) menjadi representasi vektor
            self.patch_embed = nn.Conv2d(1, embed_dim, kernel_size=(16, 8), stride=(16, 8))
            encoder_layer = nn.TransformerEncoderLayer(
                d_model=embed_dim,
                nhead=num_heads,
                dim_feedforward=embed_dim * 2,
                dropout=0.2,
                activation="relu",
                batch_first=True
            )
            self.transformer = nn.TransformerEncoder(encoder_layer, num_layers=num_layers)
            self.cls_token = nn.Parameter(torch.zeros(1, 1, embed_dim))
            self.fc = nn.Sequential(
                nn.LayerNorm(embed_dim),
                nn.Dropout(0.3),
                nn.Linear(embed_dim, num_classes)
            )

        def forward(self, x):
            # x: [B, 1, Freq, Time]
            p = self.patch_embed(x)  # [B, embed_dim, H', W']
            p = p.flatten(2).transpose(1, 2)  # [B, num_patches, embed_dim]
            b, n, _ = p.shape
            cls = self.cls_token.expand(b, -1, -1)
            tokens = torch.cat([cls, p], dim=1)
            # Encoder self-attention
            out = self.transformer(tokens)
            # Ambil output representasi dari CLS token
            cls_out = out[:, 0]
            return self.fc(cls_out)

    model = AudioTransformerClassifier(embed_dim=64, num_heads=4, num_layers=2, num_classes=10)
    optimizer = torch.optim.AdamW(model.parameters(), lr=0.0005, weight_decay=1e-3)

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
