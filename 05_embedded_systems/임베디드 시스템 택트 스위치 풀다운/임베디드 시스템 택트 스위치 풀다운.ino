/*
//150p
#define SW 2

void setup(){
  pinMode(LED_BUILTIN, OUTPUT);
  pinMode(SW, INPUT);
}

void loop() {
  int state = digitalRead(SW);
  digitalWrite(LED_BUILTIN, state);
}
*/

//151p
#define SW 2

void setup(){
  pinMode(LED_BUILTIN, OUTPUT);
  pinMode(SW, INPUT);
  Serial.begin(115200);
}

void loop() {
  int state = digitalRead(SW);

  digitalWrite(LED_BUILTIN, state);
  Serial.println(state);
}