"""
Internationalization support for Matrix Calculator.
"""

from PyQt6.QtCore import QObject, pyqtSignal


class I18n(QObject):
    """Internationalization manager with signal for language changes."""

    language_changed = pyqtSignal()

    def __init__(self):
        super().__init__()
        self._lang = "zh"  # Default to Chinese

        self._translations = {
            "en": {
                # Window
                "app_title": "Matrix Symbolic Calculator",

                # Input panel
                "title": "Matrix Calculator",
                "operation_mode": "Operation Mode:",
                "mode_single": "Single Matrix Operations",
                "mode_dual": "Binary Operations (A + B, A * B, etc.)",
                "mode_jordan": "Jordan Decomposition",
                "matrix_a": "Matrix A",
                "matrix_b": "Matrix B",
                "matrix_a_jordan": "Matrix A (for Jordan)",
                "operations": "Operations",

                # Matrix input
                "rows": "Rows:",
                "cols": "Cols:",

                # Buttons
                "btn_transpose": "A^T",
                "btn_det": "det(A)",
                "btn_rank": "rank(A)",
                "btn_trace": "tr(A)",
                "btn_inverse": "A^-1",
                "btn_char_poly": "p(λ)",
                "btn_eigenvalues": "Eigenvalues",
                "btn_eigenvectors": "Eigenvectors",
                "btn_jordan": "Jordan Decomposition",
                "btn_clear": "Clear",

                # Result panel
                "result": "Result",
                "result_will_appear": "Result will appear here",

                # Status
                "calculating": "Calculating...",
                "verification_ok": "Verification: A = PJP⁻¹  ✓",
                "verification_fail": "Verification: FAILED ✗",

                # Error messages
                "error_square": "Jordan decomposition requires a square matrix.",
                "error_calc": "Calculation Error",

                # Labels for results
                "label_det": "det(A)",
                "label_rank": "rank(A)",
                "label_trace": "tr(A)",
                "label_transpose": "A^T",
                "label_inverse": "A^{-1}",
                "label_char_poly": "p(λ)",
                "label_eigenvalues": "Eigenvalues",
                "label_eigenvectors": "Eigenvectors",
                "label_jordan": "Jordan Decomposition",
            },
            "zh": {
                # Window
                "app_title": "矩阵符号计算器",

                # Input panel
                "title": "矩阵计算器",
                "operation_mode": "运算模式：",
                "mode_single": "单个矩阵运算",
                "mode_dual": "二元运算 (A + B, A × B 等)",
                "mode_jordan": "Jordan 分解",
                "matrix_a": "矩阵 A",
                "matrix_b": "矩阵 B",
                "matrix_a_jordan": "矩阵 A (Jordan 分解)",
                "operations": "运算",

                # Matrix input
                "rows": "行数：",
                "cols": "列数：",

                # Buttons
                "btn_transpose": "A^T",
                "btn_det": "det(A)",
                "btn_rank": "rank(A)",
                "btn_trace": "tr(A)",
                "btn_inverse": "A^-1",
                "btn_char_poly": "p(λ)",
                "btn_eigenvalues": "特征值",
                "btn_eigenvectors": "特征向量",
                "btn_jordan": "Jordan 分解",
                "btn_clear": "清空",

                # Result panel
                "result": "结果",
                "result_will_appear": "结果将显示在此处",

                # Status
                "calculating": "计算中...",
                "verification_ok": "验证：A = PJP⁻¹  ✓",
                "verification_fail": "验证：失败 ✗",

                # Error messages
                "error_square": "Jordan 分解需要方阵。",
                "error_calc": "计算错误",

                # Labels for results
                "label_det": "det(A)",
                "label_rank": "rank(A)",
                "label_trace": "tr(A)",
                "label_transpose": "A^T",
                "label_inverse": "A^{-1}",
                "label_char_poly": "p(λ)",
                "label_eigenvalues": "特征值",
                "label_eigenvectors": "特征向量",
                "label_jordan": "Jordan 分解",
            }
        }

    @property
    def lang(self):
        return self._lang

    def set_lang(self, lang: str):
        """Set language: 'en' or 'zh'"""
        if lang in self._translations:
            self._lang = lang
            self.language_changed.emit()

    def t(self, key: str) -> str:
        """Translate a key."""
        return self._translations[self._lang].get(key, key)


# Global instance
i18n = I18n()