import plasma
from plasma import plasma2040
import network
import time
import requests
import ntptime

ntptime.host = "1.europe.pool.ntp.org"


# Total number of LEDs on our LED strip
NUM_LEDS = 66

# How long between cheerslight updates in seconds
delay = 60

synched = False


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


def connect():
    # Connect to the network specified in secrets.py
    wlan.active(True)
    wlan.connect(WIFI_SSID, WIFI_PASSWORD)
    while wlan.isconnected() is False:
        time.sleep(1)
    ntptime.settime()
    


# APA102 / DotStar™ LEDs
# led_strip = plasma.APA102(NUM_LEDS, 0, 0, plasma2040.DAT, plasma2040.CLK)
wlan = network.WLAN(network.STA_IF)

# WS2812 / NeoPixel™ LEDs
led_strip = plasma.WS2812(NUM_LEDS, 0, 0, plasma2040.DAT, color_order=plasma.COLOR_ORDER_BGR)

# Start connection to the network
connect()

# Store the local IP address
ip_addr = wlan.ipconfig('addr4')[0]

# Let the user know the connection has been successful
# and display the current IP address of the Plasma 2350 W


# Start updating the LED strip
led_strip.start()

def getNextFutureMinute(lastUpdate):

    lastUpdatedToCommaSeparated = lastUpdate.replace("-",",").replace("T",",").replace(":",",").replace("Z","").replace(".",",")
    
    lastUpdatedSplit = lastUpdatedToCommaSeparated.split(",")
    lastUpdatedSeconds = int(lastUpdatedSplit[0])*365*24*60*60 + int(lastUpdatedSplit[1])*30*24*60*60 + int(lastUpdatedSplit[2]) * 24*60*60 + int(lastUpdatedSplit[3])*60*60 + int(lastUpdatedSplit[4])*60 + int(lastUpdatedSplit[5])    
    
    now = time.localtime()    
    secondsOfThisDay = now[0]*365*24*60*60 + now[1]*30*24*60*60 + now[2] * 24*60*60 + now[3]*60*60 + now[4]*60 + now[5]
    
    delay = syncToFixedDelay(secondsOfThisDay,lastUpdatedSeconds)
    
    return delay

def syncToFixedDelay(secondsOfThisDay,lastUpdatedSeconds):

    global synched
    while not synched:
        lastUpdatedSeconds = lastUpdatedSeconds + 60
        if (lastUpdatedSeconds >= secondsOfThisDay):
            global synched
            synched = True
            return int(lastUpdatedSeconds) - int(secondsOfThisDay)
    return 60    


try:
    
    while True:
        
        if wlan.isconnected():
            try:
                
                req = requests.get("https://cheertree-express-server-0b0f376df1b2.herokuapp.com")
                json = req.json()
                req.close()
                colour = tuple(int(json['hex'][i:i + 2], 16) for i in (1, 3, 5))                
                lastUpdated = json['messageArrivedAt']
                delay = getNextFutureMinute(lastUpdated)
                for i in range(NUM_LEDS):
                    led_strip.set_rgb(i, *colour)
            except OSError:
                print("Error: Failed to get new colour" + "\n")

        else:
            print("Lost connection to network {}".format(WIFI_SSID) + "\n")

        message = "Delaying for: " + str(delay) + "seconds \n";
        print(message)
        time.sleep(delay)
        
except KeyboardInterrupt as ki:
    
    kiMessage = f"Unexpected {ki=}, {type(ki)=}"
    print(kiMessage)
    
except Exception as err:
    exceptionMessage = f"Unexpected {err=}, {type(err)=}"
    print(exceptionMessage)

                



