import json
from random import randint

import urequests
import utime


def main(chip_id, host):
    velocity = [0, 0]
    v1 = int(str(utime.time()).split('.')[1])
    v2 = int(str(utime.time()).split('.')[1])
    d1 = v1 / 1000000 * (-1)**(v1 % 2)
    d2 = v2 / 1000000 * (-1)**(v1 % 2)
    data = [d1, d2]
    iteration = 0
    url = host + 'data'
    while iteration != 20:
        print('Data: ', data)
        response = urequests.post(url, data=json.dumps({
            'id': chip_id,
            'iteration': iteration,
            'data': data
        }))
        # print(response.json(), response.status_code)
        while True:
            response = urequests.get(url, data=json.dumps({
                'iteration': iteration
            }))
            # print(response.json(), response.status_code)
            if response.status_code == 200:
                break

            utime.sleep_ms(5000)

        pbest = response.json()['Pbest']
        gbest = response.json()['Gbest']

        for i in range(2):
            r1 = randint(0, 100) / 100
            r2 = randint(0, 100) / 100
            velocity[i] = 0.5 * velocity[i] + 1 * r1 * (
                pbest[i] - data[i]) + 1 * r2 * (gbest[i] - data[i])
            data[i] += velocity[i]

        iteration += 1

    print('BY')


if __name__ == '__main__':
    host = 'http://192.168.1.103:8888/'
    chip_id = str(utime.time()).split('.')[1]
    main(chip_id, host)
