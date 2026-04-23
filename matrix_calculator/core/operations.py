"""
Matrix mathematical operations for symbolic calculator.
All operations maintain symbolic representation.
"""

from sympy import Matrix, Transpose, Inverse, det, eye, Trace, symbols


def add(A: Matrix, B: Matrix) -> Matrix:
    """Matrix addition A + B"""
    return A + B


def subtract(A: Matrix, B: Matrix) -> Matrix:
    """Matrix subtraction A - B"""
    return A - B


def multiply(A: Matrix, B: Matrix) -> Matrix:
    """Matrix multiplication A * B"""
    return A * B


def transpose(A: Matrix) -> Matrix:
    """Matrix transpose A^T"""
    return A.transpose()


def inverse(A: Matrix) -> Matrix:
    """Matrix inverse A^(-1)"""
    if not A.is_square:
        raise ValueError("Matrix must be square for inverse")
    return A.inv()


def determinant(A: Matrix):
    """Matrix determinant det(A)"""
    if not A.is_square:
        raise ValueError("Matrix must be square for determinant")
    return det(A)


def matrix_rank(A: Matrix):
    """Matrix rank rank(A)"""
    return A.rank()


def trace(A: Matrix):
    """Matrix trace tr(A)"""
    if not A.is_square:
        raise ValueError("Matrix must be square for trace")
    return Trace(A)


def char_poly(A: Matrix):
    """
    Characteristic polynomial of matrix A.
    Returns the symbolic characteristic polynomial p(λ) = det(A - λI)
    """
    if not A.is_square:
        raise ValueError("Matrix must be square for characteristic polynomial")
    lam = symbols('lambda')
    return A.charpoly(lam)


def eigen_values(A: Matrix):
    """
    Compute eigenvalues of matrix A.
    Returns list of (eigenvalue, multiplicity, eigenvectors) tuples.
    """
    if not A.is_square:
        raise ValueError("Matrix must be square for eigenvalues")
    return A.eigenvects()


def eigen_values_only(A: Matrix):
    """
    Compute eigenvalues of matrix A.
    Returns dict of {eigenvalue: multiplicity}.
    """
    if not A.is_square:
        raise ValueError("Matrix must be square for eigenvalues")
    return A.eigenvals()


def scalar_multiply(A: Matrix, scalar) -> Matrix:
    """Multiply matrix by scalar"""
    return A * scalar


if __name__ == "__main__":
    # Test basic operations
    from sympy import Matrix

    A = Matrix([[1, 2], [3, 4]])
    B = Matrix([[5, 6], [7, 8]])

    print("Matrix A:")
    print(A)
    print("\nMatrix B:")
    print(B)
    print(f"\nA + B = \n{add(A, B)}")
    print(f"\nA * B = \n{multiply(A, B)}")
    print(f"\nA^T = \n{transpose(A)}")
    print(f"\ndet(A) = {determinant(A)}")
    print(f"\nRank(A) = {matrix_rank(A)}")
