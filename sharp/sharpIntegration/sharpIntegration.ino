#include <ESP8266WiFi.h>
#include <WiFiUdp.h>
#include <WiFiManager.h>          //https://github.com/tzapu/WiFiManager
#include <ArduinoOTA.h>

#include <MCP3008.h>
#include <medianFilter.h>
#include <Ticker.h>


// define pin connections
#define CS_PIN D0
#define CLOCK_PIN D7
#define MOSI_PIN D5
#define MISO_PIN D6

#define NUM_sharp_GPY_SENSORS 8
#define FILTERALPHA 128.0

MCP3008 adc(CLOCK_PIN, MOSI_PIN, MISO_PIN, CS_PIN);

Ticker greenBlinker; //to asynchronously blink an LED

//UDP stuff:
WiFiUDP Udp;
const int UDP_PACKET_SIZE = 12; //change to whatever you need.
byte packetBuffer[ UDP_PACKET_SIZE ]; //buffer to hold outgoing packets


const char* host = "192.168.1.107";
const int hostPort = 5005;

static int greenLEDPin = D2; //active low
static int redLEDPin = D1;   //active low


void blink(int pin){
  digitalWrite(pin, !digitalRead(pin));     // set pin to the opposite state
}

//16 x coordinates:
const int interSensorDistance = 6.4294; //sensor

typedef struct 
{
const float m;
const float b;
const float k;
const float calibration_offset;
const float xCoordinate;
float filteredADC;
float offset;
int distance;
medianFilter Filter; //you can do that?!
} sharp_GPY;

sharp_GPY S0={.m=158245.0,.b=662.0,.k=120.0,.calibration_offset=0,.xCoordinate=0*interSensorDistance};
sharp_GPY S1={.m=156154.0,.b=650.0,.k=120.0,.calibration_offset=0,.xCoordinate=1*interSensorDistance};
sharp_GPY S2={.m=159692.0,.b=670.0,.k=120.0,.calibration_offset=0,.xCoordinate=2*interSensorDistance};
sharp_GPY S3={.m=166661.0,.b=707.0,.k=120.0,.calibration_offset=0,.xCoordinate=3*interSensorDistance};
sharp_GPY S4={.m=158214.0,.b=659.0,.k=120.0,.calibration_offset=0,.xCoordinate=4*interSensorDistance};
sharp_GPY S5={.m=169631.0,.b=741.0,.k=120.0,.calibration_offset=0,.xCoordinate=5*interSensorDistance};
sharp_GPY S6={.m=160741.0,.b=690.0,.k=120.0,.calibration_offset=0,.xCoordinate=6*interSensorDistance};
sharp_GPY S7={.m=155883.0,.b=643.0,.k=120.0,.calibration_offset=0,.xCoordinate=7*interSensorDistance};

//A quick explanation of struct pointers: http://www.eskimo.com/~scs/cclass/int/sx1d.html
sharp_GPY *sharp_GPY_map[NUM_sharp_GPY_SENSORS]={&S0,&S1,&S2,&S3,&S4,&S5,&S6,&S7}; //array of pointers to structs... 

void configModeCallback (WiFiManager *myWiFiManager) {
  Serial.println("Entered config mode");
  Serial.println("AP: " + myWiFiManager->getConfigPortalSSID());
  Serial.println("IP: " + WiFi.softAPIP().toString());
}

void setup()
{
for(int i=0 ; i<NUM_sharp_GPY_SENSORS ; i++){
    sharp_GPY_map[i]->Filter.begin();
}
Serial.begin(115200);

 WiFi.hostname("sensorBar");
  pinMode(redLEDPin, OUTPUT);
  pinMode(greenLEDPin, OUTPUT);
 
 digitalWrite(redLEDPin,LOW); //On

  greenBlinker.attach(0.1, blink, greenLEDPin);

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
  if (!wifiManager.autoConnect("sensorBar")) {
    Serial.println("failed to connect and hit timeout");
    ESP.restart(); //reset and try again, or maybe put it to deep sleep 
  }

  //OTA:
  // Port defaults to 8266
  // ArduinoOTA.setPort(8266);
  // Hostname defaults to esp8266-[ChipID]
  ArduinoOTA.setHostname("sensorBar");
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

  Serial.println("SensorBar ONLINE");
  greenBlinker.detach();


  digitalWrite(greenLEDPin,HIGH); //led OFF.
  
  

}

bool txHandled = false;
bool triggered = false;
unsigned long triggerTime=0;

void loop()
{

ArduinoOTA.handle();

float xAVG=0.0;
float yAVG=0.0;
int numTriggeredSensors=0;


for(int i=0 ; i<NUM_sharp_GPY_SENSORS ; i++)
    {
        yield(); //let the wifi core do its thing.

    //sharp_GPY_map[i]->filteredADC=((sharp_GPY_map[i]->filteredADC*FILTERALPHA)+analogRead(A0))/(FILTERALPHA+1.0f);
    //sharp_GPY_map[i]->filteredADC=((sharp_GPY_map[i]->filteredADC*FILTERALPHA)+adc.readADC(i))/(FILTERALPHA+1.0f);
    sharp_GPY_map[i]->filteredADC=sharp_GPY_map[i]->Filter.run(((sharp_GPY_map[i]->filteredADC*FILTERALPHA)+adc.readADC(i))/(FILTERALPHA+1.0f));
    sharp_GPY_map[i]->distance = (int)(sharp_GPY_map[i]->m/(sharp_GPY_map[i]->filteredADC+sharp_GPY_map[i]->b))-sharp_GPY_map[i]->k;

/*
//calibration above 70:
    if(sharp_GPY_map[i]->distance>70.0){
        sharp_GPY_map[i]->offset=(sharp_GPY_map[i]->distance-70.0)*(16.0/10);
        sharp_GPY_map[i]->distance = sharp_GPY_map[i]->distance+sharp_GPY_map[i]->offset;
        }
    else sharp_GPY_map[i]->offset=0.0;
    
*/
    //calibration above 70:
    if(sharp_GPY_map[i]->distance>79.0){
        sharp_GPY_map[i]->distance=0.0;
        }

     if(sharp_GPY_map[i]->distance<0.0){
        sharp_GPY_map[i]->distance=0.0;
        }   
    
    //add together 
    if(sharp_GPY_map[i]->distance>0.0) 
        {
        xAVG+=sharp_GPY_map[i]->xCoordinate;
        yAVG+=sharp_GPY_map[i]->distance;
        numTriggeredSensors++;
        }
    } //end of iteration through sensors.

    if(numTriggeredSensors==0) triggered=false;

    if(numTriggeredSensors>0){

        xAVG=xAVG/(float)numTriggeredSensors;
        yAVG=yAVG/(float)numTriggeredSensors;

        if(triggered==false){
            triggered=true;
            Serial.println("Triggered!");
            triggerTime=millis();
        }
    }
    

    if(triggered==true && millis()>triggerTime+500 && txHandled==false){

            Serial.println("Clamp");
            digitalWrite(greenLEDPin,LOW); //LED ON
            sendDistanceUDP(xAVG,yAVG);
            txHandled=true;

            /*Serial.print(xAVG);
            Serial.print(' ');
            Serial.println(yAVG);*/
    }

    if(triggered==false && txHandled==true){    
            digitalWrite(greenLEDPin,HIGH); //LED OFF
            txHandled=false; //reset transmit flag.
            Serial.println("Release");
        }



}



void sendDistanceUDP(float x, float y)
{
  memset(packetBuffer, 0, UDP_PACKET_SIZE);

  char txString[UDP_PACKET_SIZE];
  //                "E,xx.x,yy.y\0" //12 chars
  sprintf(txString,"E,%.1f,%.1f\n",x,y);

  //if(distanceString.length()<UDP_PACKET_SIZE){ //safety. make buffer bigger if this fails.
  Serial.print("sizeof(txString): ");
  Serial.println(sizeof(txString));

    for(int i=0;i<sizeof(txString);i++){
        packetBuffer[i]=txString[i];      
    }
  
  //else Serial.println("BIG FAIL! distance string is longer bigger than UDP_PACKET_SIZE!!: distanceString.length()=" + String(distanceString.length()) + ". UDP_PACKET_SIZE=" + String(UDP_PACKET_SIZE) );
  //Udp.beginPacket(doorIP, remotePort);
  Udp.beginPacket(host,hostPort);

  //Udp.beginPacket(doorAddress,remotePort);
  //Udp.write(packetBuffer, distanceString.length()+2); //nodeID at start, newline at end.
  Udp.write(packetBuffer, UDP_PACKET_SIZE ); //nodeID at start
  Serial.print("TX: ");
  Serial.println(txString);
  Udp.endPacket();
  //Serial.print("TX:"); Serial.println(distance);
  
}

