//H-000, V-020

int angleV = 0;

void process(String Message) {
  // Debug output to see the incoming message
  Serial.println(Message); // Check the message received

  // Adjust indices based on whether you're processing H or V
  String numberStr = Message.substring(9, 12); // For V value
  int number = numberStr.toInt();
  angleV = number;

  Serial.println(round(180 * (angleV / 100.0)));

  // Calculate the PWM value and write it to pin 13
  analogWrite(5, round(255 * (angleV / 100.0)));
}

void setup() {
  Serial.begin(9600);
  pinMode(5, OUTPUT);  // Set pin 13 as output
}

void loop() {
  if (Serial.available() > 0) {
    String command = Serial.readStringUntil('\n');
    process(command);
  }
}
