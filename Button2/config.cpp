//config.cpp
#include "config.h"
#include "flashHelper.h"

extern void safe_strncpy (char *dest, char *src, int length = MAX_STRING_LENGTH);

Config::Config(){
    SERIAL_PRINTLN ("Creating the Config object.. [Ensure it is a singleton]");
}

void Config::init() {
    loadDeviceData ();
}


/* 
   Read the device id and group id from Flash and
    embed them into the Config object. This is to be done before
   initializing the wireless and http helpers.
*/
bool Config::loadDeviceData () {
    FlashHelper F;
    F.init(this);
    F.begin();
    SERIAL_PRINTLN("Trying to read EEPROM...");

    StorageBlock block;
    bool result = F.readFlash (&block);   
    F.end();

    if (!result) {
        SERIAL_PRINTLN("\n*** --------  FATAL ERROR ------------ ***");
        SERIAL_PRINTLN("Could not read device data from flash.");
        device_id = random(100001, 999999);
        group_id = random(100001, 999999);
        SERIAL_PRINT("Assuming random device id: ");
        SERIAL_PRINTLN(device_id);
        SERIAL_PRINT("Random group id: ");
        SERIAL_PRINTLN(group_id);      
        return false;           
    } 
    SERIAL_PRINTLN("\Successfully retrieved device data from flash."); 
    device_id = block.lparam1;
    group_id = block.lparam2;
    return true;   
}

bool Config::storeDeviceData() {
    SERIAL_PRINTLN ("\nSaving the Configuration to EEPROM..");
    FlashHelper F;
    F.init(this);
    F.begin();
    bool result = F.testMemory();
    if (!result) {
        SERIAL_PRINTLN ("Basic Memory Test failed !.. aborting.");
        F.end();
        return false;
    }
    //yield();
    
    StorageBlock block;
    block.lparam1 = device_id;
    block.lparam2 = group_id;
    block.lparam3 = 0L;
    block.lparam4 = 0L;
    block.lparam5 = 0L;
    result = F.writeFlash(block);
    
    if (!result) {
        SERIAL_PRINTLN ("\nFATAL ERROR: Could not reliably write to EEPROM. Aborting.");
        F.end();
        return false;
    }    
    F.commit();
    //yield();
    SERIAL_PRINTLN ("\nReading back memory..\n");
    result = F.readFlash(&block);  // it is only a test read, so reuse the block
    F.end();   
    if (!result) {
        SERIAL_PRINTLN ("\nFATAL ERROR: Could not read from EEPROM. Aborting.");
        return false;
    }
    // the data was already in 'this' object
    SERIAL_PRINTLN ("This configuration has been saved in EEPROM: ");    
    SERIAL_PRINT ("Device ID: ");
    SERIAL_PRINTLN (device_id);     
    SERIAL_PRINT ("Group ID: ");
    SERIAL_PRINTLN (group_id);
    SERIAL_PRINTLN();
    return true;
}

bool Config::repairFlash(const char *config_str) {
    SERIAL_PRINTLN("New Flash data:");
    SERIAL_PRINTLN(config_str);
    long did,gid;
    int num_ints = sscanf (config_str, "%ld %ld", &did,&gid);
    SERIAL_PRINT("number of integers scanned= ");
    SERIAL_PRINTLN(num_ints);  
    if (num_ints != 2) {
        SERIAL_PRINT("ERROR: Expected 2 integers, but found ");
        SERIAL_PRINTLN(num_ints);
        return false;
    }    
    SERIAL_PRINT("device id= ");
    SERIAL_PRINTLN(did);  
    SERIAL_PRINT("group id= ");
    SERIAL_PRINTLN(gid);  
    device_id = did;
    group_id = gid;
    return (storeDeviceData());  // manually restart after this
}

void Config::dump() {
    SERIAL_PRINTLN("\n-----------------------------------------");
    SERIAL_PRINTLN("               configuration             ");
    SERIAL_PRINTLN("-----------------------------------------");    
    SERIAL_PRINT ("Firmware version: 1.0.");
    SERIAL_PRINTLN (FIRMWARE_VERSION);
    long freeheap = ESP.getFreeHeap();
    SERIAL_PRINT ("Free heap: ");
    SERIAL_PRINTLN (freeheap);    
    SERIAL_PRINT ("Device ID: ");
    SERIAL_PRINTLN (device_id);     
    SERIAL_PRINT ("Device Group: ");
    SERIAL_PRINTLN (group_id);  
    
    SERIAL_PRINT ("Firmware server URL: ");
    SERIAL_PRINTLN (firmware_server_url);    
    SERIAL_PRINT("Firmware version URL: ");
    SERIAL_PRINTLN(version_check_url);      
    SERIAL_PRINT ("Production server URL: ");
    SERIAL_PRINTLN (data_url);

    SERIAL_PRINTLN("-----------------------------------------\n");                     
}
 

 
