from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
import string
from contextlib import asynccontextmanager

import models, schemas, database, sorting_engine, scheduler

models.Base.metadata.create_all(bind=database.engine)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    scheduler.start_scheduler()
    yield
    # Shutdown
    scheduler.stop_scheduler()

from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="FIFA World Cup 2026 Tracker API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
@app.head("/")
def health_check():
    return {"status": "ok"}

@app.post("/seed")
def seed_database(db: Session = Depends(database.get_db)):
    # Basic seed logic
    if db.query(models.Team).first():
        return {"msg": "Database already seeded"}

    t = models.Tournament(name="FIFA World Cup", year=2026)
    db.add(t)
    db.flush()

    # Create 48 teams
    teams = []
    for i in range(1, 49):
        code = f"T{i:02d}"
        team = models.Team(name=f"Team {code}", code=code)
        db.add(team)
        teams.append(team)
    
    db.flush()

    # Assign to 12 groups (A-L), 4 teams per group
    groups = string.ascii_uppercase[:12]
    team_idx = 0
    group_teams = {g: [] for g in groups}
    for g in groups:
        for _ in range(4):
            tt = models.TournamentTeam(tournament_id=t.id, team_id=teams[team_idx].id, group_name=g)
            db.add(tt)
            group_teams[g].append(teams[team_idx])
            team_idx += 1
    
    db.flush()

    # Create round-robin matches for each group
    for g in groups:
        g_teams = group_teams[g]
        # 1v2, 3v4, 1v3, 2v4, 1v4, 2v3
        pairs = [(0,1), (2,3), (0,2), (1,3), (0,3), (1,2)]
        for h_idx, a_idx in pairs:
            m = models.Match(
                tournament_id=t.id,
                home_team_id=g_teams[h_idx].id,
                away_team_id=g_teams[a_idx].id,
                group_name=g
            )
            db.add(m)
    
    db.commit()
    return {"msg": "Seeded 48 teams, 12 groups, and group stage matches."}


def _get_standings_data(db: Session):
    matches = db.query(models.Match).all()
    tournament_teams = db.query(models.TournamentTeam).all()
    
    teams_dict = {}
    for tt in tournament_teams:
        team = db.query(models.Team).filter(models.Team.id == tt.team_id).first()
        teams_dict[team.id] = {
            'id': team.id,
            'name': team.name,
            'code': team.code,
            'group_name': tt.group_name
        }
    
    matches_list = []
    for m in matches:
        matches_list.append({
            'home_team_id': m.home_team_id,
            'away_team_id': m.away_team_id,
            'home_score': m.home_score,
            'away_score': m.away_score,
            'status': m.status,
            'group_name': m.group_name
        })
    
    standings_flat = sorting_engine.calculate_standings(matches_list, list(teams_dict.values()))
    return sorting_engine.get_group_standings(standings_flat)


@app.get("/groups", response_model=List[schemas.GroupStandings])
def get_groups(db: Session = Depends(database.get_db)):
    grouped = _get_standings_data(db)
    
    # Sort groups A-L
    result = []
    for g in sorted(grouped.keys()):
        # Sort teams within group
        sorted_teams = sorted(grouped[g], key=lambda x: (x['points'], x['goal_difference'], x['goals_for']), reverse=True)
        result.append(schemas.GroupStandings(group_name=g, standings=sorted_teams))
    
    return result

@app.get("/groups/third-place", response_model=List[schemas.TeamStanding])
def get_third_place_teams(db: Session = Depends(database.get_db)):
    grouped = _get_standings_data(db)
    top_thirds = sorting_engine.get_top_third_place_teams(grouped, top_n=8)
    return top_thirds

@app.post("/matches/{match_id}/result", response_model=schemas.Match)
def update_match_result(match_id: int, result: schemas.MatchResult, db: Session = Depends(database.get_db)):
    match = db.query(models.Match).filter(models.Match.id == match_id).first()
    if not match:
        raise HTTPException(status_code=404, detail="Match not found")
    
    match.home_score = result.home_score
    match.away_score = result.away_score
    match.status = "Finished"
    db.commit()
    db.refresh(match)
    return match

@app.post("/update-real-teams")
def update_real_teams(db: Session = Depends(database.get_db)):
    real_teams = [{"name": "Mexico", "code": "MEX"}, {"name": "South Africa", "code": "RSA"}, {"name": "South Korea", "code": "KOR"}, {"name": "Czechia", "code": "CZE"}, {"name": "Canada", "code": "CAN"}, {"name": "Bosnia-Herzegovina", "code": "BIH"}, {"name": "United States", "code": "USA"}, {"name": "Paraguay", "code": "PAR"}, {"name": "Qatar", "code": "QAT"}, {"name": "Switzerland", "code": "SUI"}, {"name": "Brazil", "code": "BRA"}, {"name": "Morocco", "code": "MAR"}, {"name": "Haiti", "code": "HAI"}, {"name": "Scotland", "code": "SCO"}, {"name": "Australia", "code": "AUS"}, {"name": "Turkey", "code": "TUR"}, {"name": "Germany", "code": "GER"}, {"name": "Cura\u00e7ao", "code": "CUW"}, {"name": "Netherlands", "code": "NED"}, {"name": "Japan", "code": "JPN"}, {"name": "Ivory Coast", "code": "CIV"}, {"name": "Ecuador", "code": "ECU"}, {"name": "Sweden", "code": "SWE"}, {"name": "Tunisia", "code": "TUN"}, {"name": "Spain", "code": "ESP"}, {"name": "Cape Verde Islands", "code": "CPV"}, {"name": "Belgium", "code": "BEL"}, {"name": "Egypt", "code": "EGY"}, {"name": "Saudi Arabia", "code": "KSA"}, {"name": "Uruguay", "code": "URY"}, {"name": "Iran", "code": "IRN"}, {"name": "New Zealand", "code": "NZL"}, {"name": "France", "code": "FRA"}, {"name": "Senegal", "code": "SEN"}, {"name": "Iraq", "code": "IRQ"}, {"name": "Norway", "code": "NOR"}, {"name": "Argentina", "code": "ARG"}, {"name": "Algeria", "code": "ALG"}, {"name": "Austria", "code": "AUT"}, {"name": "Jordan", "code": "JOR"}, {"name": "Portugal", "code": "POR"}, {"name": "Congo DR", "code": "COD"}, {"name": "England", "code": "ENG"}, {"name": "Croatia", "code": "CRO"}, {"name": "Ghana", "code": "GHA"}, {"name": "Panama", "code": "PAN"}, {"name": "Uzbekistan", "code": "UZB"}, {"name": "Colombia", "code": "COL"}]
    teams = db.query(models.Team).order_by(models.Team.id).all()
    if not teams or len(teams) < 48:
        return {"error": "Not enough teams to update."}
    for i, rt in enumerate(real_teams):
        teams[i].name = rt["name"]
        teams[i].code = rt["code"]
    db.commit()
    return {"msg": "Updated 48 teams to real names."}

from pydantic import BaseModel
from typing import Optional, Any
class DBRestoreData(BaseModel):
    teams: list[dict]
    tournament_teams: list[dict]
    matches: list[dict]

@app.post("/restore-db")
def restore_db(data: DBRestoreData, db: Session = Depends(database.get_db)):
    # Delete all existing data safely
    db.query(models.Match).delete()
    db.query(models.TournamentTeam).delete()
    db.query(models.Tournament).delete()
    db.query(models.Team).delete()
    db.flush()

    t = models.Tournament(name="FIFA World Cup", year=2026)
    db.add(t)
    db.flush()

    # Re-add teams keeping same ID mapping
    team_map = {}
    for team_dict in data.teams:
        t_model = models.Team(id=team_dict['id'], name=team_dict['name'], code=team_dict['code'])
        db.add(t_model)
        team_map[team_dict['id']] = team_dict['id']
    
    db.flush()

    for tt_dict in data.tournament_teams:
        tt_model = models.TournamentTeam(
            id=tt_dict['id'], 
            tournament_id=t.id, 
            team_id=tt_dict['team_id'], 
            group_name=tt_dict['group_name']
        )
        db.add(tt_model)

    db.flush()

    for m_dict in data.matches:
        m_model = models.Match(
            id=m_dict['id'],
            tournament_id=t.id,
            home_team_id=m_dict['home_team_id'],
            away_team_id=m_dict['away_team_id'],
            home_score=m_dict['home_score'],
            away_score=m_dict['away_score'],
            status=m_dict['status'],
            group_name=m_dict['group_name'],
            date=m_dict['date']
        )
        db.add(m_model)

    db.commit()
    return {"msg": "Database restored successfully."}

import sync_live_data

@app.post("/matches/sync-live")
def sync_live_matches(db: Session = Depends(database.get_db)):
    return sync_live_data.sync_matches_from_api(db)

@app.get("/matches", response_model=List[schemas.Match])
def get_matches(db: Session = Depends(database.get_db)):
    matches = db.query(models.Match).all()
    # Populate team names for frontend convenience
    for m in matches:
        m.home_team_name = m.home_team.name if m.home_team else "Unknown"
        m.away_team_name = m.away_team.name if m.away_team else "Unknown"
    
    # Sort matches by date if available
    return sorted(matches, key=lambda x: x.date or "")
