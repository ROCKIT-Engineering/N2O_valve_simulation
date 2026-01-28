#include <AccelStepper.h>

#define STEP_PIN 2
#define DIR_PIN  3

#define STEPS_PER_REV 1600

// 1 = driver mode (DIR + STEP)
AccelStepper stepper(1, STEP_PIN, DIR_PIN);

// V1
/*
float TIMES[] = {3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3};
float REVS[] = {0, .25, 0.375, .5, .75, 1, 1.25, 1.5, 2, 2.5, 3, 4, 5, 6, 7, 8};
*/

// V2

float TIMES[] = {3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3};
float REVS[] = {0, 0.05, 0.1, 0.2, 0.3, .4, 0.5, .75, 1, 1.25, 1.5, 2, 2.5, 3, 4};


int COUNT = sizeof(TIMES) / sizeof(TIMES[0]);

// RED: A+
// BLUE: A-
// YELLOW: B+
// BROWN: B-

void move_to(float rev){
  stepper.moveTo(-(int)(rev * STEPS_PER_REV + .5));
}
void reset(){
  stepper.setCurrentPosition(0);
}

void setup()
{
  pinMode(4, OUTPUT);
  digitalWrite(4, HIGH); // 5V Source

  stepper.setMaxSpeed(32767);     // steps per second (safe start)
  stepper.setAcceleration(32767); // smooth ramp

  reset();
  Serial.begin(9600);
}

void loop()
{
  if (stepper.distanceToGo() == 0)
  {
    Serial.println("V2 Position eingeben (0-8), reset oder auto");
    //String test = Serial.readStringUntil('z');
    while (Serial.available() == 0) {
    // wait here until the user types something
    }
    String ans = Serial.readString();
    ans.trim();
    if (ans == "auto"){
      for (int i = 0; i<COUNT; i++){
        Serial.println("REV:" + String(REVS[i]) + " T:" + String(TIMES[i]));
        unsigned long t2 = millis() + (unsigned long)(TIMES[i] * 1000);
        //Serial.println(t2);
        move_to(REVS[i]);
        while (millis() < t2) {
          stepper.run();
          //Serial.println(millis());
          //delay(500);
        }
      }
      move_to(0);
      return;
    }
    if (ans == "reset"){
      Serial.println("reset");
      reset();
      return;
    }
    float rev = ans.toFloat();
    move_to(rev);

    Serial.println(rev);
  }
  stepper.run();

}