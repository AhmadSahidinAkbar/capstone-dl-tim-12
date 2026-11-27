"""Entrypoint simulasi meja uji Tim 12."""
from __future__ import annotations

import argparse

from src.common.gladi_simulasi import jalankan_gladi_simulasi


def main():
    parser = argparse.ArgumentParser(description="Jalankan simulasi rencana sesi meja uji.")
    parser.add_argument("--simulasi", action="store_true", help="Jalankan mode simulasi.")
    parser.add_argument("aksi", choices=["jalankan"])
    parser.add_argument("rencana", help="Path ke berkas YAML rencana eksperimen.")
    args = parser.parse_args()

    if not args.simulasi:
        parser.error("mode saat ini harus ditentukan dengan --simulasi")
    jalankan_gladi_simulasi(args.rencana)


if __name__ == "__main__":
    main()
