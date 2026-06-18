#define LED_PIN 13

void setup() {
  Serial.begin(9600);           //Starter kommunikation mellem arduino og hjemmesiden med en hastighed på 9600 bit/s
  pinMode(LED_PIN, OUTPUT);     //Sætter pin 13 til at være output
  digitalWrite(LED_PIN, LOW);   //Sørger for, at LED'en er slukket ved opstart
  randomSeed(analogRead(A0));   //Intialiserer den tilfældige talgenerator
}

void loop() {
  if (Serial.available()) {                           //Hvis der er modtaget data
    String kommando = Serial.readStringUntil('\n');   //Læs kommandoen
    if (kommando == "START") {                        //Hvis kommandoen er START

      // Udfør tre målinger
      for (int maaling = 1; maaling <= 3; maaling += 1) {   //Vi tæller fra 1 til og med 3 (tælleren øges med 1 hver gang)

        digitalWrite(LED_PIN, HIGH);
        delay(3000);

        int systolisk = random(140, 160);   //Let forhøjet. Normalt systolisk er 100-139
        int diastolisk = random(90, 100);   //Let forhøjet. Normalt diastolisk er 60-89
        int puls = random(80, 110);         //Interval for let forhøjet blodtryk (puls)

        Serial.print(systolisk);
        Serial.print(",");
        Serial.print(diastolisk);
        Serial.print(",");
        Serial.println(puls);

        digitalWrite(LED_PIN, LOW);

        if (maaling < 3) {   //Laver kun pause hvis det ikke er sidste måling
          delay(1000);
        }
      }

      Serial.println("FÆRDIG");
    }
  }
}


