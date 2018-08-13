//(float) R = (1/ (A2D*m + b)) - k
//const float m=0.0001227;
//const float b=-0.010619;
//const float k=4.2;

//const int m1=6899;
//const int b1=-1;
//const int k1=4;

const float m1=158245.0;
const float b1=662.0;
const float k1=120.0;



void setup()
{
Serial.begin(9600);
}



const float filterAlpha=32.0;
float filteredADC;
float offset=0.0;

void loop()
{
filteredADC=((filteredADC*filterAlpha)+analogRead(A0))/(filterAlpha+1.0f);
int distance;
//float distanceFloat=0.0;

//distanceFloat=(1/((float)filteredADC*m+b))+k;

//if(filteredADC>abs(b1)) distance = (((float)m1/((float)filteredADC+(float)b1))-(float)k1);

//=INT(m1/(ADC+b1))-INT(k1)

distance = (int)(m1/(filteredADC+b1))-k1;

//calibration above 80:
if(distance>80.0){
   distance=0.0;
}

//calibration above 70:

if(distance>70.0){
    offset=(distance-70.0)*(16.0/10);
    distance = distance+offset;
}
else offset=0.0;

if(millis()%100==0){
Serial.print(filteredADC);
Serial.print(' ');
Serial.print(distance);
Serial.print(' ');
Serial.print(offset);
Serial.println();

//delay(10);
}
}
