import sys
import csv
from PyQt6.QtWidgets import (
    QApplication, QWidget, QHBoxLayout, QVBoxLayout, QTableWidget, QLabel,
    QLineEdit, QPushButton, QTableWidgetItem, QMessageBox, QHeaderView
)
from PyQt6.QtCore import Qt
from datetime import datetime, timedelta
from timer_manager import TimerManager
from esp32_manager import ESP32Manager

class MyApp(QWidget):
    def __init__(self):
        """Initialize the main application window"""
        super().__init__()
        self.data_file = 'data_file.csv'
        self.datas_file = 'datas.csv'
        self.data_timer = None
        self.interval_seconds = 0  # Store interval for later use
        self.gpio_columns = set()  # Track used GPIO columns

        # Initialize ESP32 manager
        self.esp32 = ESP32Manager(port='COM4', baud_rate=115200)

        self.initUI()
        self.load_csv_data(self.data_file)

    def initUI(self):
        """Setup the user interface"""
        self.setStyleSheet("font-family: Arial; background-color: white;")
        main_layout = QHBoxLayout()

        # Left part - data table
        left_layout = QVBoxLayout()
        self.table = QTableWidget()
        self.setup_table()
        left_label = QLabel("Полученные данные")
        left_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        left_label.setStyleSheet("font-weight: bold; font-size: 14pt;")
        left_layout.addWidget(left_label)
        left_layout.addWidget(self.table)

        # Right part - control panel
        right_layout = QVBoxLayout()
        right_layout.setSpacing(15)

        # Interval setting group
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

        # Button styling
        button_style = """
            border: 1px solid black;
            padding: 12px 18px;
            font-size: 12pt;
            min-width: 120px;
        """

        apply_btn = QPushButton("Применить")
        apply_btn.setStyleSheet(f"""
            {button_style}
            background-color: {'#4CAF50' if self.esp32.is_connected() else 'red'};
            color: white;
        """)

        start_btn = QPushButton("Старт")
        start_btn.setStyleSheet(f"""
            {button_style}
            background-color: {'green' if self.esp32.is_connected() else '#cccccc'};
            color: white;
        """)

        stop_btn = QPushButton("Стоп")
        stop_btn.setStyleSheet(button_style)
        save_btn = QPushButton("Сохранить")
        save_btn.setStyleSheet(button_style)
        clear_btn = QPushButton("Очистить")
        clear_btn.setStyleSheet(button_style)

        # Add elements to layout
        right_layout.addLayout(step_group)
        right_layout.addWidget(apply_btn)
        right_layout.addWidget(start_btn)
        right_layout.addSpacing(20)
        right_layout.addWidget(stop_btn)
        right_layout.addWidget(save_btn)
        right_layout.addWidget(clear_btn)

        # Connect signals
        apply_btn.clicked.connect(self.apply_clicked)
        start_btn.clicked.connect(self.start_clicked)
        stop_btn.clicked.connect(self.stop_clicked)
        save_btn.clicked.connect(self.save_clicked)
        clear_btn.clicked.connect(self.clear_clicked)

        main_layout.addLayout(left_layout)
        main_layout.addLayout(right_layout)
        self.setLayout(main_layout)

        self.setWindowTitle('Data Processing App')
        self.setGeometry(100, 100, 1000, 600)
        self.show()

    def setup_table(self):
        """Configure the data table appearance"""
        self.table.setStyleSheet("""
            QTableWidget{
                border: 2px solid black;
                gridline-color: black;
                background-color: #f5f5f5;
            }
            QTableWidget::item{
                border-bottom: 1px solid #ccc;
                border-right: 1px solid #ccc;
                padding: 5px;
            }
            QTableWidget::item:selected{
                background-color: #e0f0ff;
                color: black;
            }
            QHeaderView::section{
                background-color: #d3d3d3;
                padding: 8px;
                border: 1px solid black;
                font-weight: bold;
            }
        """)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.verticalHeader().setVisible(False)

        # Initialize basic columns
        self.table.setColumnCount(2)
        self.table.setHorizontalHeaderLabels(["Date", "Time"])

    def load_csv_data(self, filename='data_file.csv'):
        """Load data from CSV file with ';' delimiter"""
        try:
            with open(filename, 'r', encoding='utf-8') as file:
                reader = csv.reader(file, delimiter=';')
                data = list(reader)
                if data:
                    headers = data[0]
                    rows = data[1:]

                    # Check if GPIO columns exist in headers
                    for header in headers:
                        if header.startswith("GPIO"):
                            self.gpio_columns.add(header)

                    # Update table headers if GPIO columns found
                    if self.gpio_columns:
                        self.update_table_headers()

                    self.table.setColumnCount(len(headers))
                    self.table.setHorizontalHeaderLabels(headers)
                    self.table.setRowCount(len(rows))

                    for i, row in enumerate(rows):
                        for j, item in enumerate(row):
                            self.table.setItem(i, j, QTableWidgetItem(item))

                    self.table.resizeColumnsToContents()
                    self.table.resizeRowsToContents()
        except FileNotFoundError:
            print(f"File {filename} not found")
        except Exception as e:
            print(f"Error reading file: {e}")

    def save_data_to_file(self, filename=None):
        """Save data to CSV file"""
        if filename is None:
            filename = self.datas_file
        try:
            with open(filename, 'w', newline='', encoding='utf-8') as file:
                writer = csv.writer(file, delimiter=';')
                headers = [self.table.horizontalHeaderItem(i).text() for i in range(self.table.columnCount())]
                writer.writerow(headers)
                for i in range(self.table.rowCount()):
                    row = [self.table.item(i, j).text() if self.table.item(i, j) else '' for j in range(self.table.columnCount())]
                    writer.writerow(row)
        except Exception as e:
            print(f"Error saving file: {e}")

    def apply_clicked(self):
        """Handle 'Apply' button click - set the time interval"""
        try:
            time_str = self.time_edit.text().strip()
            if not time_str:
                raise ValueError("Time input field is empty")
            t = datetime.strptime(time_str, "%H:%M:%S")
            self.interval_seconds = timedelta(hours=t.hour, minutes=t.minute, seconds=t.second).total_seconds()

            # Clear time input error style
            self.time_edit.setStyleSheet(self.time_edit.styleSheet().replace("border: 2px solid red;", ""))

            # Check ESP32 connection
            if not self.esp32.is_connected():
                QMessageBox.warning(self, "Error", "No connection to ESP32. Check device connection.")
                return

            QMessageBox.information(self, "Interval set", f"Interval {time_str} saved. Click 'Start' to begin data collection.")

        except ValueError as e:
            print(f"Time format error: {e}")
            # Visual indication of error
            self.time_edit.setStyleSheet(self.time_edit.styleSheet() + "border: 2px solid red;")

    def start_clicked(self):
        """Start data collection from ESP32"""
        # Check if interval is set
        if self.interval_seconds <= 0:
            QMessageBox.warning(self, "Error", "First set interval using 'Apply' button")
            return

        # Check ESP32 connection
        if not self.esp32.is_connected():
            if not self.esp32.connect():
                QMessageBox.warning(self, "Error", "Failed to connect to ESP32")
                return

        # Stop previous timer if exists
        if self.data_timer:
            self.data_timer.stop()
            self.data_timer = None

        # Create and start new timer for ESP32 data requests
        self.data_timer = TimerManager(
            interval_ms=int(self.interval_seconds * 1000),
            callback=self.request_sensor_data
        )
        self.data_timer.start()

        QMessageBox.information(self, "Start", f"Data collection started. Interval: {self.interval_seconds} seconds")

    def request_sensor_data(self):
        """Request data from ESP32 and add to table"""
        sensor_data = self.esp32.read_sensor_data()

        if sensor_data is not None:
            # Update GPIO columns list
            new_columns = False
            for gpio in sensor_data.keys():
                if gpio not in self.gpio_columns:
                    self.gpio_columns.add(gpio)
                    new_columns = True

            # Update headers if new columns added
            if new_columns:
                self.update_table_headers()

            # Add data to table
            self.add_data_to_table(sensor_data)
            print(f"✅ Data added: {sensor_data}")
        else:
            print("⚠️  No data received from ESP32")

    def update_table_headers(self):
        """Update table headers with new GPIO columns"""
        headers = ["Date", "Time"] + sorted(list(self.gpio_columns))
        self.table.setColumnCount(len(headers))
        self.table.setHorizontalHeaderLabels(headers)

    def add_data_to_table(self, sensor_data):
        """Add a data row to the table"""
        # Get current date and time
        now = datetime.now()
        date_str = now.strftime("%d.%m.%Y")
        time_str = now.strftime("%H:%M:%S")

        # Format data row
        data_row = [date_str, time_str]
        for gpio in sorted(self.gpio_columns):
            data_row.append(sensor_data.get(gpio, ""))

        # Add data to table
        row_position = self.table.rowCount()
        self.table.insertRow(row_position)

        for col, item in enumerate(data_row):
            self.table.setItem(row_position, col, QTableWidgetItem(str(item)))

        self.table.resizeColumnsToContents()

    def stop_clicked(self):
        """Stop timer and display message"""
        if self.data_timer:
            self.data_timer.stop()
            self.data_timer = None
        QMessageBox.information(self, "Completion", "Data collection stopped")

    def save_clicked(self):
        """Save data to file"""
        self.save_data_to_file()
        QMessageBox.information(self, "Save", "Data successfully saved")

    def clear_clicked(self):
        """Clear table data"""
        if self.data_timer:
            self.data_timer.stop()
            self.data_timer = None
        self.table.setRowCount(0)
        self.gpio_columns = set()
        self.update_table_headers()
        self.time_edit.setStyleSheet(self.time_edit.styleSheet().replace("border: 2px solid red;", ""))


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MyApp()
    sys.exit(app.exec())