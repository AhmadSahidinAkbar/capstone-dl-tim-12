# Laporan Gladi Mode Simulasi & Persiapan Bahan Slot (Kartu #11)

**Tim**: 12 — Ruang Cerdas 5 Volt (Perintah Suara 10 Kata)  
**Penanggung Jawab**: Tanty Widiyastuti (123450094) — Reproduksi & Demo  
**Tanggal Simulasi**: 2026-11-11  
**Status**: Simulasi lolos; kesiapan fisik, pembagian paket, dan latihan kering perlu konfirmasi manual.

---

## 1. Verifikasi Rencana Eksperimen (`t12-perintah-suara.yaml`)
- **Seed**: `1012`
- **Faktor Partisipan**: 6 orang (P01, P02, P03, P04, P05, P06)
- **Faktor Kata**: 10 kata (`nyalakan`, `matikan`, `kipas`, `lampu`, `pompa`, `naik`, `turun`, `berhenti`, `ya`, `batal`)
- **Faktor Kipas**: 2 taraf (0, 255 PWM)
- **Ulangan**: 3 kali
- **Total Kondisi**: $6 \times 10 \times 2 \times 3 = \mathbf{360\text{ kondisi}}$

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
| 1 | P01 | nyalakan | 255 | 3 |
| 2 | P01 | pompa | 255 | 2 |
| 3 | P01 | pompa | 255 | 1 |
| 4 | P01 | nyalakan | 255 | 1 |
| 5 | P01 | batal | 0 | 2 |
| 6 | P01 | pompa | 255 | 3 |
| 7 | P01 | naik | 0 | 1 |
| 8 | P01 | matikan | 0 | 1 |
| 9 | P01 | ya | 255 | 1 |
| 10 | P01 | ya | 0 | 1 |

Semua 360 kondisi tersimpan pada `sesi-simulasi/tim-12-2026-11-11/jadwal.csv`.

## 5. Tindak Lanjut
- Bagikan seluruh folder sesi simulasi kepada Penjaga Data dan catat tanggal/penerimanya.
- Selesaikan latihan kering tanpa meja; isi `docs/latihan-kering.md`.
- Ikuti protokol rekaman ponsel pada `docs/protokol-rekaman-ponsel.md`.
