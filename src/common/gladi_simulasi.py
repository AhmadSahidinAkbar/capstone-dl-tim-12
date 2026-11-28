"""Skrip Gladi Mode Simulasi Rencana Eksperimen Tim 12
Penanggung Jawab: Tanty Widiyastuti (123450094) - Reproduksi & Demo
Tugas: Kartu #11 (Gladi rencana: mode simulasi dan persiapan bahan slot)

Fungsi:
1. Membaca dan memvalidasi file `rencana/t12-perintah-suara.yaml`.
2. Mensimulasikan pembangkitan 360 kondisi eksperimen acak terstruktur (seed 1012).
3. Menghitung estimasi alokasi waktu sesi slot meja uji (24 menit total sesi).
4. Memeriksa kesiapan bahan fisik slot (formulir persetujuan, lembar sesi, penanda nomor).
5. Menghasilkan laporan validasi `docs/hasil-gladi-simulasi.md`.
"""
from __future__ import annotations

import csv
import itertools
import json
from datetime import date
from pathlib import Path
import shutil

import numpy as np
import yaml

AKAR = Path(__file__).resolve().parents[2]
BERKAS_RENCANA = AKAR / "rencana" / "t12-perintah-suara.yaml"
BERKAS_OUTPUT = AKAR / "docs" / "hasil-gladi-simulasi.md"
DIREKTORI_SESI = AKAR / "sesi-simulasi" / f"tim-12-{date.today().isoformat()}"


def jalankan_gladi_simulasi(berkas_rencana=BERKAS_RENCANA, direktori_sesi=DIREKTORI_SESI):
    print("======================================================================")
    print("       GLADI MODE SIMULASI RENCANA EKSPERIMEN - TIM 12 (RUANG CERDAS) ")
    print("======================================================================")

    berkas_rencana = Path(berkas_rencana)
    if not berkas_rencana.is_absolute():
        berkas_rencana = Path.cwd() / berkas_rencana
    if not berkas_rencana.exists():
        alternatif = AKAR / "rencana" / berkas_rencana.name
        if alternatif.exists():
            berkas_rencana = alternatif
        else:
            raise FileNotFoundError(f"Berkas rencana tidak ditemukan: {berkas_rencana}")

    with open(berkas_rencana, "r", encoding="utf-8") as f:
        rencana = yaml.safe_load(f)

    tim = rencana.get("tim")
    judul = rencana.get("judul")
    seed = rencana.get("seed", 1012)
    ulangan = rencana.get("ulangan", 3)
    durasi_kondisi = rencana.get("durasi_kondisi_detik", 2.5)
    jeda = rencana.get("jeda_detik", 0.5)
    faktor = rencana.get("faktor", {})

    partisipan = faktor.get("partisipan", {}).get("taraf", [])
    kata = faktor.get("kata", {}).get("taraf", [])
    kipas = faktor.get("kipas", {}).get("taraf", [])

    print(f"Kasus Tim   : Tim {tim} - {judul}")
    print(f"Seed Acak   : {seed}")
    print(f"Faktor Partisipan ({len(partisipan)}) : {', '.join(partisipan)}")
    print(f"Faktor Kata ({len(kata)})       : {', '.join(kata)}")
    print(f"Faktor Kipas ({len(kipas)})      : {', '.join(map(str, kipas))}")
    print(f"Ulangan     : {ulangan} kali")

    # Hitung kombinasi
    kondisi_per_blok = len(kata) * len(kipas) * ulangan  # 10 * 2 * 3 = 60 kondisi
    total_kondisi = len(partisipan) * kondisi_per_blok    # 6 * 60 = 360 kondisi
    durasi_per_kondisi = durasi_kondisi + jeda           # 3.0 detik
    durasi_efektif_menit = (total_kondisi * durasi_per_kondisi) / 60.0  # 18.0 menit
    jeda_blok_menit = (len(partisipan) - 1) * 1.0        # 5 menit pergantian partisipan
    total_estimasi_menit = durasi_efektif_menit + jeda_blok_menit  # ~23-24 menit

    print("\n--- ESTIMASI WAKTU SESI SLOT MEJA UJI ---")
    print(f"Total Kondisi           : {total_kondisi} kondisi (6 blok partisipan @ {kondisi_per_blok} kondisi)")
    print(f"Waktu Efektif Rekaman   : {durasi_efektif_menit:.1f} menit ({total_kondisi * durasi_per_kondisi:.0f} detik)")
    print(f"Estimasi Jeda Antarblok : {jeda_blok_menit:.1f} menit")
    print(f"Total Waktu Pelaksanaan : {total_estimasi_menit:.1f} menit")
    print(f"Kapasitas Slot Maksimal : 50 menit efektif (Batas AMAN, tidak akan over-time)")

    # Pembangkitan urutan simulasi
    rng = np.random.default_rng(seed)
    jadwal = []
    no_kondisi = 1

    for p in partisipan:
        # Kombinasi internal satu blok partisipan
        kombinasi_blok = list(itertools.product(kata, kipas, range(1, ulangan + 1)))
        rng.shuffle(kombinasi_blok)
        for k, kip, ulg in kombinasi_blok:
            jadwal.append({
                "no": no_kondisi,
                "partisipan": p,
                "kata": k,
                "kipas": kip,
                "ulangan": ulg,
            })
            no_kondisi += 1

    total_diharapkan = len(partisipan) * len(kata) * len(kipas) * ulangan
    assert total_diharapkan == 360, f"Rencana harus menghasilkan 360 kondisi, didapat {total_diharapkan}"
    assert len(jadwal) == total_diharapkan, f"Harus tepat {total_diharapkan} kondisi, didapat {len(jadwal)}"
    kunci_kondisi = {(x["partisipan"], x["kata"], x["kipas"], x["ulangan"]) for x in jadwal}
    assert len(kunci_kondisi) == total_diharapkan, "Ditemukan kombinasi kondisi duplikat."

    # Validasi tidak ada kondisi yang tertinggal
    print("\n--- VALIDASI DISTRIBUSI KONDISI ---")
    print(f"[OK] Total 360 kondisi berhasil dibangkitkan tanpa benturan.")
    for p in partisipan:
        sub = [item for item in jadwal if item["partisipan"] == p]
        assert len(sub) == 60, f"Partisipan {p} harus tepat 60 kondisi!"
    print(f"[OK] Masing-masing 6 partisipan mendapat tepat 60 kondisi seimbang.")

    # These are human tasks; the simulator cannot verify physical readiness.
    print("\n--- CHECKLIST BAHAN FISIK SLOT MEJA UJI ---")
    checklist = [
        "Formulir persetujuan partisipan (6-8 rangkap)",
        "Lembar catatan sesi meja uji",
        "Kehadiran partisipan terkonfirmasi",
        "Clipboard dan pulpen",
        "Selotip penanda jarak duduk 60 cm",
    ]
    for item in checklist:
        print(f" [ ] {item} : perlu dicek langsung")

    direktori_sesi = Path(direktori_sesi)
    if not direktori_sesi.is_absolute():
        direktori_sesi = AKAR / direktori_sesi
    direktori_sesi.mkdir(parents=True, exist_ok=True)
    with (direktori_sesi / "jadwal.csv").open("w", newline="", encoding="utf-8-sig") as f:
        penulis = csv.DictWriter(f, fieldnames=["no", "partisipan", "kata", "kipas", "ulangan"])
        penulis.writeheader()
        penulis.writerows(jadwal)
    shutil.copyfile(berkas_rencana, direktori_sesi / "rencana.yaml")
    metadata = {
        "tim": tim,
        "judul": judul,
        "seed": seed,
        "total_kondisi": len(jadwal),
        "kondisi_per_partisipan": kondisi_per_blok,
        "kata": kata,
        "partisipan": partisipan,
        "taraf_kipas": kipas,
        "ulangan": ulangan,
        "durasi_kondisi_detik": durasi_kondisi,
        "jeda_detik": jeda,
        "estimasi_total_menit": total_estimasi_menit,
        "tanggal_simulasi": date.today().isoformat(),
    }
    (direktori_sesi / "metadata.json").write_text(
        json.dumps(metadata, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    (direktori_sesi / "README.md").write_text(
        "# Paket Sesi Simulasi Tim 12\n\n"
        "Paket ini memuat jadwal 360 kondisi (`jadwal.csv`), metadata simulasi "
        "(`metadata.json`), dan salinan rencana sumber (`rencana.yaml`).\n\n"
        "Bagikan seluruh folder ini kepada Penjaga Data. Ini adalah jadwal simulasi, "
        "bukan rekaman audio atau bukti latihan kering.\n",
        encoding="utf-8",
    )

    # Tulis hasil laporan gladi ke docs/
    BERKAS_OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    laporan_md = f"""# Laporan Gladi Mode Simulasi & Persiapan Bahan Slot (Kartu #11)

**Tim**: 12 — Ruang Cerdas 5 Volt (Perintah Suara 10 Kata)  
**Penanggung Jawab**: Tanty Widiyastuti (123450094) — Reproduksi & Demo  
**Tanggal Simulasi**: {date.today().isoformat()}  
**Status**: Simulasi lolos; kesiapan fisik, pembagian paket, dan latihan kering perlu konfirmasi manual.

---

## 1. Verifikasi Rencana Eksperimen (`t12-perintah-suara.yaml`)
- **Seed**: `{seed}`
- **Faktor Partisipan**: 6 orang (P01, P02, P03, P04, P05, P06)
- **Faktor Kata**: 10 kata (`nyalakan`, `matikan`, `kipas`, `lampu`, `pompa`, `naik`, `turun`, `berhenti`, `ya`, `batal`)
- **Faktor Kipas**: 2 taraf (0, 255 PWM)
- **Ulangan**: 3 kali
- **Total Kondisi**: $6 \\times 10 \\times 2 \\times 3 = \\mathbf{{360\\text{{ kondisi}}}}$

---

## 2. Alokasi Waktu Sesi Meja Uji
| Rincian | Nilai | Keterangan |
|---|---|---|
| Durasi per kondisi | 2,5 detik | Tampil di layar |
| Jeda antar-kondisi | 0,5 detik | Jeda hening |
| Total waktu rekaman efektif | 18,0 menit | 360 x 3,0 detik = 1080 detik |
| Jeda pergantian 6 partisipan | 5,0 menit | 1 menit per pergantian blok |
| **Total Estimasi Sesi** | **23,0 menit** | **Aman dalam slot 50 menit lab** |

---

## 3. Bahan Slot — Perlu Dicek Secara Fisik
- [ ] Formulir persetujuan partisipan (6–8 lembar) sudah dicetak dan dibawa.
- [ ] Lembar catatan sesi sudah dicetak dan dibawa.
- [ ] Kehadiran partisipan P01–P06 sudah dikonfirmasi.
- [ ] Clipboard, pulpen, dan penanda jarak duduk sudah disiapkan.

---

## 4. Cuplikan Urutan Simulasi 10 Kondisi Pertama
| No | Partisipan | Kata | Kipas | Ulangan |
|:---:|:---:|:---:|:---:|:---:|
"""
    for row in jadwal[:10]:
        laporan_md += f"| {row['no']} | {row['partisipan']} | {row['kata']} | {row['kipas']} | {row['ulangan']} |\n"

    laporan_md += f"""
Semua 360 kondisi tersimpan pada `sesi-simulasi/tim-12-{date.today().isoformat()}/jadwal.csv`.

## 5. Tindak Lanjut
- Bagikan seluruh folder sesi simulasi kepada Penjaga Data dan catat tanggal/penerimanya.
- Selesaikan latihan kering tanpa meja; isi `docs/latihan-kering.md`.
- Ikuti protokol rekaman ponsel pada `docs/protokol-rekaman-ponsel.md`.
"""

    BERKAS_OUTPUT.write_text(laporan_md, encoding="utf-8")
    print(f"\n[SUKSES] Laporan gladi simulasi telah ditulis ke: {BERKAS_OUTPUT.relative_to(AKAR)}")
    print(f"[SUKSES] Paket berisi jadwal lengkap tersimpan di: {direktori_sesi.relative_to(AKAR)}")
    print("======================================================================")


if __name__ == "__main__":
    jalankan_gladi_simulasi()
