//190-191p
// 아날로그 입력: 조이스틱 
#define SW_pin  2 // 조이스틱 스위치핀
#define X_pin  A0 // 조이스틱 X축
#define Y_pin  A1 // 조이스틱 Y축

void setup() {
  pinMode(SW_pin, INPUT_PULLUP);
  Serial.begin(115200);
}

void loop() {
  int sw_state = digitalRead(SW_pin);
  int x_value = analogRead(X_pin);
  int y_value = analogRead(Y_pin);

  Serial.print("Switch:  ");
  Serial.print(sw_state);
  Serial.print(" | ");
  Serial.print("X-axis: ");
  Serial.print(x_value);
  Serial.print(" | ");
  Serial.print("Y-axis: ");
  Serial.println(y_value);
  delay(10);
}