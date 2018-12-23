
/*
   Scan WiFi networks and post the SSID and RSSI signal strength as a JSON array to a HTTP server
   Note: there may  be duplicate records, so the server has to extract unique SSIDs.
*/
#include "WifiScanner.h" 
#include "ESP8266WiFi.h"

#define MAX_ATTEMPTS      30
#define NUM_SCANS         3
#define SCAN_INTERVAL     3000   // mSec
#define HTTP_TIMEOUT      3000   // mSec
#define SLEEP_DURATION    30     // seconds   
#define MAX_PAYLOAD_SIZE  80     // must be < 500 
#define LED               2

char payload[512];   
char tmp_str[12];
char main_headers[256];
char final_header[64];

void setup() {
  Serial.begin(115200);
  Serial.println("\nWiFi scanner waking up...");
  pinMode(LED, OUTPUT);
  blink();
  make_headers();
  WiFi.mode(WIFI_STA);
  disconnect_wifi();     // disconnect from any AP it was previously connected to
  delay(100);
  Serial.println("\nSetup complete.");
}

void loop() {
    for (int i=0; i<NUM_SCANS; i++) {
      scan_APs();
      // Wait a bit before scanning again
      delay(SCAN_INTERVAL);  
    }
    Serial.println("\nGoing into sleep..");
    //delay(SLEEP_DURATION * 1000);  // mSec
    ESP.deepSleep(SLEEP_DURATION * 1000L * 1000L);   // microSec
}

void scan_APs() {
    Serial.println("\nStarting AP scan...");
    // WiFi.scanNetworks will return the number of networks found
    int n = WiFi.scanNetworks();
    Serial.println("Scan done.");
    if (n == 0) {
      Serial.println("No networks were found !");
      return;
    } 
    Serial.print(n);
    Serial.println(" networks found");
    
    bool payload_full = false;
    bool last_packet = false;
    init_payload();    
    for (int i = 0; i < n; ++i) {
        if (i==(n-1))
            last_packet = true;
        payload_full = assemble_payload(i, last_packet);
        if (payload_full && (!last_packet)) {
            close_payload();
            send_payload();
            init_payload();
        }
        delay(10);
    }
    close_payload();
    send_payload();   
    disconnect_wifi();   // detach from the communicating AP
}

void init_payload() {
    sprintf(payload, "{\"DEVICE\":%d, \"APS\":[", DEVICE_ID);    
}

void close_payload() {
    strcat(payload, "]}");
    Serial.print("Payload size: ");
    Serial.println (strlen(payload));
}

bool assemble_payload(int index, bool last_packet) {
    strcat (payload, "{\"A\":\"");
    strcat (payload, WiFi.SSID(index).c_str());
    strcat (payload, "\",\"S\":");
    itoa(WiFi.RSSI(index),tmp_str,10);
    strcat (payload, tmp_str);
    strcat (payload, "}");
    if (strlen(payload) > MAX_PAYLOAD_SIZE)
        return (true);    
    if (!last_packet)
        strcat (payload, ","); 
    return(false);       
}

void send_payload() {
    Serial.println (payload); 
    if (!reconnect_wifi())  
        return;
    send_wifi_http();
}

void disconnect_wifi() {
    Serial.println ("Disconnecting wifi..");
    WiFi.disconnect(); 
    delay(100);
}

bool reconnect_wifi() {
    if (WiFi.status() == WL_CONNECTED)
        return (true);
    Serial.print("Connecting to SSID: ");
    Serial.println(WIFI_SSID);
    WiFi.mode(WIFI_STA);
    WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
    int attempts = 0;
    while (WiFi.status() != WL_CONNECTED) {
        attempts++;
        if (attempts > MAX_ATTEMPTS) {
            Serial.println("\n--- Could not connect to WiFi ---");
            return (false);
        }
        delay(500);
        Serial.print(".");
    }
    Serial.println("");
    Serial.println("WiFi connected.");
    return (true);  
}

bool send_wifi_http() {
    Serial.println("Posting data to server...");
    WiFiClient wifi_client;
    wifi_client.setTimeout (HTTP_TIMEOUT);
    wifi_client.setNoDelay(true);  // disable Nagle algorithm
    bool connected = wifi_client.connect( HOST, PORT);
    if (!connected) {
        wifi_client.stop();
        Serial.println ("Trying again...");        
        delay(1000);  // https://github.com/esp8266/Arduino/issues/722
        connected = wifi_client.connect( HOST, PORT);
    }
    if (!connected) {
        wifi_client.stop();
        Serial.println ("--- Could not connect to HTTP server ---");
        return (false);
    }   
    sprintf(final_header, "Content-length: %d\r\n\r\n", strlen(payload));
    wifi_client.print(main_headers);
    wifi_client.print(final_header); // this has the protocol blank line also
    wifi_client.print(payload);  
    wifi_client.flush();
    delay(200);  // flushing - safety margin?
    wifi_client.stop();   // close connection
    return (true);
}

void make_headers() {
    sprintf (main_headers, "POST %s  HTTP/1.1\r\nHost: %s\r\n", URI,  HOST);
    strcat (main_headers, "Content-Type: application/json; charset=utf-8\r\n");
    strcat (main_headers, "Connection: close\r\n"); 
    Serial.print ("Header length: ");
    Serial.println (strlen(main_headers));
    Serial.println (main_headers);
}

void blink() {
    for (int i=0; i<6; i++) {
        digitalWrite(LED, LOW);
        delay(150);
        digitalWrite(LED, HIGH);
        delay(150);        
    }
}

