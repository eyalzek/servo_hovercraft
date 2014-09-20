import serial
import logging
logger = logging.getLogger(__name__)

SERVO_MIN_VALUE = 0
SERVO_MAX_VALUE = 127
DUCT_MIN_VALUE = int(127*0.30)
DUCT_MAX_VALUE = int(127*0.50)
THRUST_MIN_VALUE = int(127*0.40)
THRUST_MAX_VALUE = int(127*0.60)
LED_MIN_VALUE = 0
LED_MAX_VALUE = 1
MAX_VALID_PORT = 5
FIRST_PORT_ORD = ord('0')
HEADER = 'AB'

class Protocol(object):
    def __init__(self, serial):
        self.serial = serial

    def send(self, port, value):
        assert 0 <= port <= MAX_VALID_PORT
        assert 0 <= value <= 255
        self.serial.write(HEADER + chr(FIRST_PORT_ORD + port) + chr(value))
        logger.debug('sent %d to %d' % (value, port))
        self.log_response()

    def log_response(self):
        if self.serial.inWaiting():
            logger.debug(self.serial.read(self.serial.inWaiting()))

class ServoProperty(object):
    def __init__(self, port, out_min, out_max, in_min=0.0, in_max=1.0, default=0.0):
        self.port = port
        self.out_min = out_min
        self.out_max = out_max
        self.min = in_min
        self.max = in_max
        self.value = default
        self.conversion = (out_max - out_min) / (in_max - in_min)

    def __get__(self, obj, objtype=None):
        if obj is None:
            return self
        return self.value

    def __set__(self, obj, value):
        value = self.clamp(value)
        obj.protocol.send(self.port, self.to_byte(value))
        self.value = value

    def clamp(self, value):
        return max(self.min, min(value, self.max))

    def to_byte(self, value):
        return self.out_min + int((value - self.min) * self.conversion)

_positive = ServoProperty(None, SERVO_MIN_VALUE, SERVO_MAX_VALUE)
assert _positive.to_byte(0.) == SERVO_MIN_VALUE
assert _positive.to_byte(0.5) == (SERVO_MIN_VALUE + SERVO_MAX_VALUE) / 2
assert _positive.to_byte(1.) == SERVO_MAX_VALUE
_around_zero = ServoProperty(None, SERVO_MIN_VALUE, SERVO_MAX_VALUE, in_min=-1.)
assert _around_zero.to_byte(-1.) == SERVO_MIN_VALUE
assert _around_zero.to_byte(0.) == (SERVO_MIN_VALUE + SERVO_MAX_VALUE) / 2
assert _around_zero.to_byte(1.) == SERVO_MAX_VALUE
assert _positive.clamp(0.1) == 0.1
assert _positive.clamp(-0.1) == 0.0
assert _positive.clamp(1.1) == 1.0
assert _around_zero.clamp(-0.1) == -0.1
_motor = ServoProperty(None, DUCT_MIN_VALUE, DUCT_MAX_VALUE)
assert _motor.to_byte(0.) == DUCT_MIN_VALUE
assert _motor.to_byte(0.5) == (DUCT_MIN_VALUE + DUCT_MAX_VALUE) / 2
assert _motor.to_byte(1.) == DUCT_MAX_VALUE

class Servos(object):
    def __init__(self, serial):
        self.protocol = Protocol(serial)

    thrust = ServoProperty(0, THRUST_MIN_VALUE, THRUST_MAX_VALUE)
    duct = ServoProperty(1, DUCT_MIN_VALUE, DUCT_MAX_VALUE)
    turn = ServoProperty(2, SERVO_MIN_VALUE, SERVO_MAX_VALUE, in_min=-1.)
    x = ServoProperty(3, SERVO_MIN_VALUE, SERVO_MAX_VALUE)
    y = ServoProperty(4, SERVO_MIN_VALUE, SERVO_MAX_VALUE)
    led = ServoProperty(5, LED_MIN_VALUE, LED_MAX_VALUE)

class FakeSerial(object):
    def write(self, data):
        print 'write: ' + repr(data)

    def read(self, count=1):
        return 'a' * count

    def inWaiting(self):
        return 10

if __name__ == '__main__':
    logging.basicConfig()
    logger.setLevel(logging.DEBUG)
    servos = Servos(FakeSerial())  #serial.Serial('COM5'))

    servos.thrust = 0.7
    servos.thrust = 0.0
    servos.thrust = 1.0
    print 'thrust:', servos.thrust
    servos.turn = 0.1
    servos.turn = -1.0
    servos.led = 0.0
    servos.led = 0.4
    servos.led = 0.6
    servos.led = 1.0
