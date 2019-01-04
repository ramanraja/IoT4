# general purpose Q&D web server
# Point a browser to http://127.0.0.1:5000/xxx
# http://192.168.0.100:5000/ultra?age=40&name=Raja

from flask import Flask, jsonify, abort
from flask import request, make_response

app = Flask("My web server")

@app.route('/ultra', methods=['GET', 'POST'])
def index():
    print (request)
    if request.json is not None:
        #print (request.json)
        print (request.get_json()) 
    else:
        print(request.data)
        print (request.get_data())
        print (request.args)
        print (request.form)
    print ()
    return jsonify({'result':'success!'})

app.run(host="0.0.0.0", debug=True)

# http://flask.pocoo.org/docs/1.0/api/#incoming-request-data
