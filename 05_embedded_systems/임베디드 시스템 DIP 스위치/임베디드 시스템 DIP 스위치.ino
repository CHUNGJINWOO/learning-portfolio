
//161-162p
#define N 8
int DIP[N] = {9, 8, 7, 6, 5, 4, 3, 2};

void setup() { 
  pinMode(LED_BUILTIN, OUTPUT);
  for(int i=0; i<N; i++) {
    pinMode(DIP[i], INPUT_PULLUP);
  }
  Serial.begin(115200);
}

void loop() {
  int state[N] = {0};
  for(int i=0; i<N; i++) {
    state[i] = digitalRead(DIP[i]);
  }
  for(int i=0; i<N; i++) {
    Serial.print(state[i]);
  }
  Serial.println((""));
  delay(500);
}

