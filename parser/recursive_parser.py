"""Recursive Descent Parser yang memanfaatkan call stack Python."""

import sys

from parser.tokenizer import (
    ExpressionSyntaxError,
    Token,
    TokenType,
    tokenize,
)


class _RecursiveDescentParser:
    """Parser rekursif dengan pointer token dan daftar output postfix."""

    def __init__(self, tokens: list[Token]) -> None:
        self._tokens = tokens
        self._position = 0
        self._output: list[str] = []

    def parse(self) -> list[str]:
        """Jalankan grammar hingga seluruh token terkonsumsi."""
        self._expression()
        remaining = self._peek()
        if remaining is not None:
            raise ExpressionSyntaxError(
                f"Token '{remaining.value}' tidak terduga di akhir ekspresi."
            )
        return self._output

    def _peek(self) -> Token | None:
        """Kembalikan token saat ini tanpa memajukan pointer."""
        if self._position >= len(self._tokens):
            return None
        return self._tokens[self._position]

    def _is_operator(self, *values: str) -> bool:
        """Cek apakah token saat ini adalah operator dengan nilai tertentu."""
        token = self._peek()
        return (
            token is not None
            and token.type is TokenType.OPERATOR
            and token.value in values
        )

    def _expression(self) -> None:
        """expression := term (('+' | '-') term)*"""
        self._term()
        while self._is_operator("+", "-"):
            operator = self._tokens[self._position]
            self._position += 1
            self._term()
            self._output.append(operator.value)

    def _term(self) -> None:
        """term := factor (('*' | '/') factor)*"""
        self._factor()
        while self._is_operator("*", "/"):
            operator = self._tokens[self._position]
            self._position += 1
            self._factor()
            self._output.append(operator.value)

    def _factor(self) -> None:
        """factor := unary ('^' factor)?  (asosiatif kanan)"""
        self._unary()
        if self._is_operator("^"):
            self._position += 1
            self._factor()
            self._output.append("^")

    def _unary(self) -> None:
        """unary := ('+' | '-') unary | primary"""
        token = self._peek()
        if token is not None and token.type is TokenType.UNARY_OPERATOR:
            self._position += 1
            self._unary()
            self._output.append(f"u{token.value}")
            return
        self._primary()

    def _primary(self) -> None:
        """primary := NUMBER | IDENTIFIER | '(' expression ')'"""
        token = self._peek()
        if token is None:
            raise ExpressionSyntaxError("Ekspresi berakhir sebelum operand selesai.")
        if token.type in (TokenType.NUMBER, TokenType.IDENTIFIER):
            self._position += 1
            self._output.append(token.value)
            return
        if token.type is TokenType.LEFT_PAREN:
            self._position += 1
            self._expression()
            closing = self._peek()
            if closing is None or closing.type is not TokenType.RIGHT_PAREN:
                raise ExpressionSyntaxError("Kurung buka tanpa pasangan.")
            self._position += 1
            return
        raise ExpressionSyntaxError(f"Token '{token.value}' tidak dapat menjadi operand.")


def parse(expression: str) -> list[str]:
    """Konversi ekspresi infix menjadi postfix secara rekursif.

    Args:
        expression: Ekspresi matematika dalam notasi infix.

    Returns:
        Daftar token postfix yang sama dengan parser iteratif.

    Raises:
        TokenizationError: Jika ekspresi memuat karakter tidak valid.
        ExpressionSyntaxError: Jika sintaksis tidak valid atau kedalaman
            rekursi melebihi batas yang aman.
    """
    tokens = tokenize(expression)
    if not tokens:
        raise ExpressionSyntaxError("Ekspresi kosong.")

    # Setiap tingkat kurung membutuhkan beberapa frame call stack. Batas
    # dinaikkan sementara agar ekspresi panjang masih dapat diparse.
    previous_limit = sys.getrecursionlimit()
    required_limit = min(previous_limit + len(tokens) * 10 + 100, 100_000)
    try:
        if required_limit > previous_limit:
            sys.setrecursionlimit(required_limit)
        try:
            return _RecursiveDescentParser(tokens).parse()
        except RecursionError as exc:
            raise ExpressionSyntaxError(
                "Kedalaman ekspresi melebihi batas call stack Python."
            ) from exc
    finally:
        if sys.getrecursionlimit() != previous_limit:
            sys.setrecursionlimit(previous_limit)
