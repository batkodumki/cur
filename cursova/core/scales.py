"""
Модуль шкал експертного оцінювання
Implements 6 scale types with transformation to unified cardinal scale (1.5-9.5)
"""

import numpy as np
from typing import Dict, List, Tuple


class ScaleTransformer:
    """
    Клас для роботи з різними шкалами експертного оцінювання
    і їх уніфікації до кардинальної шкали
    """

    # Unified cardinal scale bounds
    MIN_CARDINAL = 1.5
    MAX_CARDINAL = 9.5

    SCALE_NAMES = {
        1: "Ординальна",
        2: "Цілочислова",
        3: "Збалансована",
        4: "Степенева",
        5: "Ма-Чженга",
        6: "Донеган-Додд-МакМастера"
    }

    def __init__(self):
        self.transformation_log = []

    def get_scale_values(self, scale_type: int, gradations: int = 9) -> List[float]:
        """
        Отримати значення для вказаної шкали

        Args:
            scale_type: тип шкали (1-6)
            gradations: кількість градацій (3-9)

        Returns:
            список значень шкали
        """
        if scale_type == 1:  # Ординальна
            return self._ordinal_scale()
        elif scale_type == 2:  # Цілочислова
            return self._integer_scale(gradations)
        elif scale_type == 3:  # Збалансована
            return self._balanced_scale(gradations)
        elif scale_type == 4:  # Степенева
            return self._power_scale(gradations)
        elif scale_type == 5:  # Ма-Чженга
            return self._ma_zheng_scale(gradations)
        elif scale_type == 6:  # Донеган-Додд-МакМастера
            return self._donegan_dodd_scale(gradations)
        else:
            raise ValueError(f"Unknown scale type: {scale_type}")

    def _ordinal_scale(self) -> List[float]:
        """Ординальна шкала: просто менше/більше"""
        return [1.0, 9.0]  # Рівнозначність не враховується

    def _integer_scale(self, n: int = 9) -> List[float]:
        """Цілочислова шкала Сааті: 1, 2, 3, ..., n"""
        return list(range(1, n + 1))

    def _balanced_scale(self, n: int = 9) -> List[float]:
        """
        Збалансована шкала з рівномірним розподілом
        Значення розподілені рівномірно від 1 до 9
        """
        if n == 3:
            return [1.0, 5.0, 9.0]
        elif n == 5:
            return [1.0, 3.0, 5.0, 7.0, 9.0]
        elif n == 7:
            return [1.0, 2.33, 3.67, 5.0, 6.33, 7.67, 9.0]
        else:  # n == 9
            return [1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0]

    def _power_scale(self, n: int = 9) -> List[float]:
        """
        Степенева шкала: значення зростають експоненційно
        Використовує формулу: 2^(i/(n-1)) для i = 0..n-1, потім масштабується до 1-9
        """
        if n < 3:
            n = 3
        powers = [2 ** (i * 3 / (n - 1)) for i in range(n)]
        # Нормалізація до діапазону 1-9
        min_val = powers[0]
        max_val = powers[-1]
        scaled = [(p - min_val) / (max_val - min_val) * 8 + 1 for p in powers]
        return scaled

    def _ma_zheng_scale(self, n: int = 9) -> List[float]:
        """
        Шкала Ма-Чженга: 9/9, 9/8, 9/7, ..., 9/1
        Дробові відношення
        """
        return [9.0 / (10 - i) for i in range(1, min(n, 9) + 1)]

    def _donegan_dodd_scale(self, n: int = 9) -> List[float]:
        """
        Шкала Донеган-Додд-МакМастера
        Логарифмічна шкала з модифікацією
        """
        if n == 3:
            return [1.0, 4.0, 9.0]
        elif n == 5:
            return [1.0, 2.5, 4.5, 6.5, 9.0]
        elif n == 7:
            return [1.0, 2.0, 3.5, 5.0, 6.5, 8.0, 9.0]
        else:  # n == 9
            return [1.0, 1.8, 2.8, 4.0, 5.4, 6.7, 7.8, 8.6, 9.0]

    def to_cardinal(self, value: float, scale_type: int, gradations: int = 9) -> float:
        """
        Перетворення значення зі шкали до уніфікованої кардинальної шкали (1.5-9.5)

        Args:
            value: значення у вихідній шкалі
            scale_type: тип шкали (1-6)
            gradations: кількість градацій

        Returns:
            значення в кардинальній шкалі
        """
        scale_values = self.get_scale_values(scale_type, gradations)

        # Для ординальної шкали
        if scale_type == 1:
            cardinal = self.MAX_CARDINAL if value > 1.0 else self.MIN_CARDINAL
        else:
            # Знайти найближче значення у шкалі
            idx = min(range(len(scale_values)),
                     key=lambda i: abs(scale_values[i] - value))

            # Лінійна інтерполяція до кардинальної шкали
            min_scale = min(scale_values)
            max_scale = max(scale_values)

            if max_scale > min_scale:
                normalized = (value - min_scale) / (max_scale - min_scale)
                cardinal = self.MIN_CARDINAL + normalized * (self.MAX_CARDINAL - self.MIN_CARDINAL)
            else:
                cardinal = (self.MIN_CARDINAL + self.MAX_CARDINAL) / 2

        # Логування трансформації
        self.transformation_log.append({
            'original_value': value,
            'scale_type': self.SCALE_NAMES[scale_type],
            'gradations': gradations,
            'cardinal_value': cardinal
        })

        return cardinal

    def get_scale_labels(self, scale_type: int, gradations: int = 9) -> List[str]:
        """
        Отримати текстові мітки для шкали

        Returns:
            список міток
        """
        if scale_type == 1:  # Ординальна
            return ["Менше", "Більше"]

        values = self.get_scale_values(scale_type, gradations)
        base_labels = [
            "Абсолютно",
            "Дуже, дуже сильно",
            "Дуже сильно",
            "Сильно",
            "Досить сильно",
            "Слабко або незначно",
            "Дуже слабко",
            "Більше",
            "Менше"
        ]

        # Для різних кількостей градацій вибрати відповідні мітки
        if gradations <= len(base_labels):
            step = len(base_labels) // gradations
            return [base_labels[i * step] for i in range(gradations)]
        else:
            return [f"Ступінь {i+1}" for i in range(gradations)]

    def get_transformation_log(self) -> List[Dict]:
        """Отримати лог всіх трансформацій"""
        return self.transformation_log

    def clear_log(self):
        """Очистити лог трансформацій"""
        self.transformation_log = []
