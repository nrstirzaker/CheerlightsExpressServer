import plasma
from plasma import plasma2040
import network
import time
import requests

# Total number of LEDs on our LED strip
NUM_LEDS = 66

# How long between cheerslight updates in seconds
delay = 60

# Check and import the SSID and Password from secrets.py
try:
    from secrets import WIFI_SSID, WIFI_PASSWORD
    if WIFI_SSID == "":
        raise ValueError("WIFI_SSID in 'secrets.py' is empty!")
    if WIFI_PASSWORD == "":
        raise ValueError("WIFI_PASSWORD in 'secrets.py' is empty!")
except ImportError:
    raise ImportError("'secrets.py' is missing from your Plasma 2350 W!")
except ValueError as e:
    print(e)

wlan = network.WLAN(network.STA_IF)


def connect():
    # Connect to the network specified in secrets.py
    wlan.active(True)
    wlan.connect(WIFI_SSID, WIFI_PASSWORD)
    while wlan.isconnected() is False:
        print("Attempting connection to {}".format(WIFI_SSID))
        time.sleep(1)


# APA102 / DotStar™ LEDs
# led_strip = plasma.APA102(NUM_LEDS, 0, 0, plasma2040.DAT, plasma2040.CLK)

# WS2812 / NeoPixel™ LEDs
led_strip = plasma.WS2812(NUM_LEDS, 0, 0, plasma2040.DAT, color_order=plasma.COLOR_ORDER_BGR)

# Start connection to the network
connect()

# Store the local IP address
ip_addr = wlan.ipconfig('addr4')[0]

# Let the user know the connection has been successful
# and display the current IP address of the Plasma 2350 W
print("Successfully connected to {}. Your Plasma 2350 W's IP is: {}".format(WIFI_SSID, ip_addr))

# Start updating the LED strip
led_strip.start()

def getNextFutureMinute(lastUpdate):
    
    lastUpdatedToCommaSeparated = lastUpdate.replace("-",",").replace("T",",").replace(":",",").replace("Z","").replace(".",",")
    
    lastUpdatedSplit = lastUpdatedToCommaSeparated.split(",")
    

    now = time.localtime()
    nowHour = now[3]
    nowMinute = now[4]
    nowSecond = now[5]
    secondsOfThisDay = now[0]*365*24*60*60 + now[1]*30*24*60*60 + now[2] * 24*60*60 + now[3]*60*60 + now[4]*60 + now[5]
    print(secondsOfThisDay)
    lastUpdatedSeconds = int(lastUpdatedSplit[0])*365*24*60*60 + int(lastUpdatedSplit[1])*30*24*60*60 + int(lastUpdatedSplit[2]) * 24*60*60 + int(lastUpdatedSplit[3])*60*60 + int(lastUpdatedSplit[4])*60 + int(lastUpdatedSplit[5])
    print(lastUpdatedSeconds)
    
    delay = howManyMinutesTillOneMinuteAfterLastUpdate(secondsOfThisDay,lastUpdatedSeconds)
    print("delay")
    print(delay)
    return delay

def howManyMinutesTillOneMinuteAfterLastUpdate(secondsOfThisDay,lastUpdatedSeconds):
    foundTheFuture = False
    while not foundTheFuture:
        lastUpdatedSeconds = lastUpdatedSeconds + 60
        if (lastUpdatedSeconds > secondsOfThisDay):
            foundTheFuture = True
            return int(lastUpdatedSeconds - secondsOfThisDay)

while True:
    if wlan.isconnected():
        try:
            print("Getting new colour...")
            req = requests.get("https://cheertree-express-server-0b0f376df1b2.herokuapp.com", timeout=None)
            json = req.json()
            req.close()
            print("Success!")

            colour = tuple(int(json['hex'][i:i + 2], 16) for i in (1, 3, 5))
            print(colour)
            lastUpdated = json['messageArrivedAt']
            delay = getNextFutureMinute(lastUpdated)
            for i in range(NUM_LEDS):
                led_strip.set_rgb(i, *colour)
        except OSError:
            print("Error: Failed to get new colour")
    else:
        print("Lost connection to network {}".format(WIFI_SSID))

    time.sleep(delay)

