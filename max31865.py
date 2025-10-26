from machine import Pin, SPI
import time

class MAX31865:
    def __init__(self, spi, cs, wires=3):
        self.spi = spi
        self.cs = cs
        self.cs.init(Pin.OUT, value=1)
        self.wires = wires
        self.configure()

    def write_register(self, reg, value):
        self.cs.value(0)
        self.spi.write(bytearray([reg | 0x80, value]))
        self.cs.value(1)

    def read_register(self, reg, length=1):
        self.cs.value(0)
        self.spi.write(bytearray([reg & 0x7F]))
        data = self.spi.read(length)
        self.cs.value(1)
        return data

    def configure(self):
        config = 0xC2  # Vbias on, auto convert, 3-wire
        if self.wires == 2 or self.wires == 4:
            config &= ~0x10  # Clear 3-wire bit
        self.write_register(0x00, config)

    def read_rtd(self):
        data = self.read_register(0x01, 2)
        rtd = ((data[0] << 8) | data[1]) >> 1
        return rtd

    def read_rtd_raw(self):
        data = self.read_register(0x01, 2)
        rtd = ((data[0] << 8) | data[1]) >> 1
        return rtd

    def read_resistance(self, r_ref=430.0):
        rtd = self.read_rtd_raw()
        resistance = (rtd * r_ref) / 32768.0
        return resistance
    
    def temperature(self, r_ref=430.0, rtd_nominal=100.0):
        rtd = self.read_rtd()
        resistance = (rtd * r_ref) / 32768.0
        temp = (resistance / rtd_nominal - 1) / 0.00385
        return temp

# 🧰 Setup for Raspberry Pi Pico SPI0
cs = Pin(17, Pin.OUT)
spi = SPI(0, baudrate=500000, polarity=1, phase=1,
          sck=Pin(18), mosi=Pin(19), miso=Pin(16))

sensor = MAX31865(spi, cs, wires=3)

while True:
    temp = sensor.temperature()
    resistance = sensor.read_resistance()
    
    print("Resistance: {:.2f} Ω, Temperature: {:.2f} °C".format(resistance, temp))
    time.sleep(1)

