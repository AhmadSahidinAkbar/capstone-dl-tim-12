"""Modul Pemotong Jendela Audio - Tim 12 Capstone Deep Learning
Kasus: Perintah Suara Pengendali Meja (10 kata)
Penanggung Jawab: Kharisma Mustika Sari (123450034) - Penjaga Data & Evaluasi

Protokol Pemotongan:
1. Setiap kondisi eksperimen berdurasi 2.5 detik pada laju sampel 16 kHz.
2. Membuang 1.0 detik pertama (transisi alat & artefak awal kondisi).
3. Mengambil jendela 1.0 detik (16.000 sampel) di sekitar ucapan kata target
   menggunakan deteksi pusat energi (Short-Time Energy) agar kata pendek
   seperti 'ya' atau kata panjang tidak terpotong.
"""
from __future__ import annotations

import numpy as np


def potong_jendela_audio(
    sinyal: np.ndarray,
    sr: int = 16000,
    durasi_buang_awal: float = 1.0,
    durasi_jendela: float = 1.0,
) -> np.ndarray:
    """Memotong jendela audio 1 detik sesuai protokol kasus Tim 12.

    Parameters
    ----------
    sinyal : np.ndarray
        Array 1D sinyal audio mentah.
    sr : int, optional
        Sample rate audio, default 16000 Hz.
    durasi_buang_awal : float, optional
        Durasi awal kondisi yang dibuang (detik), default 1.0 detik.
    durasi_jendela : float, optional
        Panjang jendela keluaran yang diinginkan (detik), default 1.0 detik (16.000 sampel).

    Returns
    -------
    np.ndarray
        Array 1D berukuran tepat (sr * durasi_jendela) sampel.
    """
    sinyal = np.asarray(sinyal, dtype=np.float32)
    n_buang = int(durasi_buang_awal * sr)
    n_target = int(durasi_jendela * sr)

    # 1. Buang bagian awal (transisi alat/kipas)
    if len(sinyal) > n_buang:
        sisa = sinyal[n_buang:]
    else:
        sisa = sinyal

    # Jika panjang sisa kurang dari target jendela, lakukan zero-padding di belakang
    if len(sisa) <= n_target:
        hasil = np.zeros(n_target, dtype=np.float32)
        hasil[: len(sisa)] = sisa
        return hasil

    # 2. Deteksi pusat energi suara untuk menentukan jendela 1 detik
    # Menggunakan moving energy window untuk mencari interval dengan energi tertinggi
    ukuran_frame = int(0.025 * sr)  # frame 25 ms
    langkah = int(0.010 * sr)       # hop 10 ms
    
    # Hitung energi jangka pendek
    kuadrat = sisa ** 2
    n_langkah = (len(sisa) - ukuran_frame) // langkah + 1
    if n_langkah > 0:
        energi_frame = np.array([
            np.sum(kuadrat[i * langkah : i * langkah + ukuran_frame])
            for i in range(n_langkah)
        ])
        idx_puncak = int(np.argmax(energi_frame) * langkah + ukuran_frame // 2)
    else:
        idx_puncak = len(sisa) // 2

    # Tempatkan jendela 1 detik dengan pusat di sekitar puncak ucapan
    # Letakkan ucapan kira-kira pada 20%-40% dari awal jendela
    awal = idx_puncak - int(0.3 * n_target)
    awal = max(0, min(awal, len(sisa) - n_target))
    akhir = awal + n_target

    hasil = sisa[awal:akhir]
    return hasil.astype(np.float32)


def potong_batch(
    daftar_sinyal: list[np.ndarray],
    sr: int = 16000,
    durasi_buang_awal: float = 1.0,
    durasi_jendela: float = 1.0,
) -> np.ndarray:
    """Memotong sekumpulan sinyal audio menjadi matriks berdimensi [N, n_sampel]."""
    hasil = [
        potong_jendela_audio(s, sr=sr, durasi_buang_awal=durasi_buang_awal, durasi_jendela=durasi_jendela)
        for s in daftar_sinyal
    ]
    return np.stack(hasil, axis=0)


if __name__ == "__main__":
    print("=== PENGUJIAN FUNGSI PEMOTONG JENDELA AUDIO (TIM 12) ===")
    sr = 16000
    durasi_total = 2.5
    n_total = int(durasi_total * sr)  # 40.000 sampel

    # Simulasi kondisi eksperimen:
    # 0.0 - 1.0s: bising alat / transisi
    # 1.3 - 1.7s: ucapan kata perintah (sinusoidal burst)
    # 1.7 - 2.5s: jeda akhir
    t = np.linspace(0, durasi_total, n_total, endpoint=False)
    sinyal_uji = 0.05 * np.random.randn(n_total).astype(np.float32)
    
    # Sisipkan simulasi ucapan pada detik ke-1.3 s.d. 1.6 (durasi 0.3s, misal kata 'ya')
    idx_ucapan = (t >= 1.3) & (t <= 1.6)
    sinyal_uji[idx_ucapan] += np.sin(2 * np.pi * 300 * t[idx_ucapan]).astype(np.float32)

    potongan = potong_jendela_audio(sinyal_uji, sr=sr)

    print(f"Panjang sinyal mentah : {len(sinyal_uji)} sampel ({len(sinyal_uji)/sr:.1f} detik)")
    print(f"Panjang hasil potong  : {len(potongan)} sampel ({len(potongan)/sr:.1f} detik)")
    assert len(potongan) == 16000, "Ukuran hasil potong harus tepat 16000 sampel (1 detik)!"
    print("[BERHASIL] Fungsi pemotong jendela teruji dan valid untuk data simulasi tim.")
