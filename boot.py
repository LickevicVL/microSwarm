import network
import utime
from machine import Pin

ESSID = 'ESSID'
PASSWORD = 'PASSWORD'


def do_connect(log):
    sta_if = network.WLAN(network.STA_IF)
    if not sta_if.isconnected():
        log.write('connecting to network...')
        sta_if.active(True)
        sta_if.connect(ESSID, PASSWORD)
        while not sta_if.isconnected():
            pass

    log.write('network config:', sta_if.ifconfig())


def main():
    log_name = str(int(utime.time() * 1000)) + '.log'
    with open(log_name, 'a+') as file:
        do_connect(file)

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
    main()
