"""
LaTeX rendering widget for displaying mathematical expressions.
Uses Matplotlib's FigureCanvasQTAgg to render LaTeX strings.
"""

import os
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend for PyQt6

# Configure LaTeX preamble for amsmath support
matplotlib.rcParams['text.latex.preamble'] = r'\usepackage{amsmath}\usepackage{amsfonts}'

from matplotlib.figure import Figure
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
from PyQt6.QtWidgets import QScrollArea, QWidget, QVBoxLayout, QLabel
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

from matrix_calculator.ui.i18n import i18n


# LaTeX preamble for proper mathematical rendering
LATEX_PREAMBLE = r"""
\usepackage{amsmath}
\usepackage{amssymb}
\usepackage{amsfonts}
\DeclareMathSizes{10}{12}{8}{6}
"""


class LatexRenderWidget(QScrollArea):
    """
    Widget for rendering LaTeX mathematical expressions.

    Features:
    - Renders LaTeX strings using Matplotlib
    - Supports horizontal fraction lines
    - Auto-scales for large expressions
    - Dark theme compatible
    """

    def __init__(self, parent=None):
        super().__init__(parent)

        # Create figure with white background
        self.figure = Figure(figsize=(8, 4), dpi=100)
        self.figure.patch.set_facecolor('#ffffff')
        self.figure.patch.set_alpha(1)

        # Create canvas
        self.canvas = FigureCanvasQTAgg(self.figure)
        self.canvas.setStyleSheet("background-color: transparent;")

        # Wrapper widget for canvas
        self.canvas_widget = QWidget()
        layout = QVBoxLayout(self.canvas_widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.canvas)

        self.setWidget(self.canvas_widget)
        self.setWidgetResizable(True)
        self.setMinimumHeight(200)

        # Style
        self.setStyleSheet("""
            QScrollArea {
                background-color: #ffffff;
                border: 1px solid #ddd;
                border-radius: 8px;
            }
            QScrollBar:vertical {
                background-color: #f0f0f0;
                width: 12px;
            }
            QScrollBar::handle:vertical {
                background-color: #ccc;
                border-radius: 6px;
            }
        """)

        # Initial render
        self.clear()

    def set_latex(self, latex_str: str, title: str = None):
        """
        Render a LaTeX string.

        Args:
            latex_str: LaTeX expression to render
            title: Optional title/label for the expression
        """
        # Clear previous plot
        self.figure.clear()

        # Create axes with no frame
        ax = self.figure.add_subplot(111)
        ax.set_frame_on(False)
        ax.axis('off')

        # Set text color for light theme
        text_color = '#333333'

        # Build full LaTeX string
        if title:
            if title.endswith('= '):
                full_latex = rf"{title}{latex_str}"
            else:
                full_latex = rf"{title} \, : \, {latex_str}"
        else:
            full_latex = latex_str

        try:
            ax.text(0.5, 0.5, f"${full_latex}$",
                    fontsize=14,
                    ha='center', va='center',
                    color=text_color,
                    transform=ax.transAxes,
                    usetex=True,  # Use LaTeX for proper matrix rendering
                    wrap=True)

            # Adjust figure size based on content
            self.figure.tight_layout(pad=2.0)
            self.canvas.draw()

        except Exception as e:
            # Show error message
            ax.text(0.5, 0.5, f"Render error: {str(e)}",
                    fontsize=12, ha='center', va='center', color='red')
            self.canvas.draw()

    def clear(self):
        """Clear the render area."""
        self.set_latex(r"\text{Result will appear here}")

    def render_matrix(self, matrix, title: str = None):
        """
        Render a SymPy matrix with proper LaTeX formatting.

        Args:
            matrix: SymPy Matrix object
            title: Optional title for the matrix
        """
        from sympy import latex

        # Generate LaTeX for matrix - mode='plain' gives clean output with brackets
        matrix_latex = latex(matrix, mode='plain')

        if title:
            self.set_latex(matrix_latex, title=title)
        else:
            self.set_latex(matrix_latex)

    def render_operation(self, A, B, operation: str, result, op_name: str = None):
        """
        Render a binary matrix operation with result.

        Args:
            A: Left matrix (SymPy Matrix)
            B: Right matrix (SymPy Matrix)
            operation: The operator symbol (e.g., '+', '-', '*')
            result: Result matrix (SymPy Matrix)
            op_name: Optional name for the operation
        """
        from sympy import latex

        # Generate LaTeX for matrices - mode='plain' gives clean output
        def matrix_to_latex(m):
            return latex(m, mode='plain')

        A_latex = matrix_to_latex(A)
        B_latex = matrix_to_latex(B)
        result_latex = matrix_to_latex(result)

        if op_name:
            full_latex = rf"{A_latex} \ {operation} \ {B_latex} \ = \ {result_latex}"
        else:
            full_latex = rf"{A_latex} \ {operation} \ {B_latex} \ = \ {result_latex}"

        self.set_latex(full_latex, op_name)

    def render_jordan(self, A, J, P, P_inv, valid: bool, error_msg: str = None):
        """
        Render Jordan decomposition result.

        Args:
            A: Original matrix
            J: Jordan form
            P: Transformation matrix
            P_inv: Inverse of P
            valid: Whether A = PJP^(-1) is verified
            error_msg: Error message if verification failed
        """
        from sympy import latex

        def matrix_to_latex(m):
            return latex(m, mode='plain')

        A_latex = matrix_to_latex(A)
        J_latex = matrix_to_latex(J)
        P_latex = matrix_to_latex(P)
        P_inv_latex = matrix_to_latex(P_inv)

        # Verification status
        if valid:
            verify_status = r"\quad \checkmark \text{ Verified: } A = PJP^{-1}"
        else:
            verify_status = rf"\quad \times \text{{ Verification Failed }}"

        full_latex = (
            rf"A = {A_latex} \\ "
            rf"J = {J_latex} \\ "
            rf"P = {P_latex} \\ "
            rf"P^{{-1}} = {P_inv_latex} \\ "
            rf"{verify_status}"
        )

        self.set_latex(full_latex)

    def render_eigen(self, A, char_poly, eigenvalues, eigenvectors):
        """
        Render eigenanalysis results.

        Args:
            A: Original matrix
            char_poly: Characteristic polynomial
            eigenvalues: Eigenvalues dict or list
            eigenvectors: List of eigenvector tuples
        """
        from sympy import latex, simplify

        def matrix_to_latex(m):
            return latex(m, mode='plain')

        A_latex = matrix_to_latex(A)

        # Characteristic polynomial
        poly_latex = rf"p(\lambda) = \det(A - \lambda I) = {latex(simplify(char_poly))}"

        # Eigenvalues
        if hasattr(eigenvalues, 'items'):
            # Dict format
            eigen_lines = [rf"\lambda = {latex(val)}" + (f"\\; (m={mult})" if mult > 1 else "")
                          for val, mult in eigenvalues.items()]
        else:
            # List format
            eigen_lines = [rf"\lambda = {latex(val)}" for val in eigenvalues]

        eigen_latex = r" \\ ".join(eigen_lines)

        full_latex = (
            rf"A = {A_latex} \\ "
            rf"{poly_latex} \\ "
            rf"\text{Eigenvalues:} \; {eigen_latex}"
        )

        self.set_latex(full_latex)


class LatexRenderWidgetSimple(QWidget):
    """
    Simpler LaTeX label widget for inline rendering.
    Uses QLabel with text rendering for simple expressions.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.label = QLabel()
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label.setStyleSheet("""
            QLabel {
                color: #333;
                font-size: 14px;
                padding: 10px;
            }
        """)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.label)

    def set_latex(self, latex_str: str):
        """Set LaTeX text (basic formatting)."""
        self.label.setText(f"${latex_str}$")

    def clear(self):
        """Clear the label."""
        self.label.setText(r"\text{Result will appear here}")