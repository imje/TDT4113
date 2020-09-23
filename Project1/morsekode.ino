const int greenLedPin = 11;
const int yellowLedPin = 10;
const int redLedPin = 6;
const int buttonPin = 4;

int buttonPressedTime = 0;
int buttonReleasedTime = 0;
 
void setup(){
  pinMode( greenLedPin, OUTPUT );
  pinMode( yellowLedPin, OUTPUT );
  pinMode( redLedPin, OUTPUT );
  pinMode( buttonPin, INPUT );
  Serial.begin(9600);
}



void loop(){

  
  while (digitalRead(buttonPin) == HIGH) {
    if (buttonReleasedTime >0) {
      if (buttonReleasedTime >= 10 && buttonReleasedTime < 30) {
        Serial.print(3); //bokstavpause
      }
      else if (buttonReleasedTime >= 30){
        Serial.print(4); //ordpause
      }
      buttonReleasedTime = 0;
    }
    delay(100);
    buttonPressedTime++;
    if (buttonPressedTime <5) {
      digitalWrite(greenLedPin, 40);
      digitalWrite(yellowLedPin, 40);
    }
    if (buttonPressedTime >=5 && buttonPressedTime <10) {
      digitalWrite(redLedPin, 40);
      digitalWrite(greenLedPin, 0);
      digitalWrite(yellowLedPin, 0);
    }
    if (buttonPressedTime >=10) {
      digitalWrite(redLedPin, 40);
      digitalWrite(greenLedPin, 40);
      digitalWrite(yellowLedPin, 40);
    }
  }
  
  while (digitalRead(buttonPin) == LOW) {
    if (buttonPressedTime >0) {
       digitalWrite(redLedPin, 0);
      digitalWrite(greenLedPin, 0);
      digitalWrite(yellowLedPin, 0);
      if (buttonPressedTime < 5) {
        Serial.print(1); //dot
      }
      else if (buttonPressedTime >= 5 && buttonPressedTime <10) {
        Serial.print(2); //dash
      }
      else if (buttonPressedTime > 10) {
        Serial.print(5); //reset
      }
      buttonPressedTime = 0;
    }
    delay(100);
    buttonReleasedTime++;
 }
}

