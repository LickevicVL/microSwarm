import gc
import network
import ujson
import utime
from machine import Pin


def do_connect(essid, password, log):
    """Connect to the network"""
    wlan = network.WLAN(network.STA_IF)
    if not wlan.isconnected():
        log.write('connecting to network...\n')
        wlan.active(True)
        wlan.connect(essid, password)
        while not wlan.isconnected():
            pass

    log.write('network config: {}\n'.format(wlan.ifconfig()))


def main():
    with open('config.json', 'r') as file:
        config = ujson.load(file)

    # Get main parameters from config file config.json
    essid = config['essid']
    password = config['password']

    with open('log.log', 'w+') as log:
        do_connect(essid, password, log)

    # Turn on/off light. Show, that esp8266 was connected to network
    pin = Pin(2, Pin.OUT)
    enabled = True
    for i in range(5):
        if enabled:
            pin.off()
        else:
            pin.on()

        utime.sleep_ms(1000)
        enabled = not enabled


if __name__ == '__main__':
    gc.collect()
    main()
