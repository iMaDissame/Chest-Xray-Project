
import serial

ser = serial.Serial('COM3', 115200, timeout=1)  # Replace 'COM3' with your actual port
ser.flush()

while True:
    if ser.in_waiting > 0:
        line = ser.readline().decode('utf-8').strip()
        print("Received:", line)
