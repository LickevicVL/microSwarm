import gc
import network
import ujson
import utime
from machine import Pin


def do_connect(essid, password, log):
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

    essid = config['essid']
    password = config['password']

    with open('log.log', 'w+') as log:
        do_connect(essid, password, log)

    pin = Pin(2, Pin.OUT)
    enabled = True
    for i in range(5):
        if enabled:
            pin.low()
        else:
            pin.high()

        utime.sleep_ms(1000)
        enabled = not enabled


if __name__ == '__main__':
    gc.collect()
    main()
