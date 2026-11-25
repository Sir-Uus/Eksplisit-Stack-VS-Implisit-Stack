"""Tokenizer untuk ekspresi matematika infix.

Tokenizer hanya memecah teks menjadi token dan menandai operator ``+`` / ``-``
sebagai unary ketika token tersebut berada pada posisi yang mengharapkan
operand. Klasifikasi ini dipakai bersama oleh kedua parser agar hasil postfix
mereka konsisten.
"""

from enum import Enum
from typing import NamedTuple


class TokenizationError(ValueError):
    """Dilempar saat ekspresi mengandung karakter yang tidak dikenal."""


class ExpressionSyntaxError(ValueError):
    """Dilempar saat struktur sintaksis ekspresi tidak valid."""


class TokenType(Enum):
    """Jenis token yang dikenal oleh parser."""

    NUMBER = "NUMBER"
    IDENTIFIER = "IDENTIFIER"
    OPERATOR = "OPERATOR"
    UNARY_OPERATOR = "UNARY_OPERATOR"
    LEFT_PAREN = "LEFT_PAREN"
    RIGHT_PAREN = "RIGHT_PAREN"


class Token(NamedTuple):
    """Token hasil tokenisasi, terdiri dari jenis dan nilai teksnya."""

    type: TokenType
    value: str


_BINARY_OPERATORS = frozenset("+-*/^")
_UNARY_CAPABLE_OPERATORS = frozenset("+-")


def tokenize(expression: str) -> list[Token]:
    """Pecah ekspresi infix menjadi daftar :class:`Token`.

    Args:
        expression: Ekspresi matematika dalam notasi infix.

    Returns:
        Daftar token tanpa whitespace.

    Raises:
        TokenizationError: Jika ditemukan karakter tidak valid atau angka
            desimal yang salah bentuk.
    """
    tokens: list[Token] = []
    index = 0
    length = len(expression)
    expect_operand = True

    while index < length:
        char = expression[index]

        if char.isspace():
            index += 1
            continue

        if char.isdigit() or char == ".":
            start = index
            has_dot = False
            has_digit = False
            while index < length and (
                expression[index].isdigit() or expression[index] == "."
            ):
                if expression[index] == ".":
                    if has_dot:
                        raise TokenizationError(
                            f"Titik desimal ganda pada posisi {index}."
                        )
                    has_dot = True
                else:
                    has_digit = True
                index += 1
            if not has_digit:
                raise TokenizationError(
                    f"Titik desimal tanpa angka pada posisi {start}."
                )
            tokens.append(Token(TokenType.NUMBER, expression[start:index]))
            expect_operand = False
            continue

        if char.isalpha() or char == "_":
            start = index
            index += 1
            while index < length and (
                expression[index].isalnum() or expression[index] == "_"
            ):
                index += 1
            tokens.append(Token(TokenType.IDENTIFIER, expression[start:index]))
            expect_operand = False
            continue

        if char in _BINARY_OPERATORS:
            if expect_operand and char in _UNARY_CAPABLE_OPERATORS:
                tokens.append(Token(TokenType.UNARY_OPERATOR, char))
            else:
                tokens.append(Token(TokenType.OPERATOR, char))
            expect_operand = True
            index += 1
            continue

        if char == "(":
            tokens.append(Token(TokenType.LEFT_PAREN, char))
            expect_operand = True
            index += 1
            continue

        if char == ")":
            tokens.append(Token(TokenType.RIGHT_PAREN, char))
            expect_operand = False
            index += 1
            continue

        raise TokenizationError(
            f"Karakter tidak valid '{char}' pada posisi {index}."
        )

    return tokens
