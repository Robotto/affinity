#define NUM_sharp_GPY_SENSORS 8
#define FILTERALPHA 32.0

typedef struct //stick positions
{
const float m;
const float b;
const float k;
float filteredADC;
float offset;
int distance;
} sharp_GPY;

sharp_GPY S0={.m=158245.0,.b=662.0,.k=120.0};
sharp_GPY S1={.m=156154.0,.b=650.0,.k=120.0};
sharp_GPY S2={.m=159692.0,.b=670.0,.k=120.0};
sharp_GPY S3={.m=166661.0,.b=707.0,.k=120.0};
sharp_GPY S4={.m=158214.0,.b=659.0,.k=120.0};
sharp_GPY S5={.m=169631.0,.b=741.0,.k=120.0};
sharp_GPY S6={.m=160741.0,.b=690.0,.k=120.0};
sharp_GPY S7={.m=155883.0,.b=764.0,.k=120.0};

//A quick explanation of struct pointers: http://www.eskimo.com/~scs/cclass/int/sx1d.html
sharp_GPY *sharp_GPY_map[NUM_sharp_GPY_SENSORS]={&S0,&S1,&S2,&S3,&S4,&S5,&S6,&S7}; //array of pointers to structs... 

void setup()
{

Serial.begin(9600);
}


//const float filterAlpha=32.0;

void loop()
{
for(int i=0 ; i<NUM_sharp_GPY_SENSORS ; i++)
    {
    sharp_GPY_map[i]->filteredADC=((sharp_GPY_map[i]->filteredADC*FILTERALPHA)+analogRead(A0))/(FILTERALPHA+1.0f);
    sharp_GPY_map[i]->distance = (int)(sharp_GPY_map[i]->m/(sharp_GPY_map[i]->filteredADC+sharp_GPY_map[i]->b))-sharp_GPY_map[i]->k;

    //calibration above 80:
    if(sharp_GPY_map[i]->distance>80.0){
        sharp_GPY_map[i]->distance=0.0;
        }

//calibration above 70:

    if(sharp_GPY_map[i]->distance>70.0){
        sharp_GPY_map[i]->offset=(sharp_GPY_map[i]->distance-70.0)*(16.0/10);
        sharp_GPY_map[i]->distance = sharp_GPY_map[i]->distance+sharp_GPY_map[i]->offset;
        }
    else sharp_GPY_map[i]->offset=0.0;
    }


if(millis()%100==0){ //printout every 100ms
    for(int i=0 ; i<NUM_sharp_GPY_SENSORS ; i++)
    {
        Serial.print(sharp_GPY_map[i]->distance);
        if(i!=NUM_sharp_GPY_SENSORS-1) Serial.print(' ');
    }
    
    Serial.println();

    }

}