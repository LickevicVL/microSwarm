import machine
import random
import ubinascii
import ujson
import urequests
import utime
from hcsr04 import HCSR04


def func(x, y):
    return x ** 2 + y ** 2


def get_random():
    """Get random value. Useful for emulated agent"""
    tv = int(utime.time())
    utime.sleep_ms(random.randrange(1, 100))
    r = float('0.{}'.format(tv)) * (-1) ** (int(utime.time()) % 2)

    return r


def get_location():
    """Get location of agent"""
    return [get_random(), get_random()]


def get_parameters(url):
    """Get from cloud main parameters for algorithm"""
    url += '/parameters'
    response = urequests.get(url)
    response_json = response.json()
    w = response_json['w']
    c1 = response_json['c1']
    c2 = response_json['c2']
    iterations = response_json['iterations']

    response.close()

    return w, c1, c2, iterations


def post_message(url, chip_id, message):
    """Put status of agent into logger server"""
    response = urequests.post(url, data=ujson.dumps(
        {
            'id': chip_id,
            'message': message
        }
    ))
    response.close()


def post_data(url, chip_id, iteration, data, value):
    """Put data of agent into cloud"""
    response = urequests.post(url, data=ujson.dumps(
        {
            'id': chip_id,
            'iteration': iteration,
            'data': data,
            'value': value
        }
    ))
    response.close()


def get_data(url, log_url, chip_id, iteration):
    """
    Get main data from cloud.
    """
    while True:
        response = urequests.get(url, data=ujson.dumps(
            {
                'iteration': iteration
            }
        ))

        if response.status_code == 200:
            break

        message = 'Wait'
        post_message(log_url, chip_id, message)

        response.close()
        utime.sleep_ms(5000)

    response_json = response.json()
    gbest = response_json['Gbest']
    pbest = response_json['Pbest']
    r1 = response_json['r1']
    r2 = response_json['r2']

    response.close()

    return gbest, pbest, r1, r2


def run(chip_id, host, log_host, get_value_function):
    """Main program of PSO algorithm

    :param chip_id: id of the chip
    :param host: host of the cloud
    :param log_host: host of the logger server
    :param get_value_function: function,
    which return value of the agent for specified location
    """
    velocity = [0, 0]
    data = get_location()
    url = host + 'data'
    logger = log_host + 'message'

    w, c1, c2, iterations = get_parameters(url)

    for iteration in range(iterations):
        value = get_value_function(*data)

        message = ujson.dumps({
            'iteration': iteration,
            'data': data,
            'value': value
        })
        post_message(logger, chip_id, message)
        post_data(url, chip_id, iteration, data, value)

        gbest, pbest, r1, r2 = get_data(url, logger, chip_id, iteration)

        for i in range(2):
            velocity[i] = w * velocity[i] + c1 * r1 * (
                pbest[i] - data[i]) + c2 * r2 * (gbest[i] - data[i])
            data[i] += velocity[i]


def main():
    with open('config.json', 'r') as file:
        config = ujson.load(file)

    # Get main parameters from config file config.json
    IP = config['host']
    PORT = config['port']
    LOG_PORT = config['logPort']
    HOST = '{}:{}/'.format(IP, PORT)
    LOG = '{}:{}/'.format(IP, LOG_PORT)

    # Set main variables for algorithm
    CHIP_ID = machine.unique_id()
    if CHIP_ID == b'upy-non-unique':
        CHIP_ID = 'agent-{}'.format(int(utime.time()))
        GET_VALUE_FUNCTION = lambda *args: func(*args)
    else:
        CHIP_ID = ubinascii.hexlify(machine.unique_id())

        trig_pin = 16
        echo_pin = 0
        sensor = HCSR04(trigger_pin=trig_pin, echo_pin=echo_pin)
        GET_VALUE_FUNCTION = lambda *args: sensor.distance_cm()

    # Run agent program
    run(CHIP_ID, HOST, LOG, GET_VALUE_FUNCTION)


if __name__ == '__main__':
    main()
