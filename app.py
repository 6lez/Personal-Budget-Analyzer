import pandas as pd
import customtkinter as tk
import datetime
import os
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import matplotlib.dates as mdates


# ===== КОНФИГУРАЦИЯ =====
class Config:
    """Пути к файлам и настройки"""
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    DATA_FILE = os.path.join(BASE_DIR, 'data.csv')
    SAVINGS_FILE = os.path.join(BASE_DIR, 'savings.csv')
    DATE_STORAGE_FORMAT = '%Y-%m-%d'
    DATE_INPUT_FORMAT = '%d-%m-%Y'
    DATE_DISPLAY_FORMAT = '%d.%m.%Y'

    # Категории расходов для аналитики
    EXPENSE_CATEGORIES = [
        "Продукты", "Транспорт", "Жильё", "Развлечения",
        "Одежда", "Здоровье", "Образование", "Кафе/Рестораны",
        "Подписки", "Связь", "Перевод на сбережения", "Другое"
    ]


class tApp:
    def __init__(self, title, geo):
        self.app = tk.CTk()
        self.app.title(title)
        self.app.resizable(False, False)
        self.app.geometry(geo)
        self.getdata()
        self.create_main_area()
        self.create_sidebar()
        self.app.mainloop()

    # ОСНОВНОЕ ОКНО
    # создание основного окна
    def create_main_area(self):
        self.main_frame = tk.CTkFrame(self.app)
        self.main_frame.pack(side="right", expand=True, fill="both", padx=20, pady=20)
        tk.CTkLabel(self.main_frame, text="Привет!",
                    font=tk.CTkFont(size=50, weight="bold")).pack(anchor="center",pady=300)

    # метод очищения основного окна
    def clear_main_area(self):
        for widget in self.main_frame.winfo_children():
            widget.destroy()

    # САЙДБАР
    # метод создания окна сайдбара
    def create_sidebar(self):
        self.sidebar = tk.CTkFrame(self.app, width=200)
        self.sidebar.pack(side="left", fill="y")

        # Заголовок
        tk.CTkLabel(self.sidebar, text="Меню",
                    font=tk.CTkFont(size=30, weight="bold")).pack(pady=10)
        tk.CTkFrame(self.sidebar, height=2, fg_color="gray").pack(fill="x", padx=20, pady=(10, 10))
        # Кнопки
        buttons = [
            ("➕ Добавить", self.add),
            ("📊 Дашборд", self.dashboard),
            ("💰 Сбережения", self.savedmoney),
            ("💳 Транзакции", self.transactions),
            ("📈 Аналитика", self.analyze)
        ]
        for text, command in buttons:
            btn = tk.CTkButton(self.sidebar, text=text, command=command)
            btn.pack(pady=20, padx=20, fill="x")
        tk.CTkFrame(self.sidebar, height=2, fg_color="gray").pack(fill="x", padx=20, pady=(10, 10))
        tk.CTkLabel(self.sidebar, text="Сводка", font=tk.CTkFont(size=30, weight="bold")).pack(pady=10)
        self.stats()

    # метод статистики сайдбара
    def stats(self):
        self.calculate()
        if hasattr(self, 'sidebar_stats_frame'):
            self.sidebar_stats_frame.destroy()

        self.sidebar_stats_frame = tk.CTkFrame(self.sidebar, fg_color="transparent")
        self.sidebar_stats_frame.pack(fill="x", padx=20, pady=10)

        tk.CTkLabel(
            self.sidebar_stats_frame,
            text="Текущий баланс:",
            font=tk.CTkFont(size=20),
            text_color="gray"
        ).pack(anchor="s")
        balance_color = "green" if self.balance >= 0 else "red"
        tk.CTkLabel(
            self.sidebar_stats_frame,
            text=f"{self.balance:,.0f} ₽",
            font=tk.CTkFont(size=20, weight="bold"),
            text_color=balance_color
        ).pack(anchor="s", pady=(0, 15))

        # Доходы и расходы
        stats = [
            (f"Доходы: {self.total_income:,.0f} ₽", "green"),
            (f"Расходы: {self.total_expense:,.0f} ₽", "red"),
            (f"Сбережения: {self.saved:,.0f} ₽", "#9370DB")
        ]

        for text, color in stats:
            tk.CTkLabel(
                self.sidebar_stats_frame,
                text=text,
                font=tk.CTkFont(size=16),
                text_color=color
            ).pack(anchor="w", pady=2)

    # КНОПКА > ДОБАВИТЬ
    # метод окна с функцией добавления транзакции основного счёта
    def add(self):
        self.clear_main_area()
        tk.CTkLabel(
            self.main_frame,
            text="➕ Новая транзакция",
            font=tk.CTkFont(size=38, weight="bold")
        ).pack(pady=(30, 20))
        self.addframe = tk.CTkFrame(self.main_frame, fg_color="transparent", height=120)
        self.addframe.pack(fill="x", padx=20, pady=20)
        self.addframe.grid_columnconfigure(0, weight=1)
        self.addframe.grid_rowconfigure(0, weight=1)
        date_label = tk.CTkLabel(
            self.addframe,
            text="Дата транзакции:",
            font=tk.CTkFont(size=16)
        )
        date_label.grid(row=0, column=0, sticky="w", pady=(0, 5))

        self.entry_date = tk.CTkEntry(
            self.addframe,
            placeholder_text="Например: 03-02-2025",
            width=400,
            height=45,
            font=tk.CTkFont(size=16)
        )
        self.entry_date.grid(row=1, column=0, sticky="w", pady=(0, 5))

        # Подсказка под полем даты
        tk.CTkLabel(
            self.addframe,
            text="Формат: День-Месяц-Год (например: 03-02-2025)",
            font=tk.CTkFont(size=12),
            text_color="gray"
        ).grid(row=2, column=0, sticky="w", pady=(0, 30))

        # Поле описания
        disc_label = tk.CTkLabel(
            self.addframe,
            text="Описание:",
            font=tk.CTkFont(size=16)
        )
        disc_label.grid(row=3, column=0, sticky="w", pady=(0, 5))

        self.entry_disc = tk.CTkEntry(
            self.addframe,
            placeholder_text="Например: Зарплата, Продукты, Кафе...",
            width=400,
            height=45,
            font=tk.CTkFont(size=16)
        )
        self.entry_disc.grid(row=4, column=0, sticky="w", pady=(0, 50))

        # Поле суммы
        value_label = tk.CTkLabel(
            self.addframe,
            text="Сумма:",
            font=tk.CTkFont(size=16)
        )
        value_label.grid(row=5, column=0, sticky="w", pady=(0, 5))

        self.entry_value = tk.CTkEntry(
            self.addframe,
            placeholder_text="Например: 20000 (доход) или -5000 (расход)",
            width=400,
            height=45,
            font=tk.CTkFont(size=16)
        )
        self.entry_value.grid(row=6, column=0, sticky="w", pady=(0, 20))
        # Кнопки
        button_frame = tk.CTkFrame(self.addframe, fg_color="transparent")
        button_frame.grid(row=8, column=0, sticky="w")

        # Кнопка добавления
        add_btn = tk.CTkButton(
            button_frame,
            text="✅ Добавить транзакцию",
            command=self.kick_to_data,
            width=200,
            height=50,
            font=tk.CTkFont(size=16, weight="bold"),
            fg_color="#2E8B57",
            hover_color="#3CB371"
        )
        add_btn.pack(side="left", padx=(0, 20))

        # Кнопка очистки
        clear_btn = tk.CTkButton(
            button_frame,
            text="🗑️ Очистить форму",
            command=self.clear_form_fields,
            width=150,
            height=50,
            font=tk.CTkFont(size=16),
            fg_color="#696969",
            hover_color="#808080"
        )
        clear_btn.pack(side="left")

    # метод добавления данных в таблицу и переменные, после добавления транзакции
    # метод получения данных из полей
    def kick_to_data(self):
        try:
            # 1. Получаем данные из полей
            date_str = self.entry_date.get().strip()
            description = self.entry_disc.get().strip()
            value_str = self.entry_value.get().strip()
            if not date_str:
                self.show_message("Ошибка: введите дату!", "error")
                return
            if not description:
                self.show_message("Ошибка: введите описание!", "error")
                return
            if not value_str:
                self.show_message("Ошибка: введите сумму!", "error")
                return
            try:
                # Преобразуем строку в datetime
                date_obj = datetime.datetime.strptime(date_str, Config.DATE_INPUT_FORMAT)
            except ValueError:
                self.show_message("Ошибка: неверный формат даты! Используйте ДД-ММ-ГГГГ", "error")
                return
            # Проверка суммы
            try:
                value = float(value_str)
                if value == 0:
                    self.show_message("Ошибка: сумма не может быть нулевой!", "error")
                    return
            except ValueError:
                self.show_message("Ошибка: сумма должна быть числом!", "error")
                return

            if value >= 0:
                trans_type = "income"
            else:
                trans_type = "expense"
            new_transaction = pd.DataFrame([{
                'date': date_obj,
                'value': value,
                'description': description,
                'type': trans_type
            }])
            self.data = pd.concat([self.data, new_transaction], ignore_index=True)
            self.save_data()
            self.show_message("Транзакция добавлена!", "success")
            self.stats()
            self.clear_form_fields()
        except Exception as e:
            self.show_message(f"Ошибка: {str(e)}", "error")

    # КНОПКА > ДАШБОРД
    # метод окна с дашбордом
    def dashboard(self):
        self.clear_main_area()
        # ===== ЗАГОЛОВОК =====
        header = tk.CTkFrame(self.main_frame, fg_color="transparent", height=80)
        header.pack(fill="x", padx=30, pady=20)

        tk.CTkLabel(
            header,
            text="📊 Финансовый обзор",
            font=tk.CTkFont(size=36, weight="bold"),
            text_color="#2C3E50"
        ).pack(side="left")

        tk.CTkLabel(
            header,
            text=f"Обновлено сегодня, {datetime.datetime.now().strftime('%H:%M')}",
            font=tk.CTkFont(size=14),
            text_color="gray"
        ).pack(side="right", pady=10)

        # ===== БЫСТРАЯ СТАТИСТИКА =====
        quick_stats_frame = tk.CTkFrame(self.main_frame, height=120)
        quick_stats_frame.pack(fill="x", padx=30, pady=(0, 20))

        # 4 метрики в ряд
        stats = [
            ("💰 Баланс", f"{self.balance:,.0f}₽", "green"),
            ("📈 Доходы", f"{self.total_income:,.0f}₽", "#2E8B57"),
            ("📉 Расходы", f"{self.total_expense:,.0f}₽", "#DC143C"),
            ("🎯 Сбережения", f"{self.saved:,.0f}₽", "#9370DB")
        ]

        for i, (title, value, color) in enumerate(stats):
            quick_stats_frame.grid_columnconfigure(i, weight=1)
            stat_card = tk.CTkFrame(quick_stats_frame, height=100)
            stat_card.grid(row=0, column=i, padx=10, pady=10, sticky="nsew")

            # Заголовок
            tk.CTkLabel(
                stat_card,
                text=title,
                font=tk.CTkFont(size=13),
                text_color="gray"
            ).pack(pady=(15, 5))

            # Значение
            tk.CTkLabel(
                stat_card,
                text=value,
                font=tk.CTkFont(size=26, weight="bold"),
                text_color=color
            ).pack(pady=(0, 15))

        # ===== ДВЕ КОЛОНКИ: ГРАФИКИ И ПОСЛЕДНИЕ ОПЕРАЦИИ =====
        content_frame = tk.CTkFrame(self.main_frame, fg_color="transparent")
        content_frame.pack(fill="both", expand=True, padx=30, pady=10)
        content_frame.grid_rowconfigure(0, weight=1)

        # Левая колонка - 60%
        content_frame.grid_columnconfigure(0, weight=6)
        # Правая колонка - 40%
        content_frame.grid_columnconfigure(1, weight=4)

        # ЛЕВАЯ КОЛОНКА: График динамики за месяц
        charts_frame = tk.CTkFrame(content_frame)
        charts_frame.grid(row=0, column=0, padx=(0, 15), pady=10, sticky="nsew")

        tk.CTkLabel(
            charts_frame,
            text="📈 Динамика за последний месяц",
            font=tk.CTkFont(size=18, weight="bold")
        ).pack(pady=(15, 10))

        # Строим график за последние 30 дней
        self._build_dashboard_chart(charts_frame)

        # ПРАВАЯ КОЛОНКА: Последние транзакции
        recent_frame = tk.CTkFrame(content_frame)
        recent_frame.grid(row=0, column=1, padx=(15, 0), pady=10, sticky="nsew")

        tk.CTkLabel(
            recent_frame,
            text="💳 Последние операции",
            font=tk.CTkFont(size=18, weight="bold")
        ).pack(pady=(15, 10))

        # Список последних транзакций
        self._build_recent_transactions(recent_frame)

    def _build_dashboard_chart(self, parent):
        """Строит линейный график доходов/расходов за последние 30 дней"""
        if self.data.empty:
            tk.CTkLabel(
                parent,
                text="📭 Нет данных для графика.\nДобавьте транзакции!",
                font=tk.CTkFont(size=15),
                text_color="gray"
            ).pack(pady=60)
            return

        df = self.data.copy()
        df['date'] = pd.to_datetime(df['date'])

        # Фильтруем последние 30 дней
        today = pd.Timestamp.now().normalize()
        month_ago = today - pd.Timedelta(days=30)
        df_month = df[df['date'] >= month_ago]

        if df_month.empty:
            tk.CTkLabel(
                parent,
                text="📭 Нет транзакций за последние 30 дней",
                font=tk.CTkFont(size=15),
                text_color="gray"
            ).pack(pady=60)
            return

        # Группировка по дням
        income_daily = df_month[df_month['type'] == 'income'].groupby(
            df_month['date'].dt.date)['value'].sum()
        expense_daily = df_month[df_month['type'] == 'expense'].groupby(
            df_month['date'].dt.date)['value'].sum().abs()

        # Создаём полный диапазон дат за 30 дней
        all_dates = pd.date_range(start=month_ago, end=today, freq='D').date
        income_series = pd.Series(0.0, index=all_dates)
        expense_series = pd.Series(0.0, index=all_dates)
        income_series.update(income_daily)
        expense_series.update(expense_daily)

        # Накопительный баланс за месяц
        balance_series = (income_series - expense_series).cumsum()

        # ===== ПОСТРОЕНИЕ ГРАФИКА =====
        fig = Figure(figsize=(6, 3), dpi=100)
        fig.patch.set_facecolor('#2B2B2B')
        ax = fig.add_subplot(111)
        ax.set_facecolor('#2B2B2B')

        dates = [datetime.datetime.combine(d, datetime.time()) for d in all_dates]

        # Столбцы доходов и расходов
        bar_width = 0.35
        dates_num = mdates.date2num(dates)

        ax.bar(dates_num - bar_width / 2, income_series.values,
               width=bar_width, color='#2E8B57', alpha=0.7, label='Доходы')
        ax.bar(dates_num + bar_width / 2, expense_series.values,
               width=bar_width, color='#DC143C', alpha=0.7, label='Расходы')

        # Линия накопительного баланса
        ax2 = ax.twinx()
        ax2.plot(dates, balance_series.values, color='#1E90FF',
                 linewidth=2, linestyle='--', label='Баланс', marker='')
        ax2.set_facecolor('#2B2B2B')
        ax2.tick_params(colors='white', labelsize=7)
        ax2.spines['right'].set_color('gray')
        ax2.spines['top'].set_visible(False)
        ax2.yaxis.set_major_formatter(lambda x, _: f'{x:,.0f}')

        # Оформление основной оси
        ax.legend(fontsize=8, facecolor='#3B3B3B', edgecolor='gray',
                  labelcolor='white', loc='upper left')
        ax2.legend(fontsize=8, facecolor='#3B3B3B', edgecolor='gray',
                   labelcolor='white', loc='upper right')

        ax.tick_params(colors='white', labelsize=7)
        ax.spines['bottom'].set_color('gray')
        ax.spines['left'].set_color('gray')
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.yaxis.set_major_formatter(lambda x, _: f'{x:,.0f}')

        ax.xaxis.set_major_formatter(mdates.DateFormatter('%d.%m'))
        ax.xaxis.set_major_locator(mdates.WeekdayLocator())
        fig.autofmt_xdate(rotation=45)

        ax.grid(axis='y', alpha=0.15, color='gray')
        fig.tight_layout()

        canvas = FigureCanvasTkAgg(fig, master=parent)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=(0, 10))

        # Мини-статистика под графиком
        month_income = income_series.sum()
        month_expense = expense_series.sum()
        month_net = month_income - month_expense

        mini_stats = tk.CTkFrame(parent, fg_color="transparent")
        mini_stats.pack(fill="x", padx=15, pady=(0, 10))

        for text, color in [
            (f"Доход за месяц: {month_income:,.0f}₽", "#2E8B57"),
            (f"Расход за месяц: {month_expense:,.0f}₽", "#DC143C"),
            (f"Итого: {month_net:+,.0f}₽", "#1E90FF" if month_net >= 0 else "#DC143C")
        ]:
            tk.CTkLabel(
                mini_stats, text=text,
                font=tk.CTkFont(size=12, weight="bold"),
                text_color=color
            ).pack(side="left", padx=10)

    def _build_recent_transactions(self, parent):
        """Показывает последние 10 транзакций в правой колонке дашборда"""
        if self.data.empty:
            tk.CTkLabel(
                parent,
                text="📭 Пока нет транзакций",
                font=tk.CTkFont(size=14),
                text_color="gray"
            ).pack(pady=40)
            return

        # Прокручиваемый список
        scroll = tk.CTkScrollableFrame(parent, fg_color="transparent")
        scroll.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        # Последние 10 транзакций (новые сверху)
        recent = self.data.sort_values('date', ascending=False).head(10)

        for i, (_, row) in enumerate(recent.iterrows()):
            row_color = "#F8F9FA" if i % 2 == 0 else "#EAECEE"
            card = tk.CTkFrame(scroll, height=55, fg_color=row_color, corner_radius=8)
            card.pack(fill="x", pady=3, padx=5)

            # Левая часть: иконка + описание + дата
            left = tk.CTkFrame(card, fg_color="transparent")
            left.pack(side="left", fill="both", expand=True, padx=10, pady=8)

            value = row['value']
            icon = "📈" if value >= 0 else "📉"

            desc = str(row.get('description', '—'))
            if len(desc) > 22:
                desc = desc[:19] + "..."

            tk.CTkLabel(
                left,
                text=f"{icon} {desc}",
                font=tk.CTkFont(size=13, weight="bold"),
                text_color="#2C3E50"
            ).pack(anchor="w")

            date_display = pd.to_datetime(row['date']).strftime(Config.DATE_DISPLAY_FORMAT)
            tk.CTkLabel(
                left,
                text=date_display,
                font=tk.CTkFont(size=11),
                text_color="gray"
            ).pack(anchor="w")

            # Правая часть: сумма
            value_color = "#2E8B57" if value >= 0 else "#DC143C"
            value_prefix = "+" if value >= 0 else ""
            tk.CTkLabel(
                card,
                text=f"{value_prefix}{value:,.0f}₽",
                font=tk.CTkFont(size=15, weight="bold"),
                text_color=value_color
            ).pack(side="right", padx=15, pady=8)

        # Кнопка «Все транзакции»
        tk.CTkButton(
            parent,
            text="📋 Все транзакции →",
            font=tk.CTkFont(size=13),
            width=200, height=35,
            fg_color="#696969",
            hover_color="#808080",
            command=self.transactions
        ).pack(pady=(5, 15))

    # КНОПКА > СБЕРЕЖЕНИЯ
    # метод окна со статистикой сбережений
    def savedmoney(self):
        self.clear_main_area()
        header = tk.CTkFrame(self.main_frame, fg_color="transparent", height=120)
        header.pack(fill="both", padx=20, pady=20)

        tk.CTkLabel(
            header,
            text="💰 Управление сбережениями",
            font=tk.CTkFont(size=36, weight="bold"),
            text_color="#2C3E50"
        ).pack(side="left")
        tk.CTkLabel(
            header,
            text=f"Обновлено сегодня, {datetime.datetime.now().strftime('%H:%M')}",
            font=tk.CTkFont(size=14),
            text_color="gray"
        ).pack(side="right", pady=10)

        statspack = tk.CTkFrame(self.main_frame, fg_color="transparent", height=120)
        statspack.pack(fill="both", expand=True, padx=30, pady=(0, 30))
        statspack.grid_columnconfigure(0, weight=3)
        statspack.grid_columnconfigure(1, weight=7)
        statspack.grid_rowconfigure(0, weight=1)

        self.left_column = tk.CTkFrame(statspack)
        self.left_column.grid(row=0, column=0, padx=(0, 15), sticky="nsew")

        # ПРАВАЯ КОЛОНКА — история транзакций сбережений
        right_column = tk.CTkFrame(statspack)
        right_column.grid(row=0, column=1, sticky="nsew")

        # === ЛЕВАЯ КОЛОНКА: Статистика + форма ===
        savings_stats = tk.CTkFrame(self.left_column, fg_color="#4d5d53")
        savings_stats.pack(fill="x", padx=20, pady=5)
        tk.CTkLabel(
            savings_stats,
            text="📊 Статистика сбережения",
            font=tk.CTkFont(size=18, weight="bold"),
            text_color="#d0f0c0"
        ).pack(side="top", pady=(15, 10))
        total_card = tk.CTkFrame(savings_stats, height=150, corner_radius=10)
        total_card.pack(fill="x", pady=(0, 15), padx=5)

        tk.CTkLabel(
            total_card,
            text="Общий баланс",
            font=tk.CTkFont(size=14),
            text_color="gray"
        ).pack(side="top", pady=(5, 5))
        tk.CTkLabel(
            total_card,
            text=f"{self.saved:,.0f}₽",
            font=tk.CTkFont(size=28, weight="bold"),
            text_color="#9932CC"
        ).pack(side="top", pady=(5, 15))
        tk.CTkFrame(total_card, height=2, fg_color="gray").pack(fill="x", padx=15, pady=5)
        stats = [
            (f"📈 Пополнения: {self.total_income_savings:,.0f} ₽", "#2E8B57"),
            (f"📉 Снятия: {self.total_expense_savings:,.0f} ₽", "#DC143C"),
            (f"💰Остаток на счёте: {self.balance:,.0f} ₽", "#1E90FF")
        ]
        for text, color in stats:
            tk.CTkLabel(
                total_card,
                text=text,
                font=tk.CTkFont(size=16, weight="bold"),
                text_color=color
            ).pack(side="top", pady=2)
        tk.CTkFrame(self.left_column, height=2, fg_color="gray").pack(fill="x", padx=20, pady=5)
        self.operation_with_saved()

        # === ПРАВАЯ КОЛОНКА: История операций со сбережениями ===
        self._build_savings_transactions(right_column)

    def _build_savings_transactions(self, parent):
        """Прокручиваемый список транзакций сберегательного счёта"""

        # Заголовок
        header_frame = tk.CTkFrame(parent, fg_color="transparent")
        header_frame.pack(fill="x", padx=15, pady=(10, 5))

        tk.CTkLabel(
            header_frame,
            text="📜 История операций со сбережениями",
            font=tk.CTkFont(size=18, weight="bold")
        ).pack(side="left")

        count_text = f"Записей: {len(self.savings)}"
        tk.CTkLabel(
            header_frame,
            text=count_text,
            font=tk.CTkFont(size=13),
            text_color="gray"
        ).pack(side="right")

        # Разделитель
        tk.CTkFrame(parent, height=2, fg_color="gray").pack(fill="x", padx=15, pady=5)

        if self.savings.empty:
            tk.CTkLabel(
                parent,
                text="📭 Пока нет операций со сбережениями.\n\nИспользуйте форму слева,\nчтобы перевести деньги.",
                font=tk.CTkFont(size=15),
                text_color="gray",
                justify="center"
            ).pack(pady=60)
            return

        # Заголовки таблицы
        table_header = tk.CTkFrame(parent, height=35, fg_color="#2C3E50")
        table_header.pack(fill="x", padx=15)

        table_header.grid_columnconfigure(0, weight=5)
        table_header.grid_columnconfigure(1, weight=15)
        table_header.grid_columnconfigure(2, weight=20)
        table_header.grid_columnconfigure(3, weight=15)
        table_header.grid_columnconfigure(4, weight=15)

        for i, col_text in enumerate(["№", "Дата", "Тип", "Сумма", "Действие"]):
            tk.CTkLabel(
                table_header,
                text=col_text,
                font=tk.CTkFont(size=12, weight="bold"),
                text_color="white"
            ).grid(row=0, column=i, padx=8, pady=6, sticky="w")

        # Прокручиваемый список
        scroll = tk.CTkScrollableFrame(parent, fg_color="transparent")
        scroll.pack(fill="both", expand=True, padx=15, pady=(0, 10))

        # Сортировка: новые сверху
        sorted_savings = self.savings.sort_values('date', ascending=False).reset_index(drop=False)
        sorted_savings = sorted_savings.rename(columns={'index': 'original_index'})

        for row_num, (_, row) in enumerate(sorted_savings.iterrows()):
            row_color = "#F8F9FA" if row_num % 2 == 0 else "#EAECEE"
            row_frame = tk.CTkFrame(scroll, height=42, fg_color=row_color, corner_radius=6)
            row_frame.pack(fill="x", pady=2)

            row_frame.grid_columnconfigure(0, weight=5)
            row_frame.grid_columnconfigure(1, weight=15)
            row_frame.grid_columnconfigure(2, weight=20)
            row_frame.grid_columnconfigure(3, weight=15)
            row_frame.grid_columnconfigure(4, weight=15)

            # Номер
            tk.CTkLabel(
                row_frame,
                text=str(row_num + 1),
                font=tk.CTkFont(size=12),
                text_color="#555"
            ).grid(row=0, column=0, padx=8, pady=6, sticky="w")

            # Дата
            date_display = pd.to_datetime(row['date']).strftime(Config.DATE_DISPLAY_FORMAT)
            tk.CTkLabel(
                row_frame,
                text=date_display,
                font=tk.CTkFont(size=12),
                text_color="#333"
            ).grid(row=0, column=1, padx=8, pady=6, sticky="w")

            # Тип операции
            value = row['value']
            if value >= 0:
                type_text = "📥 Пополнение"
                type_color = "#2E8B57"
            else:
                type_text = "📤 Снятие"
                type_color = "#DC143C"

            tk.CTkLabel(
                row_frame,
                text=type_text,
                font=tk.CTkFont(size=12, weight="bold"),
                text_color=type_color
            ).grid(row=0, column=2, padx=8, pady=6, sticky="w")

            # Сумма
            value_prefix = "+" if value >= 0 else ""
            tk.CTkLabel(
                row_frame,
                text=f"{value_prefix}{value:,.0f} ₽",
                font=tk.CTkFont(size=13, weight="bold"),
                text_color=type_color
            ).grid(row=0, column=3, padx=8, pady=6, sticky="w")

            # Кнопка удаления
            original_idx = row['original_index']
            tk.CTkButton(
                row_frame,
                text="🗑️",
                width=40,
                height=28,
                font=tk.CTkFont(size=12),
                fg_color="#DC143C",
                hover_color="#B22222",
                command=lambda idx=original_idx: self._delete_savings_transaction(idx)
            ).grid(row=0, column=4, padx=8, pady=4, sticky="w")

        # Итоговая строка
        tk.CTkFrame(parent, height=2, fg_color="gray").pack(fill="x", padx=15, pady=5)

        summary = tk.CTkFrame(parent, fg_color="transparent")
        summary.pack(fill="x", padx=20, pady=(0, 10))

        for text, color in [
            (f"Всего пополнений: {self.total_income_savings:,.0f}₽", "#2E8B57"),
            (f"Всего снятий: {self.total_expense_savings:,.0f}₽", "#DC143C"),
            (f"Итого: {self.saved:,.0f}₽", "#9932CC")
        ]:
            tk.CTkLabel(
                summary, text=text,
                font=tk.CTkFont(size=12, weight="bold"),
                text_color=color
            ).pack(side="left", padx=10)

    def _delete_savings_transaction(self, idx):
        """Удаляет транзакцию сбережений и обновляет интерфейс"""
        try:
            if idx in self.savings.index:
                self.savings = self.savings.drop(index=idx).reset_index(drop=True)
                self.save_data()
                self.calculate()
                self.stats()
                # Перерисовываем окно сбережений
                self.savedmoney()
        except Exception as e:
            print(f"Ошибка удаления из сбережений: {e}")

    # метод окна с функцией добавления транзакции С или В сбережения
    def operation_with_saved(self):
        form_frame = tk.CTkFrame(self.left_column, fg_color="#4d5d53")
        form_frame.pack(fill="x", padx=20, pady=(0, 20))

        form_frame_label = tk.CTkFrame(form_frame, fg_color="#4d5d53")
        form_frame_label.pack(fill="x", padx=20, pady=(0, 20))
        tk.CTkLabel(
            form_frame_label,
            text="➕ Операция со сбережениями",
            font=tk.CTkFont(size=14, weight="bold"),
            text_color="#d0f0c0"
        ).pack(side="top", pady=(5, 5))

        form_frame_op = tk.CTkFrame(form_frame, fg_color="#4d5d53")
        form_frame_op.pack(fill="x", padx=20, pady=(0, 20))
        form_frame_op.grid_columnconfigure(0, weight=6)
        form_frame_op.grid_columnconfigure(1, weight=4)

        self.left_side = tk.CTkFrame(form_frame_op, fg_color="#4d5d53")
        self.left_side.grid(row=0, column=0, sticky="nsew")
        right_side = tk.CTkFrame(form_frame_op, fg_color="#4d5d53")
        right_side.grid(row=0, column=1, sticky="nsew")

        self.date_savings_frame = tk.CTkFrame(self.left_side, fg_color="#778899", height=120)
        self.date_savings_frame.pack(side="top", padx=10, pady=5)
        tk.CTkLabel(
            self.date_savings_frame,
            text="Дата",
            font=tk.CTkFont(size=16),
            text_color="#FFFAFA"
        ).pack(side='top', padx=5, pady=5)

        self.savings_entry_date = tk.CTkEntry(
            self.date_savings_frame,
            placeholder_text="Например: 03-02-2025",
            width=200,
            height=45,
            font=tk.CTkFont(size=16)
        )
        self.savings_entry_date.pack(side='top', padx=5, pady=5)

        self.amount_savings_frame = tk.CTkFrame(self.left_side, fg_color="#778899", height=120)
        self.amount_savings_frame.pack(side="top", padx=10, pady=5)
        tk.CTkLabel(
            self.amount_savings_frame,
            text="Сумма",
            font=tk.CTkFont(size=16),
            text_color="#FFFAFA"
        ).pack(side='top', padx=5, pady=5)

        self.savings_amount_entry = tk.CTkEntry(
            self.amount_savings_frame,
            placeholder_text="Введите сумму...",
            width=200,
            height=45,
            font=tk.CTkFont(size=16)
        )
        self.savings_amount_entry.pack(side='top', padx=10, pady=5)
        # Общая переменная для двух кнопок
        self.savings_op_type = tk.StringVar(value="to_savings")

        # Первая кнопка
        tk.CTkRadioButton(
            right_side,
            text="С основного счёта → сбережения",
            variable=self.savings_op_type,
            value="to_savings",
            text_color="#FFFAFA"
        ).pack(side='top', padx=5, pady=5)
        # Вторая кнопка
        tk.CTkRadioButton(
            right_side,
            text="Со сбережений → основной счёт",
            variable=self.savings_op_type,
            value="from_savings",
            text_color="#FFFAFA"
        ).pack(side='top', padx=5, pady=5)

        add_btn = tk.CTkButton(
            right_side,
            text="✅ Добавить транзакцию",
            font=tk.CTkFont(size=16, weight="bold"),
            command=self.savings_operation,
            width=150,
            height=50,
            fg_color="#2E8B57",
            hover_color="#3CB371"
        )
        add_btn.pack(side='top', padx=(0, 15), pady=5)
        clear_btn = tk.CTkButton(
            right_side,
            text="🗑️ Очистить форму",
            command=self.clear_savings_form,
            width=150,
            height=50,
            font=tk.CTkFont(size=16),
            fg_color="#696969",
            hover_color="#808080"
        )
        clear_btn.pack(side='top', padx=(0, 15), pady=5)

    def savings_operation(self):
        """Обрабатывает операцию со сбережениями"""
        try:
            date_str = self.savings_entry_date.get().strip()
            amount_str = self.savings_amount_entry.get().strip()
            operation_type = self.savings_op_type.get()

            # Валидация даты
            if not date_str:
                self.show_message_in("Ошибка: введите дату!", "error", self.left_column)
                return
            try:
                date_obj = datetime.datetime.strptime(date_str, Config.DATE_INPUT_FORMAT)
            except ValueError:
                self.show_message_in("Ошибка: неверный формат даты! Используйте ДД-ММ-ГГГГ", "error",
                                     self.left_column)
                return

            # Валидация суммы
            if not amount_str:
                self.show_message_in("Ошибка: введите сумму!", "error", self.left_column)
                return

            try:
                amount = float(amount_str)
                if amount <= 0:
                    self.show_message_in("Ошибка: сумма должна быть положительной!", "error", self.left_column)
                    return
            except ValueError:
                self.show_message_in("Ошибка: сумма должна быть числом!", "error", self.left_column)
                return

            if operation_type == "to_savings":
                # Перевод с основного счета на сбережения
                if self.balance < amount:
                    self.show_message_in("Недостаточно средств на балансе!", "error", self.left_column)
                    return

                # 1. Списываем с основного счета
                main_transaction = pd.DataFrame([{
                    'date': date_obj,
                    'value': -amount,
                    'description': 'Перевод на сбережения',
                    'type': "expense"
                }])
                self.data = pd.concat([self.data, main_transaction], ignore_index=True)

                # 2. Добавляем на сбережения
                savings_transaction = pd.DataFrame([{
                    'date': date_obj,
                    'value': amount,
                    'type': "income"
                }])
                self.savings = pd.concat([self.savings, savings_transaction], ignore_index=True)

                self.show_message_in("Деньги переведены на сбережения!", "success", self.left_column)

            elif operation_type == "from_savings":
                # Перевод со сбережений на основной счет
                if self.saved < amount:
                    self.show_message_in("Недостаточно средств на сбережениях!", "error", self.left_column)
                    return

                # 1. Списываем со сбережений
                savings_transaction = pd.DataFrame([{
                    'date': date_obj,
                    'value': -amount,
                    'type': "expense"
                }])
                self.savings = pd.concat([self.savings, savings_transaction], ignore_index=True)

                # 2. Добавляем на основной счет
                main_transaction = pd.DataFrame([{
                    'date': date_obj,
                    'value': amount,
                    'description': 'Перевод со сбережений',
                    'type': "income"
                }])
                self.data = pd.concat([self.data, main_transaction], ignore_index=True)

                self.show_message_in("Деньги переведены на основной счет!", "success", self.left_column)

            # Сохраняем и обновляем
            self.save_data()
            self.calculate()
            self.stats()

            # Очищаем поля
            self.clear_savings_form()
        except Exception as e:
            self.show_message_in(f"Ошибка: {str(e)}", "error", self.left_column)

    # КНОПКА > ТРАНЗАКЦИИ
    # метод окна со списком всех транзакций, фильтрацией и удалением
    def transactions(self):
        self.clear_main_area()

        # ===== ЗАГОЛОВОК =====
        header = tk.CTkFrame(self.main_frame, fg_color="transparent", height=60)
        header.pack(fill="x", padx=30, pady=(20, 10))

        tk.CTkLabel(
            header,
            text="💳 История транзакций",
            font=tk.CTkFont(size=36, weight="bold"),
            text_color="#2C3E50"
        ).pack(side="left")

        tk.CTkLabel(
            header,
            text=f"Всего записей: {len(self.data)}",
            font=tk.CTkFont(size=14),
            text_color="gray"
        ).pack(side="right", pady=10)

        # ===== ПАНЕЛЬ ФИЛЬТРОВ =====
        filter_frame = tk.CTkFrame(self.main_frame, height=60)
        filter_frame.pack(fill="x", padx=30, pady=(0, 15))

        tk.CTkLabel(
            filter_frame,
            text="🔍 Фильтры:",
            font=tk.CTkFont(size=14, weight="bold")
        ).pack(side="left", padx=(15, 10), pady=10)

        # Фильтр по типу (доход / расход / все)
        self.filter_type_var = tk.StringVar(value="all")
        type_menu = tk.CTkOptionMenu(
            filter_frame,
            variable=self.filter_type_var,
            values=["all", "income", "expense"],
            command=lambda _: self._refresh_transactions_table(),
            width=140,
            font=tk.CTkFont(size=13)
        )
        type_menu.pack(side="left", padx=5, pady=10)

        # Поле поиска по описанию
        self.search_var = tk.StringVar()
        search_entry = tk.CTkEntry(
            filter_frame,
            textvariable=self.search_var,
            placeholder_text="Поиск по описанию...",
            width=220,
            height=35,
            font=tk.CTkFont(size=13)
        )
        search_entry.pack(side="left", padx=10, pady=10)

        # Кнопка поиска
        tk.CTkButton(
            filter_frame,
            text="🔎 Найти",
            command=self._refresh_transactions_table,
            width=100,
            height=35,
            font=tk.CTkFont(size=13),
            fg_color="#1E90FF",
            hover_color="#4169E1"
        ).pack(side="left", padx=5, pady=10)

        # Кнопка сброса фильтров
        tk.CTkButton(
            filter_frame,
            text="↩ Сброс",
            command=self._reset_filters,
            width=100,
            height=35,
            font=tk.CTkFont(size=13),
            fg_color="#696969",
            hover_color="#808080"
        ).pack(side="left", padx=5, pady=10)

        # ===== ЗАГОЛОВКИ ТАБЛИЦЫ =====
        table_header = tk.CTkFrame(self.main_frame, height=40, fg_color="#2C3E50")
        table_header.pack(fill="x", padx=30)

        columns = [
            ("№", 0.05),
            ("Дата", 0.15),
            ("Описание", 0.35),
            ("Сумма", 0.15),
            ("Тип", 0.12),
            ("Действие", 0.18)
        ]
        for col_text, col_weight in columns:
            table_header.grid_columnconfigure(columns.index((col_text, col_weight)), weight=int(col_weight * 100))

        for i, (col_text, _) in enumerate(columns):
            tk.CTkLabel(
                table_header,
                text=col_text,
                font=tk.CTkFont(size=13, weight="bold"),
                text_color="white"
            ).grid(row=0, column=i, padx=10, pady=8, sticky="w")

        # ===== ОБЛАСТЬ ПРОКРУТКИ ДЛЯ ТРАНЗАКЦИЙ =====
        self.transactions_scroll = tk.CTkScrollableFrame(
            self.main_frame,
            fg_color="transparent"
        )
        self.transactions_scroll.pack(fill="both", expand=True, padx=30, pady=(0, 20))

        # Заполняем таблицу
        self._refresh_transactions_table()

    # метод обновления таблицы транзакций с учётом фильтров
    def _refresh_transactions_table(self):
        """Перерисовывает строки таблицы с учётом фильтров"""
        # Очищаем содержимое
        for widget in self.transactions_scroll.winfo_children():
            widget.destroy()

        if self.data.empty:
            tk.CTkLabel(
                self.transactions_scroll,
                text="📭 Транзакций пока нет. Добавьте первую!",
                font=tk.CTkFont(size=18),
                text_color="gray"
            ).pack(pady=50)
            return

        # Применяем фильтры
        filtered = self.data.copy()
        filtered = filtered.sort_values('date', ascending=False).reset_index(drop=False)
        filtered = filtered.rename(columns={'index': 'original_index'})

        # Фильтр по типу
        filter_type = self.filter_type_var.get()
        if filter_type != "all":
            filtered = filtered[filtered['type'] == filter_type]

        # Фильтр по описанию
        search_text = self.search_var.get().strip().lower()
        if search_text:
            filtered = filtered[
                filtered['description'].astype(str).str.lower().str.contains(search_text, na=False)
            ]

        if filtered.empty:
            tk.CTkLabel(
                self.transactions_scroll,
                text="🔍 Ничего не найдено по вашему запросу",
                font=tk.CTkFont(size=16),
                text_color="gray"
            ).pack(pady=50)
            return

        # Отрисовка строк
        for row_num, (_, row) in enumerate(filtered.iterrows()):
            # Чередование цвета строк
            row_color = "#F8F9FA" if row_num % 2 == 0 else "#EAECEE"
            row_frame = tk.CTkFrame(self.transactions_scroll, height=45, fg_color=row_color)
            row_frame.pack(fill="x", pady=1)

            for i in range(6):
                row_frame.grid_columnconfigure(i, weight=[5, 15, 35, 15, 12, 18][i])

            # Номер
            tk.CTkLabel(
                row_frame,
                text=str(row_num + 1),
                font=tk.CTkFont(size=13),
                text_color="#555"
            ).grid(row=0, column=0, padx=10, pady=8, sticky="w")

            # Дата
            date_display = pd.to_datetime(row['date']).strftime(Config.DATE_DISPLAY_FORMAT)
            tk.CTkLabel(
                row_frame,
                text=date_display,
                font=tk.CTkFont(size=13),
                text_color="#333"
            ).grid(row=0, column=1, padx=10, pady=8, sticky="w")

            # Описание
            desc = str(row.get('description', '—'))
            if len(desc) > 35:
                desc = desc[:32] + "..."
            tk.CTkLabel(
                row_frame,
                text=desc,
                font=tk.CTkFont(size=13),
                text_color="#333"
            ).grid(row=0, column=2, padx=10, pady=8, sticky="w")

            # Сумма
            value = row['value']
            value_color = "#2E8B57" if value >= 0 else "#DC143C"
            value_prefix = "+" if value >= 0 else ""
            tk.CTkLabel(
                row_frame,
                text=f"{value_prefix}{value:,.0f} ₽",
                font=tk.CTkFont(size=13, weight="bold"),
                text_color=value_color
            ).grid(row=0, column=3, padx=10, pady=8, sticky="w")

            # Тип
            type_text = "📈 Доход" if row['type'] == 'income' else "📉 Расход"
            tk.CTkLabel(
                row_frame,
                text=type_text,
                font=tk.CTkFont(size=12),
                text_color="#555"
            ).grid(row=0, column=4, padx=10, pady=8, sticky="w")

            # Кнопка удаления
            original_idx = row['original_index']
            tk.CTkButton(
                row_frame,
                text="🗑️ Удалить",
                width=90,
                height=30,
                font=tk.CTkFont(size=12),
                fg_color="#DC143C",
                hover_color="#B22222",
                command=lambda idx=original_idx: self._delete_transaction(idx)
            ).grid(row=0, column=5, padx=10, pady=6, sticky="w")

    # метод удаления транзакции по индексу
    def _delete_transaction(self, idx):
        """Удаляет транзакцию по оригинальному индексу в self.data"""
        try:
            if idx in self.data.index:
                self.data = self.data.drop(index=idx).reset_index(drop=True)
                self.save_data()
                self.calculate()
                self.stats()
                self._refresh_transactions_table()
        except Exception as e:
            print(f"Ошибка удаления: {e}")

    # метод сброса фильтров в окне транзакций
    def _reset_filters(self):
        """Сбрасывает все фильтры и обновляет таблицу"""
        self.filter_type_var.set("all")
        self.search_var.set("")
        self._refresh_transactions_table()

    # КНОПКА > АНАЛИТИКА
    # метод окна аналитики с графиками и прогнозами
    def analyze(self):
        self.clear_main_area()

        # ===== ЗАГОЛОВОК =====
        header = tk.CTkFrame(self.main_frame, fg_color="transparent", height=60)
        header.pack(fill="x", padx=30, pady=(20, 10))

        tk.CTkLabel(
            header,
            text="📈 Аналитика и прогнозы",
            font=tk.CTkFont(size=36, weight="bold"),
            text_color="#2C3E50"
        ).pack(side="left")

        # ===== ПЕРЕКЛЮЧАТЕЛЬ ВКЛАДОК =====
        tabs_frame = tk.CTkFrame(self.main_frame, fg_color="transparent", height=50)
        tabs_frame.pack(fill="x", padx=30, pady=(0, 10))

        self.analytics_tab = tk.StringVar(value="overview")

        tab_buttons = [
            ("📊 Обзор", "overview"),
            ("📉 Расходы по категориям", "categories"),
            ("📈 Динамика", "dynamics"),
            ("🔮 Прогноз", "forecast")
        ]

        for text, tab_value in tab_buttons:
            tk.CTkButton(
                tabs_frame,
                text=text,
                font=tk.CTkFont(size=13),
                width=180,
                height=38,
                fg_color="#1E90FF" if self.analytics_tab.get() == tab_value else "#696969",
                hover_color="#4169E1",
                command=lambda v=tab_value: self._switch_analytics_tab(v)
            ).pack(side="left", padx=5, pady=5)

        # ===== КОНТЕЙНЕР ДЛЯ СОДЕРЖИМОГО ВКЛАДКИ =====
        self.analytics_content = tk.CTkFrame(self.main_frame, fg_color="transparent")
        self.analytics_content.pack(fill="both", expand=True, padx=30, pady=(0, 20))

        # Показываем вкладку по умолчанию
        self._show_analytics_overview()

    # метод переключения вкладок аналитики
    def _switch_analytics_tab(self, tab_name):
        """Переключает вкладку аналитики"""
        self.analytics_tab.set(tab_name)

        # Очищаем контент
        for widget in self.analytics_content.winfo_children():
            widget.destroy()

        # Перерисовываем кнопки вкладок (подсветка активной)
        self.analyze()

        # Показываем нужную вкладку
        tab_methods = {
            "overview": self._show_analytics_overview,
            "categories": self._show_analytics_categories,
            "dynamics": self._show_analytics_dynamics,
            "forecast": self._show_analytics_forecast
        }
        tab_methods.get(tab_name, self._show_analytics_overview)()

    # ===== ВКЛАДКА: ОБЗОР =====
    # метод отображения общей статистики
    def _show_analytics_overview(self):
        """Общая статистика: средние, минимумы, максимумы"""
        for widget in self.analytics_content.winfo_children():
            widget.destroy()

        if self.data.empty:
            tk.CTkLabel(
                self.analytics_content,
                text="📭 Недостаточно данных для аналитики.\nДобавьте транзакции!",
                font=tk.CTkFont(size=20),
                text_color="gray"
            ).pack(pady=80)
            return

        # ===== КАРТОЧКИ СО СТАТИСТИКОЙ =====
        cards_frame = tk.CTkFrame(self.analytics_content, fg_color="transparent")
        cards_frame.pack(fill="x", pady=(10, 20))

        incomes = self.data[self.data['type'] == 'income']['value']
        expenses = self.data[self.data['type'] == 'expense']['value'].abs()

        # Средние значения
        avg_income = incomes.mean() if not incomes.empty else 0
        avg_expense = expenses.mean() if not expenses.empty else 0
        max_income = incomes.max() if not incomes.empty else 0
        max_expense = expenses.max() if not expenses.empty else 0
        min_income = incomes.min() if not incomes.empty else 0
        min_expense = expenses.min() if not expenses.empty else 0

        # Количество транзакций по типу
        n_income = len(incomes)
        n_expense = len(expenses)

        stats_data = [
            ("Средний доход", f"{avg_income:,.0f} ₽", "#2E8B57"),
            ("Средний расход", f"{avg_expense:,.0f} ₽", "#DC143C"),
            ("Макс. доход", f"{max_income:,.0f} ₽", "#228B22"),
            ("Макс. расход", f"{max_expense:,.0f} ₽", "#B22222"),
            ("Мин. доход", f"{min_income:,.0f} ₽", "#66CDAA"),
            ("Мин. расход", f"{min_expense:,.0f} ₽", "#CD5C5C"),
            ("Кол-во доходов", str(n_income), "#1E90FF"),
            ("Кол-во расходов", str(n_expense), "#FF6347"),
        ]

        for i, (title, value, color) in enumerate(stats_data):
            cards_frame.grid_columnconfigure(i % 4, weight=1)
            card = tk.CTkFrame(cards_frame, height=90)
            card.grid(row=i // 4, column=i % 4, padx=8, pady=8, sticky="nsew")

            tk.CTkLabel(
                card, text=title,
                font=tk.CTkFont(size=12), text_color="gray"
            ).pack(pady=(12, 4))
            tk.CTkLabel(
                card, text=value,
                font=tk.CTkFont(size=20, weight="bold"), text_color=color
            ).pack(pady=(0, 12))

        # ===== СООТНОШЕНИЕ ДОХОДОВ И РАСХОДОВ =====
        ratio_frame = tk.CTkFrame(self.analytics_content)
        ratio_frame.pack(fill="x", pady=10)

        tk.CTkLabel(
            ratio_frame,
            text="📊 Соотношение доходов и расходов",
            font=tk.CTkFont(size=16, weight="bold")
        ).pack(pady=(15, 10))

        total = self.total_income + self.total_expense
        if total > 0:
            income_pct = self.total_income / total * 100
            expense_pct = self.total_expense / total * 100

            bar_frame = tk.CTkFrame(ratio_frame, fg_color="transparent")
            bar_frame.pack(fill="x", padx=30, pady=(0, 15))

            # Прогресс-бар доходов
            tk.CTkLabel(bar_frame, text=f"Доходы: {income_pct:.1f}%",
                        font=tk.CTkFont(size=13), text_color="#2E8B57").pack(anchor="w")
            income_bar = tk.CTkProgressBar(bar_frame, width=400, height=20)
            income_bar.set(income_pct / 100)
            income_bar.configure(progress_color="#2E8B57")
            income_bar.pack(fill="x", pady=(2, 10))

            # Прогресс-бар расходов
            tk.CTkLabel(bar_frame, text=f"Расходы: {expense_pct:.1f}%",
                        font=tk.CTkFont(size=13), text_color="#DC143C").pack(anchor="w")
            expense_bar = tk.CTkProgressBar(bar_frame, width=400, height=20)
            expense_bar.set(expense_pct / 100)
            expense_bar.configure(progress_color="#DC143C")
            expense_bar.pack(fill="x", pady=(2, 15))

    # ===== ВКЛАДКА: РАСХОДЫ ПО КАТЕГОРИЯМ =====
    # метод отображения круговой диаграммы расходов
    def _show_analytics_categories(self):
        """Круговая диаграмма расходов по описаниям (категориям)"""
        for widget in self.analytics_content.winfo_children():
            widget.destroy()

        expenses = self.data[self.data['type'] == 'expense'].copy()

        if expenses.empty:
            tk.CTkLabel(
                self.analytics_content,
                text="📭 Нет расходов для анализа",
                font=tk.CTkFont(size=20),
                text_color="gray"
            ).pack(pady=80)
            return

        # Группируем по описанию
        expenses['value_abs'] = expenses['value'].abs()
        category_totals = expenses.groupby('description')['value_abs'].sum().sort_values(ascending=False)

        # Топ-7 категорий + "Другое"
        if len(category_totals) > 7:
            top = category_totals.head(7)
            other = category_totals.iloc[7:].sum()
            category_totals = pd.concat([top, pd.Series({'Другое': other})])

        # ===== КРУГОВАЯ ДИАГРАММА =====
        chart_frame = tk.CTkFrame(self.analytics_content)
        chart_frame.pack(fill="both", expand=True, pady=10)

        tk.CTkLabel(
            chart_frame,
            text="🥧 Структура расходов",
            font=tk.CTkFont(size=18, weight="bold")
        ).pack(pady=(15, 5))

        fig = Figure(figsize=(7, 4), dpi=100)
        fig.patch.set_facecolor('#2B2B2B')
        ax = fig.add_subplot(111)

        colors = ['#FF6384', '#36A2EB', '#FFCE56', '#4BC0C0',
                  '#9966FF', '#FF9F40', '#C9CBCF', '#7BC8A4']

        wedges, texts, autotexts = ax.pie(
            category_totals.values,
            labels=category_totals.index,
            autopct='%1.1f%%',
            colors=colors[:len(category_totals)],
            startangle=140,
            textprops={'fontsize': 9, 'color': 'white'}
        )
        for autotext in autotexts:
            autotext.set_fontsize(8)
            autotext.set_color('white')

        ax.set_facecolor('#2B2B2B')
        fig.tight_layout()

        canvas = FigureCanvasTkAgg(fig, master=chart_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True, padx=20, pady=(0, 15))

        # ===== ТАБЛИЦА КАТЕГОРИЙ =====
        table_frame = tk.CTkFrame(self.analytics_content)
        table_frame.pack(fill="x", pady=(0, 10))

        tk.CTkLabel(
            table_frame,
            text="📋 Детализация",
            font=tk.CTkFont(size=16, weight="bold")
        ).pack(pady=(10, 5))

        total_expenses = category_totals.sum()
        for i, (cat, val) in enumerate(category_totals.items()):
            pct = val / total_expenses * 100
            row_color = "#F8F9FA" if i % 2 == 0 else "#EAECEE"
            row = tk.CTkFrame(table_frame, height=35, fg_color=row_color)
            row.pack(fill="x", padx=20, pady=1)

            tk.CTkLabel(row, text=f"● {cat}", font=tk.CTkFont(size=13),
                        text_color=colors[i % len(colors)]).pack(side="left", padx=15, pady=6)
            tk.CTkLabel(row, text=f"{val:,.0f} ₽  ({pct:.1f}%)",
                        font=tk.CTkFont(size=13, weight="bold"),
                        text_color="#333").pack(side="right", padx=15, pady=6)

    # ===== ВКЛАДКА: ДИНАМИКА =====
    # метод отображения линейного графика доходов/расходов по дням
    def _show_analytics_dynamics(self):
        """Линейный график доходов и расходов по дням"""
        for widget in self.analytics_content.winfo_children():
            widget.destroy()

        if self.data.empty:
            tk.CTkLabel(
                self.analytics_content,
                text="📭 Недостаточно данных для построения графика",
                font=tk.CTkFont(size=20),
                text_color="gray"
            ).pack(pady=80)
            return

        chart_frame = tk.CTkFrame(self.analytics_content)
        chart_frame.pack(fill="both", expand=True, pady=10)

        tk.CTkLabel(
            chart_frame,
            text="📈 Динамика доходов и расходов",
            font=tk.CTkFont(size=18, weight="bold")
        ).pack(pady=(15, 5))

        # Подготовка данных: группировка по дате
        df = self.data.copy()
        df['date'] = pd.to_datetime(df['date'])

        income_daily = df[df['type'] == 'income'].groupby(
            df['date'].dt.date)['value'].sum()
        expense_daily = df[df['type'] == 'expense'].groupby(
            df['date'].dt.date)['value'].sum().abs()

        # Объединяем в один DataFrame с заполнением пропусков нулями
        all_dates = pd.date_range(
            start=df['date'].min(),
            end=df['date'].max(),
            freq='D'
        ).date

        income_series = pd.Series(0, index=all_dates)
        expense_series = pd.Series(0, index=all_dates)

        income_series.update(income_daily)
        expense_series.update(expense_daily)

        # Накопительный баланс
        balance_series = (income_series - expense_series).cumsum()

        # ===== ПОСТРОЕНИЕ ГРАФИКА =====
        fig = Figure(figsize=(8, 4), dpi=100)
        fig.patch.set_facecolor('#2B2B2B')
        ax = fig.add_subplot(111)
        ax.set_facecolor('#2B2B2B')

        dates = [datetime.datetime.combine(d, datetime.time()) for d in all_dates]

        ax.fill_between(dates, income_series.values, alpha=0.3, color='#2E8B57')
        ax.plot(dates, income_series.values, color='#2E8B57', linewidth=2, label='Доходы')

        ax.fill_between(dates, expense_series.values, alpha=0.3, color='#DC143C')
        ax.plot(dates, expense_series.values, color='#DC143C', linewidth=2, label='Расходы')

        ax.plot(dates, balance_series.values, color='#1E90FF',
                linewidth=2, linestyle='--', label='Баланс (накопит.)')

        ax.legend(fontsize=9, facecolor='#3B3B3B', edgecolor='gray',
                  labelcolor='white', loc='upper left')
        ax.tick_params(colors='white', labelsize=8)
        ax.spines['bottom'].set_color('gray')
        ax.spines['left'].set_color('gray')
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.yaxis.set_major_formatter(lambda x, _: f'{x:,.0f}')

        # Форматирование оси X
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%d.%m'))
        ax.xaxis.set_major_locator(mdates.AutoDateLocator())
        fig.autofmt_xdate(rotation=45)

        ax.grid(axis='y', alpha=0.2, color='gray')
        fig.tight_layout()

        canvas = FigureCanvasTkAgg(fig, master=chart_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True, padx=20, pady=(0, 15))

    # ===== ВКЛАДКА: ПРОГНОЗ =====
    # метод окна с финансовым прогнозом (сценарии «что если?»)
    def _show_analytics_forecast(self):
        """Прогноз: моделирование сценариев"""
        for widget in self.analytics_content.winfo_children():
            widget.destroy()

        # ===== ОПИСАНИЕ =====
        tk.CTkLabel(
            self.analytics_content,
            text="🔮 Финансовое моделирование",
            font=tk.CTkFont(size=22, weight="bold")
        ).pack(pady=(10, 5))

        tk.CTkLabel(
            self.analytics_content,
            text="Смоделируйте сценарий: как изменится баланс при новых условиях?",
            font=tk.CTkFont(size=14),
            text_color="gray"
        ).pack(pady=(0, 15))

        # ===== ДВЕ КОЛОНКИ: ФОРМА И РЕЗУЛЬТАТ =====
        columns = tk.CTkFrame(self.analytics_content, fg_color="transparent")
        columns.pack(fill="both", expand=True)
        columns.grid_columnconfigure(0, weight=4)
        columns.grid_columnconfigure(1, weight=6)

        # ЛЕВАЯ КОЛОНКА — форма ввода сценария
        form_frame = tk.CTkFrame(columns)
        form_frame.grid(row=0, column=0, padx=(0, 10), pady=5, sticky="nsew")

        tk.CTkLabel(
            form_frame,
            text="⚙️ Параметры сценария",
            font=tk.CTkFont(size=16, weight="bold")
        ).pack(pady=(15, 15))

        # Ежемесячный доход
        tk.CTkLabel(form_frame, text="Ежемесячный доход (₽):",
                    font=tk.CTkFont(size=14)).pack(anchor="w", padx=20)
        self.forecast_income = tk.CTkEntry(
            form_frame, placeholder_text="Например: 50000",
            width=250, height=38, font=tk.CTkFont(size=14)
        )
        self.forecast_income.pack(padx=20, pady=(2, 12))

        # Ежемесячный расход
        tk.CTkLabel(form_frame, text="Ежемесячные расходы (₽):",
                    font=tk.CTkFont(size=14)).pack(anchor="w", padx=20)
        self.forecast_expense = tk.CTkEntry(
            form_frame, placeholder_text="Например: 35000",
            width=250, height=38, font=tk.CTkFont(size=14)
        )
        self.forecast_expense.pack(padx=20, pady=(2, 12))

        # Разовое событие (опционально)
        tk.CTkLabel(form_frame, text="Разовое событие (₽, необязательно):",
                    font=tk.CTkFont(size=14)).pack(anchor="w", padx=20)
        self.forecast_event = tk.CTkEntry(
            form_frame, placeholder_text="Например: -120000 (аренда депозит)",
            width=250, height=38, font=tk.CTkFont(size=14)
        )
        self.forecast_event.pack(padx=20, pady=(2, 12))

        # Месяц разового события
        tk.CTkLabel(form_frame, text="На каком месяце событие (1-12):",
                    font=tk.CTkFont(size=14)).pack(anchor="w", padx=20)
        self.forecast_event_month = tk.CTkEntry(
            form_frame, placeholder_text="Например: 3",
            width=250, height=38, font=tk.CTkFont(size=14)
        )
        self.forecast_event_month.pack(padx=20, pady=(2, 12))

        # Горизонт прогноза
        tk.CTkLabel(form_frame, text="Горизонт прогноза (месяцев):",
                    font=tk.CTkFont(size=14)).pack(anchor="w", padx=20)
        self.forecast_months = tk.CTkEntry(
            form_frame, placeholder_text="Например: 12",
            width=250, height=38, font=tk.CTkFont(size=14)
        )
        self.forecast_months.pack(padx=20, pady=(2, 15))

        # Кнопка расчёта
        tk.CTkButton(
            form_frame,
            text="🚀 Рассчитать прогноз",
            font=tk.CTkFont(size=15, weight="bold"),
            width=250, height=45,
            fg_color="#1E90FF",
            hover_color="#4169E1",
            command=self._run_forecast
        ).pack(padx=20, pady=(5, 20))

        # ПРАВАЯ КОЛОНКА — результат (график + выводы)
        self.forecast_result_frame = tk.CTkFrame(columns)
        self.forecast_result_frame.grid(row=0, column=1, padx=(10, 0), pady=5, sticky="nsew")

        tk.CTkLabel(
            self.forecast_result_frame,
            text="📊 Результат появится здесь",
            font=tk.CTkFont(size=16),
            text_color="gray"
        ).pack(pady=80)

    # метод расчёта и отображения прогноза
    def _run_forecast(self):
        """Рассчитывает прогноз и отображает график"""
        # Очищаем правую колонку
        for widget in self.forecast_result_frame.winfo_children():
            widget.destroy()

        # Валидация
        try:
            monthly_income = float(self.forecast_income.get().strip() or "0")
            monthly_expense = float(self.forecast_expense.get().strip() or "0")
            months = int(self.forecast_months.get().strip() or "12")

            event_str = self.forecast_event.get().strip()
            event_amount = float(event_str) if event_str else 0

            event_month_str = self.forecast_event_month.get().strip()
            event_month = int(event_month_str) if event_month_str else 0

            if months < 1 or months > 120:
                self._forecast_error("Горизонт: от 1 до 120 месяцев")
                return
            if monthly_expense < 0:
                monthly_expense = abs(monthly_expense)

        except ValueError:
            self._forecast_error("Проверьте введённые числа!")
            return

        # ===== РАСЧЁТ =====
        current_balance = self.balance
        balances = [current_balance]
        savings_line = [self.saved]

        monthly_net = monthly_income - monthly_expense

        for m in range(1, months + 1):
            new_balance = balances[-1] + monthly_net
            # Применяем разовое событие
            if m == event_month:
                new_balance += event_amount
            balances.append(new_balance)
            savings_line.append(savings_line[-1])  # сбережения не меняются в прогнозе

        months_range = list(range(0, months + 1))

        # Определяем, когда баланс станет отрицательным
        negative_month = None
        for i, b in enumerate(balances):
            if b < 0:
                negative_month = i
                break

        # ===== ЗАГОЛОВОК РЕЗУЛЬТАТА =====
        tk.CTkLabel(
            self.forecast_result_frame,
            text="📊 Прогноз баланса",
            font=tk.CTkFont(size=18, weight="bold")
        ).pack(pady=(10, 5))

        # ===== ГРАФИК =====
        fig = Figure(figsize=(6, 3.5), dpi=100)
        fig.patch.set_facecolor('#2B2B2B')
        ax = fig.add_subplot(111)
        ax.set_facecolor('#2B2B2B')

        # Основная линия баланса
        ax.plot(months_range, balances, color='#1E90FF', linewidth=2.5, label='Баланс')
        ax.fill_between(months_range, balances, alpha=0.15, color='#1E90FF')

        # Линия нуля
        ax.axhline(y=0, color='#DC143C', linewidth=1, linestyle='--', alpha=0.7, label='Нулевой баланс')

        # Отметка разового события
        if event_amount != 0 and 0 < event_month <= months:
            ax.axvline(x=event_month, color='#FFD700', linewidth=1.5,
                       linestyle=':', alpha=0.8, label=f'Событие (мес. {event_month})')
            ax.scatter([event_month], [balances[event_month]], color='#FFD700', s=80, zorder=5)

        ax.legend(fontsize=8, facecolor='#3B3B3B', edgecolor='gray',
                  labelcolor='white', loc='best')
        ax.set_xlabel('Месяц', fontsize=10, color='white')
        ax.set_ylabel('Баланс (₽)', fontsize=10, color='white')
        ax.tick_params(colors='white', labelsize=8)
        ax.spines['bottom'].set_color('gray')
        ax.spines['left'].set_color('gray')
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.yaxis.set_major_formatter(lambda x, _: f'{x:,.0f}')
        ax.grid(axis='y', alpha=0.2, color='gray')

        fig.tight_layout()

        canvas = FigureCanvasTkAgg(fig, master=self.forecast_result_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=(0, 10))

        # ===== ВЫВОДЫ =====
        summary_frame = tk.CTkFrame(self.forecast_result_frame)
        summary_frame.pack(fill="x", padx=10, pady=(0, 10))

        final_balance = balances[-1]
        final_color = "#2E8B57" if final_balance >= 0 else "#DC143C"

        conclusions = [
            (f"Баланс через {months} мес:", f"{final_balance:,.0f} ₽", final_color),
            (f"Ежемесячный итог:", f"{monthly_net:+,.0f} ₽",
             "#2E8B57" if monthly_net >= 0 else "#DC143C"),
        ]

        if event_amount != 0:
            conclusions.append(
                (f"Разовое событие (мес. {event_month}):",
                 f"{event_amount:+,.0f} ₽",
                 "#FFD700")
            )

        if negative_month is not None:
            conclusions.append(
                ("⚠️ Баланс уйдёт в минус на:", f"месяце {negative_month}", "#DC143C")
            )
        else:
            conclusions.append(
                ("✅ Баланс остаётся положительным", "весь период", "#2E8B57")
            )

        for title, value, color in conclusions:
            row = tk.CTkFrame(summary_frame, fg_color="transparent")
            row.pack(fill="x", padx=15, pady=3)
            tk.CTkLabel(row, text=title, font=tk.CTkFont(size=13),
                        text_color="gray").pack(side="left")
            tk.CTkLabel(row, text=value, font=tk.CTkFont(size=13, weight="bold"),
                        text_color=color).pack(side="right")

    # метод отображения ошибки прогноза
    def _forecast_error(self, text):
        """Показывает ошибку в области прогноза"""
        for widget in self.forecast_result_frame.winfo_children():
            widget.destroy()
        tk.CTkLabel(
            self.forecast_result_frame,
            text=f"❌ {text}",
            font=tk.CTkFont(size=16, weight="bold"),
            text_color="#DC143C"
        ).pack(pady=80)

    # УКАЗАНИЯ ПОЛЬЗОВАТЕЛЮ
    # универсальный метод указаний пользователю о чём-либо
    def show_message_in(self, text, msg_type='info', parent=None):
        """Универсальный метод отображения сообщений в любом контейнере"""
        if parent is None:
            parent = self.main_frame

        color_map = {
            "success": "#2E8B57",
            "error": "#DC143C",
            "info": "#1E90FF"
        }

        # Удаляем предыдущее сообщение в этом контейнере, если есть
        attr_name = f'_msg_label_{id(parent)}'
        if hasattr(self, attr_name):
            old_label = getattr(self, attr_name)
            if old_label.winfo_exists():
                old_label.destroy()

        label = tk.CTkLabel(
            parent,
            text=text,
            text_color="white",
            font=tk.CTkFont(size=16, weight="bold"),
            fg_color=color_map.get(msg_type, "#1E90FF"),
            corner_radius=5,
            height=40
        )
        label.pack(pady=(10, 0), padx=5, fill="x")
        setattr(self, attr_name, label)

        # Автоматически скрываем через 3 секунды
        self.app.after(3000, lambda: label.destroy() if label.winfo_exists() else None)

    # обратная совместимость для формы добавления (grid-контейнер)
    def show_message(self, text, msg_type='info'):
        """Сообщение в форме добавления транзакции (использует grid)"""
        color_map = {
            "success": "#2E8B57",
            "error": "#DC143C",
            "info": "#1E90FF"
        }
        if hasattr(self, 'message_label') and self.message_label.winfo_exists():
            self.message_label.destroy()

        self.message_label = tk.CTkLabel(
            self.addframe,
            text=text,
            text_color="white",
            font=tk.CTkFont(size=20, weight="bold"),
            fg_color=color_map.get(msg_type, "#1E90FF"),
            corner_radius=5
        )
        self.message_label.grid(row=9, column=0, sticky="nw", pady=(10, 0), padx=(60, 0))

        self.app.after(3000, lambda: self.message_label.destroy()
                       if hasattr(self, 'message_label') and self.message_label.winfo_exists()
                       else None)

    # метод стирания полей после взаимодействия
    def clear_form_fields(self):
        """Очищает поля формы"""
        self.entry_date.delete(0, 'end')
        self.entry_disc.delete(0, 'end')
        self.entry_value.delete(0, 'end')

    def clear_savings_form(self):
        if hasattr(self, 'savings_entry_date') and self.savings_entry_date.winfo_exists():
            self.savings_entry_date.delete(0, 'end')
        if hasattr(self, 'savings_amount_entry') and self.savings_amount_entry.winfo_exists():
            self.savings_amount_entry.delete(0, 'end')

    # ПОЛУЧЕНИЕ ДАННЫХ
    # метод получения данных из таблицы .csv
    def getdata(self):
        # Загрузка основных данных
        self.data = self._load_csv(
            Config.DATA_FILE,
            ['date', 'value', 'description', 'type']
        )
        # Загрузка сбережений
        self.savings = self._load_csv(
            Config.SAVINGS_FILE,
            ['date', 'value', 'type']
        )
        self.calculate()

    def _load_csv(self, filepath, required_columns):
        """Безопасная загрузка CSV с валидацией"""
        try:
            df = pd.read_csv(filepath)

            # Проверяем наличие обязательных колонок
            missing = set(required_columns) - set(df.columns)
            if missing:
                print(f"Внимание: в {filepath} отсутствуют колонки {missing}. Создаю новый файл.")
                df = pd.DataFrame(columns=required_columns)
                df.to_csv(filepath, index=False)
                return df

            # Парсим дату с явным форматом
            df['date'] = pd.to_datetime(df['date'], format=Config.DATE_STORAGE_FORMAT, errors='coerce')

            # Проверяем, есть ли невалидные даты
            bad_dates = df['date'].isna().sum()
            if bad_dates > 0:
                print(f"Внимание: {bad_dates} записей с некорректной датой в {filepath}.")
                df = df.dropna(subset=['date'])

            # Проверяем числовые значения
            df['value'] = pd.to_numeric(df['value'], errors='coerce')
            bad_values = df['value'].isna().sum()
            if bad_values > 0:
                print(f"Внимание: {bad_values} записей с некорректной суммой в {filepath}.")
                df = df.dropna(subset=['value'])

            return df

        except FileNotFoundError:
            df = pd.DataFrame(columns=required_columns)
            df.to_csv(filepath, index=False)
            return df

        except pd.errors.ParserError:
            print(f"Ошибка: файл {filepath} повреждён. Создаю резервную копию.")
            backup_path = filepath + '.backup'
            if os.path.exists(filepath):
                os.rename(filepath, backup_path)
            df = pd.DataFrame(columns=required_columns)
            df.to_csv(filepath, index=False)
            return df

        except Exception as e:
            print(f"Непредвиденная ошибка при загрузке {filepath}: {e}")
            df = pd.DataFrame(columns=required_columns)
            return df

    # метод записывания данных из таблицы .csv в переменные программы
    def calculate(self):
        """Считает баланс, доходы, расходы"""
        if not self.data.empty:
            self.balance = self.data['value'].sum()
            self.total_income = self.data[self.data['type'] == 'income']['value'].sum()
            self.total_expense = abs(self.data[self.data['type'] == 'expense']['value'].sum())
        else:
            self.balance = 0
            self.total_income = 0
            self.total_expense = 0
        if not self.savings.empty:
            self.saved = self.savings['value'].sum()
            self.total_income_savings = self.savings[self.savings['type'] == 'income']['value'].sum()
            self.total_expense_savings = abs(self.savings[self.savings['type'] == 'expense']['value'].sum())
        else:
            self.saved = 0
            self.total_income_savings = 0
            self.total_expense_savings = 0

    # метод записи данных в таблицу .csv
    def save_data(self):
        """Сохраняет данные в CSV файлы с атомарной записью"""
        try:
            self._save_csv(self.data, Config.DATA_FILE)
            self._save_csv(self.savings, Config.SAVINGS_FILE)
        except Exception as e:
            print(f"Ошибка сохранения данных: {e}")

    def _save_csv(self, df, filepath):
        """Атомарное сохранение DataFrame в CSV"""
        if df is None:
            df = pd.DataFrame()

        temp_path = filepath + '.tmp'
        data_to_save = df.copy()

        # Сохраняем дату в едином формате
        if 'date' in data_to_save.columns and not data_to_save.empty:
            data_to_save['date'] = pd.to_datetime(data_to_save['date']).dt.strftime(Config.DATE_STORAGE_FORMAT)

        data_to_save.to_csv(temp_path, index=False, encoding='utf-8')
        os.replace(temp_path, filepath)


t = tApp('Финансы', '1480x800')