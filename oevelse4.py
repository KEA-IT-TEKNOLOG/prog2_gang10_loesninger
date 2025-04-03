"""
ØVELSE 4 lav en scheduler klasse til at vande når jordfugtiheden er lav

Scriptet skal tjekke om jordfugtiheden er lav (om det er tid til at vande planten)
hver morgen klokken 07:00.
Schedule skal anvendes til dette.
Hvis jordfugtigheden er lav, så skal der vandes (pumpen køre) I 3 sekunder.

Test ved at køre hvert sekund eller minut og tjek at den vander hvis
jordfugtiheds sensoreren er tør, og at den IKKE vander hvis jordfugtihedssensoren er våd.

Prøv til sidst at køre scriptet som en daemon (se sidste uges slides)
"""

import smbus
import time
import pigpio
import schedule

class GreenhouseControl:
    def __init__(self, pump_gpio, i2c_address=0x4B, dry=767, wet=297):
        self.pump_gpio = pump_gpio
        self.wet = wet
        self.dry = dry
        self.pump_running = False
        self.i2c_address = i2c_address
        self.bus = smbus.SMBus(1)# RPi revision 2 (0 for revision 1)​
        self.pi = pigpio.pi()
        self.pi.write(pump_gpio, 0)
        self.soil_percentage = None
       

    def soil_raw_adc(self):
        # Reads word (2 bytes) as int - 0 is comm byte​
        rd = self.bus.read_word_data(self.i2c_address, 0)
        # Exchanges high and low bytes​
        data = ((rd & 0xFF) << 8) | ((rd & 0xFF00) >> 8)
        # Ignores two least significiant bits​
        data = data >> 2
        return data

    def soil_percent(self):
        data = self.soil_raw_adc()
        if data < self.wet:
            data = 100

        else:
            # tør måling - ADC måling * 100.0 / tør måling - våd måling. ​
            percentage = (self.dry - data) * 100.0 / (self.dry - self.wet) 
            data = round(percentage, 2)
            if percentage < 0:
                data = 0
        
        return data

    def water_plants(self):
        soil_p = self.soil_percent()
        print("Data: ", soil_p)
        if soil_p < 10 and self.pump_running == False:
            self.pi.write(self.pump_gpio, 1)
            self.pump_running = True
            time.sleep(3)
            self.pi.write(self.pump_gpio, 0)
            self.pump_running = False

greenhouse = GreenhouseControl(13)
schedule.every(1).day.at("07:00").do(greenhouse.water_plants)

while True:
    schedule.run_pending()
    time.sleep(1)