#include <Ticker.h>
#include <SoftwareSerial.h>
//                   RX  TX  INVERT BUFFER_SIZE
SoftwareSerial swSer(D5, D6, true, 64);

Ticker greenBlinker; //to asynchronously blink an LED
Ticker redBlinker; //to asynchronously blink an LED


uint16_t distance_milimeter;
static int greenLEDPin = D1; //active low, a 68ohm resistor yelds 17.6mA
static int redLEDPin = D7;   //active low, a 68ohm resistor yelds 19.6mA
static int btnPin = D2; //active low, configured as INPUT_PULLUP


uint16_t first;
uint16_t threshold=100;

float vBatt=4.2;
bool doBatteryCheck=true;



void setup(void) {

  Serial.begin(115200); //DEBUG // PC
  Serial.println("Hello!");
  

 
  pinMode(redLEDPin, OUTPUT);
  pinMode(greenLEDPin, OUTPUT);
  pinMode(btnPin, INPUT_PULLUP);

  digitalWrite(redLEDPin,HIGH);

  delay(200);

  if(digitalRead(btnPin)==LOW) doBatteryCheck=false; //if button is held on reset.

  measureBatteryVoltage();  

  Serial.print("vBatt="); Serial.println(vBatt);

  if(vBatt<3.6) {
    redBlinker.attach(0.1,blink, redLEDPin);
    while(1) yield(); //halt forever.
  }

  greenBlinker.attach(0.1, blink, greenLEDPin);

  
  //WiFi.persistent(false);
  //WiFi.mode(WIFI_STA); //prevent random APs from forming?!

  swSer.begin(9600); //sonar

  

  delay(2000); //make sure the maxbotix sensor is ready

  //establish baseline for about 5 seconds.
  first = getDistance();
  delay(1000);
  while(abs(first-getDistance())>100) //10cm
  {
    delay(1000);
    first=getDistance();//wait til distance measurement settles to within 5cm
  }

  greenBlinker.detach();
  //analogWrite(greenLEDPin,900);
  digitalWrite(greenLEDPin,LOW); //led ON.
  //digitalWrite(greenLEDPin,HIGH); //led OFF.

  Serial.print("first="); Serial.println(first);
}

//unsigned long printTime=0;
//unsigned long pulsestart;
bool txHandled = false;

void loop(void) {

measureBatteryVoltage();  

if(vBatt<3.6) {
    redBlinker.attach(0.1, blink , redLEDPin); //flash the red LED and halt.
    while(1); //halt forever.
  }


if(vBatt<3.7) digitalWrite(redLEDPin,LOW); //turn on the red LED
else digitalWrite(redLEDPin,HIGH); //turn off the red LED
 

if(swSer.available()) swSer.read(); //keep buffer clean.

distance_milimeter = getDistance();
while(distance_milimeter<30) distance_milimeter = getDistance();

//Serial.print("distance_milimeter="); Serial.println(distance_milimeter);

//if baseline is broken, report.
int diff=first-distance_milimeter;
if (diff<0) diff=diff*(-1);
//  Serial.print("diff="); Serial.println(diff);

while(diff>threshold) { //TRIGGERED send distance to server!
  
  Serial.println("hit!");

  if(swSer.available()) swSer.read(); //keep buffer clean.


  yield();

  if(!txHandled){ //but only once.
  digitalWrite(greenLEDPin,HIGH); //LED OFF
//  sendDistanceUDP(distance_milimeter);
  txHandled=true;
  Serial.println(distance_milimeter);
  
  }

    distance_milimeter = getDistance();
  diff=first-distance_milimeter;
  if (diff<0) diff=diff*(-1);

}
    
if(txHandled){    
    digitalWrite(greenLEDPin,LOW); //LED ON 
    txHandled=false; //reset transmit flag.
    Serial.println("Release");
//if(millis()-printTime>20){
//  Serial.println(distance_milimeter);
//  printTime=millis();
//}
}

if(digitalRead(btnPin)==LOW) resetBaseline();
  
}

unsigned int getDistance()
{

  /*
while(digitalRead(pingPin)==HIGH); //wait for fall.

//if(digitalRead(pingPin)==LOW) {
  while(digitalRead(pingPin)==LOW); //wait for rise
  pulsestart=micros(); 
  while(digitalRead(pingPin)==HIGH){} //wait for fall
  return micros()-pulsestart;
//  }*/

if(swSer.available()) 
{
  //char rx=swSer.read();
  //if(rx=='\r') Serial.write('\n');
  //if(rx!='R')Serial.write(rx);

  while(swSer.read()!='R'); //wait for beginning of measurement
  
  char rx=swSer.read();
  Serial.print(rx);
  
  while(rx!='R') {
      if(swSer.available()){
      rx=swSer.read();
      Serial.print(rx);}
  }
  int measurement = swSer.parseInt();
  //Serial.println(measurement);
  return measurement;

}

return 0; //if no serial data available.

}

void blink(int pin){
  digitalWrite(pin, !digitalRead(pin));     // set pin to the opposite state
}

void resetBaseline(void){
  greenBlinker.attach(0.1, blink, greenLEDPin);  
  first = getDistance();
  delay(1000);
  while(abs(first-getDistance())>100) //10cm
  {
    delay(1000);
    first=getDistance();//wait til distance measurement settles to within 5cm
  }
  Serial.print("baseline: "); Serial.println(first);
  greenBlinker.detach();
}

void measureBatteryVoltage(void){
  float analogSum;
  for(int i=0;i<16;i++) analogSum+=analogRead(A0);
  float battRaw=analogSum/16.0;
  if(doBatteryCheck) vBatt = battRaw * (4.2 / 1023.0);
}