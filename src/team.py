from configuration import Configuration
from enum import Enum
from sqlalchemy import String, Integer, DateTime, func, ForeignKey, Enum as sqlalchemyenum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from database import db, Base

class TeamEnum(Enum):
    RED = 1
    BLACK = 2


class Team(db.Model):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    side: Mapped[Enum] = mapped_column(sqlalchemyenum(TeamEnum))
    # game_id: Mapped[int] = mapped_column(ForeignKey('foosball_game.id'),nullable=True)
    player1: Mapped[int] = mapped_column(ForeignKey('player.id'), nullable=True)
    player2: Mapped[int] = mapped_column(ForeignKey('player.id'), nullable=True)
    score: Mapped[int] = mapped_column(Integer, default=0)

    # game: Mapped["FoosballGame"] = relationship(back_populates="game")

    def __init__(self, side):
        self.side = side
        # db.session.add(self)
        # db.session.commit()

    def getScore(self):
        score = db.session.execute(db.select(Team).where(Team.id == self.id)).scalar()
        return score

    def addPlayer(self, player):
        if self.player1 is None:
            self.player1 = player
            return True
        elif self.player1 is not None and self.player2 is None:
            self.player2 = player
            return True
        else:
            return False
        
    def removePlayer(self, player):
        if self.player1 is not None and self.player1.username == player.username:
            self.player1 = None
            return True
        elif self.player2 is not None and self.player2.username == player.username:
            self.player2 = None
            return True
        else:
            return False
        
    def isTeamReady(self):
        return self.player1 is not None

    def addScore(self):
        if self.score < Configuration.gameWinningAmount:
            self.score += 1

    def removeScore(self):
        if self.score > 0:
            self.score -= 1


