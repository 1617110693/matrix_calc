"""
Matrix input widget using QTableWidget.
Provides dynamic matrix dimension adjustment.
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QSpinBox, QLabel, QPushButton, QGroupBox, QFormLayout
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont, QColor, QPalette

from sympy import Matrix

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from matrix_calculator.core.parser import parse_expression, matrix_from_strings
from ui.i18n import i18n


class MatrixInputWidget(QWidget):
    """
    Widget for matrix input with dynamic dimension control.

    Signals:
        matrix_changed(Matrix): Emitted when matrix content changes
    """

    matrix_changed = pyqtSignal(object)

    def __init__(self, label: str = "Matrix", default_rows: int = 2, default_cols: int = 2, parent=None):
        super().__init__(parent)

        self.default_rows = default_rows
        self.default_cols = default_cols
        self.label_text = label

        self._init_ui()

    def _init_ui(self):
        """Initialize the user interface."""
        main_layout = QVBoxLayout(self)

        # Group box
        self.group = QGroupBox(self.label_text)
        group_layout = QVBoxLayout()

        # Dimension controls
        dim_layout = QHBoxLayout()

        rows_label = QLabel(i18n.t("rows"))
        rows_label.setStyleSheet("color: #333; font-weight: bold;")
        dim_layout.addWidget(rows_label)

        # Custom rows control with +/- buttons
        rows_control = QHBoxLayout()
        rows_minus = QPushButton("-")
        rows_minus.setStyleSheet("""
            QPushButton {
                background-color: #0d6efd;
                color: white;
                border: none;
                border-radius: 4px;
                width: 32px;
                height: 32px;
                font-size: 18px;
                font-weight: bold;
            }
            QPushButton:hover { background-color: #0b5ed7; }
            QPushButton:pressed { background-color: #0a58ca; }
        """)
        rows_minus.clicked.connect(lambda: self._change_rows(-1))
        rows_control.addWidget(rows_minus)

        self.rows_value = QLabel(str(self.default_rows))
        self.rows_value.setStyleSheet("""
            color: #333;
            font-weight: bold;
            font-size: 16px;
            min-width: 30px;
            alignment: center;
        """)
        rows_control.addWidget(self.rows_value)

        rows_plus = QPushButton("+")
        rows_plus.setStyleSheet("""
            QPushButton {
                background-color: #0d6efd;
                color: white;
                border: none;
                border-radius: 4px;
                width: 32px;
                height: 32px;
                font-size: 18px;
                font-weight: bold;
            }
            QPushButton:hover { background-color: #0b5ed7; }
            QPushButton:pressed { background-color: #0a58ca; }
        """)
        rows_plus.clicked.connect(lambda: self._change_rows(1))
        rows_control.addWidget(rows_plus)
        dim_layout.addLayout(rows_control)

        cols_label = QLabel(i18n.t("cols"))
        cols_label.setStyleSheet("color: #333; font-weight: bold;")
        dim_layout.addWidget(cols_label)

        # Custom cols control with +/- buttons
        cols_control = QHBoxLayout()
        cols_minus = QPushButton("-")
        cols_minus.setStyleSheet("""
            QPushButton {
                background-color: #0d6efd;
                color: white;
                border: none;
                border-radius: 4px;
                width: 32px;
                height: 32px;
                font-size: 18px;
                font-weight: bold;
            }
            QPushButton:hover { background-color: #0b5ed7; }
            QPushButton:pressed { background-color: #0a58ca; }
        """)
        cols_minus.clicked.connect(lambda: self._change_cols(-1))
        cols_control.addWidget(cols_minus)

        self.cols_value = QLabel(str(self.default_cols))
        self.cols_value.setStyleSheet("""
            color: #333;
            font-weight: bold;
            font-size: 16px;
            min-width: 30px;
            alignment: center;
        """)
        cols_control.addWidget(self.cols_value)

        cols_plus = QPushButton("+")
        cols_plus.setStyleSheet("""
            QPushButton {
                background-color: #0d6efd;
                color: white;
                border: none;
                border-radius: 4px;
                width: 32px;
                height: 32px;
                font-size: 18px;
                font-weight: bold;
            }
            QPushButton:hover { background-color: #0b5ed7; }
            QPushButton:pressed { background-color: #0a58ca; }
        """)
        cols_plus.clicked.connect(lambda: self._change_cols(1))
        cols_control.addWidget(cols_plus)
        dim_layout.addLayout(cols_control)

        dim_layout.addStretch()

        # Clear button
        clear_btn = QPushButton(i18n.t("btn_clear") if hasattr(i18n, 't') else "Clear")
        clear_btn.setStyleSheet("""
            QPushButton {
                background-color: #ff4444;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px 20px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #ff2222;
            }
            QPushButton:pressed {
                background-color: #dd0000;
            }
        """)
        clear_btn.clicked.connect(self._clear_matrix)
        dim_layout.addWidget(clear_btn)

        group_layout.addLayout(dim_layout)

        # Table widget
        self.table = QTableWidget()
        self.table.setStyleSheet("""
            QTableWidget {
                background-color: #ffffff;
                color: #333;
                gridline-color: #ddd;
                border: 1px solid #ddd;
                border-radius: 4px;
            }
            QTableWidget::item {
                padding: 4px;
            }
            QTableWidget::item:selected {
                background-color: #cce0ff;
            }
            QHeaderView::section {
                background-color: #f0f0f0;
                color: #333;
                padding: 4px;
                border: 1px solid #ddd;
            }
        """)
        self.table.setFont(QFont("Consolas", 12))
        self.table.setAlternatingRowColors(True)
        self.table.setSizeAdjustPolicy(QTableWidget.SizeAdjustPolicy.AdjustToContents)

        # Initialize table
        self._setup_table(self.default_rows, self.default_cols)

        group_layout.addWidget(self.table)

        self.group.setLayout(group_layout)
        main_layout.addWidget(self.group)

        # Set light theme for group
        self.group.setStyleSheet("""
            QGroupBox {
                color: #333;
                border: 1px solid #ddd;
                border-radius: 8px;
                margin-top: 8px;
                font-weight: bold;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top left;
                padding: 4px 8px;
                color: #666;
            }
        """)

    def _setup_table(self, rows: int, cols: int):
        """
        Setup table dimensions and headers.

        Args:
            rows: Number of rows
            cols: Number of columns
        """
        self.table.blockSignals(True)
        self.table.setRowCount(rows)
        self.table.setColumnCount(cols)

        # Set headers
        for i in range(cols):
            header_item = QTableWidgetItem(f"col {i+1}")
            header_item.setBackground(QColor("#333"))
            self.table.setHorizontalHeaderItem(i, header_item)

        for i in range(rows):
            header_item = QTableWidgetItem(f"row {i+1}")
            header_item.setBackground(QColor("#333"))
            self.table.setVerticalHeaderItem(i, header_item)

        # Initialize empty cells
        for i in range(rows):
            for j in range(cols):
                item = QTableWidgetItem("")
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.table.setItem(i, j, item)

        self.table.blockSignals(False)

    def _on_dimension_changed(self):
        """Handle dimension spinbox changes."""
        rows = int(self.rows_value.text())
        cols = int(self.cols_value.text())
        self._setup_table(rows, cols)
        self.matrix_changed.emit(self.get_matrix())

    def _change_rows(self, delta: int):
        """Change row count by delta."""
        current = int(self.rows_value.text())
        new_val = max(1, min(6, current + delta))
        self.rows_value.setText(str(new_val))
        self._setup_table(new_val, int(self.cols_value.text()))
        self.matrix_changed.emit(self.get_matrix())

    def _change_cols(self, delta: int):
        """Change column count by delta."""
        current = int(self.cols_value.text())
        new_val = max(1, min(6, current + delta))
        self.cols_value.setText(str(new_val))
        self._setup_table(int(self.rows_value.text()), new_val)
        self.matrix_changed.emit(self.get_matrix())

    def _clear_matrix(self):
        """Clear all matrix entries to empty."""
        for i in range(self.table.rowCount()):
            for j in range(self.table.columnCount()):
                self.table.item(i, j).setText("")

    def set_label(self, label: str):
        """Set the group box title."""
        self.label_text = label
        self.group.setTitle(label)

    def get_matrix(self) -> Matrix:
        """
        Get the matrix from user input.

        Returns:
            sympy.Matrix: The parsed matrix
        """
        rows = self.table.rowCount()
        cols = self.table.columnCount()

        data = []
        for i in range(rows):
            row = []
            for j in range(cols):
                item = self.table.item(i, j)
                text = item.text().strip() if item else ""
                try:
                    row.append(parse_expression(text))
                except ValueError:
                    row.append(0)  # Default for invalid input
            data.append(row)

        return Matrix(data)

    def set_matrix(self, matrix: Matrix):
        """
        Set the matrix values from a SymPy matrix.

        Args:
            matrix: SymPy Matrix to display
        """
        rows, cols = matrix.shape
        self.rows_spin.setValue(rows)
        self.cols_spin.setValue(cols)

        self.table.blockSignals(True)
        for i in range(rows):
            for j in range(cols):
                item = self.table.item(i, j)
                value = matrix[i, j]
                # Format value for display
                item.setText(str(value))
        self.table.blockSignals(False)

    def set_cell(self, row: int, col: int, value: str):
        """Set a specific cell value."""
        if 0 <= row < self.table.rowCount() and 0 <= col < self.table.columnCount():
            self.table.item(row, col).setText(value)

    def connect_cell_changed(self, slot):
        """Connect cell change signal."""
        self.table.itemChanged.connect(slot)

    def is_valid_input(self) -> bool:
        """
        Check if all cells have valid input.

        Returns:
            bool: True if all non-empty cells have valid expressions
        """
        for i in range(self.table.rowCount()):
            for j in range(self.table.columnCount()):
                item = self.table.item(i, j)
                text = item.text().strip() if item else ""
                if text:
                    try:
                        parse_expression(text)
                    except ValueError:
                        return False
        return True


class DualMatrixInput(QWidget):
    """
    Widget containing two matrix inputs for binary operations.
    """

    def __init__(self, parent=None):
        super().__init__(parent)

        layout = QHBoxLayout(self)

        # First matrix
        self.matrix_a = MatrixInputWidget(label="Matrix A", default_rows=2, default_cols=2)
        layout.addWidget(self.matrix_a)

        # Operator selector (visual only, actual operation selected in main window)
        self.operator_label = QLabel("+")
        self.operator_label.setStyleSheet("""
            color: #333;
            font-size: 24px;
            font-weight: bold;
            padding: 10px;
        """)
        layout.addWidget(self.operator_label)

        # Second matrix
        self.matrix_b = MatrixInputWidget(label="Matrix B", default_rows=2, default_cols=2)
        layout.addWidget(self.matrix_b)

    def set_labels(self, label_a: str, label_b: str):
        """Set labels for both matrices."""
        self.matrix_a.set_label(label_a)
        self.matrix_b.set_label(label_b)

    def set_operator(self, op: str):
        """Set the operator symbol."""
        self.operator_label.setText(op)

    def get_matrices(self):
        """Get both matrices."""
        return self.matrix_a.get_matrix(), self.matrix_b.get_matrix()
