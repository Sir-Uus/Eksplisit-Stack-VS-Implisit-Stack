"""Buat Gambar 2 (waktu eksekusi median) dari results/time_results.csv.

Jalankan dari folder proyek (stack-comparison):
    pip install matplotlib        # sekali saja
    python profiling/plot_time.py

Keluaran: results/fig_waktu.png (300 dpi) dan results/fig_waktu.pdf.
(a) atas: ekspresi panjang tanpa kurung bersarang, skala log-log;
(b) bawah: kurung bersarang, skala linear.
Tersusun atas-bawah, selebar satu kolom IEEE (sekitar 3,5 inci).
"""

import csv
from pathlib import Path

import matplotlib.pyplot as plt

PROJECT_ROOT = Path(__file__).resolve().parents[1]
CSV_PATH = PROJECT_ROOT / "results" / "time_results.csv"
PNG_PATH = PROJECT_ROOT / "results" / "fig_waktu.png"
PDF_PATH = PROJECT_ROOT / "results" / "fig_waktu.pdf"


def load(pattern: str) -> tuple[list[int], list[float], list[float]]:
    """Baca ukuran dan median (dalam ms) untuk satu pola input."""
    sizes: list[int] = []
    iterative: list[float] = []
    recursive: list[float] = []
    with CSV_PATH.open(newline="", encoding="utf-8") as csv_file:
        for row in csv.DictReader(csv_file):
            if row["pattern"] != pattern:
                continue
            sizes.append(int(row["size"]))
            iterative.append(float(row["iterative_median_s"]) * 1000)
            recursive.append(float(row["recursive_median_s"]) * 1000)
    return sizes, iterative, recursive


def main() -> None:
    plt.rcParams.update({"font.size": 9, "font.family": "serif"})
    fig, (ax_a, ax_b) = plt.subplots(2, 1, figsize=(3.5, 5.2))

    n, it_n, rc_n = load("panjang")
    ax_a.plot(n, it_n, "o-", label="Iteratif")
    ax_a.plot(n, rc_n, "s--", label="Rekursif")
    ax_a.set_xscale("log")
    ax_a.set_yscale("log")
    ax_a.set_xlabel("Jumlah operand (n)")
    ax_a.set_ylabel("Waktu median (ms)")
    ax_a.set_title("(a) Tanpa kurung bersarang", fontsize=9)

    d, it_d, rc_d = load("bersarang")
    ax_b.plot(d, it_d, "o-", label="Iteratif")
    ax_b.plot(d, rc_d, "s--", label="Rekursif")
    ax_b.set_xlabel("Kedalaman kurung (d)")
    ax_b.set_ylabel("Waktu median (ms)")
    ax_b.set_title("(b) Kurung bersarang", fontsize=9)

    for ax in (ax_a, ax_b):
        ax.grid(True, which="both", alpha=0.3)
        ax.legend(frameon=False)

    fig.tight_layout()
    fig.savefig(PNG_PATH, dpi=300)
    fig.savefig(PDF_PATH)
    print(f"Tersimpan: {PNG_PATH}")
    print(f"Tersimpan: {PDF_PATH}")


if __name__ == "__main__":
    main()
