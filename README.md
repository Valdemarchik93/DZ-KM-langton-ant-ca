# 🐜 Муравей Лэнгтона: клеточный автомат с 3 уровнями сложности

[![Python](https://img.shields.io/badge/Python-3.14-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![NumPy](https://img.shields.io/badge/NumPy-2.5-013243?logo=numpy&logoColor=white)](https://numpy.org/)
[![Matplotlib](https://img.shields.io/badge/Matplotlib-3.11-11557c?logo=matplotlib&logoColor=white)](https://matplotlib.org/)
[![pytest](https://img.shields.io/badge/pytest-39%20passed-0A9EDC?logo=pytest&logoColor=white)](tests/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Version](https://img.shields.io/badge/version-v1.0-blue)](https://github.com/Valdemarchik93/langton-ant-ca)

> Домашнее задание по курсу **«Компьютерное моделирование»**  
> МГТУ им. Н.Э. Баумана, кафедра СМ-6

---

## 📖 Оглавление

- [О проекте](#-о-проекте)
- [Три уровня сложности](#-три-уровня-сложности)
- [Установка](#-установка)
- [Быстрый старт](#-быстрый-старт)
- [Результаты исследования](#-результаты-исследования)
- [Архитектура](#-архитектура)
- [Тестирование](#-тестирование)
- [Документация](#-документация)
- [Лицензия](#-лицензия)

---

## 🎯 О проекте

Реализация клеточного автомата **«Муравей Лэнгтона»** с тремя уровнями сложности
и полным исследованием режимов поведения. Задача — показать, как из **простых
локальных правил** возникает **сложное эмерджентное поведение**.

### Ключевые результаты

| Уровень | Что исследуется | Главный результат |
|---------|-----------------|-------------------|
| **L1** | Классический муравей | Хайвей после ~10 000 шагов, период 104 |
| **L2** | Многоцветные правила (q=2..4) | **336 правил** перебрано, 50% дают хайвей |
| **L3** | Несколько муравьёв | Sequential vs Synchronous, коллективное поведение |

### Статистика проекта

- **39 автотестов** (`pytest`) — все проходят
- **3 уровня сложности** — L1, L2, L3
- **336 правил** перебрано автоматически
- **~15 GIF-анимаций** сгенерировано
- **~10 графиков** и диаграмм

---

## 🎮 Три уровня сложности

### L1 — Классический муравей Лэнгтона

Два цвета, один муравей, правило R/L. За ~10 000 шагов строит **диагональный хайвей**.

```powershell
python -m src.main run-l1 --steps 15000 --boundary expand --output results/l1
```

**Результат:** `results/l1/ant_animation.gif`, графики `black_ratio.png`, `visited_area.png`.

---

### L2 — Многоцветный муравей

`q` цветов, строка правил из `R/L/F/U`. Перебираем **все** правила для q=2, 3, 4.

```powershell
# Одно правило
python -m src.main run-l2 --rule RLLR --steps 5000

# Полный перебор (336 правил)
python -m src.main sweep-l2 --max-q 4 --steps 2000

# Анализ результатов
python -m src.analyze
```

**Результат:** `results/sweep/` — 2 графика, JSON с классификацией, 9 GIF топ-правил.

**Ключевой вывод:**
> С ростом q доля `bounded` падает (75% → 25%), доля `highway` растёт (25% → 55.5%).
> `unbounded` появляется только при q ≥ 3.

| q | bounded | highway | unbounded |
|---|---------|---------|-----------|
| 2 | 75% | 25% | 0% |
| 3 | 54.7% | 35.9% | 9.4% |
| 4 | **25%** | **55.5%** | 19.5% |

---

### L3 — Несколько муравьёв

`n` муравьёв на общем поле. Два режима обновления: **sequential** и **synchronous**.
Правила столкновений: **allow** (в одной клетке) и **block** (нельзя).

```powershell
python -m src.main run-l3 --ants 2 --update sequential --steps 3000
python -m src.main run-l3 --ants 2 --update synchronous --steps 3000
python -m src.main run-l3 --ants 3 --update sequential --steps 3000
```

**Результат:** `results/l3_*/` — GIF, финальный PNG, **график взаимодействия**.

**Ключевой вывод:**
> При отсутствии прямых столкновений sequential и synchronous дают **визуально
> идентичные** структуры — значит, порядок обновления влияет только при
> реальном взаимодействии агентов.

---

## 🚀 Установка

### Требования
- Python 3.10+
- pip

### Шаги

```powershell
# 1. Клонировать репозиторий
git clone https://github.com/Valdemarchik93/langton-ant-ca.git
cd langton-ant-ca

# 2. Создать виртуальное окружение
python -m venv .venv

# 3. Активировать (Windows)
.venv\Scripts\Activate.ps1

# 4. Установить зависимости
pip install -r requirements.txt
```

---

## ⚡ Быстрый старт

### Все тесты
```powershell
python -m pytest tests/ -v
```
Ожидается: **39 passed** ✅

### L1 — хайвей
```powershell
python -m src.main run-l1 --steps 15000 --boundary expand --output results/l1_expand
```

### L2 — полный sweep
```powershell
python -m src.main sweep-l2 --max-q 4 --steps 2000
python -m src.analyze
```

### L3 — сравнение sequential vs synchronous
```powershell
python -m src.main run-l3 --ants 2 --update sequential --output results/l3_seq
python -m src.main run-l3 --ants 2 --update synchronous --output results/l3_sync
```

---

## 📊 Результаты исследования

### L1 — Динамика муравья

| Шаг | Что видно |
|-----|-----------|
| 0 | Одна чёрная клетка в центре |
| ~500 | Симметричный «снежинкоподобный» узор |
| ~5 000 | Неупорядоченный хаос |
| ~10 000 | Появление диагонального хайвея |
| 15 000 | Стабильный хайвей, муравей уходит в бесконечность |

### L2 — Классификация 336 правил

См. `results/sweep/regime_distribution.png` и `results/sweep/regime_by_q.png`.

### L3 — Коллективное поведение

См. `results/l3_*/animation.gif`, `final_frame.png`, `interaction_metrics.png`.

---

## 🏗 Архитектура

```
langton-ant-ca/
├── src/
│   ├── ant.py                  # L1: классический муравей
│   ├── multi_color_ant.py      # L2: многоцветный
│   ├── multi_ant.py            # L3: мир муравьёв
│   ├── metrics.py              # метрики + классификация
│   ├── simulate.py             # запуск сценариев
│   ├── visualize.py            # графики + GIF
│   ├── analyze.py              # анализ sweep
│   ├── cli.py                  # CLI на click
│   └── main.py                 # точка входа
├── tests/
│   ├── test_ant.py             # 14 тестов L1
│   ├── test_multi_color.py     # 13 тестов L2
│   └── test_multi_ant.py       # 12 тестов L3
├── results/                    # генерируется (в .gitignore)
├── requirements.txt
└── README.md
```

---

## 🧪 Тестирование

```powershell
python -m pytest tests/ -v
```

**Покрытие:**

| Модуль | Тестов | Что проверяется |
|--------|--------|-----------------|
| `test_ant.py` | 14 | Повороты, границы, метрики, детектор хайвея |
| `test_multi_color.py` | 13 | Циклы цвета, команды R/L/F/U, границы |
| `test_multi_ant.py` | 12 | Порядок обновления, столкновения, симметрия |

Все **39 тестов** проходят за **~0.3 секунды**.

---

## 📚 Документация

- **Отчёт**: `REPORT.md` (или PDF в Google Class)
- **Полный отчёт с исследованием**: раздел «Практическая часть» в REPORT.md
- **API**: см. docstrings в каждом модуле

### CLI-команды

| Команда | Описание |
|---------|----------|
| `run-l1` | Классический муравей |
| `run-l2` | Многоцветный муравей |
| `sweep-l2` | Перебор всех правил |
| `run-l3` | Несколько муравьёв |
| `info` | Справка |

Подробнее: `python -m src.main --help`

---

## 📄 Лицензия

MIT License — свободно для образовательных и исследовательских целей.

<p align="center">
  <i>«Из простых локальных правил — сложное эмерджентное поведение»</i>
</p>