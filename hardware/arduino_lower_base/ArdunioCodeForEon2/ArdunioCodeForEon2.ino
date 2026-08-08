/*
--------------------------------------------------------------------------------------------
COMMAND STRUCTURE
8 byte data will be send from computer to ardunio:
First two quadruplets (4 set of character) will determine the speed of each motor individually.
So for the motors for the each quadruplets, first character will be the command 
and rest 3 characters are the numbers representing speed which 
needed to convert from string to int.


For example:
"F100B120" can be broken as below:
"F100" => Select Right Motor for speed 100 in forward direction
"B120" => Select Left Motor for speed 120 in backward direction


F090B090

STRUCTURE: 
[
F/B speed (Right Motor), 
F/B speed (Left Motor), 
]

Once computer sends command and the command is executed properly, then the arudnio
sends an acknoledgement only after then the computer is supposed to send next command, 
not before that.
--------------------------------------------------------------------------------------------
SPEED LIMIT:
Forward backward speed 80 to 255
Turn left and turn right speed 140 to 255

--------------------------------------------------------------------------------------------
HOW Serial.read() WORKS:
  Arduino has a serial receive buffer (like a queue).
  When the computer sends bytes, they get stored in this buffer.
  Serial.read() takes ONE byte from the buffer and removes it.
    char a = Serial.read();
    char b = Serial.read();
  will read two bytes, one after another, if two bytes are available.
--------------------------------------------------------------------------------------------
STRNCPY() FUNCTION
char *strncpy(char *dest, const char *src, size_t n);
  dest: Pointer to the destination array where the content is copied.
  src: Pointer to the source string to be copied.
  n: The maximum number of characters to copy.

ATOIO() FUNCTION
In C programming, atoi() (short for "ASCII to integer") is a library function 
that converts a string representing a number into its integer value.
int atoi(const char *str);
It reads characters until it hits a non-digit character (like a decimal point or letter).
*/

#define MOTOR_SPEED 80 //min speed 80 and max 255

// Motor Driver Pins
int in1_left_motor = 5; //in1 and in2 for left motor
int in2_left_motor = 4;
int in3_right_motor = 3; //in3 and in4 for right motor
int in4_right_motor = 2;
int leftMotor_pwm = 6; // PWM pin leftMotor_pwm
int rightMotor_pwm = 11; // PWM pin rightMotor_pwm

char command[8]; // array for accepting 8 byte command 


void setup() {
  pinMode(in1_left_motor, OUTPUT);
  pinMode(in2_left_motor, OUTPUT);
  pinMode(in3_right_motor, OUTPUT);
  pinMode(in4_right_motor, OUTPUT);

 
  Serial.begin(9600);
  Serial.println("Comm initialized");
 
}

void loop() {
/*
we have done if(Serial.available()>8) instead if(Serial.available()>0) because in that case it would 
read even if 1 character available and rest 7 are not. So, in that case if the speed of Serial.read()
is greater than the speed at which sender is sending, then after reading the received character it
will read garbage or -1 value for missing characters as they have not arrived yet. So making sure
using if(Serial.available()>=8) that it reads only after all 8 bytes are available

*/

  if(Serial.available()>=8){ //reads only after 8 bytes has arrived (not >= is used instead > otherwise it would only read for greater than 8 char while our command is 8 characters only)
    //---------------------------------------Reading the Command------------------------------------
    for(int i=0; i<8; i++){
      command[i] = Serial.read();
    }
      while (Serial.available() > 0) {Serial.read();} //clears the buffer after reading the main command only if in case if there is anything extra or garbage value in the buffer by chance/accident

    //--------------------------------------Decoding the Command-------------------------------------
    char temp[4]; //used to store parts of string from command string

    /*--------Right motor decoding--------*/
    char RightMotorDirection = command[0];
    strncpy(temp, command + 1, 3); //command is a pointer and +1 means the string having initial address as command+1 following pointer arithmatic
    //copying the string from index 1 to 3 in temp
    temp[3]='\0'; //after storing the 3 characters last character will be the terminal character for making this array a string.
    int RightMotorSpeed=atoi(temp); //atoi converts string into number in c. And it reads characters until it hits a non-digit character

    /*--------Left motor decoding--------*/
    char LeftMotorDirection = command[4];
    strncpy(temp, command + 5, 3); 
    temp[3]='\0'; 
    int LeftMotorSpeed=atoi(temp); 


    /*
    Available Vairables:
                RightMotorDirection,
                RightMotorSpeed,
                LeftMotorDirection,
                LeftMotorSpeed,
    */

    //--------------------------------------Executing the Command-------------------------------------
    rightMotor(RightMotorDirection, RightMotorSpeed);
    leftMotor(LeftMotorDirection, LeftMotorSpeed);
    Serial.println("ok");//gives acknoeledgement after which only next command will be sent by computer
  }
 
}

void rightMotor(char dir, int speed){
  if(dir == 'F'){
    digitalWrite(in3_right_motor, HIGH);
    digitalWrite(in4_right_motor, LOW);
    analogWrite(rightMotor_pwm, speed);
  }
  else if(dir == 'B'){
    digitalWrite(in3_right_motor, LOW);
    digitalWrite(in4_right_motor, HIGH); 
    analogWrite(rightMotor_pwm, speed); 
  }
  else{
    //do nothing
  }
}

void leftMotor(char dir, int speed){
  if(dir == 'F'){
    digitalWrite(in1_left_motor, LOW);
    digitalWrite(in2_left_motor, HIGH);
    analogWrite(leftMotor_pwm, speed);
  }
  else if(dir == 'B'){
    digitalWrite(in1_left_motor, HIGH);
    digitalWrite(in2_left_motor, LOW);
    analogWrite(leftMotor_pwm, speed);
  }
  else{
    //do nothing
  }
}

//ok
