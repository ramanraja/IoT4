// httpPoster.cpp

#include "httpPoster.h"
///#include "externDeclare.h"
 
extern void safe_strncpy (char *dest, char *src, int length = MAX_STRING_LENGTH);
 
HttpPoster::HttpPoster(){
}

void HttpPoster::init(Config *configptr, MyFi *myfiptr){
    SERIAL_PRINTLN("HttpPoster: initializing...");
    this->pC = configptr;
    this->pW = myfiptr;
}

// this has to be called immediately after checkForCommand() to retrieve the result
const char* HttpPoster::getCommand(){
    return (reponse_string);
}
 
int HttpPoster::getResponseCode() {
    return (reponse_code);
} 

int HttpPoster::sendByte (byte payload) {
  char pl[2] = "*";
  pl[0] = payload;
  sendStatus ((char *)pl);
}

int HttpPoster::sendStatus (const char *payload){
  sendStatus(payload, pC->data_url);
}

int HttpPoster::sendStatus (const char *payload, const char *url){
  if (!pW->isConnected()) {
    SERIAL_PRINTLN("HttpPoster: No Wi-Fi connection");
    if (!pW->reconnect())   // this is essential for WifiMulti !
        return 1;
  }
  SERIAL_PRINT("HttpPoster: Posting data to Gateway: ");
  SERIAL_PRINTLN(url);
  
  HTTPClient http_client;  // TODO: make it class member?
  //http_client.setReuse (true);  // enable this for class level operation
  http_client.setTimeout(3000); // milliSec; (does not work ?!)
   
  bool begun = http_client.begin (url);   // this just parses the url
  if (!begun) {
    SERIAL_PRINTLN("Invalid HTTP POST URL");
    http_client.end();   // releases buffers (useful for class level variable) 
    return 2;
  }
  http_client.addHeader("Content-Type", "application/json; charset=utf-8");
  
  reponse_code = http_client.POST(payload);
  
  SERIAL_PRINT("HttpPoster: HTTP POST return code:");
  SERIAL_PRINTLN(reponse_code);

  if (reponse_code < 0) {
     SERIAL_PRINTLN("HttpPoster: Could not connect to Gateway !");
     SERIAL_PRINTLN(http_client.errorToString(reponse_code));   //.c_str());
     http_client.end();
     return 3;
  } 
   if (reponse_code < 200 || reponse_code >= 300) {
      SERIAL_PRINTLN ("HttpPoster: HTTP server returned an error !");
      http_client.end();   // close connection
      return 4;
   } 
   // response_string is valid only when this function returns 0
   safe_strncpy (reponse_string, (char *)http_client.getString().c_str());
   ///SERIAL_PRINTLN (reponse_string);
   SERIAL_PRINTLN ("Ending HTTP connection.\n");
   http_client.end();   // close the connection
   return 0;
}


   
 
