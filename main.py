from flask import Flask
from flask_socketio import SocketIO

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
socketio = SocketIO(app)

@app.route('/')
def index():
    return 'Server is running!'

if __name__ == '__main__':
    socketio.run(app, port=5000, debug=True)
