import os
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

BASE_DIR = Path(r"c:\Users\ahmad\workbench-workspace\capstone-dl-tim-12")
NPZ_PATH = BASE_DIR / "data" / "audio_primer_16khz.npz"
CSV_PATH = BASE_DIR / "data" / "ringkasan_data_primer.csv"
PNG_PATH = BASE_DIR / "data" / "visualisasi_spektrogram_10_kata.png"

# Muat data
data = np.load(NPZ_PATH)
X = data["X"]            # [360, 64, 32]
y = data["y"]            # [360]
partisipan = data["partisipan"]  # [360]

kata_map = {
    0: "nyalakan", 1: "matikan", 2: "kipas", 3: "lampu", 4: "pompa",
    5: "naik", 6: "turun", 7: "berhenti", 8: "ya", 9: "batal"
}

# 1. Buat file CSV ringkasan tabel per kondisi agar bisa dibuka di Excel / VS Code
with open(CSV_PATH, "w", encoding="utf-8") as f:
    f.write("no_kondisi,partisipan,kelas_id,kata,rata_energi,min_val,max_val\n")
    for i in range(len(X)):
        p = partisipan[i]
        cls = y[i]
        k = kata_map[cls]
        mean_val = float(np.mean(X[i]))
        min_v = float(np.min(X[i]))
        max_v = float(np.max(X[i]))
        f.write(f"{i+1},{p},{cls},{k},{mean_val:.4f},{min_v:.4f},{max_v:.4f}\n")

print(f"[OK] CSV ringkasan dibuat: {CSV_PATH}")

# 2. Buat gambar spektrogram perwakilan 10 kata
fig, axes = plt.subplots(2, 5, figsize=(16, 7))
axes = axes.flatten()

for cls_idx in range(10):
    # Ambil sampel pertama untuk tiap kata
    sample_idx = np.where(y == cls_idx)[0][0]
    spectrogram = X[sample_idx]  # [64, 32]
    
    ax = axes[cls_idx]
    im = ax.imshow(spectrogram, origin='lower', aspect='auto', cmap='magma')
    ax.set_title(f"Kata: {kata_map[cls_idx]}\n(Sampel #{sample_idx+1}, {partisipan[sample_idx]})", fontsize=11, fontweight='bold')
    ax.set_xlabel("Frame Waktu (32)")
    ax.set_ylabel("Pita Mel (64)")

plt.suptitle("Visualisasi Log-mel Spektrogram 64 Pita - 10 Kata Meja Uji Fisik (Tim 12)", fontsize=14, fontweight='bold')
plt.tight_layout()
plt.savefig(PNG_PATH, dpi=150)
plt.close()

print(f"[OK] Gambar spektrogram dibuat: {PNG_PATH}")
