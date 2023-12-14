from configuration import Configuration
from team import Team, TeamEnum
from sqlalchemy import Integer, DateTime, func, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from database import db, Base


class FoosballGame(db.Model):    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    startDate: Mapped[DateTime] = mapped_column(DateTime, server_default=func.now())
    finishDate: Mapped[DateTime] = mapped_column(DateTime, nullable=True)
    blackTeam_id: Mapped[int] = mapped_column(ForeignKey('team.id'))
    redTeam_id: Mapped[int] = mapped_column(ForeignKey('team.id'))
    winningTeam: Mapped["Team"] = mapped_column(ForeignKey('team.id'))

    # blackTeam: Mapped["Team"] = relationship(back_populates="blackTeam")
    # redTeam: Mapped["Team"] = relationship(back_populates="redTeam")


    def __init__(self):
        self.blackTeam = Team(TeamEnum.BLACK)
        self.redTeam = Team(TeamEnum.RED)

        self.blackTeam_id = self.blackTeam.id
        self.redTeam_id = self.redTeam.id

    def addScore(self, team):
        if self.isFinished():
            print('game already finished, cannot change score')
            return

        if (team == TeamEnum.BLACK.name):
            self.blackTeam.addScore()
        elif (team == TeamEnum.RED.name):
            self.redTeam.addScore()
        else:
            print(f'addScore(): team: {team} does not exist')
    
    def removeScore(self, team):
        if self.isFinished():
            print('game already finished, cannot change score')
            return
        if (team == TeamEnum.BLACK.name):
            self.blackTeam.removeScore()
        elif (team == TeamEnum.RED.name):
            self.redTeam.removeScore()        
        else:
            print(f'removeScore(): team: {team} does not exist')

    def removePlayer(self, player):
        if self.blackTeam.removePlayer(player):
            return True
        if self.redTeam.removePlayer(player):
            return True
        return False

    def isGameReady(self):
        if self.blackTeam.isTeamReady() and self.redTeam.isTeamReady():
            return True
        else:
            return False

    def isFinished(self):
        if self.blackTeam.getScore() and self.blackTeam.getScore() >= Configuration.gameWinningAmount:
            self.winningTeam = self.blackTeam
            return True
        elif self.redTeam.getScore() and self.redTeam.getScore() >= Configuration.gameWinningAmount:
            self.winningTeam = self.redTeam
            return True
        else:
            return False

    def getGameData(self):
        return {
            'redTeam': {
                'players': [
                    self.redTeam.player1.username if self.redTeam.player1 else None,
                    self.redTeam.player2.username if self.redTeam.player2 else None,
                ],
                'score': self.redTeam.getScore()
            },
            'blackTeam': {
                'players': [
                    self.blackTeam.player1.username if self.blackTeam.player1 else None,
                    self.blackTeam.player2.username if self.blackTeam.player2 else None,
                ],
                'score': self.blackTeam.getScore()
            },
            'finished': self.isFinished(),
            'winningTeam': self.winningTeam.side.name if self.winningTeam else None
        }


class FoosballGameManager():
    currentGame = None

    def __init__(self, socketio) -> None:
        self.socketio = socketio
        with db.session.begin():
            self.currentGame = db.session.query(FoosballGame).first() or FoosballGame()

    def newGame(self):
        self.currentGame = FoosballGame()
    
    def isCurrentGameReady(self):
        if self.currentGame.isGameReady():
            db.session.add(self.currentGame)
            db.session.add(self.currentGame.redTeam)
            db.session.add(self.currentGame.blackTeam)
            db.session.commit()
            return True
        return False
        
    def updateCurrentGameData(self):
        self.socketio.emit('update_game', self.currentGame.getGameData())