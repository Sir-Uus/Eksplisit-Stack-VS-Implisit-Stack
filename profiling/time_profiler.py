"""Pengukuran waktu eksekusi parser iteratif vs rekursif (Bab IV.A).

Prosedur (sesuai Bagian II.F makalah):
- waktu diukur dengan time.perf_counter, hanya untuk pemanggilan parse();
- 1 kali pemanasan sebelum pengukuran;
- 30 pengulangan per ukuran (10 pengulangan untuk n = 50.000);
- garbage collector dinonaktifkan selama pengukuran;
- hasil dilaporkan sebagai median dan simpangan baku (detik -> mikrodetik).

Dua pola input:
- "panjang": 1+2*3-4/5+6*7-... dengan n operand, tanpa kurung bersarang;
- "bersarang": 1+(1+(1+(...1))) dengan kedalaman kurung d.

Jalankan dari folder proyek:  python profiling/time_profiler.py
Hasil disimpan ke results/time_results.csv
"""

import csv
import gc
import platform
import sys
from pathlib import Path
from statistics import median, stdev
from time import perf_counter
from typing import Callable

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from parser.iterative_parser import parse as parse_iterative
from parser.recursive_parser import parse as parse_recursive

LONG_SIZES = (10, 100, 1000, 10_000, 50_000)
NESTED_DEPTHS = (10, 50, 100, 200, 320)
REPEATS = 30
REPEATS_LARGE = 10  # untuk n = 50.000
LARGE_THRESHOLD = 50_000
RESULTS_PATH = PROJECT_ROOT / "results" / "time_results.csv"

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


def measure(expression: str, repeats: int) -> dict[str, tuple[float, float]]:
    """Ukur kedua parser pada ekspresi yang sama.

    Pengukuran kedua parser diselang-seling pada tiap pengulangan supaya
    pergeseran kondisi komputer (suhu, proses latar) berdampak sama pada
    keduanya.

    Returns:
        {"iterative": (median, stdev), "recursive": (median, stdev)} dalam detik.
    """
    parsers: dict[str, Parser] = {
        "iterative": parse_iterative,
        "recursive": parse_recursive,
    }
    samples: dict[str, list[float]] = {name: [] for name in parsers}

    # Pemanasan satu kali + validasi keluaran identik.
    warm = {name: fn(expression) for name, fn in parsers.items()}
    if warm["iterative"] != warm["recursive"]:
        raise AssertionError("Kedua parser menghasilkan postfix berbeda.")
    del warm

    gc.collect()
    gc.disable()
    try:
        for _ in range(repeats):
            for name, fn in parsers.items():
                start = perf_counter()
                result = fn(expression)
                elapsed = perf_counter() - start
                samples[name].append(elapsed)
                del result
    finally:
        gc.enable()

    return {
        name: (median(values), stdev(values) if len(values) > 1 else 0.0)
        for name, values in samples.items()
    }


def fmt(seconds: float) -> str:
    """Format detik ke satuan µs / ms / s agar mudah dibaca."""
    if seconds < 1e-3:
        return f"{seconds * 1e6:.1f} µs"
    if seconds < 1:
        return f"{seconds * 1e3:.3f} ms"
    return f"{seconds:.3f} s"


def faster_percent(iterative: float, recursive: float) -> str:
    """Selisih relatif terhadap waktu yang lebih lambat, plus pemenangnya."""
    if iterative == recursive:
        return "setara"
    slower, faster = max(iterative, recursive), min(iterative, recursive)
    winner = "rekursif" if recursive < iterative else "iteratif"
    return f"{winner} lebih cepat {(slower - faster) / slower * 100:.1f}%"


def run_profiling() -> None:
    """Jalankan seluruh pengukuran, cetak tabel, dan tulis CSV."""
    print(f"Python  : {platform.python_version()} ({platform.python_implementation()})")
    print(f"Sistem  : {platform.platform()}")
    print(f"Prosesor: {platform.processor() or platform.machine()}")
    print("Tutup aplikasi lain dan jangan pakai komputer selama pengukuran.\n")

    RESULTS_PATH.parent.mkdir(parents=True, exist_ok=True)
    rows: list[list[object]] = []
    header = (
        f"{'input':>10} {'iteratif (median)':>18} {'SD':>11} "
        f"{'rekursif (median)':>18} {'SD':>11}  selisih"
    )
    print(header)
    print("-" * len(header))

    jobs: list[tuple[str, int, str]] = []
    for n in LONG_SIZES:
        jobs.append(("panjang", n, build_long_expression(n)))
    for d in NESTED_DEPTHS:
        jobs.append(("bersarang", d, build_nested_expression(d)))

    for pattern, size, expression in jobs:
        repeats = REPEATS_LARGE if size >= LARGE_THRESHOLD and pattern == "panjang" else REPEATS
        result = measure(expression, repeats)
        it_med, it_sd = result["iterative"]
        rc_med, rc_sd = result["recursive"]
        label = f"n={size}" if pattern == "panjang" else f"d={size}"
        print(
            f"{label:>10} {fmt(it_med):>18} {fmt(it_sd):>11} "
            f"{fmt(rc_med):>18} {fmt(rc_sd):>11}  {faster_percent(it_med, rc_med)}"
        )
        rows.append(
            [pattern, size, repeats, it_med, it_sd, rc_med, rc_sd]
        )

    with RESULTS_PATH.open("w", newline="", encoding="utf-8") as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(
            [
                "pattern", "size", "repeats",
                "iterative_median_s", "iterative_stdev_s",
                "recursive_median_s", "recursive_stdev_s",
            ]
        )
        writer.writerows(rows)

    print(f"\nSelesai. Hasil: {RESULTS_PATH}")


if __name__ == "__main__":
    run_profiling()
