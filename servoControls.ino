#include <Servo.h>

Servo baseServo;
Servo shoulderServo;
Servo elbowServo;
Servo clawServo;
Servo elbowServo2;

const int trigPin = 6;
const int echoPin = 7;

const int grabThreshold = 10; 

const int minAngle = -180;
const int maxAngle = 180;

int baseAngle = 90;
int shoulderAngle = 90;
int elbowAngle = 90;

bool clawClosed = false;

enum Direction { NONE, LEFT, RIGHT, UP, DOWN, END };

void setup() {
  Serial.begin(9600);

  baseServo.attach(2);
  shoulderServo.attach(3);
  elbowServo.attach(8);
  clawServo.attach(5);
  elbowServo2.attach(4);

  pinMode(trigPin, OUTPUT);
  pinMode(echoPin, INPUT);

  baseServo.write(baseAngle);
  shoulderServo.write(shoulderAngle);
  elbowServo.write(elbowAngle);
  openClaw();
  delay(1000);
}

void loop() {
  int distance = getDistanceCM();

  if (distance > 0 && distance < grabThreshold && !clawClosed) {
    closeClaw();
    clawClosed = true;
    delay(4000);
    openClaw();
    clawClosed = false;
  }

  Direction dir = getDirectionFromSerial();
  if (dir != NONE && clawClosed != true) {
    moveTowardsDirection(dir);
  }
}

Direction getDirectionFromSerial() {
  if (Serial.available()) {
    char command = Serial.read();
    switch (command) {
      case 'L': return LEFT;
      case 'R': return RIGHT;
      case 'U': return UP;
      case 'D': return DOWN;
      case 'E': return END;
      default: return NONE;
    }
  }
  return NONE;
}

void moveTowardsDirection(Direction dir) {
  switch (dir) {
    case LEFT:
      baseAngle = constrain(baseAngle - 2, minAngle, maxAngle);
      break;
    case RIGHT:
      baseAngle = constrain(baseAngle + 2, minAngle, maxAngle);
      break;
    case UP:
      shoulderAngle = constrain(shoulderAngle - 2, minAngle, maxAngle);
      elbowAngle = constrain(elbowAngle - 2, minAngle, maxAngle);
      break;
    case DOWN:
      shoulderAngle = constrain(shoulderAngle + 2, minAngle, maxAngle);
      elbowAngle = constrain(elbowAngle + 2, minAngle, maxAngle);
      break;
    case END:
      baseAngle = 90;
      shoulderAngle = 90;
      elbowAngle = 90;
    default: break;
  }

  baseServo.write(baseAngle);
  shoulderServo.write(shoulderAngle);
  elbowServo.write(elbowAngle);
  elbowServo2.write(90);
}

int getDistanceCM() {
  digitalWrite(trigPin, LOW);
  delayMicroseconds(5);
  digitalWrite(trigPin, HIGH);
  delayMicroseconds(10);
  digitalWrite(trigPin, LOW);

  long duration = pulseIn(echoPin, HIGH, 30000);
  if (duration == 0) return -1;

  return duration * 0.034 / 2;
}

void openClaw() {
  clawServo.write(0);
  clawClosed = false;
}

void closeClaw() {
  clawServo.write(180);
  clawClosed = true;
}
