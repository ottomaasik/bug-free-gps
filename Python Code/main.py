import serial
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from collections import deque

# Adjust to your COM port and baudrate
ser = serial.Serial('COM6', 115200, timeout=1)  # Replace COMx with your port (e.g. COM5 or /dev/ttyACM0)

pressure_data = deque(maxlen=100)  # Rolling buffer of latest 100 values

fig, ax = plt.subplots()
line, = ax.plot([], [], lw=2)
ax.set_ylim(1000, 1020)
ax.set_xlim(0, 100)
ax.set_xlabel('Sample')
ax.set_ylabel('Pressure (hPa)')
ax.set_title('Live Pressure from LPS22HH')

def update(frame):
    line.set_ydata(pressure_data)
    line.set_xdata(range(len(pressure_data)))
    try:
        line_str = ser.readline().decode().strip()
        pressure = float(line_str)
        pressure_data.append(pressure)
    except:
        pass
    return line,

ani = animation.FuncAnimation(fig, update, interval=200, blit=True)
plt.tight_layout()
plt.show()
