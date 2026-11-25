"""Program utama: menu perbandingan parser iteratif dan rekursif."""

import sys
from pathlib import Path
from typing import Callable

PROJECT_ROOT = Path(__file__).resolve().parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from parser.iterative_parser import parse as parse_iterative
from parser.recursive_parser import parse as parse_recursive
from parser.tokenizer import ExpressionSyntaxError, TokenizationError

Parser = Callable[[str], list[str]]


def _format_postfix(tokens: list[str]) -> str:
    """Format daftar token postfix menjadi satu baris teks."""
    return " ".join(tokens) if tokens else "-"


def _run_parser(name: str, parser: Parser, expression: str) -> None:
    """Tampilkan hasil konversi dan status validasi untuk satu parser."""
    print(f"\n--- {name} ---")
    try:
        postfix = parser(expression)
    except (ExpressionSyntaxError, TokenizationError) as exc:
        print(f"Infix   : {expression}")
        print("Postfix : -")
        print(f"Status  : TIDAK VALID ({exc})")
    else:
        print(f"Infix   : {expression}")
        print(f"Postfix : {_format_postfix(postfix)}")
        print("Status  : VALID")


def compare(expression: str) -> None:
    """Jalankan kedua parser dan tampilkan hasil serta konsistensinya."""
    results: dict[str, list[str] | None] = {}
    for name, parser in (
        ("Iteratif (ArrayStack)", parse_iterative),
        ("Rekursif (Call Stack)", parse_recursive),
    ):
        print(f"\n--- {name} ---")
        try:
            postfix = parser(expression)
            results[name] = postfix
            print(f"Postfix : {_format_postfix(postfix)}")
            print("Status  : VALID")
        except (ExpressionSyntaxError, TokenizationError) as exc:
            results[name] = None
            print("Postfix : -")
            print(f"Status  : TIDAK VALID ({exc})")

    print(f"Infix     : {expression}")
    iterative_result = results["Iteratif (ArrayStack)"]
    recursive_result = results["Rekursif (Call Stack)"]
    if iterative_result == recursive_result and iterative_result is not None:
        print("Konsisten: YA")
    else:
        print("Konsisten: TIDAK")


def menu() -> None:
    """Tampilkan menu interaktif hingga pengguna memilih keluar."""
    while True:
        print("\n=== Perbandingan Parsing Ekspresi Matematika ===")
        print("1. Parsing Iteratif")
        print("2. Parsing Rekursif")
        print("3. Membandingkan hasil kedua parser")
        print("4. Keluar")
        try:
            choice = input("Pilihan (1-4): ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nKeluar dari program.")
            return

        if choice == "4":
            print("Keluar dari program.")
            return
        if choice not in {"1", "2", "3"}:
            print("Pilihan tidak dikenal. Coba lagi.")
            continue

        try:
            expression = input("Masukkan ekspresi infix: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nKeluar dari program.")
            return

        if choice == "1":
            _run_parser("Parsing Iteratif (ArrayStack)", parse_iterative, expression)
        elif choice == "2":
            _run_parser("Parsing Rekursif (Call Stack)", parse_recursive, expression)
        else:
            compare(expression)


if __name__ == "__main__":
    menu()
