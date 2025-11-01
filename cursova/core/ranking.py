"""
Модуль для обчислення вагових коефіцієнтів та ранжування альтернатив
Weight calculation using eigenvector method and geometric mean
"""

import numpy as np
from typing import Dict, List, Tuple
from scipy import linalg


class RankingCalculator:
    """
    Клас для обчислення ваг та рангів альтернатив
    """

    def __init__(self):
        pass

    def calculate_weights_eigenvector(self, matrix: np.ndarray) -> np.ndarray:
        """
        Обчислити ваги методом власного вектора (Saaty)

        Args:
            matrix: матриця парних порівнянь

        Returns:
            вектор нормалізованих ваг
        """
        # Знайти власні значення та вектори
        eigenvalues, eigenvectors = linalg.eig(matrix)

        # Знайти максимальне власне значення
        max_index = np.argmax(eigenvalues.real)

        # Відповідний власний вектор
        principal_eigenvector = np.abs(eigenvectors[:, max_index].real)

        # Нормалізувати
        weights = principal_eigenvector / principal_eigenvector.sum()

        return weights

    def calculate_weights_geometric_mean(self, matrix: np.ndarray) -> np.ndarray:
        """
        Обчислити ваги методом геометричного середнього

        Args:
            matrix: матриця парних порівнянь

        Returns:
            вектор нормалізованих ваг
        """
        n = len(matrix)

        # Обчислити геометричне середнє для кожного рядка
        geo_means = np.zeros(n)
        for i in range(n):
            product = np.prod(matrix[i, :])
            geo_means[i] = product ** (1.0 / n)

        # Нормалізувати
        weights = geo_means / geo_means.sum()

        return weights

    def calculate_weights_normalized_column(self, matrix: np.ndarray) -> np.ndarray:
        """
        Обчислити ваги методом нормалізованих стовпців

        Args:
            matrix: матриця парних порівнянь

        Returns:
            вектор нормалізованих ваг
        """
        n = len(matrix)

        # Нормалізувати кожен стовпець
        normalized_matrix = np.zeros((n, n))
        for j in range(n):
            col_sum = matrix[:, j].sum()
            if col_sum > 0:
                normalized_matrix[:, j] = matrix[:, j] / col_sum

        # Обчислити середнє значення кожного рядка
        weights = normalized_matrix.mean(axis=1)

        return weights

    def calculate_ranks(self, weights: np.ndarray) -> np.ndarray:
        """
        Обчислити ранги на основі ваг

        Args:
            weights: вектор ваг

        Returns:
            вектор рангів (1 = найвищий пріоритет)
        """
        # Сортувати за спаданням та присвоїти ранги
        ranks = np.argsort(-weights) + 1

        # Повернути ранги у вихідному порядку
        result = np.zeros(len(weights), dtype=int)
        for i, rank in enumerate(ranks):
            result[np.where(ranks == i + 1)[0][0]] = rank

        return result

    def get_ranking_results(self, matrix: np.ndarray, alternatives: List[str],
                           method: str = 'eigenvector') -> Dict:
        """
        Отримати повні результати ранжування

        Args:
            matrix: матриця парних порівнянь
            alternatives: список назв альтернатив
            method: метод обчислення ('eigenvector', 'geometric_mean', 'normalized_column')

        Returns:
            словник з результатами
        """
        # Вибрати метод обчислення ваг
        if method == 'eigenvector':
            weights = self.calculate_weights_eigenvector(matrix)
        elif method == 'geometric_mean':
            weights = self.calculate_weights_geometric_mean(matrix)
        elif method == 'normalized_column':
            weights = self.calculate_weights_normalized_column(matrix)
        else:
            raise ValueError(f"Unknown method: {method}")

        # Обчислити ранги
        ranks = self.calculate_ranks(weights)

        # Створити список результатів
        results = []
        for i, alt in enumerate(alternatives):
            results.append({
                'alternative': alt,
                'weight': float(weights[i]),
                'weight_percent': float(weights[i] * 100),
                'rank': int(ranks[i])
            })

        # Сортувати за рангом
        results.sort(key=lambda x: x['rank'])

        return {
            'method': method,
            'alternatives_count': len(alternatives),
            'results': results,
            'weights': weights.tolist(),
            'ranks': ranks.tolist()
        }

    def compare_methods(self, matrix: np.ndarray, alternatives: List[str]) -> Dict:
        """
        Порівняти результати різних методів обчислення ваг

        Args:
            matrix: матриця парних порівнянь
            alternatives: список назв альтернатив

        Returns:
            словник з порівнянням методів
        """
        methods = ['eigenvector', 'geometric_mean', 'normalized_column']
        comparison = {}

        for method in methods:
            comparison[method] = self.get_ranking_results(matrix, alternatives, method)

        return comparison

    def get_priority_vector(self, weights: np.ndarray, normalize: bool = True) -> np.ndarray:
        """
        Отримати вектор пріоритетів

        Args:
            weights: вектор ваг
            normalize: нормалізувати до суми 1

        Returns:
            вектор пріоритетів
        """
        if normalize:
            total = weights.sum()
            return weights / total if total > 0 else weights
        return weights
