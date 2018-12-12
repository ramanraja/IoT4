//config.h
#ifndef CONFIG_H
#define CONFIG_H
 
#include "common.h"
#include "keys.h"

// increment this number for every version
#define  FIRMWARE_VERSION       2


#define  BAUD_RATE              115200

//----------------------------- HTTPClient ----------------------------------------

// File name: ultra.bin   
  
#define  FW_SERVER_URL      "http://192.168.0.104:8000/ota/ultra.bin"
#define  FW_VERSION_URL     "http://192.168.0.104:8000/ota/ultra.txt"
#define  DATA_PROD_URL      "http://192.168.0.104:5000/ultra"
//----------------------------------------------------------------------------------
 
class Config {
public :
int  current_firmware_version =  FIRMWARE_VERSION;  

char *firmware_server_url = FW_SERVER_URL;
char *version_check_url = FW_VERSION_URL;
bool verison_check_enabled = true;

char *data_url =  DATA_PROD_URL;    
    
// the actual IDs and threshold will be read from EEPROM and plugged in here
long device_id = 0;      
long group_id  = 0;
 

// * Timer durations SHOULD be unsigned LONG int, if they are > 16 bit! 
unsigned long data_interval    = 2000L;   // milliSec, to send data to gateway

/* The following constants should be updated in  "keys.h" file  */
const char *wifi_ssid1        = WIFI_SSID1;
const char *wifi_password1    = WIFI_PASSWORD1;
const char *wifi_ssid2        = WIFI_SSID2;
const char *wifi_password2    = WIFI_PASSWORD2;
const char *wifi_ssid3        = WIFI_SSID3;
const char *wifi_password3    = WIFI_PASSWORD3;


Config();
void init();
void dump();
bool loadDeviceData (); 
bool storeDeviceData();
bool repairFlash(const char *config_str);

};  
#endif 
 
