import serial
import time
import re
from datetime import datetime

class ESP32Manager:
    def __init__(self, port='COM4', baud_rate=115200, timeout=1.0):
        """Initialize the ESP32 manager with connection parameters"""
        self.port = port
        self.baud_rate = baud_rate
        self.timeout = timeout
        self.ser = None
        self.connected = False

        self.connect()

    def connect(self):
        """Establish connection with ESP32"""
        try:
            # Close existing connection if open
            if self.ser and self.ser.is_open:
                self.ser.close()

            # Attempt to connect to ESP32
            self.ser = serial.Serial(self.port, self.baud_rate, timeout=self.timeout)
            print(f"✅ Connected to ESP32 on port {self.port}")

            # Allow time for initialization
            time.sleep(2)

            # Clear input buffer
            while self.ser.in_waiting:
                self.ser.readline()

            self.connected = True
            return True

        except serial.SerialException as e:
            print(f"❌ ESP32 connection error: {e}")
            self.connected = False
            return False

    def disconnect(self):
        """Disconnect from ESP32"""
        if self.ser and self.ser.is_open:
            self.ser.close()
        self.connected = False
        print("🔌 Disconnected from ESP32")

    def read_sensor_data(self):
        """Read sensor data from ESP32 in format :gpio X Y,...,gpio X Y;"""
        if not self.connected:
            return None

        try:
            # Look for data start symbol ':'
            while self.connected:
                if self.ser.in_waiting:
                    line = self.ser.readline().decode('utf-8', errors='replace').strip()
                    if line == ':':
                        break
                    # Small delay to prevent CPU overload
                    time.sleep(0.01)

            # Collect data until symbol ';'
            data_lines = []
            while self.connected:
                if self.ser.in_waiting:
                    line = self.ser.readline().decode('utf-8', errors='replace').strip()
                    if line == ';':
                        break
                    elif line and line != ',':
                        data_lines.append(line)
                # Small delay to prevent CPU overload
                time.sleep(0.01)

            # Process collected data
            sensor_data = {}
            for line in data_lines:
                # Look for pattern "gpio X Y"
                match = re.match(r'gpio\s+(\d+)\s+(\d+)', line)
                if match:
                    gpio_num = match.group(1)
                    value = match.group(2)
                    sensor_data[f"GPIO{gpio_num}"] = value

            if sensor_data:
                return sensor_data

            return None

        except Exception as e:
            print(f"❌ Error reading data: {e}")
            self.connected = False
            return None

    def is_connected(self):
        """Check if connected to ESP32"""
        return self.connected