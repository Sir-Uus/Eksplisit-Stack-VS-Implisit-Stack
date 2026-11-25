# Analisis Perbandingan Kinerja Eksplisit Stack vs Implisit Stack

Proyek Python sederhana untuk membandingkan dua pendekatan parsing ekspresi
matematika infix menjadi postfix:

1. **Iteratif OOP** — algoritma Shunting Yard dengan ADT `ArrayStack` buatan
   sendiri (eksplisit stack).
2. **Rekursif** — Recursive Descent Parser yang memanfaatkan call stack Python
   (implisit stack).

Fokus proyek hanya pada implementasi ADT Stack, unit testing, dan memory
profiling menggunakan `tracemalloc`.

## Tujuan Penelitian

Menganalisis perbedaan konsumsi memori antara eksplisit stack dan implisit stack
pada validasi sintaksis dan konversi infix ke postfix, dengan memastikan kedua
pendekatan menghasilkan output postfix yang identik untuk ekspresi yang setara.

Konvensi operator:

- Prioritas: unary `+` / `-` > `^` > `*` / `/` > `+` / `-`.
- Asosiativitas: `^` dan operator unary bersifat kanan; operator lain kiri.
- Operator unary pada output postfix ditulis `u+` / `u-` agar tidak tertukar
  dengan operator biner.

## Struktur Direktori

```text
stack-comparison/
├── main.py
├── README.md
├── stack/
│   ├── __init__.py
│   └── array_stack.py
├── parser/
│   ├── __init__.py
│   ├── tokenizer.py
│   ├── iterative_parser.py
│   └── recursive_parser.py
├── testing/
│   ├── __init__.py
│   ├── test_stack.py
│   ├── test_iterative.py
│   └── test_recursive.py
├── profiling/
│   └── memory_profiler.py
└── results/
    └── memory_results.csv
```

## Fungsi Setiap File

| File | Fungsi |
| --- | --- |
| `main.py` | Menu interaktif: parsing iteratif, rekursif, perbandingan, keluar. |
| `stack/array_stack.py` | ADT Stack dengan `push`, `pop`, `peek`, `is_empty`, `size`, `clear` serta exception underflow/overflow. |
| `parser/tokenizer.py` | Memecah infix menjadi token, mendeteksi karakter tidak valid, menandai operator unary. |
| `parser/iterative_parser.py` | Shunting Yard berbasis `ArrayStack`, menghasilkan postfix dan validasi sintaksis. |
| `parser/recursive_parser.py` | Recursive Descent Parser dengan call stack Python dan penanganan `RecursionError`. |
| `testing/test_stack.py` | Pengujian operasi Stack, LIFO, underflow, overflow. |
| `testing/test_iterative.py` | Pengujian parser iteratif dan kumpulan kasus valid/invalid bersama. |
| `testing/test_recursive.py` | Pengujian parser rekursif dan konsistensi postfix kedua parser. |
| `profiling/memory_profiler.py` | Pengukuran current/peak memory dengan `tracemalloc` dan penulisan CSV. |
| `results/memory_results.csv` | Hasil pengukuran aktual (bukan data simulasi). |

## Cara Menjalankan Aplikasi

Dari dalam direktori `stack-comparison`:

```bash
python main.py
```

Pilih menu 1, 2, atau 3, lalu masukkan ekspresi seperti
`(3 + 4) * 2.5 - x ^ 2`.

Contoh penggunaan sebagai modul:

```python
from parser.iterative_parser import parse as parse_iterative
from parser.recursive_parser import parse as parse_recursive

print(parse_iterative("3 + 4 * 2"))  # ['3', '4', '2', '*', '+']
print(parse_recursive("3 + 4 * 2"))  # ['3', '4', '2', '*', '+']
```

## Cara Menjalankan Unit Testing

```bash
python -m unittest discover -s testing -v
```

## Cara Menjalankan Memory Profiling

```bash
python profiling/memory_profiler.py
```

Profiler memakai ekspresi dengan 10, 100, 500, dan 1000 token yang identik
untuk kedua parser, mengulang pengukuran sebanyak 7 kali per ukuran, lalu
menyimpan median `current_bytes` dan `peak_bytes` ke
`results/memory_results.csv`.

## Dependensi

Python 3 tanpa pustaka pihak ketiga. Seluruh modul memakai library bawaan:
`unittest`, `tracemalloc`, `csv`, `gc`, `statistics`, `enum`, `typing`, dan `sys`.
