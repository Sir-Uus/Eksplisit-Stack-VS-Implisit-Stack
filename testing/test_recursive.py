"""Unit test untuk parser rekursif dan konsistensi kedua parser."""

import unittest
from typing import Callable

from parser.iterative_parser import parse as parse_iterative
from parser.recursive_parser import parse as parse_recursive
from parser.tokenizer import ExpressionSyntaxError, TokenizationError
from testing.test_iterative import INVALID_EXPRESSIONS, VALID_CASES


class RecursiveParserTests(unittest.TestCase):
    """Menguji recursive descent parser."""

    def test_valid_expressions(self) -> None:
        for expression, expected in VALID_CASES:
            with self.subTest(expression=expression):
                self.assertEqual(parse_recursive(expression), expected)

    def test_operator_precedence(self) -> None:
        self.assertEqual(
            parse_recursive("2 + 3 * 4 ^ 2 - 1"),
            ["2", "3", "4", "2", "^", "*", "+", "1", "-"],
        )

    def test_parentheses(self) -> None:
        self.assertEqual(
            parse_recursive("((1 + 2) * (3 - 4))"),
            ["1", "2", "+", "3", "4", "-", "*"],
        )

    def test_decimal_numbers(self) -> None:
        self.assertEqual(
            parse_recursive("1.25 * 2 + .5"),
            ["1.25", "2", "*", ".5", "+"],
        )

    def test_invalid_expressions(self) -> None:
        for expression in INVALID_EXPRESSIONS:
            with self.subTest(expression=expression):
                with self.assertRaises((ExpressionSyntaxError, TokenizationError)):
                    parse_recursive(expression)

    def test_deeply_nested_expression(self) -> None:
        """Ekspresi bersarang dalam harus selesai tanpa RecursionError."""
        expression = "1" + "+1" * 200
        expression = "(" * 200 + expression + ")" * 200
        self.assertEqual(parse_recursive(expression)[0], "1")
        self.assertEqual(parse_recursive(expression).count("+"), 200)


class CrossParserConsistencyTests(unittest.TestCase):
    """Memastikan kedua parser menghasilkan postfix yang identik."""

    def test_same_postfix_for_valid_expressions(self) -> None:
        expressions = [expression for expression, _ in VALID_CASES]
        expressions.extend(
            [
                "2 + 3 * 4 ^ 2 - 1",
                "((1 + 2) * (3 - 4))",
                "1.25 * 2 + .5",
                "-(-2 ^ 3) / 4",
                "a * (b + c ^ 2) - d",
            ]
        )
        for expression in expressions:
            with self.subTest(expression=expression):
                self.assertEqual(
                    parse_iterative(expression), parse_recursive(expression)
                )

    def test_same_error_status_for_invalid_expressions(self) -> None:
        for expression in INVALID_EXPRESSIONS:
            with self.subTest(expression=expression):
                iterative_error = self._error_type(parse_iterative, expression)
                recursive_error = self._error_type(parse_recursive, expression)
                self.assertIsNotNone(iterative_error)
                self.assertIsNotNone(recursive_error)

    @staticmethod
    def _error_type(
        parser: Callable[[str], list[str]], expression: str
    ) -> type[Exception] | None:
        """Kembalikan tipe exception parser atau None jika ekspresi valid."""
        try:
            parser(expression)
        except (ExpressionSyntaxError, TokenizationError) as exc:
            return type(exc)
        return None


if __name__ == "__main__":
    unittest.main()
