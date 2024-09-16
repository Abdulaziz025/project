import serial
import RPi.GPIO as GPIO
from time import sleep

# Настройка GPIO
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BOARD)
GPIO.setup(8, GPIO.OUT, initial=GPIO.LOW)   # Управление клапаном или другим устройством
GPIO.setup(3, GPIO.IN)  # Кнопка старта
GPIO.setup(5, GPIO.IN)  # Кнопка аварийной остановки

# Настройка последовательного порта для связи с HPLC насосом
ser = serial.Serial(
    port='/dev/ttyUSB0',  # Убедитесь, что это правильный порт
    baudrate=4800,        # Скорость, указанная в спецификации
    timeout=1,            # Таймаут для получения данных
    parity=serial.PARITY_EVEN,
    stopbits=serial.STOPBITS_ONE,
    bytesize=serial.EIGHTBITS
)

# Пример команды для запуска насоса (в зависимости от протокола)
start_command = [0xF8, 0x55, 0xCE, 0x01, 0x00, 0x23, 0x00, 0x00]  # Возможно, нужно уточнить протокол

# Конвертация команды в байтовый массив
byte_array = bytearray(start_command)

while True:
    # Если нажата кнопка старта, отправляем команду на старт насоса
    if GPIO.input(3) == True:
        print("Starting the pump...")
        ser.write(byte_array)  # Отправка команды для запуска насоса
        sleep(1)

        # Чтение данных от насоса
        response = ser.read(16)  # Чтение ответа (16 байт - пример, возможно нужно изменить)
        print("Response from pump: ", response)

        # Пример обработки ответа, в зависимости от протокола
        if len(response) >= 10:
            pressure_bytes = response[6:10]  # Предполагаем, что 6-9 байт содержат данные о давлении
            pressure = int.from_bytes(pressure_bytes, byteorder='little')
            print(f"Current pressure: {pressure} MPa")

            # Если давление превышает 42 MPa (максимальное), выключаем насос
            if pressure > 42:
                print("Pressure too high! Stopping the pump.")
                GPIO.output(8, GPIO.LOW)  # Остановка насоса или закрытие клапана

    # Аварийная остановка
    if GPIO.input(5) == True:
        print("Emergency stop activated!")
        GPIO.output(8, GPIO.LOW)  # Остановка насоса

    sleep(1)  # Задержка перед следующей итерацией цикла

ser.close()
