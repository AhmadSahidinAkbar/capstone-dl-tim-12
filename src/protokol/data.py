"""Pemuat data kasus tim — Tim 12 (SmartDesk Voice Control).
Kasus: Perintah Suara Pengendali Meja (10 kata)
Input: Log-mel spektrogram 64 pita frekuensi, durasi 1.0 detik (16 kHz)
Target: 10 kelas (0..9) perintah suara (+ bising/diam)
"""
from __future__ import annotations

from pathlib import Path
import numpy as np

from src.common import manifest, split

TUGAS = "klasifikasi"
BERKAS_DATA = manifest.AKAR / "data" / "audio_primer_16khz.npz"


def muat():
    """Memuat data Log-mel spektrogram 64 pita untuk kasus Tim 12."""
    if BERKAS_DATA.exists():
        arsip = np.load(BERKAS_DATA)
        X = arsip["X"]  # Matriks [N, 64, T] atau [N, fitur]
        y = arsip["y"].astype(np.int64)
        X_test = arsip.get("X_test", None)
        y_test = arsip.get("y_test", None)
        if y_test is not None:
            y_test = y_test.astype(np.int64)
    else:
        # Pembangkit data representasi awal untuk pengujian pipeline baseline Sprint 0
        rng = np.random.default_rng(2026)
        n_sampel = 180  # 6 partisipan x 10 kata x 3 ulangan
        X = rng.standard_normal((n_sampel, 64, 32), dtype=np.float32)
        y = np.repeat(np.arange(10), n_sampel // 10).astype(np.int64)
        X_test, y_test = None, None

    # Split baku menggunakan seed 2026 sesuai protokol starter
    tr, va = split.indeks(len(X), porsi_val=0.1, seed=2026)
    return X[tr], y[tr], X[va], y[va], X_test, y_test
