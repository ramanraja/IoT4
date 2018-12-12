from flask import Flask
from flask import request
import logging

app = Flask("Button Server")
log = logging.getLogger('werkzeug')
log.disabled = True
app.logger.disabled = True
cmd_str = 'OK'


# http://192.168.0.104:5000/
@app.route('/')
def root():
    return ("<h2>Hi, this is buttton server</h2>")


# http://192.168.0.104:5000/command?cmd=Hi+there
# http://192.168.0.104:5000/command?cmd=Restart
# http://192.168.0.104:5000/command?cmd=C+2+1
# http://192.168.0.104:5000/command?cmd=Fwupdate
@app.route('/command')
def command():
    global cmd_str
    cmd_str = request.args['cmd']
    print(cmd_str)
    return ("Command registered.")
  
    
@app.route('/ultra', methods = ['POST'])
def ultra():
    global cmd_str
    try:
        #print (request.data)
        reqstr = request.data.decode('utf-8')
        if (reqstr[0] == '#'):
            print(reqstr)
            return ('OK [comment]')
        num = int(reqstr)
        N = 1
        if (num > 5): N = 7
        for i in range(num+N):
            print ('*', end='')
        print()    
        cmd_str_copy = cmd_str
        cmd_str = 'OK'
        return (cmd_str_copy)
    except Exception as e:
        return ('ERROR')
        
        
        
app.run(host='0.0.0.0', port=5000, debug=True)