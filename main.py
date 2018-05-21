import json

import machine
import urequests
import utime


def get_random():
    tv = int(str(utime.time()).split('.')[1])
    r = tv / 1000000 * (-1) ** (tv % 2)

    return r


def main(chip_id, host):
    velocity = [0, 0]
    data = [get_random(), get_random()]
    iteration = 0
    url = host + 'data'
    while iteration != 20:
        print('Data: ', data)
        urequests.post(url, data=json.dumps({
            'id': chip_id,
            'iteration': iteration,
            'data': data
        }))
        while True:
            response = urequests.get(url, data=json.dumps({
                'iteration': iteration
            }))
            if response.status_code == 200:
                break

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
    HOST = 'http://192.168.10.102:8888/'
    CHIP_ID = machine.unique_id()
    if CHIP_ID == b'upy-non-unique':
        CHIP_ID = str(utime.time()).split('.')[1]

    main(CHIP_ID, HOST)
