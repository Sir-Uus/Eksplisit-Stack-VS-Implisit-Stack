"""Unit test untuk ADT ArrayStack."""

import unittest

from stack.array_stack import ArrayStack, StackOverflowError, StackUnderflowError


class ArrayStackTests(unittest.TestCase):
    """Menguji operasi dasar dan penanganan underflow/overflow."""

    def test_push_and_pop(self) -> None:
        stack: ArrayStack[int] = ArrayStack(capacity=3)
        stack.push(10)
        stack.push(20)
        self.assertEqual(stack.pop(), 20)
        self.assertEqual(stack.pop(), 10)

    def test_lifo_principle(self) -> None:
        stack: ArrayStack[str] = ArrayStack(capacity=5)
        for value in ("a", "b", "c"):
            stack.push(value)
        self.assertEqual([stack.pop() for _ in range(3)], ["c", "b", "a"])

    def test_peek_does_not_remove_item(self) -> None:
        stack: ArrayStack[int] = ArrayStack(capacity=2)
        stack.push(7)
        self.assertEqual(stack.peek(), 7)
        self.assertEqual(stack.size(), 1)
        self.assertEqual(stack.pop(), 7)

    def test_empty_stack_raises_underflow(self) -> None:
        stack: ArrayStack[int] = ArrayStack(capacity=2)
        self.assertTrue(stack.is_empty())
        with self.assertRaises(StackUnderflowError):
            stack.pop()
        with self.assertRaises(StackUnderflowError):
            stack.peek()

    def test_size_and_clear(self) -> None:
        stack: ArrayStack[int] = ArrayStack(capacity=4)
        stack.push(1)
        stack.push(2)
        self.assertEqual(stack.size(), 2)
        stack.clear()
        self.assertTrue(stack.is_empty())
        self.assertEqual(stack.size(), 0)

    def test_full_stack_raises_overflow(self) -> None:
        stack: ArrayStack[int] = ArrayStack(capacity=2)
        stack.push(1)
        stack.push(2)
        with self.assertRaises(StackOverflowError):
            stack.push(3)
        self.assertEqual(stack.size(), 2)

    def test_invalid_capacity(self) -> None:
        with self.assertRaises(ValueError):
            ArrayStack(capacity=0)


if __name__ == "__main__":
    unittest.main()
