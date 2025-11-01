#!/bin/bash
# Скрипт запуску GUI застосунку

echo "╔══════════════════════════════════════════════════════════════════╗"
echo "║  Запуск: Метод експертних попарних порівнянь                    ║"
echo "╚══════════════════════════════════════════════════════════════════╝"
echo ""

# Перевірка Python
if ! command -v python &> /dev/null; then
    echo "✗ Python не знайдено!"
    exit 1
fi

echo "✓ Python знайдено: $(python --version)"

# Перевірка залежностей
echo "Перевірка залежностей..."

python -c "import numpy" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "  Встановлення numpy..."
    pip install numpy -q
fi

python -c "import scipy" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "  Встановлення scipy..."
    pip install scipy -q
fi

python -c "import tkinter" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "✗ Tkinter не знайдено!"
    echo ""
    echo "Для встановлення:"
    echo "  Ubuntu/Debian: sudo apt-get install python3-tk"
    echo "  Fedora:        sudo dnf install python3-tkinter"
    echo ""
    echo "Альтернатива: запустіть консольну версію:"
    echo "  python test_example.py"
    exit 1
fi

echo "✓ Всі залежності встановлені"
echo ""
echo "Запуск GUI застосунку..."
echo ""

# Запуск
cd /home/user/cur/cursova
python -m gui.app
