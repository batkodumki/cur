"""
Модуль для роботи з матрицями парних порівнянь
Pairwise Comparison Matrix operations
"""

import numpy as np
from typing import List, Dict


class PairwiseComparisonMatrix:
    """
    Клас для роботи з матрицею парних порівнянь
    """

    def __init__(self, n_alternatives: int, alternatives: List[str] = None):
        """
        Args:
            n_alternatives: кількість альтернатив
            alternatives: список назв альтернатив
        """
        self.n = n_alternatives
        self.matrix = np.ones((n_alternatives, n_alternatives), dtype=float)
        self.alternatives = alternatives or [f"Alt_{i+1}" for i in range(n_alternatives)]
        self.comparisons_made = set()

    def set_comparison(self, i: int, j: int, value: float):
        """
        Встановити порівняння між альтернативами i та j

        Args:
            i: індекс першої альтернативи
            j: індекс другої альтернативи
            value: значення переваги (i над j)
        """
        if i == j:
            self.matrix[i, j] = 1.0
            return

        self.matrix[i, j] = value
        self.matrix[j, i] = 1.0 / value if value != 0 else 0

        self.comparisons_made.add((min(i, j), max(i, j)))

    def get_comparison(self, i: int, j: int) -> float:
        """Отримати значення порівняння"""
        return self.matrix[i, j]

    def is_complete(self) -> bool:
        """Перевірити, чи всі порівняння виконані"""
        required = (self.n * (self.n - 1)) // 2
        return len(self.comparisons_made) >= required

    def get_progress(self) -> Dict:
        """Отримати прогрес заповнення матриці"""
        required = (self.n * (self.n - 1)) // 2
        completed = len(self.comparisons_made)
        return {
            'completed': completed,
            'total': required,
            'percentage': (completed / required * 100) if required > 0 else 100
        }

    def get_matrix(self) -> np.ndarray:
        """Отримати матрицю парних порівнянь"""
        return self.matrix.copy()

    def get_next_comparison(self) -> tuple:
        """
        Отримати наступну пару для порівняння

        Returns:
            (i, j) - індекси альтернатив для порівняння, або None якщо всі порівняння виконані
        """
        for i in range(self.n):
            for j in range(i + 1, self.n):
                if (i, j) not in self.comparisons_made:
                    return (i, j)
        return None

    def reset(self):
        """Скинути всі порівняння"""
        self.matrix = np.ones((self.n, self.n), dtype=float)
        self.comparisons_made = set()

    def to_dict(self) -> Dict:
        """Конвертувати матрицю в словник"""
        return {
            'alternatives': self.alternatives,
            'matrix': self.matrix.tolist(),
            'n_alternatives': self.n,
            'progress': self.get_progress()
        }

    def __str__(self) -> str:
        """Текстове представлення матриці"""
        lines = [f"Pairwise Comparison Matrix ({self.n}x{self.n}):"]
        lines.append("     " + "  ".join(f"{alt:>8s}" for alt in self.alternatives))

        for i, alt in enumerate(self.alternatives):
            row_str = f"{alt:>4s} " + "  ".join(f"{self.matrix[i,j]:>8.2f}" for j in range(self.n))
            lines.append(row_str)

        return "\n".join(lines)
