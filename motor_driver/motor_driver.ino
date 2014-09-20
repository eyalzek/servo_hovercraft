/*
* Motor Driver
*
* Listens to simple commands on the serial port, drives motors.
*/

#include <Servo.h>

const int DETACH_THRESHOLD = 0.5 * 1000;

const int ERROR = -1;
const char PACKET_SEPARATOR0 = 'A';
const char PACKET_SEPARATOR1 = 'B';

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
unsigned long last_command[SERVO_COUNT];
Servo servos[SERVO_COUNT];

void setup() {
  pinMode(LED_PIN, OUTPUT);
  Serial.begin(9600);
  Serial.println("init");
  for (int i = 0; i < SERVO_COUNT; i++) {
    write(i, INITIAL[i]);
  }
  Serial.println("done initializing");
}

void write(int port, char value) {
  if (!servos[port].attached()) {
    attach(port);
  }
  servos[port].write(value);
}

void attach(int i) {
  servos[i].attach(MOTOR_PIN[i]);
  last_command[i] = millis();
}

void loop() {
  detach_unused_servos();
  if (!read_start_marker()) {
    Serial.println("out of sync");
    return;
  }
  int port = read_port();
  if (port == ERROR) {
    return;
  }
  int value = read_value();
  if (port == LED) {
    digitalWrite(LED_PIN, value ? HIGH : LOW);
  } else {
    write(port, value);
  }
}

char read_byte() {
  while (true) {
    if (Serial.available()) {
      return Serial.read();
    }
  }
}

int read_start_marker() {
  if (read_byte() == PACKET_SEPARATOR0) {
    if (read_byte() == PACKET_SEPARATOR1) {
      return true;
    }
  }
  return false;
}

int read_port() {
  int port = read_byte() - '0';
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

void detach_unused_servos() {
  unsigned long threshold = millis() - DETACH_THRESHOLD;
  for (int i = 0; i < SERVO_COUNT; i++) {
    if (last_command[i] < threshold && servos[i].attached()) {
      servos[i].detach();
    }
  }
}