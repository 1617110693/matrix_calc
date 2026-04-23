"""
Main window for Matrix Symbolic Calculator.
Provides UI for matrix operations and Jordan decomposition.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QSplitter,
    QPushButton, QLabel, QComboBox, QGroupBox, QFormLayout,
    QTextEdit, QScrollArea, QMessageBox, QApplication, QSizePolicy
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QTimer
from PyQt6.QtGui import QFont

from sympy import Matrix, simplify

from ui.matrix_input import MatrixInputWidget, DualMatrixInput
from ui.latex_renderer import LatexRenderWidget
from core.operations import (
    add, subtract, multiply, transpose, inverse,
    determinant, matrix_rank, trace, char_poly,
    eigen_values, eigen_values_only
)
from core.jordan import jordan_decomposition, verify_jordan


class CalculationThread(QThread):
    """
    Thread for performing heavy matrix calculations without blocking UI.
    """

    finished = pyqtSignal(object)
    error = pyqtSignal(str)
    progress = pyqtSignal(str)

    def __init__(self, func, *args, **kwargs):
        super().__init__()
        self.func = func
        self.args = args
        self.kwargs = kwargs

    def run(self):
        try:
            self.progress.emit("Calculating...")
            result = self.func(*self.args, **self.kwargs)
            self.finished.emit(result)
        except Exception as e:
            self.error.emit(str(e))


class MainWindow(QMainWindow):
    """
    Main application window for Matrix Symbolic Calculator.
    """

    def __init__(self):
        super().__init__()

        self.setWindowTitle("Matrix Symbolic Calculator")
        self.setMinimumSize(1200, 800)

        # Apply dark theme
        self._apply_stylesheet()

        # Current operation mode
        self.current_mode = "single"  # "single", "dual", "jordan"

        # Thread for calculations
        self.calc_thread = None

        self._init_ui()

    def _apply_stylesheet(self):
        """Apply light theme stylesheet."""
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f5f5f5;
            }
            QWidget {
                background-color: #ffffff;
                color: #333333;
            }
            QPushButton {
                background-color: #0d6efd;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 10px 20px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #0b5ed7;
            }
            QPushButton:pressed {
                background-color: #0a58ca;
            }
            QPushButton:disabled {
                background-color: #ccc;
                color: #888;
            }
            QLabel {
                color: #333333;
            }
            QComboBox {
                background-color: #ffffff;
                color: #333333;
                border: 1px solid #ccc;
                border-radius: 4px;
                padding: 6px 12px;
            }
            QComboBox::drop-down {
                border: none;
            }
            QComboBox::item {
                background-color: #ffffff;
                color: #333333;
            }
            QComboBox::item:hover {
                background-color: #e6f0ff;
            }
            QGroupBox {
                border: 1px solid #ddd;
                border-radius: 8px;
                margin-top: 12px;
                font-weight: bold;
                color: #333333;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top left;
                padding: 4px 8px;
                color: #666666;
            }
        """)

    def _init_ui(self):
        """Initialize the user interface."""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QHBoxLayout(central_widget)

        # Create splitter for resizable panels
        splitter = QSplitter(Qt.Orientation.Horizontal)
        main_layout.addWidget(splitter)

        # Left panel - Input
        left_panel = self._create_input_panel()
        splitter.addWidget(left_panel)

        # Right panel - Results
        right_panel = self._create_result_panel()
        splitter.addWidget(right_panel)

        # Set initial splitter sizes
        splitter.setSizes([600, 600])

    def _create_input_panel(self) -> QWidget:
        """Create the left input panel."""
        panel = QWidget()
        layout = QVBoxLayout(panel)

        # Title
        title = QLabel("Matrix Calculator")
        title.setStyleSheet("""
            font-size: 24px;
            font-weight: bold;
            color: #4a9eff;
            padding: 10px;
        """)
        layout.addWidget(title)

        # Mode selector
        mode_layout = QHBoxLayout()
        mode_label = QLabel("Operation Mode:")
        mode_label.setStyleSheet("font-weight: bold;")

        self.mode_combo = QComboBox()
        self.mode_combo.addItems([
            "Single Matrix Operations",
            "Binary Operations (A + B, A * B, etc.)",
            "Jordan Decomposition"
        ])
        self.mode_combo.currentIndexChanged.connect(self._on_mode_changed)
        mode_layout.addWidget(mode_label)
        mode_layout.addWidget(self.mode_combo)
        mode_layout.addStretch()

        layout.addLayout(mode_layout)

        # Stacked widget for different input modes
        self.input_stack = QWidget()
        stack_layout = QVBoxLayout(self.input_stack)
        stack_layout.setContentsMargins(0, 10, 0, 10)

        # Single matrix mode
        self.single_input = MatrixInputWidget(label="Matrix A", default_rows=2, default_cols=2)
        self.single_input.matrix_changed.connect(self._on_matrix_changed)
        stack_layout.addWidget(self.single_input)

        # Dual matrix mode
        self.dual_input = DualMatrixInput()
        self.dual_input.hide()
        stack_layout.addWidget(self.dual_input)

        # Jordan mode
        self.jordan_input = MatrixInputWidget(label="Matrix A (for Jordan)", default_rows=2, default_cols=2)
        self.jordan_input.hide()
        stack_layout.addWidget(self.jordan_input)

        layout.addWidget(self.input_stack)

        # Operation buttons
        self._create_operation_buttons(layout)

        layout.addStretch()

        return panel

    def _create_operation_buttons(self, parent_layout: QVBoxLayout):
        """Create operation buttons based on current mode."""
        # Buttons container
        buttons_group = QGroupBox("Operations")
        buttons_layout = QVBoxLayout()

        # Single matrix operations
        self.single_ops_frame = QWidget()
        single_ops_layout = QHBoxLayout(self.single_ops_frame)
        single_ops_layout.setContentsMargins(0, 0, 0, 0)

        transpose_btn = self._create_button("A^T", self._on_transpose)
        det_btn = self._create_button("det(A)", self._on_determinant)
        rank_btn = self._create_button("rank(A)", self._on_rank)
        trace_btn = self._create_button("tr(A)", self._on_trace)
        inverse_btn = self._create_button("A^-1", self._on_inverse)

        single_ops_layout.addWidget(transpose_btn)
        single_ops_layout.addWidget(det_btn)
        single_ops_layout.addWidget(rank_btn)
        single_ops_layout.addWidget(trace_btn)
        single_ops_layout.addWidget(inverse_btn)

        buttons_layout.addWidget(self.single_ops_frame)

        # Eigen analysis buttons
        eigen_frame = QWidget()
        eigen_layout = QHBoxLayout(eigen_frame)
        eigen_layout.setContentsMargins(0, 0, 0, 0)

        char_poly_btn = self._create_button("p(λ)", self._on_char_poly)
        eigen_btn = self._create_button("Eigenvalues", self._on_eigenvalues)
        eigen_vec_btn = self._create_button("Eigenvectors", self._on_eigenvectors)

        eigen_layout.addWidget(char_poly_btn)
        eigen_layout.addWidget(eigen_btn)
        eigen_layout.addWidget(eigen_vec_btn)

        buttons_layout.addWidget(eigen_frame)

        # Binary operations
        self.dual_ops_frame = QWidget()
        self.dual_ops_frame.hide()
        dual_ops_layout = QHBoxLayout(self.dual_ops_frame)
        dual_ops_layout.setContentsMargins(0, 0, 0, 0)

        add_btn = self._create_button("A + B", lambda: self._on_binary_op("+"))
        sub_btn = self._create_button("A - B", lambda: self._on_binary_op("-"))
        mul_btn = self._create_button("A * B", lambda: self._on_binary_op("*"))

        dual_ops_layout.addWidget(add_btn)
        dual_ops_layout.addWidget(sub_btn)
        dual_ops_layout.addWidget(mul_btn)

        buttons_layout.addWidget(self.dual_ops_frame)

        # Jordan decomposition
        self.jordan_ops_frame = QWidget()
        self.jordan_ops_frame.hide()
        jordan_ops_layout = QHBoxLayout(self.jordan_ops_frame)
        jordan_ops_layout.setContentsMargins(0, 0, 0, 0)

        jordan_btn = self._create_button("Jordan Decomposition", self._on_jordan, accent=True)
        jordan_btn.setMinimumHeight(45)

        jordan_ops_layout.addWidget(jordan_btn)

        buttons_layout.addWidget(self.jordan_ops_frame)

        buttons_group.setLayout(buttons_layout)
        parent_layout.addWidget(buttons_group)

    def _create_button(self, text: str, handler, accent: bool = False) -> QPushButton:
        """Create a styled button."""
        btn = QPushButton(text)
        if accent:
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #28a745;
                    color: white;
                    border: none;
                    border-radius: 6px;
                    padding: 12px 24px;
                    font-size: 14px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #218838;
                }
            """)
        btn.clicked.connect(handler)
        return btn

    def _create_result_panel(self) -> QWidget:
        """Create the right result display panel."""
        panel = QWidget()
        layout = QVBoxLayout(panel)

        # Title
        title = QLabel("Result")
        title.setStyleSheet("""
            font-size: 20px;
            font-weight: bold;
            color: #4a9eff;
            padding: 10px;
        """)
        layout.addWidget(title)

        # LaTeX renderer
        self.latex_renderer = LatexRenderWidget()
        layout.addWidget(self.latex_renderer)

        # Status indicator
        self.status_label = QLabel("")
        self.status_label.setStyleSheet("""
            color: #aaa;
            font-size: 12px;
            padding: 5px;
        """)
        layout.addWidget(self.status_label)

        return panel

    def _on_mode_changed(self, index: int):
        """Handle operation mode change."""
        modes = ["single", "dual", "jordan"]
        self.current_mode = modes[index]

        # Show/hide appropriate inputs
        self.single_input.setVisible(self.current_mode == "single")
        self.dual_ops_frame.setVisible(self.current_mode == "dual")
        self.single_ops_frame.setVisible(self.current_mode == "single")
        self.dual_input.setVisible(self.current_mode == "dual")
        self.jordan_input.setVisible(self.current_mode == "jordan")
        self.jordan_ops_frame.setVisible(self.current_mode == "jordan")

        # Show/hide relevant frames
        for frame in [self.single_ops_frame.parent()]:
            if hasattr(frame, 'setVisible'):
                pass

        self.latex_renderer.clear()
        self.status_label.setText("")

    def _on_matrix_changed(self, matrix: Matrix):
        """Handle matrix content change."""
        pass  # Can add live preview here

    def _get_current_matrix(self) -> Matrix:
        """Get the current matrix based on operation mode."""
        if self.current_mode == "single":
            return self.single_input.get_matrix()
        elif self.current_mode == "dual":
            return self.dual_input.matrix_a.get_matrix()
        else:  # jordan
            return self.jordan_input.get_matrix()

    def _run_calculation(self, func, *args, callback):
        """
        Run a calculation in a separate thread.

        Args:
            func: Function to run
            *args: Arguments to pass to function
            callback: Callback to receive result
        """
        # Cancel any existing thread
        if self.calc_thread and self.calc_thread.isRunning():
            self.calc_thread.terminate()
            self.calc_thread.wait()

        self.calc_thread = CalculationThread(func, *args)
        self.calc_thread.finished.connect(callback)
        self.calc_thread.error.connect(self._on_calculation_error)
        self.calc_thread.progress.connect(self.status_label.setText)
        self.calc_thread.start()

        self.status_label.setText("Calculating...")

    def _on_calculation_error(self, error_msg: str):
        """Handle calculation error."""
        self.status_label.setText(f"Error: {error_msg}")
        self.status_label.setStyleSheet("color: #ff6b6b; font-size: 12px; padding: 5px;")
        QMessageBox.critical(self, "Calculation Error", error_msg)

    def _on_transpose(self):
        """Handle transpose operation."""
        A = self._get_current_matrix()
        self._run_calculation(lambda: transpose(A), callback=self._display_single_result)

    def _on_determinant(self):
        """Handle determinant calculation."""
        A = self._get_current_matrix()
        self._run_calculation(lambda: determinant(A), callback=self._display_scalar_result)

    def _on_rank(self):
        """Handle rank calculation."""
        A = self._get_current_matrix()
        self._run_calculation(lambda: matrix_rank(A), callback=self._display_scalar_result)

    def _on_trace(self):
        """Handle trace calculation."""
        A = self._get_current_matrix()
        self._run_calculation(lambda: trace(A), callback=self._display_scalar_result)

    def _on_inverse(self):
        """Handle inverse operation."""
        A = self._get_current_matrix()
        self._run_calculation(lambda: inverse(A), callback=self._display_single_result)

    def _on_char_poly(self):
        """Handle characteristic polynomial."""
        A = self._get_current_matrix()
        self._run_calculation(lambda: char_poly(A), callback=self._display_poly_result)

    def _on_eigenvalues(self):
        """Handle eigenvalue calculation."""
        A = self._get_current_matrix()
        self._run_calculation(lambda: eigen_values_only(A), callback=self._display_eigen_result)

    def _on_eigenvectors(self):
        """Handle eigenvector calculation."""
        A = self._get_current_matrix()
        self._run_calculation(lambda: eigen_values(A), callback=self._display_eigenvec_result)

    def _on_binary_op(self, op: str):
        """Handle binary operations."""
        A, B = self.dual_input.get_matrices()

        try:
            if op == "+":
                result = add(A, B)
            elif op == "-":
                result = subtract(A, B)
            elif op == "*":
                result = multiply(A, B)
            else:
                raise ValueError(f"Unknown operation: {op}")

            self._run_calculation(lambda: result, callback=self._display_dual_result)

        except Exception as e:
            self._on_calculation_error(str(e))

    def _on_jordan(self):
        """Handle Jordan decomposition."""
        A = self.jordan_input.get_matrix()

        if not A.is_square:
            QMessageBox.warning(self, "Invalid Matrix", "Jordan decomposition requires a square matrix.")
            return

        def do_jordan():
            J, P, P_inv = jordan_decomposition(A)
            valid, msg = verify_jordan(A, J, P, P_inv)
            return (J, P, P_inv, valid, msg)

        self._run_calculation(do_jordan, callback=self._display_jordan_result)

    def _display_single_result(self, result):
        """Display single matrix result."""
        self.status_label.setText("")
        self.status_label.setStyleSheet("color: #aaa; font-size: 12px; padding: 5px;")
        self.latex_renderer.render_matrix(result, title="Result")

    def _display_scalar_result(self, result):
        """Display scalar result."""
        self.status_label.setText("")
        from sympy import latex
        latex_str = latex(simplify(result))
        self.latex_renderer.set_latex(latex_str, title="Result")

    def _display_poly_result(self, result):
        """Display characteristic polynomial."""
        self.status_label.setText("")
        from sympy import latex
        poly_latex = latex(simplify(result))
        lam = self.latex_renderer
        lam.set_latex(rf"p(\lambda) = {poly_latex}", title="Characteristic Polynomial")

    def _display_eigen_result(self, eigenvalues):
        """Display eigenvalues."""
        self.status_label.setText("")
        from sympy import latex
        if hasattr(eigenvalues, 'items'):
            eigen_lines = []
            for val, mult in eigenvalues.items():
                mult_str = f" (m={mult})" if mult > 1 else ""
                eigen_lines.append(rf"{latex(val)}{mult_str}")
            eigen_latex = r", \; ".join(eigen_lines)
        else:
            eigen_latex = latex(eigenvalues)
        self.latex_renderer.set_latex(rf"\lambda = {eigen_latex}", title="Eigenvalues")

    def _display_eigenvec_result(self, eigenvecs):
        """Display eigenvectors."""
        self.status_label.setText("")
        lines = []
        for val, mult, vecs in eigenvecs:
            from sympy import latex
            val_latex = latex(val)
            for i, vec in enumerate(vecs):
                lines.append(rf"\lambda = {val_latex} : \; {latex(vec.T.tolist()[0])}")
        full_latex = r" \\ ".join(lines)
        self.latex_renderer.set_latex(full_latex, title="Eigenvectors")

    def _display_dual_result(self, result):
        """Display binary operation result."""
        self.status_label.setText("")
        self.latex_renderer.render_matrix(result, title="Result")

    def _display_jordan_result(self, result):
        """Display Jordan decomposition result."""
        J, P, P_inv, valid, msg = result
        self.status_label.setText("")
        self.latex_renderer.render_jordan(
            self.jordan_input.get_matrix(),
            J, P, P_inv, valid, msg
        )
        if valid:
            self.status_label.setText("Verification: A = PJP⁻¹  ✓")
            self.status_label.setStyleSheet("color: #28a745; font-size: 14px; padding: 5px; font-weight: bold;")
        else:
            self.status_label.setText("Verification: FAILED ✗")
            self.status_label.setStyleSheet("color: #ff6b6b; font-size: 14px; padding: 5px; font-weight: bold;")
