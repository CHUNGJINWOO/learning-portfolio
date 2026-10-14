/*
//137-138p
#define  N_SEG 8

const unsigned int FND[N_SEG] =  {12, 11, 5, 8, 7, 9, 10, 6};

unsigned int interval = 500;

void setup(){
  for(int i=0; i<N_SEG; i++) { 
  pinMode(FND[i], OUTPUT);
  }
}

void loop() {
  for(int i=0; i<N_SEG; i++) {
    digitalWrite(FND[i], HIGH);
    delay(interval);
  }

  clear_all_LED();
  delay(interval);
}

void clear_all_LED() {
  for(int i=0; i<N_SEG; i++) {
    digitalWrite(FND[i], LOW);
  }
}
*/

/*
//139p
#define  N_SEG 8

const unsigned int FND[N_SEG] =  {12, 11, 5, 8, 7, 9, 10, 6};
const unsigned int num0[N_SEG] =  {1, 1, 1, 1, 1, 1, 0, 0};

unsigned int interval = 500;

void setup(){
  for(int i=0; i<N_SEG; i++) { 
  pinMode(FND[i], OUTPUT);
  }
}

void loop() {
  for(int i=0; i<N_SEG; i++) {
    digitalWrite(FND[i], num0[i]);
  }
}
*/

//140-141p
#define  N_SEG 8

const unsigned int FND[N_SEG] =  {12, 11, 5, 8, 7, 9, 10, 6};
const unsigned int num[17][N_SEG] =  {
  {1, 1, 1, 1, 1, 1, 0, 0}, // 0
  {0, 1, 1, 0, 0, 0, 0, 0}, // 1
  {1, 1, 0, 1, 1, 0, 1, 0}, // 2 
  {1, 1, 1, 1, 0, 0, 1, 0}, // 3
  {0, 1, 1, 0, 0, 1, 1, 0}, // 4
  {1, 0, 1, 1, 0, 1, 1, 0}, // 5
  {1, 0, 1, 1, 1, 1, 1, 0}, // 6
  {1, 1, 1, 0, 0, 0, 0, 0}, // 7
  {1, 1, 1, 1, 1, 1, 1, 0}, // 8
  {1, 1, 1, 1, 0, 1, 1, 0}, // 9
  {1, 1, 1, 0, 1, 1, 1, 0}, // A
  {0, 0, 1, 1, 1, 1, 1, 0}, // b
  {1, 0, 0, 1, 1, 1, 0, 0}, // C
  {0, 1, 1, 1, 1, 0, 1, 0}, // d
  {1, 0, 0, 1, 1, 1, 1, 0}, // E
  {1, 0, 0, 0, 1, 1, 1, 0}, // F
  {0, 0, 0, 0, 0, 0, 0, 1}  // DP
  };


unsigned int interval = 1000;

void setup(){
  for(int i=0; i<N_SEG; i++) { 
  pinMode(FND[i], OUTPUT);
  }
}

void loop() {
  for(int i=0; i<17; i++) {
    displayFND(i);
    delay(interval);
  }
}

void displayFND(int n) {
  for(int i=0; i<N_SEG; i++) {
    digitalWrite(FND[i], num[n][i]);
  }
}