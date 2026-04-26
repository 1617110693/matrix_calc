# Matrix Symbolic Calculator

一个专业级 Windows 桌面矩阵符号计算器应用程序，使用 Python 3、PyQt6 和 SymPy 开发。

##功能特性

- **动态矩阵维度**: 支持 2x2 到 6x6 矩阵
- **符号精确输入**: 支持分数、平方根、π 等符号
- **基础运算**:
  - 矩阵加法、减法、乘法
  - 转置、逆矩阵、行列式、秩
- **特征分析**:
  - 特征多项式
  - 特征值与特征向量
- **Jordan 分解**: 自动验证 A = PJP⁻¹
- **LaTeX 渲染输出**: 专业数学公式显示

##技术栈

- Python 3
- PyQt6 (GUI)
- SymPy (符号计算)
- NumPy (数值计算)

##安装

```bash
pip install -r requirements.txt
```

##运行

```bash
python matrix_calculator/main.py
```

##打包为 exe

```bash
pyinstaller MatrixCalculator.spec
```

打包后的文件位于 `dist/` 目录。
