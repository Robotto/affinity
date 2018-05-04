
#include <ESP8266WiFi.h>
#include <WiFiUdp.h>
#include <WiFiClient.h>
#include <WiFiManager.h>          //https://github.com/tzapu/WiFiManager
#include <ArduinoOTA.h>
#include <Ticker.h>
#include <SoftwareSerial.h>
//                   RX  TX  INVERT BUFFER_SIZE
SoftwareSerial swSer(D5, D6, true, 64);

Ticker blinker; //to asynchronously blink an LED

unsigned long distance_milimeter;
static unsigned int pingPin = D0;
static unsigned int LEDPin = D1;

int first;
int threshold=50;

void configModeCallback (WiFiManager *myWiFiManager) {
  Serial.println("Entered config mode");
  Serial.println("AP: " + myWiFiManager->getConfigPortalSSID());
  Serial.println("IP: " + WiFi.softAPIP().toString());
}

void setup(void) {

  WiFi.hostname("ESPing_01_01");

  pinMode(LEDPin, OUTPUT);

  blinker.attach(0.1, blink, LEDPin);

  
  //WiFi.persistent(false);
  //WiFi.mode(WIFI_STA); //prevent random APs from forming?!

  Serial.begin(115200); //DEBUG // PC
  swSer.begin(9600); //sonar
  Serial.println("Hello!");
  
  //WiFiManager
  //Local intialization. Once its business is done, there is no need to keep it around
  WiFiManager wifiManager;
  Serial.println("Connecting to wifi..");
  wifiManager.setAPCallback(configModeCallback); //set callback that gets called when connecting to previous WiFi fails, and enters Access Point mode
  wifiManager.setConnectTimeout(60); //try to connect to known wifis for a long time before defaulting to AP mode
  
  //fetches ssid and pass and tries to connect
  //if it does not connect it starts an access point with the specified name
  //here  "ESPNFC"
  //and goes into a blocking loop awaiting configuration
  if (!wifiManager.autoConnect("ESPing_01")) {
    Serial.println("failed to connect and hit timeout");
    ESP.restart(); //reset and try again, or maybe put it to deep sleep 
  }

  //OTA:
  // Port defaults to 8266
  // ArduinoOTA.setPort(8266);
  // Hostname defaults to esp8266-[ChipID]
  ArduinoOTA.setHostname("ESPing_01");
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

  Serial.println("ESPing_01 ONLINE");

  pinMode(pingPin,INPUT);

  delay(500); //make sure the maxbotix sensor is ready

  //establish baseline for about 5 seconds.
  first = getDistance();
  delay(1000);
  while(abs(first-getDistance())>50) //5cm
  {
    delay(1000);
    first=getDistance();//wait til distance measurement settles to within 5cm
  }

  blinker.detach();
  //analogWrite(LEDPin,900);
  //digitalWrite(LEDPin,LOW); //led ON.
  digitalWrite(LEDPin,HIGH); //led OFF.


}

unsigned long printTime=0;
unsigned long pulsestart;

void loop(void) {

distance_milimeter = getDistance();


//if baseline is broken, report.

//reestablish baseline?

if(abs(first-distance_milimeter)>threshold) digitalWrite(LEDPin,LOW); //LED ON
else digitalWrite(LEDPin,HIGH); 

if(millis()-printTime>20){
  Serial.println(distance_milimeter);
  printTime=millis();
}


  
}

int getDistance()
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
  return measurement;

}

return 0; //if no serial data available.

}

void blink(unsigned int pin){
  digitalWrite(pin, !digitalRead(pin));     // set pin to the opposite state
}