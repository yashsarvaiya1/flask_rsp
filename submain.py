from flask import Flask, render_template, request
from flask_socketio import SocketIO, join_room, leave_room, emit
import random

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
socketio = SocketIO(app)

# To store player data for each room
rooms = {}

@app.route('/')
def home():
    return 'Welcome to the Rock-Paper-Scissors Game!'

# Join a game room
@socketio.on('join')
def on_join(data):
    username = data['username']
    room = data['room']
    join_room(room)

    if room not in rooms:
        rooms[room] = {}

    rooms[room][username] = {'choice': None}
    emit('message', {'msg': f'{username} has joined the room!'}, room=room)

# Leave a game room
@socketio.on('leave')
def on_leave(data):
    username = data['username']
    room = data['room']
    leave_room(room)

    if room in rooms and username in rooms[room]:
        del rooms[room][username]
        emit('message', {'msg': f'{username} has left the room.'}, room=room)

# Handle a player's choice
@socketio.on('play')
def on_play(data):
    username = data['username']
    room = data['room']
    choice = data['choice']

    if room in rooms and username in rooms[room]:
        rooms[room][username]['choice'] = choice
        emit('message', {'msg': f'{username} chose {choice}.'}, room=room)

        # Check if all players in the room have made a choice
        if all(player['choice'] for player in rooms[room].values()) and len(rooms[room]) >= 2:
            result = determine_winner(rooms[room])
            emit('result', {'result': result}, room=room)
            # Reset choices after the game
            for player in rooms[room]:
                rooms[room][player]['choice'] = None

def determine_winner(players):
    """Determine the winner of the game."""
    choices = {username: player['choice'] for username, player in players.items()}
    unique_choices = set(choices.values())

    if len(unique_choices) == 1:
        return 'It\'s a tie!'

    beats = {
        'rock': 'scissors',
        'scissors': 'paper',
        'paper': 'rock'
    }

    winners = [username for username, choice in choices.items()
        if all(beats[choice] == other_choice for other_choice in choices.values() if other_choice != choice)]

    if len(winners) == 1:
        return f'{winners[0]} wins!'
    return 'It\'s a tie!'

if __name__ == '__main__':
    socketio.run(app, port=5000, debug=True)
