
#include <ESP8266WiFi.h>
#include <WiFiUdp.h>
#include <WiFiClient.h>
#include <WiFiManager.h>          //https://github.com/tzapu/WiFiManager
#include <ArduinoOTA.h>
#include <Ticker.h>
#include <SoftwareSerial.h>
//                   RX  TX  INVERT BUFFER_SIZE
SoftwareSerial swSer(D5, D6, true, 64);

Ticker greenBlinker; //to asynchronously blink an LED
Ticker redBlinker; //to asynchronously blink an LED

//UDP stuff:
WiFiUDP Udp;
//const unsigned int remotePort = 1337;
const int UDP_PACKET_SIZE = 8; //change to whatever you need.
byte packetBuffer[ UDP_PACKET_SIZE ]; //buffer to hold outgoing packets


const char* host = "192.168.1.107";
const int hostPort = 5005;

uint16_t distance_milimeter;
static int greenLEDPin = D1; //active low, a 68ohm resistor yelds 17.6mA
static int redLEDPin = D7;   //active low, a 68ohm resistor yelds 19.6mA
static int btnPin = D2; //active low, configured as INPUT_PULLUP

//sensors on A and B return inches, C and D returns mm.
const String deviceName = "D";
const char* apName = "ESPing_D";
const char nodeID='D';

uint16_t first;
uint16_t threshold=100;

float vBatt=4.2;
bool doBatteryCheck=true;


void configModeCallback (WiFiManager *myWiFiManager) {
  Serial.println("Entered config mode");
  Serial.println("AP: " + myWiFiManager->getConfigPortalSSID());
  Serial.println("IP: " + WiFi.softAPIP().toString());
}

void setup(void) {

  Serial.begin(115200); //DEBUG // PC
  Serial.println("Hello!");
  

 
  WiFi.hostname(apName);
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

  //WiFiManager
  //Local intialization. Once its business is done, there is no need to keep it around
  WiFiManager wifiManager;
  Serial.println("Connecting to wifi..");
  wifiManager.setAPCallback(configModeCallback); //set callback that gets called when connecting to previous WiFi fails, and enters Access Point mode
  wifiManager.setConnectTimeout(30); //try to connect to known wifis for a long time before defaulting to AP mode
  
  //fetches ssid and pass and tries to connect
  //if it does not connect it starts an access point with the specified name
  //here  "ESPNFC"
  //and goes into a blocking loop awaiting configuration
  if (!wifiManager.autoConnect(apName)) {
    Serial.println("failed to connect and hit timeout");
    ESP.restart(); //reset and try again, or maybe put it to deep sleep 
  }

  //OTA:
  // Port defaults to 8266
  // ArduinoOTA.setPort(8266);
  // Hostname defaults to esp8266-[ChipID]
  ArduinoOTA.setHostname(apName);
  // No authentication by default
  //ArduinoOTA.setPassword((const char *)"1804020311");
  //ArduinoOTA.setPasswordHash((const char *)"77ca9ed101ac99e43b6842c169c20fda");

  ArduinoOTA.onStart([]() {
    Serial.println("OTA START!");
    delay(500);
  });

  ArduinoOTA.onEnd([]() {
  	Serial.println("OTA End.. brace for reset");
  	ESP.restart();
  });

  ArduinoOTA.onProgress([](unsigned int progress, unsigned int total) {
    Serial.printf("Progress: %u%%\r", (progress / (total / 100)));
    });

  ArduinoOTA.onError([](ota_error_t error) {
    String buffer=String("Error[") + String(error) + String("]: ");
    if (error == OTA_AUTH_ERROR) buffer+=String("Auth Failed");
    else if (error == OTA_BEGIN_ERROR) buffer+=String("Begin Failed");
    else if (error == OTA_CONNECT_ERROR) buffer+=String("Connect Failed");
    else if (error == OTA_RECEIVE_ERROR) buffer+=String("Receive Failed");
    else if (error == OTA_END_ERROR) buffer+=String("End Failed");
    
    Serial.println(buffer);
  });

  ArduinoOTA.begin();

  Serial.println("ESPing_" + deviceName + " ONLINE");


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
  
  //Serial.println("hit!");

  if(swSer.available()) swSer.read(); //keep buffer clean.


  yield();

  if(!txHandled){ //but only once.
  digitalWrite(greenLEDPin,HIGH); //LED OFF
  sendDistanceUDP(distance_milimeter);
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
  int measurement = swSer.parseInt();
  //Serial.println(measurement);

  //sensors on A and B return inches, sensors on C and D return mm.
  if(nodeID=='C' || nodeID=='D') return measurement;

  if(nodeID=='A' || nodeID=='B') return int((float)measurement*25.4);
  
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

void sendDistanceUDP(unsigned int distance)
{
  memset(packetBuffer, 0, UDP_PACKET_SIZE);
  
  //String distanceString = String(distance, DEC);

  //if(distanceString.length()<UDP_PACKET_SIZE){ //safety. make buffer bigger if this fails.

  packetBuffer[0]=nodeID; 
  
//unsigned integer format:  
// aaaaaaaa bbbbbbbb

  packetBuffer[1]=(distance>>8);//&0x00ff; //aaaaaaaa
  packetBuffer[2]=distance;    //bbbbbbbb
  packetBuffer[3]='\0';
  
  /*
  for(int i=0;i<distanceString.length();i++){

  packetBuffer[i+1]=distanceString.charAt(i); //there's a nodeID at place 0.
  }

  packetBuffer[distanceString.length()+1]='\n'; 

  }*/
  //else Serial.println("BIG FAIL! distance string is longer bigger than UDP_PACKET_SIZE!!: distanceString.length()=" + String(distanceString.length()) + ". UDP_PACKET_SIZE=" + String(UDP_PACKET_SIZE) );
  //Udp.beginPacket(doorIP, remotePort);
  Udp.beginPacket(host,hostPort);
  
  //Udp.beginPacket(doorAddress,remotePort);
  //Udp.write(packetBuffer, distanceString.length()+2); //nodeID at start, newline at end.
  Udp.write(packetBuffer, 4); //nodeID at start
  Udp.endPacket();
  Serial.print("TX:"); Serial.println(distance);
  
}

void measureBatteryVoltage(void){
  float analogSum;
  for(int i=0;i<16;i++) analogSum+=analogRead(A0);
  float battRaw=analogSum/16.0;
  if(doBatteryCheck) vBatt = battRaw * (4.2 / 1023.0);
}