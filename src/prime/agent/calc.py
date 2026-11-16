"""Arithmetic for the agent's `calculate` tool. Parses with `ast`; never calls eval."""

import ast
import operator
from collections.abc import Callable

_BINARY: dict[type[ast.operator], Callable[[float, float], float]] = {
    ast.Add: operator.add, ast.Sub: operator.sub, ast.Mult: operator.mul,
    ast.Div: operator.truediv, ast.Pow: operator.pow,
}  # fmt: skip
MAX_LENGTH, MAX_EXPONENT = 500, 100


def calculate(expression: str) -> float:
    """Evaluate + - * / ** and parentheses over numeric literals. Anything else raises ValueError."""
    if len(expression) > MAX_LENGTH:
        raise ValueError("expression too long")
    try:
        tree = ast.parse(expression, mode="eval")
    except SyntaxError as e:
        raise ValueError(f"not an arithmetic expression: {e.msg}") from e
    return _eval(tree.body)


def _eval(node: ast.expr) -> float:
    if (
        isinstance(node, ast.Constant)
        and isinstance(node.value, int | float)
        and type(node.value) is not bool
    ):
        return float(node.value)
    if isinstance(node, ast.UnaryOp) and isinstance(node.op, ast.USub | ast.UAdd):
        value = _eval(node.operand)
        return -value if isinstance(node.op, ast.USub) else value
    if isinstance(node, ast.BinOp) and type(node.op) in _BINARY:
        left, right = _eval(node.left), _eval(node.right)
        if isinstance(node.op, ast.Pow) and abs(right) > MAX_EXPONENT:
            raise ValueError("exponent too large")
        try:
            return _BINARY[type(node.op)](left, right)
        except ZeroDivisionError as e:
            raise ValueError("division by zero") from e
    raise ValueError(f"unsupported element: {type(node).__name__}")
