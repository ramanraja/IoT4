// wifi AP sniffer
// https://github.com/RicardoOliveira/ESPProLib

#include "esppl_functions.h"

void callback( esppl_frame_info *info) {
    Serial.print("\n");
    for (int i = 0; i < 6; i++) Serial.printf("%02x", info->sourceaddr[i]);
    Serial.print("\t");
    Serial.print(info->rssi);
    Serial.print("\t");
    if (info->ssid_length == 0) 
    return;
    for (int i = 0; i < info->ssid_length; i++)
        Serial.print((char) info->ssid[i]);    
}

void setup() {
    Serial.begin(115200);  
    delay(50);
    esppl_init(callback);
    delay(50);    
    esppl_sniffing_start();    
}

void loop() {
    for (int i = 1; i < 15; i++ ) {
      esppl_set_channel(i);
      while (esppl_process_frames()) 
        ;
    }
}
