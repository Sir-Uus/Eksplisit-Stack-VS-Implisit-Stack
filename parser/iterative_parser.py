"""Parser iteratif menggunakan algoritma Shunting Yard dan ADT ArrayStack."""

from stack.array_stack import ArrayStack
from parser.tokenizer import (
    ExpressionSyntaxError,
    Token,
    TokenType,
    tokenize,
)

_PRECEDENCE: dict[str, int] = {
    "+": 1,
    "-": 1,
    "*": 2,
    "/": 2,
    "^": 3,
    "u+": 4,
    "u-": 4,
}
_RIGHT_ASSOCIATIVE = frozenset({"^", "u+", "u-"})
_OPERATOR_TYPES = (TokenType.OPERATOR, TokenType.UNARY_OPERATOR)


def _operator_key(token: Token) -> str:
    """Kembalikan kunci operator, misalnya ``u-`` untuk unary minus."""
    if token.type is TokenType.UNARY_OPERATOR:
        return f"u{token.value}"
    return token.value


def parse(expression: str) -> list[str]:
    """Konversi ekspresi infix menjadi postfix secara iteratif.

    Args:
        expression: Ekspresi matematika dalam notasi infix.

    Returns:
        Daftar token postfix. Operator unary ditulis sebagai ``u+`` / ``u-``.

    Raises:
        TokenizationError: Jika ekspresi memuat karakter tidak valid.
        ExpressionSyntaxError: Jika sintaksis ekspresi tidak valid.
    """
    tokens = tokenize(expression)
    if not tokens:
        raise ExpressionSyntaxError("Ekspresi kosong.")

    # Kapasitas stack mengikuti jumlah token agar overflow tidak terjadi pada
    # ekspresi yang secara sintaksis valid.
    operator_stack: ArrayStack[Token] = ArrayStack(capacity=len(tokens) + 1)
    output: list[str] = []
    expect_operand = True

    for token in tokens:
        token_type = token.type

        if token_type in (TokenType.NUMBER, TokenType.IDENTIFIER):
            if not expect_operand:
                raise ExpressionSyntaxError(
                    f"Operand '{token.value}' tidak memiliki operator sebelumnya."
                )
            output.append(token.value)
            expect_operand = False

        elif token_type is TokenType.UNARY_OPERATOR:
            if not expect_operand:
                raise ExpressionSyntaxError(
                    f"Operator unary '{token.value}' berada setelah operand."
                )
            operator_stack.push(token)

        elif token_type is TokenType.OPERATOR:
            if expect_operand:
                raise ExpressionSyntaxError(
                    f"Operator '{token.value}' kehilangan operand kiri."
                )
            current_key = _operator_key(token)
            current_precedence = _PRECEDENCE[current_key]

            while (
                not operator_stack.is_empty()
                and operator_stack.peek().type in _OPERATOR_TYPES
            ):
                top_token = operator_stack.peek()
                top_key = _operator_key(top_token)
                top_precedence = _PRECEDENCE[top_key]
                should_pop = top_precedence > current_precedence or (
                    top_precedence == current_precedence
                    and top_key not in _RIGHT_ASSOCIATIVE
                )
                if not should_pop:
                    break
                output.append(_operator_key(operator_stack.pop()))

            operator_stack.push(token)
            expect_operand = True

        elif token_type is TokenType.LEFT_PAREN:
            if not expect_operand:
                raise ExpressionSyntaxError("Operator hilang sebelum tanda '('.")
            operator_stack.push(token)
            expect_operand = True

        else:  # TokenType.RIGHT_PAREN
            if expect_operand:
                raise ExpressionSyntaxError("Kurung tutup tidak memiliki operand.")
            while (
                not operator_stack.is_empty()
                and operator_stack.peek().type is not TokenType.LEFT_PAREN
            ):
                output.append(_operator_key(operator_stack.pop()))
            if operator_stack.is_empty():
                raise ExpressionSyntaxError("Kurung tutup tanpa pasangan.")
            operator_stack.pop()  # Buang kurung buka yang cocok.
            expect_operand = False

    if expect_operand:
        raise ExpressionSyntaxError("Ekspresi berakhir dengan operator.")

    while not operator_stack.is_empty():
        remaining = operator_stack.pop()
        if remaining.type is TokenType.LEFT_PAREN:
            raise ExpressionSyntaxError("Kurung buka tanpa pasangan.")
        output.append(_operator_key(remaining))

    return output
