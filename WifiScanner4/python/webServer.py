# Sample server to test the 8266 Wifi scanner WiFiScanner4.ino
# Point a browser to http://127.0.0.1:5000/aplist

from flask import Flask, jsonify, abort
from flask import request, make_response

app = Flask("My web server")

@app.route('/aplist', methods=['GET', 'POST'])
def index():
    #print (request)
    if request.json:
        print (request.json)
    else:
        print('invalid JSON request')
        return jsonify({'result':'failed!'})
        #abort(400)
    return jsonify({'result':'success!'})

app.run(host="0.0.0.0", debug=True)