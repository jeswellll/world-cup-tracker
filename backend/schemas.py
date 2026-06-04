from pydantic import BaseModel
from typing import Optional, List

class TeamBase(BaseModel):
    name: str
    code: str

class Team(TeamBase):
    id: int
    class Config:
        from_attributes = True

class TournamentBase(BaseModel):
    name: str
    year: int

class Tournament(TournamentBase):
    id: int
    class Config:
        from_attributes = True

class MatchResult(BaseModel):
    home_score: int
    away_score: int

class MatchBase(BaseModel):
    home_team_id: int
    away_team_id: int
    group_name: Optional[str] = None

class Match(MatchBase):
    id: int
    tournament_id: int
    home_score: Optional[int] = None
    away_score: Optional[int] = None
    status: str
    date: Optional[str] = None
    venue: Optional[str] = None
    home_team_name: Optional[str] = None
    away_team_name: Optional[str] = None

    class Config:
        from_attributes = True

class TeamStanding(BaseModel):
    team_id: int
    team_name: str
    team_code: str
    played: int
    won: int
    drawn: int
    lost: int
    goals_for: int
    goals_against: int
    goal_difference: int
    points: int
    group_name: str
    locked_rank: Optional[int] = None

class GroupStandings(BaseModel):
    group_name: str
    standings: List[TeamStanding]
