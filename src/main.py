from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO
from foosballGame import FoosballGameManager
from player import PlayerManager
from database import db

app = Flask(__name__)
socketio = SocketIO(app)

# configure the SQLite database, relative to the app instance folder
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///project.db"
db.init_app(app)

# create tables in database
with app.app_context():
    db.create_all()

gameManager = FoosballGameManager(socketio)
playerManager = PlayerManager(socketio)

@app.route('/')
def index():
    redTeamPlayers = playerManager.getAllPlayers()
    blackTeamPlayers = playerManager.getAllPlayers()
    return render_template('join_game.html', redTeamPlayers=redTeamPlayers, blackTeamPlayers=blackTeamPlayers)

@app.route('/new_game')
def newGame():
    gameManager.newGame()
    return index()

@app.route('/start_game', methods=['POST'])
def start_game():
    if gameManager.isCurrentGameReady():
        return jsonify({'success': True})
    return jsonify({'success': False})

@app.route('/add_user', methods=['POST'])
def addUser():
    return playerManager.addNewPlayer(request, gameManager.currentGame)

@app.route('/game_page')
def game_page():
    return render_template('game_page.html')

@socketio.on('get_initial_data')
def handle_get_initial_data():
    gameManager.updateCurrentGameData()

@socketio.on('change_score')
def handle_change_score(data):
    if 'team' in data and 'action' in data:
        team = data['team']
        action = data['action']

        if action == 'minus':
            gameManager.currentGame.removeScore(team.upper())
        elif action == 'plus':
            gameManager.currentGame.addScore(team.upper())
        else:
            print('incorrect action')
        gameManager.updateCurrentGameData()

@socketio.on('update_player')
def handle_update_player(data):
    playerManager.updatePlayers(data, gameManager.currentGame)
    

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5001, debug=True)