"""
Модуль для перевірки узгодженості матриці парних порівнянь
Consistency checking: λ_max, CI (Consistency Index), CR (Consistency Ratio)
"""

import numpy as np
from typing import Dict, List


class ConsistencyChecker:
    """
    Клас для перевірки узгодженості матриці парних порівнянь
    """

    # Random Consistency Index (RI) для різних розмірів матриць (Saaty)
    RI_VALUES = {
        1: 0.00,
        2: 0.00,
        3: 0.58,
        4: 0.90,
        5: 1.12,
        6: 1.24,
        7: 1.32,
        8: 1.41,
        9: 1.45,
        10: 1.49,
        11: 1.51,
        12: 1.48,
        13: 1.56,
        14: 1.57,
        15: 1.59
    }

    # Порогове значення CR для прийнятної узгодженості
    CR_THRESHOLD = 0.10  # 10%

    def __init__(self):
        pass

    def calculate_lambda_max(self, matrix: np.ndarray, weights: np.ndarray) -> float:
        """
        Обчислити максимальне власне значення λ_max

        Args:
            matrix: матриця парних порівнянь
            weights: вектор ваг (власний вектор)

        Returns:
            λ_max
        """
        n = len(matrix)
        # Обчислити Aw
        aw = np.dot(matrix, weights)

        # λ_max = середнє значення (Aw)_i / w_i
        lambda_max = np.mean(aw / weights)

        return lambda_max

    def calculate_ci(self, matrix: np.ndarray, weights: np.ndarray = None) -> float:
        """
        Обчислити індекс узгодженості CI (Consistency Index)

        CI = (λ_max - n) / (n - 1)

        Args:
            matrix: матриця парних порівнянь
            weights: вектор ваг (якщо None, обчислюється автоматично)

        Returns:
            CI
        """
        n = len(matrix)

        if n <= 1:
            return 0.0

        if weights is None:
            # Обчислити власний вектор
            eigenvalues, eigenvectors = np.linalg.eig(matrix)
            max_index = np.argmax(eigenvalues.real)
            lambda_max = eigenvalues[max_index].real
        else:
            lambda_max = self.calculate_lambda_max(matrix, weights)

        ci = (lambda_max - n) / (n - 1)

        return ci

    def calculate_cr(self, matrix: np.ndarray, weights: np.ndarray = None) -> float:
        """
        Обчислити коефіцієнт узгодженості CR (Consistency Ratio)

        CR = CI / RI

        Args:
            matrix: матриця парних порівнянь
            weights: вектор ваг

        Returns:
            CR
        """
        n = len(matrix)

        if n <= 2:
            return 0.0

        ci = self.calculate_ci(matrix, weights)
        ri = self.RI_VALUES.get(n, 1.5)

        cr = ci / ri if ri > 0 else 0.0

        return cr

    def is_consistent(self, matrix: np.ndarray, weights: np.ndarray = None,
                     threshold: float = None) -> bool:
        """
        Перевірити, чи матриця узгоджена

        Args:
            matrix: матриця парних порівнянь
            weights: вектор ваг
            threshold: порогове значення CR (за замовчуванням 0.10)

        Returns:
            True якщо CR <= threshold
        """
        if threshold is None:
            threshold = self.CR_THRESHOLD

        cr = self.calculate_cr(matrix, weights)
        return cr <= threshold

    def get_consistency_metrics(self, matrix: np.ndarray,
                                weights: np.ndarray = None) -> Dict:
        """
        Отримати всі метрики узгодженості

        Returns:
            словник з λ_max, CI, CR, RI, is_consistent
        """
        n = len(matrix)

        if weights is None:
            # Обчислити власний вектор
            eigenvalues, eigenvectors = np.linalg.eig(matrix)
            max_index = np.argmax(eigenvalues.real)
            lambda_max = eigenvalues[max_index].real
            weights = np.abs(eigenvectors[:, max_index].real)
            weights = weights / weights.sum()
        else:
            lambda_max = self.calculate_lambda_max(matrix, weights)

        ci = self.calculate_ci(matrix, weights)
        cr = self.calculate_cr(matrix, weights)
        ri = self.RI_VALUES.get(n, 1.5)
        is_consistent = cr <= self.CR_THRESHOLD

        return {
            'lambda_max': float(lambda_max),
            'n': n,
            'ci': float(ci),
            'ri': float(ri),
            'cr': float(cr),
            'cr_threshold': self.CR_THRESHOLD,
            'is_consistent': is_consistent
        }

    def get_suggestions(self, matrix: np.ndarray, weights: np.ndarray = None) -> List[Dict]:
        """
        Отримати рекомендації для покращення узгодженості

        Args:
            matrix: матриця парних порівнянь
            weights: вектор ваг

        Returns:
            список рекомендацій
        """
        n = len(matrix)
        suggestions = []

        if weights is None:
            eigenvalues, eigenvectors = np.linalg.eig(matrix)
            max_index = np.argmax(eigenvalues.real)
            weights = np.abs(eigenvectors[:, max_index].real)
            weights = weights / weights.sum()

        # Знайти порівняння з найбільшими відхиленнями
        deviations = []
        for i in range(n):
            for j in range(i + 1, n):
                # Очікуване значення на основі ваг
                expected = weights[i] / weights[j] if weights[j] > 0 else 1.0
                actual = matrix[i, j]

                # Відхилення
                deviation = abs(actual - expected) / expected if expected > 0 else 0

                deviations.append({
                    'i': i,
                    'j': j,
                    'actual': actual,
                    'expected': expected,
                    'deviation': deviation
                })

        # Сортувати за відхиленням
        deviations.sort(key=lambda x: x['deviation'], reverse=True)

        # Взяти топ-5 найбільших відхилень
        for dev in deviations[:5]:
            suggestions.append({
                'pair': (dev['i'], dev['j']),
                'current_value': dev['actual'],
                'suggested_value': dev['expected'],
                'deviation_percent': dev['deviation'] * 100,
                'message': f"Розгляньте перегляд порівняння {dev['i']+1} vs {dev['j']+1}"
            })

        return suggestions
