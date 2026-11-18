"""Skrip Ekstraksi dan Pembuatan Data Primer Meja Uji - Tim 12
Mengubah 21 rekaman WAV (48 kHz) dari folder meja uji menjadi:
  - X: [360, 64, 32] Log-mel 64 pita frekuensi, 1 detik (16 kHz)
  - y: [360] Label 10 kelas (0..9)
  - partisipan: [360] ID penutur P01..P06
Disimpan ke data/audio_primer_16khz.npz dan memperbarui data/MANIFEST.json
"""
import os
import sys
import wave
import json
import hashlib
from pathlib import Path
import numpy as np
import scipy.signal

# Path konfigurasi
BASE_DIR = Path(r"c:\Users\ahmad\workbench-workspace\capstone-dl-tim-12")
RAW_AUDIO_DIR = Path(r"D:\Downloads\tim12_web-20261116-175659-113b\audio")
OUTPUT_NPZ = BASE_DIR / "data" / "audio_primer_16khz.npz"
MANIFEST_PATH = BASE_DIR / "data" / "MANIFEST.json"

# Import pemotong tim
sys.path.insert(0, str(BASE_DIR))
from src.common.pemotong import potong_jendela_audio

def muat_semua_audio_mentah(folder_audio):
    """Membaca dan menyatukan seluruh potongan WAV 48 kHz secara berurutan."""
    berkas_wav = sorted([f for f in folder_audio.glob("*.wav")])
    print(f"[*] Menemukan {len(berkas_wav)} berkas audio WAV mentah di {folder_audio}")
    
    daftar_sampel = []
    sr_asli = 48000
    for f in berkas_wav:
        with wave.open(str(f), "rb") as wf:
            sr_asli = wf.getframerate()
            n_frames = wf.getnframes()
            data_bytes = wf.readframes(n_frames)
            # Konversi int16 ke float32 [-1.0, 1.0]
            audio_array = np.frombuffer(data_bytes, dtype=np.int16).astype(np.float32) / 32768.0
            daftar_sampel.append(audio_array)
            
    sinyal_lengkap = np.concatenate(daftar_sampel)
    durasi_detik = len(sinyal_lengkap) / sr_asli
    print(f"[*] Total audio mentah tergabung: {len(sinyal_lengkap)} sampel ({durasi_detik:.2f} detik / {durasi_detik/60:.2f} menit)")
    return sinyal_lengkap, sr_asli

def resample_ke_16khz(sinyal, sr_asli=48000, sr_target=16000):
    """Menurunkan laju sampel dari 48 kHz ke 16 kHz."""
    print(f"[*] Melakukan resampling dari {sr_asli} Hz ke {sr_target} Hz...")
    n_target = int(len(sinyal) * sr_target / sr_asli)
    sinyal_16k = scipy.signal.resample(sinyal, n_target).astype(np.float32)
    return sinyal_16k

def bangun_mel_filterbank(sr=16000, n_fft=512, n_mels=64, fmin=0.0, fmax=8000.0):
    """Membuat filterbank Mel standar (64 pita frekuensi)."""
    def hz_to_mel(hz):
        return 2595.0 * np.log10(1.0 + hz / 700.0)

    def mel_to_hz(mel):
        return 700.0 * (10.0**(mel / 2595.0) - 1.0)

    mel_min = hz_to_mel(fmin)
    mel_max = hz_to_mel(fmax)
    mel_points = np.linspace(mel_min, mel_max, n_mels + 2)
    hz_points = mel_to_hz(mel_points)
    bin_points = np.floor((n_fft + 1) * hz_points / sr).astype(int)
    
    n_freq_bins = int(n_fft // 2 + 1)
    fbank = np.zeros((n_mels, n_freq_bins), dtype=np.float32)
    for m in range(1, n_mels + 1):
        f_m_minus = bin_points[m - 1]
        f_m = bin_points[m]
        f_m_plus = min(bin_points[m + 1], n_freq_bins)
        
        for k in range(f_m_minus, f_m):
            if f_m != f_m_minus and k < n_freq_bins:
                fbank[m - 1, k] = (k - bin_points[m - 1]) / (f_m - f_m_minus)
        for k in range(f_m, f_m_plus):
            if f_m_plus != f_m and k < n_freq_bins:
                fbank[m - 1, k] = (bin_points[m + 1] - k) / (bin_points[m + 1] - f_m)
                
    return fbank

def ekstrak_log_mel(audio_1s, fbank, sr=16000, n_fft=512, hop=500):
    """Mengekstrak Log-mel spektrogram [64, 32] dari 1 detik audio (16000 sampel)."""
    f, t, Zxx = scipy.signal.stft(
        audio_1s, 
        fs=sr, 
        nperseg=n_fft, 
        noverlap=n_fft - hop, 
        nfft=n_fft, 
        boundary=None
    )
    power = np.abs(Zxx[:, :32])**2
    mel = np.dot(fbank, power)
    log_mel = np.log(np.maximum(mel, 1e-6))
    # Normalisasi z-score per sampel untuk kestabilan konvergensi model
    log_mel = (log_mel - np.mean(log_mel)) / (np.std(log_mel) + 1e-6)
    return log_mel.astype(np.float32)

def main():
    print("=" * 65)
    print("PROSES PREPROCESSING DATA PRIMER MEJA UJI - TIM 12")
    print("=" * 65)
    
    if not RAW_AUDIO_DIR.exists():
        print(f"[!] Folder {RAW_AUDIO_DIR} tidak ditemukan!")
        return

    # 1. Muat dan gabungkan seluruh audio mentah
    audio_48k, sr_asli = muat_semua_audio_mentah(RAW_AUDIO_DIR)
    
    # 2. Resample ke 16.000 Hz
    audio_16k = resample_ke_16khz(audio_48k, sr_asli=sr_asli, sr_target=16000)
    
    # 3. Setup parameter desain eksperimen Tim 12
    partisipan_list = ["P01", "P02", "P03", "P04", "P05", "P06"]
    kata_list = ["nyalakan", "matikan", "kipas", "lampu", "pompa", "naik", "turun", "berhenti", "ya", "batal"]
    n_ulangan = 3
    taraf_kipas = [0, 255]
    
    durasi_per_kondisi = 3.0  # 2.5s bicara + 0.5s jeda
    sampel_per_kondisi = int(durasi_per_kondisi * 16000)  # 48.000 sampel
    
    total_kondisi = len(partisipan_list) * len(taraf_kipas) * len(kata_list) * n_ulangan
    print(f"[*] Desain eksperimen: {total_kondisi} kondisi total (360 kondisi).")
    
    fbank = bangun_mel_filterbank(sr=16000, n_fft=512, n_mels=64)
    
    X_list = []
    y_list = []
    p_list = []
    
    idx_kondisi = 0
    # Iterasi sekuensial sesuai urutan eksekusi eksperimen di meja
    for p_id in partisipan_list:
        for k_val in taraf_kipas:
            for kata_idx, kata_nama in enumerate(kata_list):
                for u in range(n_ulangan):
                    start_sampel = idx_kondisi * sampel_per_kondisi
                    end_sampel = start_sampel + sampel_per_kondisi
                    
                    if end_sampel <= len(audio_16k):
                        segmen_kondisi = audio_16k[start_sampel:end_sampel]
                    else:
                        segmen_kondisi = audio_16k[start_sampel:]
                        pad = np.zeros(sampel_per_kondisi - len(segmen_kondisi), dtype=np.float32)
                        segmen_kondisi = np.concatenate([segmen_kondisi, pad])
                        
                    # Potong jendela 1 detik menggunakan modul pemotong tim (Kartu #4)
                    audio_1s = potong_jendela_audio(segmen_kondisi, sr=16000, durasi_buang_awal=1.0, durasi_jendela=1.0)
                    
                    # Ekstrak Log-mel [64, 32]
                    fitur_mel = ekstrak_log_mel(audio_1s, fbank, sr=16000)
                    
                    X_list.append(fitur_mel)
                    y_list.append(kata_idx)
                    p_list.append(p_id)
                    
                    idx_kondisi += 1

    X = np.stack(X_list, axis=0)  # [360, 64, 32]
    y = np.array(y_list, dtype=np.int64)  # [360]
    partisipan_arr = np.array(p_list)
    
    print(f"[*] Berhasil mengekstrak matriks fitur X : {X.shape}, dtype={X.dtype}")
    print(f"[*] Berhasil mengekstrak vektor label y  : {y.shape}, kelas unik: {np.unique(y)}")
    
    # 4. Simpan ke data/audio_primer_16khz.npz
    OUTPUT_NPZ.parent.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(OUTPUT_NPZ, X=X, y=y, partisipan=partisipan_arr)
    print(f"[+] Dataset primer meja tersimpan di: {OUTPUT_NPZ}")
    
    # 5. Hitung SHA-256 dan perbarui data/MANIFEST.json
    hasher = hashlib.sha256()
    with open(OUTPUT_NPZ, "rb") as f:
        while chunk := f.read(8192):
            hasher.update(chunk)
    hash_npz = hasher.hexdigest()
    print(f"[+] SHA-256 data_hash baru: {hash_npz}")
    
    manifest_data = {
        "sumber": "Rekaman Meja Uji 5 Volt Fisik (16 Nov 2026, Sesi 126)",
        "berkas": [
            "data/audio_primer_16khz.npz"
        ],
        "catatan": "Data primer meja uji fisik 6 partisipan (P01-P06), 10 kata perintah suara, 2 taraf bising kipas (0 dan 255), 3 ulangan (total 360 kondisi). Format masukan: Log-mel 64 pita frekuensi, 1 detik (16 kHz).",
        "data_hash": hash_npz,
        "n_sampel": int(len(X)),
        "dimensi_fitur": list(X.shape[1:])
    }
    
    with open(MANIFEST_PATH, "w", encoding="utf-8") as f:
        json.dump(manifest_data, f, indent=2)
    print(f"[+] MANIFEST.json berhasil diperbarui dengan data_hash resmi tim.")
    print("=" * 65)

if __name__ == "__main__":
    main()
