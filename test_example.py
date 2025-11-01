#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Приклад використання без GUI
Демонстрація роботи всіх компонентів системи
"""

import sys
import numpy as np

sys.path.insert(0, '/home/user/cur')

from cursova.core.scales import ScaleTransformer
from cursova.core.pcm import PairwiseComparisonMatrix
from cursova.core.consistency import ConsistencyChecker
from cursova.core.ranking import RankingCalculator


def print_header(text):
    """Красиво надрукувати заголовок"""
    print("\n" + "=" * 70)
    print(f"  {text}")
    print("=" * 70)


def test_scales():
    """Тест всіх типів шкал"""
    print_header("ТЕСТ ШКАЛ ЕКСПЕРТНОГО ОЦІНЮВАННЯ")

    st = ScaleTransformer()

    print("\nДоступні шкали:")
    for scale_id, name in st.SCALE_NAMES.items():
        print(f"  {scale_id}. {name}")

    print("\n" + "-" * 70)
    print("Приклади значень для різних шкал:")
    print("-" * 70)

    # Ординальна
    values = st.get_scale_values(1)
    print(f"\n1. Ординальна: {values}")

    # Цілочислова
    values = st.get_scale_values(2, 9)
    print(f"2. Цілочислова (9): {values}")

    # Збалансована
    for n in [3, 5, 9]:
        values = st.get_scale_values(3, n)
        print(f"3. Збалансована ({n}): {values}")

    # Степенева
    values = st.get_scale_values(4, 5)
    print(f"4. Степенева (5): {[f'{v:.2f}' for v in values]}")

    # Ма-Чженга
    values = st.get_scale_values(5, 9)
    print(f"5. Ма-Чженга (9): {[f'{v:.2f}' for v in values]}")

    # Донеган-Додд-МакМастера
    values = st.get_scale_values(6, 9)
    print(f"6. Донеган-Додд-МакМастера (9): {[f'{v:.2f}' for v in values]}")


def test_pairwise_comparison():
    """Тест повного циклу парних порівнянь"""
    print_header("ПРИКЛАД ЕКСПЕРТНОГО ОЦІНЮВАННЯ")

    # Альтернативи
    alternatives = [
        "Проект А (Інноваційний)",
        "Проект Б (Стабільний)",
        "Проект В (Ризиковий)"
    ]

    print("\nАльтернативи для оцінювання:")
    for i, alt in enumerate(alternatives, 1):
        print(f"  {i}. {alt}")

    # Створити матрицю
    pcm = PairwiseComparisonMatrix(len(alternatives), alternatives)
    st = ScaleTransformer()

    print("\n" + "-" * 70)
    print("Експертні порівняння:")
    print("-" * 70)

    # Експерт робить порівняння в різних шкалах
    comparisons = [
        (0, 1, 5.0, 2, 9, "Проект А сильно переважає Проект Б"),
        (0, 2, 7.0, 3, 5, "Проект А дуже сильно переважає Проект В"),
        (1, 2, 3.0, 2, 9, "Проект Б досить переважає Проект В"),
    ]

    for i, j, value, scale_type, gradations, description in comparisons:
        cardinal = st.to_cardinal(value, scale_type, gradations)
        pcm.set_comparison(i, j, cardinal)

        scale_name = st.SCALE_NAMES[scale_type]
        print(f"\n  {alternatives[i]} vs {alternatives[j]}")
        print(f"    Шкала: {scale_name} (градацій: {gradations})")
        print(f"    Оцінка: {value:.1f} → Кардинальна: {cardinal:.2f}")
        print(f"    Опис: {description}")

    # Отримати матрицю
    matrix = pcm.get_matrix()

    print("\n" + "-" * 70)
    print("Матриця парних порівнянь:")
    print("-" * 70)
    print(pcm)

    # Обчислити ваги
    print("\n" + "-" * 70)
    print("ОБЧИСЛЕННЯ ВАГ ТА РАНГІВ")
    print("-" * 70)

    rc = RankingCalculator()

    # Порівняти різні методи
    methods = {
        'eigenvector': 'Метод власного вектора (Saaty)',
        'geometric_mean': 'Геометричне середнє',
        'normalized_column': 'Нормалізовані стовпці'
    }

    for method, method_name in methods.items():
        results = rc.get_ranking_results(matrix, alternatives, method=method)

        print(f"\n{method_name}:")
        for res in results['results']:
            print(f"  Ранг {res['rank']}: {res['alternative']}")
            print(f"    Вага: {res['weight']:.4f} ({res['weight_percent']:.2f}%)")

    # Перевірка узгодженості
    print("\n" + "-" * 70)
    print("ПЕРЕВІРКА УЗГОДЖЕНОСТІ")
    print("-" * 70)

    cc = ConsistencyChecker()
    metrics = cc.get_consistency_metrics(matrix)

    print(f"\nМаксимальне власне значення (λ_max): {metrics['lambda_max']:.4f}")
    print(f"Індекс узгодженості (CI):            {metrics['ci']:.4f}")
    print(f"Випадковий індекс (RI):               {metrics['ri']:.2f}")
    print(f"Коефіцієнт узгодженості (CR):        {metrics['cr']:.4f}")
    print(f"Поріг CR:                             {metrics['cr_threshold']:.2f}")
    print(f"\nРезультат: {'✓ УЗГОДЖЕНА' if metrics['is_consistent'] else '✗ НЕУЗГОДЖЕНА'}")

    if not metrics['is_consistent']:
        print(f"\nУвага! CR = {metrics['cr']:.4f} > {metrics['cr_threshold']}")
        print("Рекомендується переглянути деякі порівняння.")

        # Показати рекомендації
        suggestions = cc.get_suggestions(matrix)

        print("\n" + "-" * 70)
        print("РЕКОМЕНДАЦІЇ ДЛЯ ПОКРАЩЕННЯ УЗГОДЖЕНОСТІ")
        print("-" * 70)

        for idx, sug in enumerate(suggestions[:3], 1):
            i, j = sug['pair']
            print(f"\n{idx}. {alternatives[i]} vs {alternatives[j]}")
            print(f"   Поточне значення:     {sug['current_value']:.2f}")
            print(f"   Рекомендоване:        {sug['suggested_value']:.2f}")
            print(f"   Відхилення:           {sug['deviation_percent']:.1f}%")

    # Лог трансформацій
    print("\n" + "-" * 70)
    print("ЛОГ ТРАНСФОРМАЦІЙ ШКАЛ")
    print("-" * 70)

    for log_entry in st.get_transformation_log():
        print(f"\nШкала: {log_entry['scale_type']} ({log_entry['gradations']} градацій)")
        print(f"  {log_entry['original_value']:.2f} → {log_entry['cardinal_value']:.2f}")

    print("\n" + "=" * 70)
    print("  ЗАВЕРШЕНО")
    print("=" * 70 + "\n")


def main():
    """Головна функція"""
    print("\n")
    print("╔" + "=" * 68 + "╗")
    print("║" + " " * 68 + "║")
    print("║" + "  СИСТЕМА ЕКСПЕРТНИХ ПОПАРНИХ ПОРІВНЯНЬ".center(68) + "║")
    print("║" + "  з уточненням ступеня переваги".center(68) + "║")
    print("║" + " " * 68 + "║")
    print("╚" + "=" * 68 + "╝")

    try:
        # Тест 1: Шкали
        test_scales()

        # Тест 2: Повний цикл
        test_pairwise_comparison()

        print("\n✓ Всі тести виконані успішно!\n")
        print("Для запуску GUI версії використайте:")
        print("  cd /home/user/cur/cursova")
        print("  python -m gui.app\n")

    except Exception as e:
        print(f"\n✗ Помилка: {e}\n")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()
