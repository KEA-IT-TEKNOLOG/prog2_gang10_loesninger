"""
Lav en ny underside på jeres website fra sidste uge, hvor i viser målingerne.
Sørg også for at status på om pumpen er tændt eller slukket vises på websiden.
"""
from flask import Flask, render_template
from flask_socketio import SocketIO, emit
import pigpio
from pigpio_dht import DHT11
from time import sleep
import threading
import smbus

DHT11_PIN = 19
sensor = DHT11(DHT11_PIN)
sidste_temp = None
BUTTON_GPIO_PIN = 4 
LED_GPIO_PIN = 13


pi = pigpio.pi()
app = Flask(__name__)
socketio = SocketIO(app)

class WaterPump:
    def __init__(self, PUMP_GPIO_PIN=20):
        self.PUMP_GPIO_PIN = PUMP_GPIO_PIN # der står 38 på adapter
        self.pump_running = False
    
    def water_plants(self, duration_seconds):
        self.pump_running = True
        pi.write(self.PUMP_GPIO_PIN, 1)
        sleep(duration_seconds)
        pi.write(self.PUMP_GPIO_PIN, 0)
        self.pump_running = False

class SoilMoist:
    def __init__(self, dry=767, wet=297, i2c_addr=0x4B):
        self.dry = dry
        self.wet = wet
        self.soil_moisture_percent = None
        self.i2c_addr = i2c_addr
        self.bus = smbus.SMBus(1)
        self.water_pump = WaterPump() # Composition
        
    def soil_raw_adc(self):
        # Reads word (2 bytes) as int - 0 is comm byte​
        rd = self.bus.read_word_data(self.i2c_addr, 0)
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
        if data < 10:
            self.water_pump.water_plants(3)
        return data
    
    def continous_measure(self):
        while True:
            self.soil_moisture_percent = self.soil_percent()
            #print(self.soil_moisture_percent)
            sleep(0.2)
    def start_continous_measure(self):
        soil_thread = threading.Thread(target=self.continous_measure)
        soil_thread.start()

soil_measure = SoilMoist()
soil_measure.start_continous_measure()

def tilstand():
    button_state = pi.read(BUTTON_GPIO_PIN)
    socketio.emit('button_state', button_state)

@socketio.on('connect')
def connect():
    tilstand()
# https://abyz.me.uk/rpi/pigpio/python.html#callback
def cbf(gpio, level, tick):
    tilstand()

pi.callback(BUTTON_GPIO_PIN, pigpio.EITHER_EDGE, cbf)

@socketio.on('skru')
def skru(data):
    lysstyrke = int(data['lysstyrke'])

    if lysstyrke < 0:
        lysstyrke = 0

    if lysstyrke > 255:
        lysstyrke = 255
    print(lysstyrke)
    pi.set_PWM_dutycycle(LED_GPIO_PIN, lysstyrke)

@socketio.on('hent_temp')
def hent_temp():
    sleep(0.5)
    socketio.emit('temp', sidste_temp)

@app.route("/")
def home():
    return render_template("home.html", methods=['GET'])

@app.route("/site1/")
def site1():
    return render_template("site1.html", methods=['GET'])

@app.route("/site2/")
def site2():
    return render_template("site2.html", methods=['GET'])

@socketio.on('hent_soil')
def hent_soil():
    print(soil_measure.soil_moisture_percent)
    sleep(0.5)
    data = {"moist_percentage":soil_measure.soil_moisture_percent,
            "pump_state": soil_measure.water_pump.pump_running
            }
    socketio.emit('soil', data)
    

@app.route("/soil/")
def soil():
    return render_template("soil_moist.html", methods=['GET'])

def read_temp():
    global sidste_temp
    while True:
        sleep(2)
        try:
            sidste_temp = sensor.read()
        except:
            sidste_temp = None

temp_thread = threading.Thread(target=read_temp)
temp_thread.start()

if __name__ == '__main__':
    socketio.run(app, host="0.0.0.0", debug=True)