import json

import machine
import urequests
import utime


def func(x):
    return sum([i**2 for i in x])


def get_random():
    tv = int(str(utime.time()).split('.')[1])
    r = tv / 1000000 * (-1) ** (tv % 2)

    return r


def main(chip_id, host, log):
    velocity = [0, 0]
    data = [get_random(), get_random()]
    iteration = 0
    url = host + 'data'
    logger = log + 'message'

    while iteration != 20:
        value = func(data)
        urequests.post(logger, data=json.dumps({
            'id': chip_id,
            'message': '--> {}'.format(json.dumps({
                'iteration': iteration,
                'data': data,
                'value': value
            }))
        }))
        urequests.post(url, data=json.dumps({
            'id': chip_id,
            'iteration': iteration,
            'data': data,
            'value': value
        }))
        while True:
            response = urequests.get(url, data=json.dumps({
                'iteration': iteration
            }))
            if response.status_code == 200:
                break

            urequests.post(logger, data=json.dumps({
                'id': chip_id,
                'message': '<-- Wait'
            }))
            utime.sleep_ms(5000)

        response_json = response.json()
        pbest = response_json['Pbest']
        gbest = response_json['Gbest']

        parameters = response_json['parameters']
        w = parameters['w']
        c1 = parameters['c1']
        c2 = parameters['c2']
        r1 = parameters['r1']
        r2 = parameters['r2']

        for i in range(2):
            velocity[i] = w * velocity[i] + c1 * r1 * (
                pbest[i] - data[i]) + c2 * r2 * (gbest[i] - data[i])
            data[i] += velocity[i]

        iteration += 1

if __name__ == '__main__':
    PORT = '8888'
    LOG_PORT = '8080'
    IP = 'http://192.168.10.102:{}/'
    HOST = IP.format(PORT)
    LOG = IP.format(LOG_PORT)

    CHIP_ID = machine.unique_id()
    if CHIP_ID == b'upy-non-unique':
        CHIP_ID = str(utime.time()).split('.')[1]

    main(CHIP_ID, HOST, LOG)
