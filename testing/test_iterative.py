"""Unit test untuk parser iteratif (Shunting Yard)."""

import unittest

from parser.iterative_parser import parse
from parser.tokenizer import ExpressionSyntaxError, TokenizationError

# (infix, postfix) — dipakai ulang oleh test_recursive.py dan untuk cek
# konsistensi kedua parser.
VALID_CASES: list[tuple[str, list[str]]] = [
    ("3 + 4 * 2", ["3", "4", "2", "*", "+"]),
    ("(3 + 4) * 2", ["3", "4", "+", "2", "*"]),
    ("2 ^ 3 ^ 2", ["2", "3", "2", "^", "^"]),
    ("3.5 + 2 * 0.5", ["3.5", "2", "0.5", "*", "+"]),
    ("a + b * c", ["a", "b", "c", "*", "+"]),
    ("-3 + 5", ["3", "u-", "5", "+"]),
    ("2 ^ -3", ["2", "3", "u-", "^"]),
]

INVALID_EXPRESSIONS: list[str] = [
    "",
    "3 +",
    "(3 + 4",
    "3 + 4)",
    "3 * / 4",
    "3 4",
    "3 @ 4",
    "1.2.3",
    "()",
]


class IterativeParserTests(unittest.TestCase):
    """Menguji konversi infix ke postfix dan validasi sintaksis."""

    def test_valid_expressions(self) -> None:
        for expression, expected in VALID_CASES:
            with self.subTest(expression=expression):
                self.assertEqual(parse(expression), expected)

    def test_operator_precedence(self) -> None:
        self.assertEqual(
            parse("2 + 3 * 4 ^ 2 - 1"),
            ["2", "3", "4", "2", "^", "*", "+", "1", "-"],
        )

    def test_parentheses(self) -> None:
        self.assertEqual(
            parse("((1 + 2) * (3 - 4))"),
            ["1", "2", "+", "3", "4", "-", "*"],
        )

    def test_decimal_numbers(self) -> None:
        self.assertEqual(
            parse("1.25 * 2 + .5"),
            ["1.25", "2", "*", ".5", "+"],
        )

    def test_invalid_expressions(self) -> None:
        for expression in INVALID_EXPRESSIONS:
            with self.subTest(expression=expression):
                with self.assertRaises((ExpressionSyntaxError, TokenizationError)):
                    parse(expression)


if __name__ == "__main__":
    unittest.main()
