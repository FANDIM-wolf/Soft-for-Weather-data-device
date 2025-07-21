import sys
import csv
import os
from PyQt6.QtWidgets import (QApplication, QWidget, QHBoxLayout, QVBoxLayout,
                             QTableWidget, QLabel, QLineEdit, QPushButton,
                             QTableWidgetItem, QMessageBox, QHeaderView)
from PyQt6.QtCore import Qt, QTimer
from datetime import datetime, timedelta
from timer_manager import TimerManager
class MyApp(QWidget):
    def __init__(self):
        super().__init__()
        self.data_file = 'data_file.csv'
        self.datas_file = 'datas.csv'
        self.data_timer = None  # Добавьте это в __init__
        self.initUI()
        self.load_csv_data(self.data_file)

    def initUI(self):
        self.setStyleSheet("font-family: Arial; background-color: white;")
        main_layout = QHBoxLayout()

        # Левая часть - таблица
        left_layout = QVBoxLayout()
        self.table = QTableWidget()
        self.setup_table()

        left_label = QLabel("Полученные данные")
        left_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        left_label.setStyleSheet("font-weight: bold; font-size: 14pt;")

        left_layout.addWidget(left_label)
        left_layout.addWidget(self.table)

        # Правая часть - элементы управления
        right_layout = QVBoxLayout()
        right_layout.setSpacing(15)

        # Группа "Шаг"
        step_group = QHBoxLayout()
        step_group.setSpacing(10)

        time_label = QLabel("Шаг")
        time_label.setStyleSheet("font-size: 14pt;")
        time_label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)

        self.time_edit = QLineEdit()
        self.time_edit.setPlaceholderText("hh:mm:ss")
        self.time_edit.setStyleSheet("""
            border: 1px solid gray;
            padding: 5px;
            font-size: 12pt;
            min-width: 120px;
        """)

        step_group.addWidget(time_label)
        step_group.addWidget(self.time_edit)

        # Стилизация кнопок
        button_style = """
            border: 1px solid black;
            padding: 12px 18px;
            font-size: 12pt;
            min-width: 120px;
        """

        apply_btn = QPushButton("Применить")
        apply_btn.setStyleSheet(f"""
            {button_style}
            background-color: red;
            color: white;
        """)

        start_btn = QPushButton("Старт")
        start_btn.setStyleSheet(f"""
            {button_style}
            background-color: green;
            color: white;
        """)

        stop_btn = QPushButton("Стоп")
        stop_btn.setStyleSheet(button_style)

        save_btn = QPushButton("Сохранить")
        save_btn.setStyleSheet(button_style)

        clear_btn = QPushButton("Очистить")
        clear_btn.setStyleSheet(button_style)

        # Добавление элементов
        right_layout.addLayout(step_group)
        right_layout.addWidget(apply_btn)
        right_layout.addWidget(start_btn)
        right_layout.addSpacing(20)
        right_layout.addWidget(stop_btn)
        right_layout.addWidget(save_btn)
        right_layout.addWidget(clear_btn)

        # Сигналы
        apply_btn.clicked.connect(self.apply_clicked)
        start_btn.clicked.connect(self.start_clicked)
        stop_btn.clicked.connect(self.stop_clicked)
        save_btn.clicked.connect(self.save_clicked)
        clear_btn.clicked.connect(self.clear_clicked)

        main_layout.addLayout(left_layout)
        main_layout.addLayout(right_layout)

        self.setLayout(main_layout)
        self.setWindowTitle('Data Processing App')
        self.setGeometry(100, 100, 950, 600)
        self.show()

    def setup_table(self):
        """Настройка таблицы"""
        self.table.setStyleSheet("""
            QTableWidget {
                border: 2px solid black;
                gridline-color: black;
                background-color: #f5f5f5;
            }
            QTableWidget::item {
                border-bottom: 1px solid #ccc;
                border-right: 1px solid #ccc;
                padding: 5px;
            }
            QTableWidget::item:selected {
                background-color: #e0f0ff;
                color: black;
            }
            QHeaderView::section {
                background-color: #d3d3d3;
                padding: 8px;
                border: 1px solid black;
                font-weight: bold;
            }
        """)

        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.verticalHeader().setVisible(False)

    def load_csv_data(self, filename='data_file.csv'):
        """Загрузка данных из CSV файла с разделителем ';'"""
        try:
            with open(filename, 'r', encoding='utf-8') as file:
                reader = csv.reader(file, delimiter=';')
                data = list(reader)

            if data:
                headers = data[0]
                rows = data[1:]

                self.table.setColumnCount(len(headers))
                self.table.setHorizontalHeaderLabels(headers)
                self.table.setRowCount(len(rows))

                for i, row in enumerate(rows):
                    for j, item in enumerate(row):
                        self.table.setItem(i, j, QTableWidgetItem(item))

            self.table.resizeColumnsToContents()
            self.table.resizeRowsToContents()

        except FileNotFoundError:
            print(f"Файл {filename} не найден")
        except Exception as e:
            print(f"Ошибка чтения файла: {e}")

    def save_data_to_file(self, filename=None):
        """Сохранение данных в CSV файл"""
        if filename is None:
            filename = self.datas_file

        try:
            with open(filename, 'w', newline='', encoding='utf-8') as file:
                writer = csv.writer(file, delimiter=';')

                # Записываем заголовки
                headers = [self.table.horizontalHeaderItem(i).text() for i in range(self.table.columnCount())]
                writer.writerow(headers)

                # Записываем данные
                for i in range(self.table.rowCount()):
                    row = [self.table.item(i, j).text() if self.table.item(i, j) else ''
                           for j in range(self.table.columnCount())]
                    writer.writerow(row)
        except Exception as e:
            print(f"Ошибка сохранения файла: {e}")

    def apply_clicked(self):
        """Обработка нажатия на кнопку Применить"""

        """Обработка нажатия на кнопку Применить"""
        try:
            time_str = self.time_edit.text().strip()
            if not time_str:
                raise ValueError("Поле ввода времени пустое")

            t = datetime.strptime(time_str, "%H:%M:%S")
            interval_seconds = timedelta(hours=t.hour, minutes=t.minute, seconds=t.second).total_seconds()

            # Остановка предыдущего таймера, если он был
            if self.data_timer:
                self.data_timer.stop()
                self.data_timer = None

            # Создание и запуск нового таймера через TimerManager
            self.data_timer = TimerManager(
                interval_ms=int(interval_seconds * 1000),
                callback=self.remove_last_row
            )
            self.data_timer.start()

            # Сброс ошибки ввода времени
            self.time_edit.setStyleSheet(self.time_edit.styleSheet().replace("border: 2px solid red;", ""))

        except ValueError as e:
            print(f"Ошибка формата времени: {e}")
            # Визуальное обозначение ошибки
            self.time_edit.setStyleSheet(self.time_edit.styleSheet() + "border: 2px solid red;")


    def remove_last_row(self):
        """Удаление последней строки из таблицы"""
        row_count = self.table.rowCount()
        if row_count > 0:
            self.table.removeRow(row_count - 1)

    def stop_clicked(self):
        """Остановка таймера и вывод сообщения"""
        """Остановка таймера и вывод сообщения"""
        if self.data_timer:
            self.data_timer.stop()
            self.data_timer = None

        QMessageBox.information(self, "Завершение", "Сбор данных окончен")

    def save_clicked(self):
        """Сохранение данных в файл"""
        self.save_data_to_file()
        QMessageBox.information(self, "Сохранение", "Данные успешно сохранены")

    def clear_clicked(self):
        """Очистка таблицы"""
        if self.data_timer:
            self.data_timer.stop()
            self.data_timer = None

        self.table.setRowCount(0)
        self.time_edit.setStyleSheet(self.time_edit.styleSheet().replace("border: 2px solid red;", ""))

    def start_clicked(self):
        """Запуск генерации тестовых данных"""
        test_data = [
            ["12.04.2022", "20:00:00", "32", "32", "25", "23", "14", "12"],
            ["12.04.2022", "21:00:00", "31", "33", "24", "22", "15", "11"]
        ]

        # Проверка наличия заголовков
        headers = [self.table.horizontalHeaderItem(i).text() for i in range(self.table.columnCount())]
        if not headers or headers == ['']:
            headers = ["data", "time", "T1", "T2", "T3", "T4", "H1", "H2"]
            self.table.setColumnCount(len(headers))
            self.table.setHorizontalHeaderLabels(headers)

        # Добавление тестовых данных
        start_row = self.table.rowCount()
        self.table.setRowCount(start_row + len(test_data))

        for i, row in enumerate(test_data):
            for j, item in enumerate(row):
                self.table.setItem(start_row + i, j, QTableWidgetItem(item))

        self.table.resizeColumnsToContents()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MyApp()
    sys.exit(app.exec())