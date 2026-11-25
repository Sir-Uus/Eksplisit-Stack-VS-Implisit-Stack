"""Implementasi Abstract Data Type (ADT) Stack berbasis array (list Python)."""

from typing import Generic, TypeVar

T = TypeVar("T")


class StackError(Exception):
    """Induk dari seluruh exception yang terkait dengan operasi Stack."""


class StackUnderflowError(StackError):
    """Dilempar saat pop/peek dilakukan pada Stack kosong."""


class StackOverflowError(StackError):
    """Dilempar saat push dilakukan pada Stack yang sudah penuh."""


class ArrayStack(Generic[T]):
    """Stack dengan kapasitas tetap yang mengikuti prinsip LIFO.

    Elemen disimpan di dalam list privat. Kapasitas dibatasi sejak pembuatan
    objek sehingga kondisi overflow dapat dideteksi secara eksplisit.
    """

    def __init__(self, capacity: int = 1024) -> None:
        """Buat Stack kosong dengan ``capacity`` maksimum.

        Args:
            capacity: Jumlah maksimum elemen yang dapat ditampung.

        Raises:
            ValueError: Jika ``capacity`` bukan bilangan bulat positif.
        """
        if capacity <= 0:
            raise ValueError("Kapasitas Stack harus lebih besar dari 0.")
        self._items: list[T] = []
        self._capacity = capacity

    def push(self, item: T) -> None:
        """Tambahkan elemen ke puncak Stack.

        Raises:
            StackOverflowError: Jika kapasitas Stack sudah terlampaui.
        """
        if self.size() >= self._capacity:
            raise StackOverflowError(
                f"Stack penuh: tidak dapat menambah elemen (kapasitas {self._capacity})."
            )
        self._items.append(item)

    def pop(self) -> T:
        """Hapus dan kembalikan elemen puncak Stack.

        Raises:
            StackUnderflowError: Jika Stack kosong.
        """
        if self.is_empty():
            raise StackUnderflowError("Stack kosong: tidak dapat melakukan pop.")
        return self._items.pop()

    def peek(self) -> T:
        """Kembalikan elemen puncak tanpa menghapusnya.

        Raises:
            StackUnderflowError: Jika Stack kosong.
        """
        if self.is_empty():
            raise StackUnderflowError("Stack kosong: tidak dapat melakukan peek.")
        return self._items[-1]

    def is_empty(self) -> bool:
        """Kembalikan True jika Stack tidak memiliki elemen."""
        return len(self._items) == 0

    def size(self) -> int:
        """Kembalikan jumlah elemen yang tersimpan di Stack."""
        return len(self._items)

    def clear(self) -> None:
        """Hapus seluruh elemen Stack."""
        self._items.clear()
