# Інструкція запуску програми

## Метод 1: Запуск GUI застосунку (рекомендовано)

### Крок 1: Встановіть залежності
```bash
cd C:\Users\Acer\Desktop\cur
pip install numpy scipy
```

### Крок 2: Запустіть програму

**Windows (найпростіший спосіб):**
```powershell
cd C:\Users\Acer\Desktop\cur
# Подвійний клік на run_app.bat або запустіть:
run_app.bat
```

**Або через Python (універсальний спосіб):**
```powershell
cd C:\Users\Acer\Desktop\cur
python run_app.py
```

**Або через модуль:**
```powershell
cd C:\Users\Acer\Desktop\cur
python -m cursova.main
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

```powershell
# Windows PowerShell:

# Перейти до БАТЬКІВСЬКОЇ директорії
cd C:\Users\Acer\Desktop\cur

# Встановити залежності
pip install numpy scipy

# Запустити (НАЙПРОСТІШИЙ спосіб):
run_app.bat

# АБО через Python:
python run_app.py

# АБО через модуль:
python -m cursova.main
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
**Рішення**: Запускайте з БАТЬКІВСЬКОЇ директорії (не з середини cursova):

**ПРАВИЛЬНО ✅:**
```powershell
cd C:\Users\Acer\Desktop\cur
python run_app.py
# або
python -m cursova.main
```

**НЕПРАВИЛЬНО ❌:**
```powershell
cd C:\Users\Acer\Desktop\cur\cursova
python main.py  # ← НЕ ПРАЦЮЄ!
```
