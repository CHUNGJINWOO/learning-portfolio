//169-170p
#define PIR 2

void setup() { 
  pinMode(LED_BUILTIN, OUTPUT);
  pinMode(PIR, INPUT);
  Serial.begin(115200);
}

void loop() {
  int state = digitalRead(PIR);

  digitalWrite(LED_BUILTIN, state);
  if(state == HIGH)
  {
    Serial.println("Somebody is in this area!");
  }
  else
  {
    Serial.println(("NO one!"));
  }
  delay(500);
}