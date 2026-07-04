from sqlalchemy import Column, Integer, String, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from database import Base

class Tournament(Base):
    __tablename__ = "tournaments"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    year = Column(Integer)

class Team(Base):
    __tablename__ = "teams"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    code = Column(String, unique=True, index=True)

class TournamentTeam(Base):
    __tablename__ = "tournament_teams"

    id = Column(Integer, primary_key=True, index=True)
    tournament_id = Column(Integer, ForeignKey("tournaments.id"))
    team_id = Column(Integer, ForeignKey("teams.id"))
    group_name = Column(String, index=True)

    tournament = relationship("Tournament")
    team = relationship("Team")

class Match(Base):
    __tablename__ = "matches"

    id = Column(Integer, primary_key=True, index=True)
    tournament_id = Column(Integer, ForeignKey("tournaments.id"))
    home_team_id = Column(Integer, ForeignKey("teams.id"), nullable=True)
    away_team_id = Column(Integer, ForeignKey("teams.id"), nullable=True)
    home_score = Column(Integer, nullable=True)
    away_score = Column(Integer, nullable=True)
    home_score_penalties = Column(Integer, nullable=True)
    away_score_penalties = Column(Integer, nullable=True)
    status = Column(String, default="Scheduled") # Scheduled, Finished
    group_name = Column(String, index=True, nullable=True)
    date = Column(String, nullable=True)
    venue = Column(String, nullable=True)
    is_knockout = Column(Boolean, default=False)
    next_match_id = Column(Integer, ForeignKey("matches.id"), nullable=True)
    is_next_match_home = Column(Boolean, default=True)
    stage_name = Column(String, nullable=True)


    tournament = relationship("Tournament")
    home_team = relationship("Team", foreign_keys=[home_team_id])
    away_team = relationship("Team", foreign_keys=[away_team_id])
