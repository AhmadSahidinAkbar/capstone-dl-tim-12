from __future__ import annotations

import argparse
import time
import subprocess
import sys
from pathlib import Path

import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.utils.data import TensorDataset, DataLoader
from torchvision.models import mobilenet_v3_small, MobileNet_V3_Small_Weights

from src.protokol import data

NIM = "123450034"
DEFAULT_SEED = 2026
EPOCHS = 10
BATCH_SIZE = 16
DEVICE = torch.device("cpu")


class SpectrogramMobileNet(nn.Module):
    def __init__(self, unfreeze_blocks=2):
        super().__init__()

        weights = MobileNet_V3_Small_Weights.DEFAULT
        self.backbone = mobilenet_v3_small(weights=weights)

        # Ganti klasifikasi ImageNet menjadi 10 kelas.
        in_features = self.backbone.classifier[-1].in_features
        self.backbone.classifier[-1] = nn.Linear(in_features, 10)

        # Bekukan fitur pretrained terlebih dahulu.
        for param in self.backbone.features.parameters():
            param.requires_grad = False

        # Fine-tuning dua blok fitur terakhir.
        if unfreeze_blocks > 0:
            for layer in list(self.backbone.features.children())[-unfreeze_blocks:]:
                for param in layer.parameters():
                    param.requires_grad = True

    def forward(self, x):
        # Bentuk awal: (batch, 64, 32)
        x = x.unsqueeze(1)
        x = torch.sigmoid(x)
        x = x.repeat(1, 3, 1, 1)

        # Ubah ukuran agar sesuai untuk MobileNetV3.
        x = F.interpolate(
            x, size=(128, 128),
            mode="bilinear", align_corners=False
        )

        # Normalisasi sesuai preprocessing bobot ImageNet.
        mean = x.new_tensor([0.485, 0.456, 0.406]).view(1, 3, 1, 1)
        std = x.new_tensor([0.229, 0.224, 0.225]).view(1, 3, 1, 1)
        x = (x - mean) / std

        return self.backbone(x)


def main(seed: int = DEFAULT_SEED, unfreeze_blocks: int = 2, run_tag: str = 'main'):
    torch.manual_seed(seed)
    np.random.seed(seed)
    torch.set_num_threads(2)
    output_dir = Path('results') / NIM
    output_dir.mkdir(parents=True, exist_ok=True)

    X_train, y_train, X_val, y_val, _, _ = data.muat()

    X_train = torch.tensor(X_train, dtype=torch.float32)
    y_train = torch.tensor(y_train, dtype=torch.long)
    X_val = torch.tensor(X_val, dtype=torch.float32)

    train_loader = DataLoader(
        TensorDataset(X_train, y_train),
        batch_size=BATCH_SIZE,
        shuffle=True
    )

    model = SpectrogramMobileNet(unfreeze_blocks=unfreeze_blocks).to(DEVICE)

    optimizer = torch.optim.AdamW(
        filter(lambda p: p.requires_grad, model.parameters()),
        lr=0.0001,
        weight_decay=0.0001
    )

    criterion = nn.CrossEntropyLoss()
    best_acc = -1.0
    start = time.time()

    print("=== TRANSFER LEARNING MOBILENETV3 SMALL ===")
    print("Perangkat:", DEVICE)
    print("Data latih:", len(X_train))
    print("Data validasi:", len(X_val))
    print("Jumlah kelas: 10")

    for epoch in range(EPOCHS):
        model.train()
        model.backbone.features.eval()

        # Blok terakhir yang dilatih tetap dalam mode train.
        if unfreeze_blocks > 0:
            for layer in list(model.backbone.features.children())[-unfreeze_blocks:]:
                layer.train()

        total_loss = 0.0

        for xb, yb in train_loader:
            xb, yb = xb.to(DEVICE), yb.to(DEVICE)

            optimizer.zero_grad()
            output = model(xb)
            loss = criterion(output, yb)
            loss.backward()
            optimizer.step()

            total_loss += loss.item() * len(xb)

        model.eval()
        with torch.no_grad():
            val_output = model(X_val.to(DEVICE))
            val_pred = val_output.argmax(dim=1).cpu().numpy()
            val_acc = float((val_pred == np.asarray(y_val)).mean())

        avg_loss = total_loss / len(X_train)
        print(
            f"Epoch {epoch + 1}/{EPOCHS} | "
            f"Loss: {avg_loss:.4f} | "
            f"Val Acc: {val_acc:.4f}"
        )

        if val_acc > best_acc:
            best_acc = val_acc
            Path("results/" + NIM).mkdir(parents=True, exist_ok=True)
            torch.save(
                model.state_dict(),
                str(output_dir / f"best_model_{run_tag}_seed{seed}.pth")
            )

    # Muat model dengan hasil validasi terbaik.
    model.load_state_dict(
        torch.load(
            "results/" + NIM + f"/best_model_seed{seed}.pth",
            map_location=DEVICE,
            weights_only=True
        )
    )

    model.eval()
    with torch.no_grad():
        val_output = model(X_val.to(DEVICE))
        pred_val = val_output.argmax(dim=1).cpu().numpy()

    output_dir = Path("results") / NIM
    np.save(output_dir / f"pred_val_{run_tag}_seed{seed}.npy", pred_val)
    np.save(output_dir / "pred_val.npy", pred_val)
    np.save(output_dir / "pred_val.npy", pred_val)

    duration = time.time() - start
    print("\nPrediksi validasi berhasil disimpan.")
    print("Akurasi validasi terbaik:", round(best_acc, 4))
    print("Durasi pelatihan:", round(duration, 2), "detik")

    command = [
        sys.executable, "-m", "src.common.evaluate",
        "--nim", NIM,
        "--model", "tl",
        "--seed", str(seed),
        "--pred-val", str(output_dir / f"pred_val_{run_tag}_seed{seed}.npy"),
        "--durasi", str(round(duration, 2)),
        "--perangkat", "cpu laptop"
    ]

    subprocess.run(command, check=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--seed", type=int, default=DEFAULT_SEED)
    parser.add_argument("--unfreeze-blocks", type=int, choices=[0, 1, 2], default=2)
    parser.add_argument("--run-tag", type=str, default="main")
    args = parser.parse_args()
    main(args.seed, args.unfreeze_blocks, args.run_tag)
