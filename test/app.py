from flask import Flask, render_template
from flask_bootstrap import Bootstrap
from flask_socketio import SocketIO, send, emit
import time

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
bootstrap = Bootstrap(app)

socketio = SocketIO()
socketio.init_app(app)


@app.route('/index1')
def index1():
    return render_template('index1.html')

@app.route('/index2')
def index2():
    return render_template('index2.html')

@app.route('/index3')
def index3():
    return 'index3'

@app.route('/ping')
def ping():
    socketio.emit('my_pong', namespace='/test')
    return 'my_pong!'
    
@app.route('/event1')
def event1():
    print('event1')
    socketio.emit('event1', namespace='/test')
    return 'event1'

@socketio.on('my event')
def handle_my_custom_event(json):
    print('received json: ' + str(json))

# gunicorn --workers 1 --bind 0.0.0.0:5001 --worker-class eventlet app:app
if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5001, debug=True)

