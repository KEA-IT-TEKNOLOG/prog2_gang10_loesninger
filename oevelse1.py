"""
Øvelse 1

Lav en funktion der omregner ADC værdien til en procentværdi og returnere denne værdi af fugtigheden.
Test jeres egen sensor i vand og luft eller i tør jord og fugtig jord
 og brug værdierne fra den tørre og våde måling som input til funktionen. 
 Ligeledes skal funktionen også løbende have ADC værdien.

Hvis denne måling er mindre end værdien i den våde måling så sæt fugtigheden til 100.
Ellers så sæt fugtigheden til at være:
tør måling - ADC måling * 100.0 / tør måling - våd måling.

(Husk paranteser så addition og substraktion udregnes først)
Hvis målingen er mindre end 0 så sæt fugtigheden til 0.0 
"""

import smbus
import time

bus = smbus.SMBus(1)# RPi revision 2 (0 for revision 1)​
i2c_address = 0x4B  # default address​

# OPDATER TIL EGNE MÅLINGER!
dry = 767
wet = 297

def soil_raw_adc():
    # Reads word (2 bytes) as int - 0 is comm byte​
    rd = bus.read_word_data(i2c_address, 0)
    # Exchanges upper and lower bytes​
    data = ((rd & 0xFF) << 8) | ((rd & 0xFF00) >> 8)
    # Ignores two least significiant bits​
    data = data >> 2
    return data

def soil_percent():
    data = soil_raw_adc()
    if data < wet:
        data = 100

    else:
        # tør måling - ADC måling * 100.0 / tør måling - våd måling. ​
        percentage = (dry - data) * 100.0 / (dry - wet) 
        data = round(percentage, 2)
        if percentage < 0:
            data = 0
    
    return data

while True:

    print("Data: ", soil_percent())
    time.sleep(1)