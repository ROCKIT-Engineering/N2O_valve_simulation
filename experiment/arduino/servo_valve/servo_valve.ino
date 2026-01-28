#include <Servo.h>
Servo s;

// V1
float TIMES[] = {3, 3, 3, 3, 3};
float ANGLES[] = {0, 5, 10, 20, 45};

int COUNT = sizeof(TIMES) / sizeof(TIMES[0]);
float OVERSHOOT = 3.0;
int OVERSHOOT_DELAY = 100;

// Servo Constants
int maxAngle = 100;
int startAngle = 0;
int revTime = 1; // in s / 90
int pulsWidth1 = 1000;
int pulsWidth2 = 2000;
int pulsTravel = 100;
//100, 1000, 2000
// Servo State Variables
int currentAngle = -1;
int offsetAngle = 0;

//Wiring:
// Pin 9: Servo Signal

void setup() {
  Serial.begin(9600);
  s.attach(9, pulsWidth1, pulsWidth2);
  setServoAngle(startAngle);
}

void setServoAngle(float angle) {
  if (currentAngle == angle){
    return;
  }
  float realAngle = angle + offsetAngle;
  realAngle = constrain(realAngle, 0, maxAngle);
  if (realAngle != angle + offsetAngle){
    Serial.println("ERROR: " + String(angle) + " not in "+  String(-offsetAngle) + " - " + String(maxAngle - offsetAngle));
  }
  int overshootSign = 1;
  if (angle < currentAngle){
    overshootSign = -1;
  }
  else if (currentAngle == -1){
    overshootSign = 0;
  }
  int us_final = map(realAngle, 0, pulsTravel, pulsWidth1, pulsWidth2);
  int us_overshoot = map(realAngle + overshootSign * OVERSHOOT, 0, pulsTravel, pulsWidth1, pulsWidth2);
  
  s.writeMicroseconds(us_overshoot);

  // Wait
  float angleTravel = abs(angle - currentAngle);
  if (currentAngle == -1){
    angleTravel = max(abs(angle), abs(angle - maxAngle));
  }
  delay(int(angleTravel / maxAngle * revTime * 1000) + OVERSHOOT_DELAY);

  s.writeMicroseconds(us_final);
  currentAngle = angle;
}

void setServoAngleAndWait(float angle){
  setServoAngle(angle);
}

void reset(){
  if (currentAngle == -1){
    Serial.println("Error: current position is undefined");
    return;
  }
  offsetAngle += currentAngle;
  currentAngle = 0; 
  Serial.println("New offset: " + String(offsetAngle) + " Valid Angles: " + String(-offsetAngle) + "-" + String(maxAngle - offsetAngle));
}

void loop()
{
  Serial.println("V1 Winkel eingeben " + String(-offsetAngle) + " - " + String(maxAngle - offsetAngle) + ", reset oder auto");
  while (Serial.available() == 0) {
  // wait here until the user types something
  }
  String ans = Serial.readString();
  ans.trim();
  if (ans == "auto"){
    for (int i = 0; i < COUNT; i++){
      Serial.println("ANGLE:" + String(ANGLES[i]) + " T:" + String(TIMES[i]));
      unsigned long t2 = millis() + (unsigned long)(TIMES[i] * 1000);
      setServoAngleAndWait(ANGLES[i]);
      if(millis() > t2){
        Serial.println("Real T: " + String((millis() - t2 + (unsigned long)(TIMES[i] * 1000)) / 1000.0) + "s");
      }
      while (millis() < t2) {
        delay(10);
      }
    }
    setServoAngleAndWait(0);
    return;
  }
  if (ans == "reset"){
    Serial.println("reset");
    reset();
    return;
  }
  float angle = ans.toFloat();
  Serial.println("GOTO: " + String(angle));
  setServoAngle(angle);
}