import pyaudio
import numpy
import math
import matplotlib.pyplot as plt
import matplotlib.animation
from multiprocessing import Process
import RPi.GPIO as GPIO
import time 

High = 38
Mid = 31
Low = 40


RATE = 44100
BUFFER = 1024

p = pyaudio.PyAudio()
p.get_default_input_device_info()
stream = p.open(
    format = pyaudio.paFloat32,
    channels = 1,
    rate = RATE,
    input = True,
    output = False,
    frames_per_buffer = BUFFER
)

fig = plt.figure()
line1 = plt.plot([],[])[0]
line2 = plt.plot([],[])[0]

r = range(0,int(RATE/2+1),int(RATE/BUFFER))
l = len(r)

def init_line():
        line1.set_data(r, [-1000]*l)
        line2.set_data(r, [-1000]*l)
        return (line1,line2,)
# def grab():
#         time.sleep(3)
#         print(line1.get_data())
#         # return (line1,line2,)
def update_line(i):
    data = numpy.fft.rfft(numpy.fromstring(
        stream.read(BUFFER, exception_on_overflow = False), dtype=numpy.float32)
    )
    data = numpy.log10(numpy.sqrt(
        numpy.real(data)**2+numpy.imag(data)**2) / BUFFER) * 10
    line1.set_data(r, data)
    line2.set_data(numpy.maximum(line1.get_data(), line2.get_data()))
    # print(data[0])
    GPIO.output([Low, Mid, High],0)
    if data[0] > -10:
        print("red")
        GPIO.output(High,1)
    elif data[0] <-10 and data[0]>-30:
        print("amber")
        GPIO.output(Mid,1)
    else:
        print("green")
        GPIO.output(Low,1)
    # if linee2[0].any() >2000:
    #     print("red")
    # else: print("green")
    return (line1,line2,)

plt.xlim(0, RATE/2+1)
plt.ylim(-60, 0)
plt.xlabel('Frequency')
plt.ylabel('dB')
plt.title('Spectrometer')
plt.grid()

line_ani = matplotlib.animation.FuncAnimation(
    fig, update_line, init_func=init_line, interval=0, blit=True
)
def setup():
    GPIO.setmode(GPIO.BOARD)       # Numbers GPIOs by physical location
    GPIO.setup(High, GPIO.OUT)   # Set LedPin's mode is output
    GPIO.setup(Mid, GPIO.OUT)
    GPIO.setup(Low, GPIO.OUT) 
    print("setup")
    GPIO.output(Mid,1)
    time.sleep(3)
    GPIO.output(Mid,0)
    plt.show()
setup()