/*
 * SafeSpace: Smart Environmental Monitor for Neurodiversity
 * Developed for Hackathon Diversity & Inclusion Category
 */

// Pin Definitions
const int soundPin = A0; 
const int lightPin = A1;
const int greenLED = 2;  // Safe
const int yellowLED = 3; // Warning
const int redLED = 4;    // Overload

// Thresholds (Calibrate these based on your room)
const int soundDanger = 600; 
const int lightDanger = 700;
const int soundWarning = 300;
const int lightWarning = 500;

void setup() {
  Serial.begin(9600);
  
  pinMode(greenLED, OUTPUT);
  pinMode(yellowLED, OUTPUT);
  pinMode(redLED, OUTPUT);

  // Startup Test: Blink all LEDs
  digitalWrite(greenLED, HIGH);
  digitalWrite(yellowLED, HIGH);
  digitalWrite(redLED, HIGH);
  delay(1000);
  digitalWrite(greenLED, LOW);
  digitalWrite(yellowLED, LOW);
  digitalWrite(redLED, LOW);
}

void loop() {
  // 1. Data Acquisition
  int soundValue = analogRead(soundPin);
  int lightValue = analogRead(lightPin);

  // 2. Serial Logging (For Time-Series Analysis)
  // Format: SoundValue, LightValue
  Serial.print(soundValue);
  Serial.print(",");
  Serial.println(lightValue);

  // 3. Logic: Multi-Sensor Fusion
  // RED: Either is dangerous, OR both are high (Cumulative Stress)
  if (soundValue > soundDanger || lightValue > lightDanger || (soundValue > 500 && lightValue > 600)) {
    updateLEDs(LOW, LOW, HIGH); // Red Only
  } 
  // YELLOW: Approaching limits
  else if (soundValue > soundWarning || lightValue > lightWarning) {
    updateLEDs(LOW, HIGH, LOW); // Yellow Only
  } 
  // GREEN: Ideal environment
  else {
    updateLEDs(HIGH, LOW, LOW); // Green Only
  }

  delay(250); // Balanced for real-time response without jitter
}

// Helper function to keep loop clean
void updateLEDs(int g, int y, int r) {
  digitalWrite(greenLED, g);
  digitalWrite(yellowLED, y);
  digitalWrite(redLED, r);
}