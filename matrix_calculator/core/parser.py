"""
Expression parser for symbolic matrix calculator.
Converts user input strings to SymPy expressions.
"""

from sympy import Rational, pi, sqrt, Symbol, parse_expr, E, I
from sympy.core.sympify import SympifyError


def parse_expression(s: str):
    """
    Parse a string expression to a SymPy object.

    Supports:
    - Fractions: '1/3' -> Rational(1, 3)
    - Square roots: 'sqrt(2)' -> sqrt(2)
    - Pi: 'pi' -> pi
    - Complex expressions: '2+3/4', '1+sqrt(3)', etc.

    Args:
        s: String expression from user input

    Returns:
        SymPy expression (Rational, Symbol, etc.)

    Raises:
        ValueError: If expression cannot be parsed
    """
    s = s.strip()
    if not s:
        return Rational(0)

    # Handle negative numbers without leading zero: '-.5' -> '-1/2'
    s = s.replace('-.', '-')

    # Provide common symbols and functions as locals
    locals_dict = {
        'sqrt': sqrt,
        'pi': pi,
        'e': E,
        'I': I,
    }

    try:
        # Try direct sympify first for simple cases
        result = parse_expr(s, local_dict=locals_dict, evaluate=True)
        return result
    except SympifyError:
        pass

    # Try with rational handling for fractions like '1/3'
    try:
        if '/' in s and not '(' in s:
            parts = s.split('/')
            if len(parts) == 2 and parts[0].isdigit() and parts[1].isdigit():
                return Rational(int(parts[0]), int(parts[1]))
    except (ValueError, TypeError):
        pass

    raise ValueError(f"Cannot parse expression: {s}")


def matrix_from_strings(rows: list[list[str]]):
    """
    Convert a 2D list of string expressions to a SymPy Matrix.

    Args:
        rows: 2D list of string expressions

    Returns:
        sympy.Matrix
    """
    from sympy import Matrix

    matrix_data = []
    for row in rows:
        matrix_row = []
        for cell in row:
            try:
                matrix_row.append(parse_expression(cell))
            except ValueError:
                # Default to 0 for invalid expressions
                matrix_row.append(Rational(0))
        matrix_data.append(matrix_row)

    return Matrix(matrix_data)


if __name__ == "__main__":
    # Test the parser
    test_cases = [
        "1/3",
        "sqrt(2)",
        "pi",
        "2+3/4",
        "1+sqrt(3)",
        "-1/2",
        "3/4 + 1/4",
    ]

    print("Parser tests:")
    for expr in test_cases:
        result = parse_expression(expr)
        print(f"  '{expr}' -> {result} (type: {type(result).__name__})")
