"""
Jordan decomposition for symbolic matrix calculator.
Computes Jordan canonical form J and transformation matrix P such that A = PJP^(-1).
"""

from sympy import Matrix, simplify, eye, zeros, ImmutableMatrix
from sympy.matrices import Matrix as SymPyMatrix


def jordan_decomposition(A: Matrix):
    """
    Compute Jordan decomposition of matrix A.

    Returns:
        tuple: (J, P, P_inv) where:
            - J: Jordan canonical form
            - P: Transformation matrix
            - P_inv: Inverse of P (i.e., P^(-1))

    Raises:
        ValueError: If matrix is not square

    Note:
        Uses diagonalize() for diagonalizable matrices (jordan_form has bugs in sympy 1.14).
        For non-diagonalizable matrices, uses jordan_form() with error handling.
    """
    if not A.is_square:
        raise ValueError("Jordan decomposition requires a square matrix")

    try:
        # Try diagonalize first (more reliable in sympy 1.14.0)
        if A.is_diagonalizable():
            P, J = A.diagonalize()
            P_inv = P.inv()
            J = simplify(J)
            P = simplify(P)
            P_inv = simplify(P_inv)
            return J, P, P_inv
    except Exception:
        pass

    # Fallback to jordan_form for non-diagonalizable matrices
    try:
        J, P = A.jordan_form()
        P_inv = P.inv()
        J = simplify(J)
        P = simplify(P)
        P_inv = simplify(P_inv)
        return J, P, P_inv
    except Exception as e:
        raise ValueError(f"Jordan decomposition failed: {str(e)}")


def verify_jordan(A: Matrix, J: Matrix, P: Matrix, P_inv: Matrix):
    """
    Verify that A = P * J * P^(-1).

    Returns:
        tuple: (is_valid: bool, error_message: str or None)
    """
    try:
        # Compute P * J * P^(-1)
        reconstructed = P * J * P_inv

        # Simplify and check equality
        diff = simplify(reconstructed - A)

        # Check if difference is zero matrix
        is_zero = all(abs(x) < 1e-10 for x in diff)

        if is_zero:
            return True, None
        else:
            # Try symbolic equality check
            is_equal = simplify(diff) == zeros(diff.rows, diff.cols)
            if is_equal:
                return True, None
            return False, f"A ≠ PJP⁻¹\n\nA =\n{A}\n\nPJP⁻¹ =\n{reconstructed}"

    except Exception as e:
        return False, f"Verification error: {str(e)}"


def jordan_blocks_info(J: Matrix):
    """
    Extract information about Jordan blocks from Jordan form.

    Returns:
        list: List of (eigenvalue, block_size, multiplicity) tuples
    """
    from sympy import Rational

    blocks = []
    n = J.rows
    i = 0

    while i < n:
        eigenvalue = J[i, i]
        block_size = 1
        j = i + 1

        # Count consecutive ones on subdiagonal for this block
        while j < n and J[j-1, j] == 1:
            block_size += 1
            j += 1

        blocks.append((eigenvalue, block_size, block_size))
        i = j

    return blocks


if __name__ == "__main__":
    # Test with simple matrices
    from sympy import Rational, symbols

    print("Test 1: 2x2 diagonalizable matrix")
    A1 = Matrix([[1, 2], [3, 4]])
    try:
        J1, P1, P_inv1 = jordan_decomposition(A1)
        print(f"A = \n{A1}")
        print(f"J = \n{J1}")
        print(f"P = \n{P1}")
        print(f"P_inv = \n{P_inv1}")
        valid, msg = verify_jordan(A1, J1, P1, P_inv1)
        print(f"Verification: {'PASSED' if valid else 'FAILED'}")
        if msg:
            print(msg)
    except Exception as e:
        print(f"Error: {e}")

    print("\n" + "="*50 + "\n")

    print("Test 2: 2x2 matrix with fractions")
    A2 = Matrix([[Rational(1, 2), Rational(3, 4)], [Rational(1, 4), Rational(1, 2)]])
    try:
        J2, P2, P_inv2 = jordan_decomposition(A2)
        print(f"A = \n{A2}")
        print(f"J = \n{J2}")
        print(f"P = \n{P2}")
        print(f"P_inv = \n{P_inv2}")
        valid, msg = verify_jordan(A2, J2, P2, P_inv2)
        print(f"Verification: {'PASSED' if valid else 'FAILED'}")
    except Exception as e:
        print(f"Error: {e}")
