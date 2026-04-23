"""
Matrix Symbolic Calculator - Main Entry Point

A professional-grade Windows desktop application for symbolic matrix computation
using Python 3, PyQt6, and SymPy.

Features:
- Dynamic matrix dimensions (2x2 to 6x6)
- Exact symbolic input (fractions, sqrt, pi)
- Basic operations: add, subtract, multiply, transpose, inverse, determinant, rank
- Eigen analysis: characteristic polynomial, eigenvalues, eigenvectors
- Jordan decomposition with auto-verification A = PJP^(-1)
- LaTeX rendered output with horizontal fraction lines
"""

import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt

from ui.main_window import MainWindow


def main():
    """Application entry point."""
    # Enable high DPI scaling
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )

    # Create application
    app = QApplication(sys.argv)
    app.setApplicationName("Matrix Symbolic Calculator")
    app.setOrganizationName("MatrixCalc")

    # Set application style
    app.setStyle('Fusion')

    # Create and show main window
    window = MainWindow()
    window.show()

    # Run application
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
