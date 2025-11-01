# Інструкція запуску програми

## Метод 1: Запуск GUI застосунку (рекомендовано)

### Крок 1: Встановіть залежності
```bash
cd /home/user/cur/cursova
pip install -r requirements.txt
```

### Крок 2: Запустіть програму
```bash
# Варіант 1 (рекомендовано):
python -m gui.app

# Варіант 2 (альтернативний):
python main.py
```

### Крок 3: Використовуйте інтерфейс
1. **Панель 1** - Введіть альтернативи (по одній на рядок)
2. **Панель 2** - Оберіть шкалу і порівняйте пари
3. **Панель 3** - Перегляньте результати та експортуйте

---

## Метод 2: Використання без GUI (для тестування)

Якщо GUI не доступний (сервер без X11), можна використати консольну версію:

```bash
cd /home/user/cur
python test_example.py
```

---

## Системні вимоги

- **Python**: 3.8 або новіше
- **Tkinter**: для GUI (зазвичай входить до Python)
- **numpy**: для матричних обчислень
- **scipy**: для власних векторів

### Перевірка tkinter:
```bash
python -c "import tkinter; print('Tkinter доступний!')"
```

Якщо помилка - встановіть:
```bash
# Ubuntu/Debian:
sudo apt-get install python3-tk

# Fedora:
sudo dnf install python3-tkinter

# macOS (зазвичай вже встановлений):
# Переконайтеся, що використовуєте офіційний Python з python.org
```

---

## Приклад використання

```bash
# Перейти до директорії
cd /home/user/cur/cursova

# Встановити залежності
pip install numpy scipy

# Запустити
python -m gui.app
```

---

## Структура файлів

```
cursova/
├── gui/
│   └── app.py          ← Головний GUI файл
├── core/
│   ├── scales.py       ← 6 типів шкал
│   ├── pcm.py          ← Матриця порівнянь
│   ├── consistency.py  ← Перевірка узгодженості
│   └── ranking.py      ← Обчислення ваг
└── main.py             ← Точка входу
```

---

## Можливі проблеми

### Проблема: "No module named 'tkinter'"
**Рішення**: Встановіть python3-tk (див. вище)

### Проблема: "No module named 'numpy'"
**Рішення**:
```bash
pip install numpy scipy
```

### Проблема: "No module named 'cursova'"
**Рішення**: Запускайте з правильної директорії:
```bash
cd /home/user/cur/cursova
python -m gui.app
```

Або з батьківської директорії:
```bash
cd /home/user/cur
python -m cursova.gui.app
```
