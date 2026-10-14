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

/*
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
*/

/*
//153-154p
#define SW 2

int count = 0;
int prev_state;

void setup(){
  pinMode(SW, INPUT);
  Serial.begin(115200);
  prev_state = digitalRead(SW);
}

void loop() {
  int state = digitalRead(SW);

  if(state != prev_state)
  {
    if(state == LOW)
    {
      count++;
      Serial.println(count);
    }
    prev_state = state;
  }
}
*/

//156-157p
#define SW 2

int count = 0;
int state_stable, prev_state;

unsigned long last_bounce_time = 0;
unsigned long interval_debounce = 10;

void setup(){
  pinMode(SW, INPUT);
  Serial.begin(115200);
  prev_state = digitalRead(SW);
  state_stable = prev_state;
}

void loop() {
  int state = digitalRead(SW);

  if(state != prev_state)
  {
    last_bounce_time = millis();
    prev_state = state;
  }

  if ((millis() - last_bounce_time) > interval_debounce)
  {
    if (state != state_stable)
    {
      state_stable = state;

      if (state_stable == LOW)
      {
        count++;
        Serial.println(count);
      }
    }
  }
}