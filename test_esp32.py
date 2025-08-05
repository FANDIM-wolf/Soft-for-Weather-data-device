import serial
import time

# === НАСТРОЙКИ ===
PORT = 'COM4'
BAUD_RATE = 115200
INTERVAL = 7

# === КОД ===
try:
    ser = serial.Serial(PORT, BAUD_RATE, timeout=1.0)
    print(f"✅ Подключено к {PORT} со скоростью {BAUD_RATE} бод\n")

    # Пропускаем начальные данные (приветствие)
    time.sleep(2)
    while ser.in_waiting:
        ser.readline()  # Очищаем буфер

    while True:
        # Отправляем команду
        ser.write(b"read\n")
        print(f"📤 Отправлено: read")

        # Ждём немного, чтобы ESP32 успел ответить
        time.sleep(0.5)

        # Читаем ВСЁ, что пришло
        responses = []
        while ser.in_waiting:
            line = ser.readline().decode('utf-8', errors='replace').strip()
            if line:
                responses.append(line)

        # Обрабатываем ответы
        if responses:
            for resp in responses:
                print(f"📥 Получено: {resp}")
        else:
            print("⚠️  Нет ответа")

        # Ожидание до следующей отправки
        for i in range(INTERVAL):
            print(f"⏳ Ожидание... {INTERVAL - i} с", end="\r")
            time.sleep(1)
        print()

except serial.SerialException as e:
    print(f"❌ Ошибка подключения к порту: {e}")
except KeyboardInterrupt:
    print("\n\n🛑 Тест остановлен пользователем.")
    ser.close()