/*
* Motor Driver
*
* Listens to simple commands on the serial port, drives motors.
*/

#include <Servo.h> 

const int ERROR = -1;
const char PACKET_SEPARATOR0 = '\xFF';
const char PACKET_SEPARATOR1 = '\x00';

#define SERVO_COUNT 5

#define THRUST  0
#define THRUST_PIN  5
#define DUCT 1
#define DUCT_PIN 6
#define TURN 2
#define TURN_PIN 9
#define X 3
#define X_PIN 10
#define Y 4
#define Y_PIN 11
// great for debugging
#define LED 5
#define LED_PIN 13
const int MOTOR_PIN[] = {THRUST_PIN, DUCT_PIN,TURN_PIN,  X_PIN, Y_PIN};
// turn: 0 is hard left, all others start at 0
const int INITIAL[] = {0, 0, 128, 0, 0};
Servo servos[SERVO_COUNT];

void setup() {
  pinMode(LED_PIN, OUTPUT);
  Serial.begin(9600);
  Serial.println("init");
  for (int i = 0; i < SERVO_COUNT; i++) {
    servos[i].attach(MOTOR_PIN[i]);
    servos[i].write(INITIAL[i]);
  }
  Serial.println("done initializing");
}

void loop() {
  read_start_marker();
  int port = read_port();
  if (port == ERROR) {
    return;
  }
  int value = read_value();
  if (port == LED) {
    digitalWrite(LED_PIN, value ? HIGH : LOW);
  } else {
    servos[port].write(value);
  }
}

char read_byte() {
  while (true) {
    if (Serial.available()) {
      return Serial.read();
    }
  }
}

void read_start_marker() {
  while (true) {
    if (read_byte() == PACKET_SEPARATOR0) {
      if (read_byte() == PACKET_SEPARATOR1) {
        return;
      }
    }
    Serial.println("out of sync");
  }
}

int read_port() {
  int port = read_byte();
  // +1 for LED
  if (port > 0 && port < SERVO_COUNT + 1) {
    return port;
  }
  Serial.print("error: port unsupported: ");
  Serial.println(port);
  return ERROR;
}

int read_value() {
  return read_byte();
}
