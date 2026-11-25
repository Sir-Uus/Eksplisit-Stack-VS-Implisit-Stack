"""Pengukuran batas kedalaman rekursi parser iteratif vs rekursif (Bab IV.C).

Yang diukur (input: 1+(1+(1+(...1))) dengan kedalaman kurung d):

1. Kedalaman pemanggilan maksimum parser rekursif dengan sys.setprofile
   (hanya menghitung fungsi rantai rekursi: _expression, _term, _factor,
   _unary, _primary) -> jumlah frame per tingkat kurung.
2. Kedalaman kurung maksimum yang berhasil (pencarian biner) untuk:
   - Rekursif (limit 1000)  : parser dipanggil langsung, limit bawaan Python;
   - Rekursif (limit 10000) : parser dipanggil langsung, limit dinaikkan;
   - Rekursif via parse()   : fungsi parse() proyek, yang menaikkan limit
                              secara otomatis (maks 100.000);
   - Iteratif               : tidak memakai rekursi (diuji sampai batas atas).
3. Sapuan d = 100..2000 langkah 100: success rate dan error rate tiap parser.

Catatan: "parser dipanggil langsung" memakai kelas _RecursiveDescentParser
tanpa pembungkus parse(), karena parse() menaikkan recursionlimit sendiri
sehingga batas bawaan Python tidak pernah tercapai. Nilai d maksimum juga
bergantung pada jumlah frame pemanggil (skrip ini), jadi jangan mengubah
struktur pemanggilan antar-pengukuran.

Jalankan dari folder proyek:  python profiling/depth_bab4.py
Hasil: results/depth_bab4_results.csv dan results/depth_bab4_sweep.csv
"""

import csv
import platform
import sys
from pathlib import Path
from typing import Callable

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from parser.iterative_parser import parse as parse_iterative
from parser.recursive_parser import _RecursiveDescentParser
from parser.recursive_parser import parse as parse_recursive
from parser.tokenizer import ExpressionSyntaxError, tokenize

ITERATIVE_CAP = 200_000          # batas atas pencarian parser iteratif
WRAPPER_SEARCH_CAP = 100_000     # batas atas pencarian parse() rekursif
SWEEP = tuple(range(100, 2001, 100))
CHAIN = frozenset({"_expression", "_term", "_factor", "_unary", "_primary"})
RESULTS_PATH = PROJECT_ROOT / "results" / "depth_bab4_results.csv"
SWEEP_PATH = PROJECT_ROOT / "results" / "depth_bab4_sweep.csv"

Check = Callable[[int], bool]


def build_nested_expression(depth: int) -> str:
    """Bangun 1+(1+(1+(...1))) dengan kedalaman kurung ``depth``."""
    return "1+(" * depth + "1" + ")" * depth


def check_direct(limit: int) -> Check:
    """Pemeriksa: parser rekursif dipanggil langsung pada recursionlimit ``limit``."""

    def check(depth: int) -> bool:
        tokens = tokenize(build_nested_expression(depth))
        previous = sys.getrecursionlimit()
        sys.setrecursionlimit(limit)
        try:
            _RecursiveDescentParser(tokens).parse()
            return True
        except RecursionError:
            return False
        finally:
            sys.setrecursionlimit(previous)

    return check


def check_wrapper(depth: int) -> bool:
    """Pemeriksa: fungsi parse() rekursif proyek (limit dinaikkan otomatis)."""
    try:
        parse_recursive(build_nested_expression(depth))
        return True
    except (ExpressionSyntaxError, RecursionError):
        return False


def check_iterative(depth: int) -> bool:
    """Pemeriksa: parser iteratif."""
    try:
        parse_iterative(build_nested_expression(depth))
        return True
    except (ExpressionSyntaxError, RecursionError):
        return False


def max_success(check: Check, upper: int) -> tuple[int, bool]:
    """Cari d terbesar yang berhasil dengan pencarian biner.

    Returns:
        (d maksimum, True bila batas atas ``upper`` sendiri masih berhasil).
    """
    if check(upper):
        return upper, True
    low, high = 0, upper  # low: berhasil (0 = tidak ada), high: gagal
    while high - low > 1:
        mid = (low + high) // 2
        if check(mid):
            low = mid
        else:
            high = mid
    return low, False


def max_chain_depth(depth: int) -> int:
    """Kedalaman maksimum rantai rekursi parser untuk kurung bersarang ``depth``."""
    tokens = tokenize(build_nested_expression(depth))
    state = {"current": 0, "max": 0}

    def profiler(frame, event, arg):  # type: ignore[no-untyped-def]
        if frame.f_code.co_name in CHAIN:
            if event == "call":
                state["current"] += 1
                if state["current"] > state["max"]:
                    state["max"] = state["current"]
            elif event == "return":
                state["current"] -= 1

    previous = sys.getrecursionlimit()
    sys.setrecursionlimit(max(previous, 20 * depth + 1000))
    sys.setprofile(profiler)
    try:
        _RecursiveDescentParser(tokens).parse()
    finally:
        sys.setprofile(None)
        sys.setrecursionlimit(previous)
    return state["max"]


def run_profiling() -> None:
    """Jalankan seluruh pengukuran, cetak tabel, dan tulis CSV."""
    print(f"Python  : {platform.python_version()} ({platform.python_implementation()})")
    print(f"Sistem  : {platform.platform()}")
    print(f"Limit awal sys.getrecursionlimit(): {sys.getrecursionlimit()}\n")
    RESULTS_PATH.parent.mkdir(parents=True, exist_ok=True)
    summary: list[list[object]] = []

    # 1. Frame per tingkat kurung
    print("1) Kedalaman pemanggilan maksimum parser rekursif (sys.setprofile)")
    depths = {d: max_chain_depth(d) for d in (10, 50, 100)}
    for d, frames in depths.items():
        print(f"   d = {d:>3} -> {frames} frame")
        summary.append(["call_depth", f"d={d}", frames])
    per_level = (depths[100] - depths[50]) / 50
    print(f"   Frame per tingkat kurung (dari d=50 dan d=100): {per_level:g}\n")
    summary.append(["frames_per_level", "d=50..100", per_level])

    # 2. Kedalaman maksimum yang berhasil
    print("2) Kedalaman kurung maksimum yang berhasil (Tabel IV)")
    configs: list[tuple[str, str, Check, int]] = [
        ("Rekursif (limit 1000)", "1000", check_direct(1000), 50_000),
        ("Rekursif (limit 10000)", "10000", check_direct(10_000), 50_000),
        ("Rekursif via parse() (limit otomatis)", "otomatis", check_wrapper,
         WRAPPER_SEARCH_CAP),
        ("Iteratif", "-", check_iterative, ITERATIVE_CAP),
    ]
    for name, limit, check, upper in configs:
        best, hit_cap = max_success(check, upper)
        note = "batas pencarian (bukan batas parser)" if hit_cap else f"galat pada {best + 1}"
        print(f"   {name:<40} d maks = {best:>8,}   {note}")
        summary.append(["max_depth", name, best])
        summary.append(["max_depth_note", name, note])

    # 3. Sapuan success / error rate
    print(f"\n3) Sapuan d = {SWEEP[0]}..{SWEEP[-1]} langkah 100 ({len(SWEEP)} titik)")
    sweep_checks: list[tuple[str, Check]] = [
        ("iterative", check_iterative),
        ("recursive_limit1000", check_direct(1000)),
        ("recursive_limit10000", check_direct(10_000)),
        ("recursive_parse_auto", check_wrapper),
    ]
    sweep_rows: list[list[object]] = []
    successes = {name: 0 for name, _ in sweep_checks}
    for d in SWEEP:
        row: list[object] = [d]
        for name, check in sweep_checks:
            ok = check(d)
            successes[name] += int(ok)
            row.append(int(ok))
        sweep_rows.append(row)
    for name, _ in sweep_checks:
        ok = successes[name]
        rate = ok / len(SWEEP) * 100
        print(
            f"   {name:<22} berhasil {ok:>2} dari {len(SWEEP)} "
            f"-> success {rate:5.1f}%, error {100 - rate:5.1f}%"
        )
        summary.append(["success_count", name, ok])
        summary.append(["success_rate_percent", name, rate])

    with RESULTS_PATH.open("w", newline="", encoding="utf-8") as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(["metric", "config", "value"])
        writer.writerows(summary)
    with SWEEP_PATH.open("w", newline="", encoding="utf-8") as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(["d"] + [name for name, _ in sweep_checks])
        writer.writerows(sweep_rows)

    print(f"\nSelesai. Hasil: {RESULTS_PATH}")
    print(f"         Sapuan: {SWEEP_PATH}")


if __name__ == "__main__":
    run_profiling()
