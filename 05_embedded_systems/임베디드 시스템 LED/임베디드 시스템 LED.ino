#include <Arduino.h>

//115p
/*
void setup() {
  pinMode(LED_BUILTIN, OUTPUT);

}

void loop() {
  digitalWrite(LED_BUILTIN, HIGH);
  delay(500);
  digitalWrite(LED_BUILTIN, LOW);
  delay(500);

}
*/
//117p
// #define LED_R 12

// void setup() {
//   pinMode(LED_R, OUTPUT);

// }

// void loop() {
//   digitalWrite(LED_R, HIGH);
//   delay(500);
//   digitalWrite(LED_R, LOW);
//   delay(500);

// }

//119-120p

/*
#define LED_R 12
#define LED_B 11

unsigned int interval = 500;

void setup() {
  pinMode(LED_R, OUTPUT);
  pinMode(LED_B, OUTPUT);

}

void loop() {
  digitalWrite(LED_R, HIGH);
  digitalWrite(LED_B, LOW);
  delay(interval);
  digitalWrite(LED_R, LOW);
  digitalWrite(LED_B, HIGH);
  delay(interval);

}
*/
/*
//121-122p
const unsigned int LED0 = 12;
const unsigned int LED1 = 11;
const unsigned int LED2 = 10;
const unsigned int LED3 =  9;
const unsigned int LED4 =  8;
const unsigned int LED5 =  7;
const unsigned int LED6 =  6;
const unsigned int LED7 =  5;

unsigned int interval = 500;

void setup() {
  pinMode(LED0, OUTPUT);
  pinMode(LED1, OUTPUT);
  pinMode(LED2, OUTPUT);
  pinMode(LED3, OUTPUT);
  pinMode(LED4, OUTPUT);
  pinMode(LED5, OUTPUT);
  pinMode(LED6, OUTPUT);
  pinMode(LED7, OUTPUT);
}

void loop() {
  digitalWrite(LED0, HIGH);
  delay(interval);
  digitalWrite(LED1, HIGH);
  delay(interval);
  digitalWrite(LED2, HIGH);
  delay(interval);
  digitalWrite(LED3, HIGH);
  delay(interval);
  digitalWrite(LED4, HIGH);
  delay(interval);
  digitalWrite(LED5, HIGH);
  delay(interval);
  digitalWrite(LED6, HIGH);
  delay(interval);
  digitalWrite(LED7, HIGH);
  delay(interval);

  digitalWrite(LED0, LOW);
  digitalWrite(LED1, LOW);
  digitalWrite(LED2, LOW);
  digitalWrite(LED3, LOW);
  digitalWrite(LED4, LOW);
  digitalWrite(LED5, LOW);
  digitalWrite(LED6, LOW);
  digitalWrite(LED7, LOW);
  delay(interval);
}
*/
/*
//123-125p
const unsigned int LED[8] =  {12, 11, 10, 9, 8, 7, 6, 5};

unsigned int interval = 500;

void setup(){
  for(int i=0; i<8; i++){ 
  pinMode(LED[i], OUTPUT);
  }
}

void loop() {
  for(int i=0; i<8; i++){
    digitalWrite(LED[i], HIGH);
    delay(interval);
  }

  clear_all_LED();
  delay(interval);
}

void clear_all_LED() {
  for(int i=0; i<8; i++) {
    digitalWrite(LED[i], LOW);
  }
}
*/
/*
//126-127p
const unsigned int LED[8] =  {12, 11, 10, 9, 8, 7, 6, 5};

unsigned int interval = 500;

void setup(){
  for(int i=0; i<8; i++){ 
  pinMode(LED[i], OUTPUT);
  }
}

void loop() {
  for(int i=0; i<8; i++){
    int j = 7 - i;
    digitalWrite(LED[j], HIGH);
    delay(interval);
  }

  clear_all_LED();
  delay(interval);
}

void clear_all_LED() {
  for(int i=0; i<8; i++) {
    digitalWrite(LED[i], LOW);
  }
}
*/
/*
//130p
const unsigned int LED[8] =  {12, 11, 10, 9, 8, 7, 6, 5};

unsigned int interval = 500;

void setup(){
  for(int i=0; i<8; i++){ 
  pinMode(LED[i], OUTPUT);
  }
}

void loop() {
  for(int i=0; i<8; i++){
    //int j = i - 1;
    //if(j<0) j += 8;
    int j = (i<1) ? (i - 1 + 8) : (i -1);
    digitalWrite(LED[j], LOW);
    digitalWrite(LED[i], HIGH);
    delay(interval);
  }
}
*/
/*
//131p
const unsigned int LED[8] =  {12, 11, 10, 9, 8, 7, 6, 5};

unsigned int interval = 500;

void setup(){
  for(int i=0; i<8; i++){ 
  pinMode(LED[i], OUTPUT);
  }
}

void loop() {
  for(int i=0; i<8; i++){
      int j = (i - 1 + 8) % 8;
    digitalWrite(LED[j], LOW);
    digitalWrite(LED[i], HIGH);
    delay(interval);
  }
}
*/
/*
//132p
#define  N_LED 8

const unsigned int LED[8] =  {12, 11, 10, 9, 8, 7, 6, 5};

unsigned int interval = 500;

void setup(){
  for(int i=0; i<8; i++){ 
  pinMode(LED[i], OUTPUT);
  }
}

void loop() {
  for(int i=0; i<N_LED; i++){
      int j = (i - 1 + N_LED) % N_LED;
    digitalWrite(LED[j], LOW);
    digitalWrite(LED[i], HIGH);
    delay(interval);
  }
}
*/
/*
//133p
#define  N_LED 8

const unsigned int LED[8] =  {12, 11, 10, 9, 8, 7, 6, 5};

unsigned int interval = 500;

void setup(){
  for(int i=0; i<8; i++){ 
  pinMode(LED[i], OUTPUT);
  }
}

void loop() {
  for(int i=0; i<N_LED; i++){
      int j = (i - 1 + N_LED) % N_LED;
    digitalWrite(LED[j], LOW);
    digitalWrite(LED[N_LED-1-j], LOW);
    digitalWrite(LED[i], HIGH);
    digitalWrite(LED[N_LED-1-i], HIGH);
    delay(interval);
  }
}
*/

//134-135p
#define  N_LED 8

const unsigned int LED[8] =  {12, 11, 10, 9, 8, 7, 6, 5};

unsigned int interval = 500;

void setup(){
  for(int i=0; i<8; i++){ 
  pinMode(LED[i], OUTPUT);
  }
}

void loop() {
  for(int i=0; i<N_LED; i++){
      int j = (i - 1 + N_LED) % N_LED;
      //if((N_LED%2 == 0) && (N_LED/2 == i)) continue;
      if((N_LED%2 == 0) && (N_LED>>1 == i)) continue;
    digitalWrite(LED[j], LOW);
    digitalWrite(LED[N_LED-1-j], LOW);
    digitalWrite(LED[i], HIGH);
    digitalWrite(LED[N_LED-1-i], HIGH);
    delay(interval);
  }
}