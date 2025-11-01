"""
Головний модуль GUI застосунку
Main application window with three panels
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import json
import csv
import numpy as np
from pathlib import Path

from ..core.scales import ScaleTransformer
from ..core.pcm import PairwiseComparisonMatrix
from ..core.consistency import ConsistencyChecker
from ..core.ranking import RankingCalculator


class ExpertComparisonApp:
    """
    Головне вікно застосунку для методу експертних попарних порівнянь
    """

    def __init__(self, root):
        self.root = root
        self.root.title("Метод експертних попарних порівнянь з уточненням ступеня переваги")
        self.root.geometry("1000x700")

        # Initialize core components
        self.scale_transformer = ScaleTransformer()
        self.consistency_checker = ConsistencyChecker()
        self.ranking_calculator = RankingCalculator()

        # Application state
        self.alternatives = []
        self.pcm = None
        self.current_pair = None
        self.current_scale = 2  # За замовчуванням Цілочислова
        self.current_gradations = 9
        self.results = None

        # Create UI
        self.create_widgets()

    def create_widgets(self):
        """Створити всі віджети інтерфейсу"""

        # Main container with three panels
        main_container = ttk.PanedWindow(self.root, orient=tk.HORIZONTAL)
        main_container.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Panel 1: Введення альтернатив
        panel1 = ttk.LabelFrame(main_container, text="1. Введення альтернатив", padding=10)
        main_container.add(panel1, weight=1)
        self.create_panel1(panel1)

        # Panel 2: Парні порівняння
        panel2 = ttk.LabelFrame(main_container, text="2. Парні порівняння", padding=10)
        main_container.add(panel2, weight=2)
        self.create_panel2(panel2)

        # Panel 3: Результати
        panel3 = ttk.LabelFrame(main_container, text="3. Результати", padding=10)
        main_container.add(panel3, weight=1)
        self.create_panel3(panel3)

    def create_panel1(self, parent):
        """Панель введення альтернатив"""

        # Текстове поле для введення альтернатив
        ttk.Label(parent, text="Введіть альтернативи (по одній на рядок):").pack(anchor=tk.W)

        self.alternatives_text = tk.Text(parent, height=15, width=30)
        self.alternatives_text.pack(fill=tk.BOTH, expand=True, pady=5)

        # Кнопки
        btn_frame = ttk.Frame(parent)
        btn_frame.pack(fill=tk.X, pady=5)

        ttk.Button(btn_frame, text="Завантажити з файлу",
                  command=self.load_alternatives_from_file).pack(side=tk.LEFT, padx=2)

        ttk.Button(btn_frame, text="Почати порівняння",
                  command=self.start_comparison).pack(side=tk.RIGHT, padx=2)

        # Приклад
        example_text = "Приклад:\nАльтернатива 1\nАльтернатива 2\nАльтернатива 3"
        self.alternatives_text.insert("1.0", example_text)

    def create_panel2(self, parent):
        """Панель парних порівнянь"""

        # Вибір типу шкали
        scale_frame = ttk.LabelFrame(parent, text="Вибір типу шкали", padding=10)
        scale_frame.pack(fill=tk.X, pady=5)

        self.scale_var = tk.IntVar(value=2)

        scales = [
            (1, "Ординальна"),
            (2, "Цілочислова"),
            (3, "Збалансована"),
            (4, "Степенева"),
            (5, "Ма-Чженга (9/9-9/1)"),
            (6, "Донеган-Додд-МакМастера")
        ]

        for value, text in scales:
            ttk.Radiobutton(scale_frame, text=text, variable=self.scale_var,
                           value=value, command=self.on_scale_changed).pack(anchor=tk.W)

        # Вибір кількості градацій
        grad_frame = ttk.Frame(scale_frame)
        grad_frame.pack(fill=tk.X, pady=5)

        ttk.Label(grad_frame, text="Кількість градацій:").pack(side=tk.LEFT)
        self.gradations_var = tk.IntVar(value=9)
        gradations_combo = ttk.Combobox(grad_frame, textvariable=self.gradations_var,
                                       values=[3, 5, 7, 9], width=5, state='readonly')
        gradations_combo.pack(side=tk.LEFT, padx=5)
        gradations_combo.bind('<<ComboboxSelected>>', lambda e: self.on_scale_changed())

        # Відображення поточного порівняння
        comparison_frame = ttk.LabelFrame(parent, text="Поточне порівняння", padding=10)
        comparison_frame.pack(fill=tk.BOTH, expand=True, pady=5)

        self.comparison_label = ttk.Label(comparison_frame,
                                         text="Оберіть альтернативи та почніть порівняння",
                                         font=('Arial', 12, 'bold'))
        self.comparison_label.pack(pady=10)

        # Шкала для вибору переваги
        self.preference_frame = ttk.Frame(comparison_frame)
        self.preference_frame.pack(fill=tk.BOTH, expand=True, pady=10)

        self.preference_var = tk.DoubleVar(value=5.0)
        self.preference_scale = None
        self.preference_labels_frame = None

        # Прогрес бар
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(comparison_frame, variable=self.progress_var,
                                           maximum=100)
        self.progress_bar.pack(fill=tk.X, pady=5)

        self.progress_label = ttk.Label(comparison_frame, text="0 / 0 порівнянь виконано")
        self.progress_label.pack()

        # Кнопка підтвердження
        ttk.Button(comparison_frame, text="Підтвердити",
                  command=self.confirm_comparison).pack(pady=10)

    def create_panel3(self, parent):
        """Панель результатів"""

        # Таблиця результатів
        table_frame = ttk.Frame(parent)
        table_frame.pack(fill=tk.BOTH, expand=True, pady=5)

        # Створити Treeview для результатів
        columns = ('Ранг', 'Альтернатива', 'Вага', 'Вага %')
        self.results_tree = ttk.Treeview(table_frame, columns=columns, show='headings', height=10)

        for col in columns:
            self.results_tree.heading(col, text=col)
            self.results_tree.column(col, width=100)

        self.results_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Scrollbar
        scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.results_tree.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.results_tree.configure(yscrollcommand=scrollbar.set)

        # Метрики узгодженості
        metrics_frame = ttk.LabelFrame(parent, text="Метрики узгодженості", padding=10)
        metrics_frame.pack(fill=tk.X, pady=5)

        self.metrics_text = tk.Text(metrics_frame, height=6, width=30)
        self.metrics_text.pack(fill=tk.BOTH, expand=True)

        # Кнопки експорту
        export_frame = ttk.Frame(parent)
        export_frame.pack(fill=tk.X, pady=5)

        ttk.Button(export_frame, text="Експорт CSV",
                  command=self.export_csv).pack(side=tk.LEFT, padx=2)

        ttk.Button(export_frame, text="Експорт JSON",
                  command=self.export_json).pack(side=tk.LEFT, padx=2)

    def load_alternatives_from_file(self):
        """Завантажити альтернативи з файлу"""
        filename = filedialog.askopenfilename(
            title="Виберіть файл",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )

        if filename:
            try:
                with open(filename, 'r', encoding='utf-8') as f:
                    content = f.read()
                    self.alternatives_text.delete("1.0", tk.END)
                    self.alternatives_text.insert("1.0", content)
            except Exception as e:
                messagebox.showerror("Помилка", f"Не вдалося завантажити файл: {e}")

    def start_comparison(self):
        """Почати процес порівняння"""
        # Отримати альтернативи з текстового поля
        text = self.alternatives_text.get("1.0", tk.END)
        self.alternatives = [line.strip() for line in text.split('\n') if line.strip()]

        if len(self.alternatives) < 2:
            messagebox.showwarning("Попередження",
                                  "Потрібно ввести принаймні 2 альтернативи")
            return

        # Створити матрицю парних порівнянь
        self.pcm = PairwiseComparisonMatrix(len(self.alternatives), self.alternatives)

        # Отримати першу пару для порівняння
        self.current_pair = self.pcm.get_next_comparison()

        if self.current_pair:
            self.update_comparison_display()
            self.update_progress()
        else:
            messagebox.showinfo("Інформація", "Порівняння вже завершені")

    def on_scale_changed(self):
        """Обробник зміни типу шкали"""
        self.current_scale = self.scale_var.get()
        self.current_gradations = self.gradations_var.get()

        # Оновити відображення шкали
        if self.current_pair:
            self.update_comparison_display()

    def update_comparison_display(self):
        """Оновити відображення поточного порівняння"""
        if not self.current_pair:
            return

        i, j = self.current_pair
        alt1 = self.alternatives[i]
        alt2 = self.alternatives[j]

        self.comparison_label.config(
            text=f"Порівняйте: {alt1} vs {alt2}"
        )

        # Очистити попередні віджети
        for widget in self.preference_frame.winfo_children():
            widget.destroy()

        # Отримати значення шкали
        scale_values = self.scale_transformer.get_scale_values(
            self.current_scale, self.current_gradations
        )

        # Для ординальної шкали - спрощений інтерфейс
        if self.current_scale == 1:
            self.create_ordinal_comparison(alt1, alt2)
        else:
            self.create_cardinal_comparison(alt1, alt2, scale_values)

    def create_ordinal_comparison(self, alt1, alt2):
        """Створити інтерфейс для ординального порівняння"""
        frame = ttk.Frame(self.preference_frame)
        frame.pack(expand=True)

        ttk.Label(frame, text=f"{alt1}", font=('Arial', 10)).pack(side=tk.LEFT, padx=20)

        self.ordinal_var = tk.StringVar(value="=")

        ttk.Radiobutton(frame, text="Менше", variable=self.ordinal_var,
                       value="<").pack(side=tk.LEFT, padx=10)
        ttk.Radiobutton(frame, text="Більше", variable=self.ordinal_var,
                       value=">").pack(side=tk.LEFT, padx=10)

        ttk.Label(frame, text=f"{alt2}", font=('Arial', 10)).pack(side=tk.LEFT, padx=20)

    def create_cardinal_comparison(self, alt1, alt2, scale_values):
        """Створити інтерфейс для кардинального порівняння"""
        # Мітки шкали
        labels = self.scale_transformer.get_scale_labels(
            self.current_scale, self.current_gradations
        )

        # Рамка з мітками альтернатив
        alt_frame = ttk.Frame(self.preference_frame)
        alt_frame.pack(fill=tk.X, pady=10)

        ttk.Label(alt_frame, text=f"Фактор 1: {alt1}",
                 foreground='red', font=('Arial', 10, 'bold')).pack(side=tk.LEFT, padx=10)
        ttk.Label(alt_frame, text=f"Фактор 2: {alt2}",
                 foreground='blue', font=('Arial', 10, 'bold')).pack(side=tk.RIGHT, padx=10)

        # Слайдер для вибору значення
        slider_frame = ttk.Frame(self.preference_frame)
        slider_frame.pack(fill=tk.X, pady=10)

        min_val = min(scale_values)
        max_val = max(scale_values)
        mid_val = (min_val + max_val) / 2

        self.preference_var.set(mid_val)

        self.preference_scale = tk.Scale(slider_frame, from_=min_val, to=max_val,
                                        orient=tk.HORIZONTAL,
                                        variable=self.preference_var,
                                        resolution=0.1,
                                        length=400)
        self.preference_scale.pack(pady=5)

        # Мітки значень
        value_label = ttk.Label(slider_frame,
                               text=f"Значення: {self.preference_var.get():.1f}",
                               font=('Arial', 10))
        value_label.pack()

        def update_value_label(*args):
            value_label.config(text=f"Значення: {self.preference_var.get():.1f}")

        self.preference_var.trace('w', update_value_label)

    def confirm_comparison(self):
        """Підтвердити поточне порівняння"""
        if not self.current_pair or not self.pcm:
            messagebox.showwarning("Попередження",
                                  "Спочатку почніть процес порівняння")
            return

        i, j = self.current_pair

        # Отримати значення
        if self.current_scale == 1:  # Ординальна
            ordinal = self.ordinal_var.get()
            if ordinal == ">":
                value = 9.0
            elif ordinal == "<":
                value = 1.0 / 9.0
            else:
                value = 1.0
        else:
            value = self.preference_var.get()

        # Перетворити до кардинальної шкали
        cardinal_value = self.scale_transformer.to_cardinal(
            value, self.current_scale, self.current_gradations
        )

        # Зберегти порівняння
        self.pcm.set_comparison(i, j, cardinal_value)

        # Отримати наступну пару
        self.current_pair = self.pcm.get_next_comparison()

        if self.current_pair:
            self.update_comparison_display()
            self.update_progress()
        else:
            # Всі порівняння завершені
            self.calculate_results()

    def update_progress(self):
        """Оновити прогрес бар"""
        if not self.pcm:
            return

        progress = self.pcm.get_progress()
        self.progress_var.set(progress['percentage'])
        self.progress_label.config(
            text=f"{progress['completed']} / {progress['total']} порівнянь виконано"
        )

    def calculate_results(self):
        """Обчислити результати"""
        if not self.pcm:
            return

        matrix = self.pcm.get_matrix()

        # Обчислити ваги
        ranking_results = self.ranking_calculator.get_ranking_results(
            matrix, self.alternatives, method='eigenvector'
        )

        # Обчислити метрики узгодженості
        weights = np.array(ranking_results['weights'])
        consistency_metrics = self.consistency_checker.get_consistency_metrics(
            matrix, weights
        )

        self.results = {
            'ranking': ranking_results,
            'consistency': consistency_metrics
        }

        # Відобразити результати
        self.display_results()

        # Перевірити узгодженість
        if not consistency_metrics['is_consistent']:
            self.show_consistency_warning()

    def display_results(self):
        """Відобразити результати у таблиці"""
        # Очистити таблицю
        for item in self.results_tree.get_children():
            self.results_tree.delete(item)

        # Додати результати
        for res in self.results['ranking']['results']:
            self.results_tree.insert('', tk.END, values=(
                res['rank'],
                res['alternative'],
                f"{res['weight']:.4f}",
                f"{res['weight_percent']:.2f}%"
            ))

        # Відобразити метрики
        metrics = self.results['consistency']
        metrics_text = f"""
λ_max: {metrics['lambda_max']:.4f}
CI (Індекс узгодженості): {metrics['ci']:.4f}
RI (Випадковий індекс): {metrics['ri']:.2f}
CR (Коефіцієнт узгодженості): {metrics['cr']:.4f}

Поріг CR: {metrics['cr_threshold']:.2f}
Узгоджена: {'Так' if metrics['is_consistent'] else 'Ні'}
        """
        self.metrics_text.delete("1.0", tk.END)
        self.metrics_text.insert("1.0", metrics_text)

    def show_consistency_warning(self):
        """Показати попередження про неузгодженість"""
        cr = self.results['consistency']['cr']

        msg = f"Коефіцієнт узгодженості CR = {cr:.4f} перевищує поріг {self.consistency_checker.CR_THRESHOLD}.\n\n"
        msg += "Рекомендується переглянути деякі порівняння для покращення узгодженості."

        response = messagebox.askquestion(
            "Попередження про узгодженість",
            msg + "\n\nПоказати рекомендації?",
            icon='warning'
        )

        if response == 'yes':
            self.show_suggestions()

    def show_suggestions(self):
        """Показати рекомендації для покращення узгодженості"""
        matrix = self.pcm.get_matrix()
        weights = np.array(self.results['ranking']['weights'])

        suggestions = self.consistency_checker.get_suggestions(matrix, weights)

        msg = "Рекомендації для покращення узгодженості:\n\n"
        for i, sug in enumerate(suggestions[:3], 1):
            pair = sug['pair']
            alt1 = self.alternatives[pair[0]]
            alt2 = self.alternatives[pair[1]]

            msg += f"{i}. {alt1} vs {alt2}\n"
            msg += f"   Поточне значення: {sug['current_value']:.2f}\n"
            msg += f"   Рекомендоване: {sug['suggested_value']:.2f}\n"
            msg += f"   Відхилення: {sug['deviation_percent']:.1f}%\n\n"

        messagebox.showinfo("Рекомендації", msg)

    def export_csv(self):
        """Експортувати результати у CSV"""
        if not self.results:
            messagebox.showwarning("Попередження",
                                  "Немає результатів для експорту")
            return

        filename = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )

        if filename:
            try:
                with open(filename, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.writer(f)
                    writer.writerow(['Ранг', 'Альтернатива', 'Вага', 'Вага %'])

                    for res in self.results['ranking']['results']:
                        writer.writerow([
                            res['rank'],
                            res['alternative'],
                            res['weight'],
                            res['weight_percent']
                        ])

                messagebox.showinfo("Успіх", f"Результати експортовано до {filename}")
            except Exception as e:
                messagebox.showerror("Помилка", f"Не вдалося експортувати: {e}")

    def export_json(self):
        """Експортувати результати у JSON"""
        if not self.results:
            messagebox.showwarning("Попередження",
                                  "Немає результатів для експорту")
            return

        filename = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )

        if filename:
            try:
                export_data = {
                    'ranking': self.results['ranking'],
                    'consistency': self.results['consistency'],
                    'scale_transformations': self.scale_transformer.get_transformation_log()
                }

                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump(export_data, f, ensure_ascii=False, indent=2)

                messagebox.showinfo("Успіх", f"Результати експортовано до {filename}")
            except Exception as e:
                messagebox.showerror("Помилка", f"Не вдалося експортувати: {e}")


def main():
    """Головна функція запуску застосунку"""
    root = tk.Tk()
    app = ExpertComparisonApp(root)
    root.mainloop()


if __name__ == '__main__':
    main()
