"""Pengukuran puncak memori parser iteratif vs rekursif (Bab IV.B).

Prosedur (sesuai Bagian II.F makalah):
- memori diukur dengan tracemalloc, dimulai SETELAH string masukan dibuat;
- hanya pemanggilan parse() yang diukur;
- 5 pengulangan per ukuran, dilaporkan sebagai median;
- puncak (peak) dilaporkan dalam KB (1 KB = 1024 byte).

Dua pola input yang sama dengan pengukuran waktu:
- "panjang": 1+2*3-4/5+6*7-... dengan n operand, tanpa kurung bersarang;
- "bersarang": 1+(1+(1+(...1))) dengan kedalaman kurung d.

Catatan: tracemalloc hanya melacak alokasi objek Python di heap. Ruang frame
Call Stack parser rekursif tidak terwakili penuh, sehingga angka kedua parser
tidak sepenuhnya setara (jelaskan ini di makalah).

Jalankan dari folder proyek:  python profiling/memory_bab4.py
Hasil disimpan ke results/memory_bab4_results.csv
(file memory_results.csv yang lama tidak ditimpa).
"""

import csv
import gc
import platform
import sys
import tracemalloc
from pathlib import Path
from statistics import median
from typing import Callable

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from parser.iterative_parser import parse as parse_iterative
from parser.recursive_parser import parse as parse_recursive

LONG_SIZES = (10, 100, 1000, 10_000, 50_000)
NESTED_DEPTHS = (10, 50, 100, 200, 320)
REPEATS = 5
RESULTS_PATH = PROJECT_ROOT / "results" / "memory_results.csv"
KB = 1024

Parser = Callable[[str], list[str]]


def build_long_expression(operands: int) -> str:
    """Bangun 1+2*3-4/5+... dengan jumlah operand tertentu, tanpa kurung."""
    operators = ("+", "*", "-", "/")
    parts = ["1"]
    for i in range(1, operands):
        parts.append(operators[(i - 1) % 4])
        parts.append(str(i % 9 + 1))
    return "".join(parts)


def build_nested_expression(depth: int) -> str:
    """Bangun 1+(1+(1+(...1))) dengan kedalaman kurung ``depth``."""
    return "1+(" * depth + "1" + ")" * depth


def measure(parser: Parser, expression: str) -> tuple[float, float]:
    """Kembalikan (median current, median peak) dalam KB untuk satu parser."""
    current_samples: list[float] = []
    peak_samples: list[float] = []
    for _ in range(REPEATS):
        gc.collect()
        tracemalloc.start()
        try:
            result = parser(expression)
            current, peak = tracemalloc.get_traced_memory()
        finally:
            tracemalloc.stop()
        current_samples.append(current / KB)
        peak_samples.append(peak / KB)
        del result
    return median(current_samples), median(peak_samples)


def smaller_percent(iterative: float, recursive: float) -> str:
    """Selisih relatif terhadap angka yang lebih besar, plus pemenangnya."""
    if iterative == recursive:
        return "setara"
    larger, smaller = max(iterative, recursive), min(iterative, recursive)
    winner = "rekursif" if recursive < iterative else "iteratif"
    return f"{winner} lebih kecil {(larger - smaller) / larger * 100:.1f}%"


def run_profiling() -> None:
    """Jalankan seluruh pengukuran, cetak tabel, dan tulis CSV."""
    print(f"Python  : {platform.python_version()} ({platform.python_implementation()})")
    print(f"Sistem  : {platform.platform()}")
    print(f"Prosesor: {platform.processor() or platform.machine()}\n")

    RESULTS_PATH.parent.mkdir(parents=True, exist_ok=True)
    jobs: list[tuple[str, int, str]] = []
    for n in LONG_SIZES:
        jobs.append(("panjang", n, build_long_expression(n)))
    for d in NESTED_DEPTHS:
        jobs.append(("bersarang", d, build_nested_expression(d)))

    header = (
        f"{'input':>10} {'iteratif peak (KB)':>19} {'rekursif peak (KB)':>19}  selisih"
    )
    print(header)
    print("-" * len(header))

    rows: list[list[object]] = []
    for pattern, size, expression in jobs:
        # Validasi keluaran identik (di luar pengukuran memori).
        if parse_iterative(expression) != parse_recursive(expression):
            raise AssertionError("Kedua parser menghasilkan postfix berbeda.")

        it_cur, it_peak = measure(parse_iterative, expression)
        rc_cur, rc_peak = measure(parse_recursive, expression)

        label = f"n={size}" if pattern == "panjang" else f"d={size}"
        print(
            f"{label:>10} {it_peak:>19.1f} {rc_peak:>19.1f}  "
            f"{smaller_percent(it_peak, rc_peak)}"
        )
        rows.append([pattern, size, REPEATS, it_peak, rc_peak, it_cur, rc_cur])

    with RESULTS_PATH.open("w", newline="", encoding="utf-8") as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(
            [
                "pattern", "size", "repeats",
                "iterative_peak_kb", "recursive_peak_kb",
                "iterative_current_kb", "recursive_current_kb",
            ]
        )
        writer.writerows(rows)

    print(f"\nSelesai. Hasil: {RESULTS_PATH}")


if __name__ == "__main__":
    run_profiling()
