
/*
//181p
// 아날로그 입력: 가변저항
#define VR A0

void setup() {
  Serial.begin(115200); 		        // 시리얼 통신 속도 설정: 115200bps
}

void loop() {
  int value = analogRead(VR);	      // 아날로그 신호 측정
  Serial.println(value); 		        // 시리얼 모니터로 전송(출력)
}
*/

//182p
// 아날로그 입력: 포텐셔미터
#define VR A0

void setup() {
  Serial.begin(115200); 		        // 시리얼 통신 속도 설정: 115200bps
}

void loop() {
  int adcVal = analogRead(VR);	    // 아날로그 신호 측정
  // 원시 데이터 값(0 ~ 1023)을 전압(0.0V ~ 5.0V)으로 변환
  float voltage = adcVal * 5.0 / 1023.0;
  Serial.println(voltage); 		      // 시리얼 모니터로 전압 출력
  delay(10);
}