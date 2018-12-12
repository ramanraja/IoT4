// sends PIR and Radar status (0 - 3) over UDP every 1 second
//use the test tool: https://packetsender.com/documentation
/*
    TODO: 
    revice commandHandler; implement on the air update of IP address, device id and group id.
    temperature and humidity are often 0. investigate.
    surround all constant strings with F().
    The JsonParser is very heavy. Implement your own.
    Bring all the HTTP work in OTA helper into HttpPoster class.
    Develop the utility class with other utility functions.
    Disable serial port and test it.
*/
#include "button.h"

//#define  SUMULATION_MODE
//#define  FLASH_REPAIR_MODE

Config C;
Timer T;
MyFi W;
OtaHelper O;
HttpPoster POSTER; 

char *tmp_ptr;
char notification_str[32];

void setup() {
    randomSeed(micros());
    init_serial();
    C.init();
    C.dump();   
    sprintf (notification_str, "{\"ID\":%ld, \"G\":%ld}", C.device_id, C.group_id);    
    #ifdef FLASH_REPAIR_MODE
        display_flash_msg();
    #else
        W.init(&C);  
        POSTER.init(&C, &W);
        O.init(&C);
        yield();  
        T.every (C.data_interval,  send_status);    
        /////T.after(2000L, send_notification);    // for button
        SERIAL_PRINTLN("# Setup complete.");        
    #endif  
}

#ifdef FLASH_REPAIR_MODE
void display_flash_msg() {
      SERIAL_PRINTLN("\n--------------------------------------------------");
      SERIAL_PRINTLN("        ENTERING FLASH MEMORY REPAIR MODE           ");
      SERIAL_PRINTLN("Input 2 numbers on the serial console in the format:");
      SERIAL_PRINTLN("999 999");
      SERIAL_PRINTLN("[device_id, group_id]"); 
      SERIAL_PRINTLN("--------------------------------------------------\n");
}
#endif

void loop() {
 #ifdef FLASH_REPAIR_MODE
     repair_flash();
 #else
     T.update();    
 #endif    
}  

#ifdef FLASH_REPAIR_MODE
void repair_flash() {
    if (!Serial.available())
        return;
    String config_str = Serial.readStringUntil('\n');
    
    bool result = C.repairFlash(config_str.c_str());   
    if (result) {
      SERIAL_PRINTLN("\nFlash repair completed.");
      SERIAL_PRINTLN("Next steps:"); 
      SERIAL_PRINTLN("  1. Comment out 'FLASH_REPAIR_MODE' in code and compile.");
      SERIAL_PRINTLN("  2. Upload the program again.");
    }
    else 
      SERIAL_PRINTLN("\nFlash repair failed.");
    // junk the remaining chars, if any
    while(Serial.available()) 
        Serial.read();     
}
#endif

byte status_byte = 9;
int result;
void send_status() {   
    result = POSTER.sendByte('0' + status_byte);
    status_byte = (status_byte+1)%6;
    // response_string is valid only when this function returns 0
    if (result==0)
        process_command(POSTER.getCommand());
}


void send_notification() {   
    POSTER.sendStatus((const char*)notification_str);
    //delay(1000);
    //ESP.deepSleep(0);
}
 
// TODO: move this to command handler class
void process_command (const char* command_str) {
    SERIAL_PRINT("Command received: ");
    SERIAL_PRINTLN(command_str);
    char cmd = command_str[0];   // the command is of the form  "X 999 999"  
    switch (cmd) {
        case 'H':   
            POSTER.sendStatus("# Hello world!");
            break;      
        case 'R':
            POSTER.sendStatus ("# Rebooting ESP!..");      
            delay(1000);  
            ESP.restart();
            break;     
        case 'C':
            set_config(command_str);
            break;                
        case 'F':
            update_firmware();
            break;                
    }
}
 
void set_config(const char* command_str) {  
      tmp_ptr = (char *)command_str+1;  // go past the cmd char; any spaces will be ignored
      bool result = C.repairFlash (tmp_ptr);
      if (!result) {
          POSTER.sendStatus("# ERROR: could not save configuration.");
          return;
      }
      POSTER.sendStatus ("# Configuration saved successfully.");
      POSTER.sendStatus ("# If you have changed the IP address, reconnect to it now.");
      POSTER.sendStatus ("# Restarting ESP...");
      delay(1000);   // let the messge go out
      ESP.restart();
}

// this is done only on-demand through a targetted UDP command 
void update_firmware() {
    POSTER.sendStatus ("# Checking for firmware updates..");
    int result = O.check_and_update();  // if there was an update, this will restart 8266
    SERIAL_PRINT ("OtaHelper: response code: ");  
    SERIAL_PRINTLN (result);
    POSTER.sendStatus ("# No firmware updates.");
}

void init_serial () {
    #ifdef ENABLE_DEBUG
        Serial.begin(BAUD_RATE); 
        #ifdef VERBOSE_MODE
           Serial.setDebugOutput(true);
        #endif
        Serial.setTimeout(250);
    #endif    
    SERIAL_PRINTLN("\n\n# IoT Button starting...  \n"); 
}
