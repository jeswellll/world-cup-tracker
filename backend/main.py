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

@app.post("/reset-db")
def reset_database(db: Session = Depends(database.get_db)):
    # Drop all tables and recreate them cleanly
    models.Base.metadata.drop_all(bind=database.engine)
    models.Base.metadata.create_all(bind=database.engine)
    return {"msg": "Database completely wiped and recreated."}

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
    
    # Seed Knockout Matches
    knockouts = [
        {'id': 73, 'next_match_id': 90, 'is_next_match_home': True, 'stage': 'LAST_32', 'date': '2026-06-28T19:00:00.000Z', 'venue': 'Los Angeles (Inglewood)'},
        {'id': 74, 'next_match_id': 89, 'is_next_match_home': True, 'stage': 'LAST_32', 'date': '2026-06-29T20:30:00.000Z', 'venue': 'Boston (Foxborough)'},
        {'id': 75, 'next_match_id': 90, 'is_next_match_home': False, 'stage': 'LAST_32', 'date': '2026-06-30T01:00:00.000Z', 'venue': 'Monterrey (Guadalupe)'},
        {'id': 76, 'next_match_id': 91, 'is_next_match_home': True, 'stage': 'LAST_32', 'date': '2026-06-29T17:00:00.000Z', 'venue': 'Houston'},
        {'id': 77, 'next_match_id': 89, 'is_next_match_home': False, 'stage': 'LAST_32', 'date': '2026-06-30T21:00:00.000Z', 'venue': 'New York/New Jersey (East Rutherford)'},
        {'id': 78, 'next_match_id': 91, 'is_next_match_home': False, 'stage': 'LAST_32', 'date': '2026-06-30T17:00:00.000Z', 'venue': 'Dallas (Arlington)'},
        {'id': 79, 'next_match_id': 92, 'is_next_match_home': True, 'stage': 'LAST_32', 'date': '2026-07-01T01:00:00.000Z', 'venue': 'Mexico City'},
        {'id': 80, 'next_match_id': 92, 'is_next_match_home': False, 'stage': 'LAST_32', 'date': '2026-07-01T16:00:00.000Z', 'venue': 'Atlanta'},
        {'id': 81, 'next_match_id': 94, 'is_next_match_home': True, 'stage': 'LAST_32', 'date': '2026-07-02T00:00:00.000Z', 'venue': 'San Francisco Bay Area (Santa Clara)'},
        {'id': 82, 'next_match_id': 94, 'is_next_match_home': False, 'stage': 'LAST_32', 'date': '2026-07-01T20:00:00.000Z', 'venue': 'Seattle'},
        {'id': 83, 'next_match_id': 93, 'is_next_match_home': True, 'stage': 'LAST_32', 'date': '2026-07-02T23:00:00.000Z', 'venue': 'Toronto'},
        {'id': 84, 'next_match_id': 93, 'is_next_match_home': False, 'stage': 'LAST_32', 'date': '2026-07-02T19:00:00.000Z', 'venue': 'Los Angeles (Inglewood)'},
        {'id': 85, 'next_match_id': 96, 'is_next_match_home': True, 'stage': 'LAST_32', 'date': '2026-07-03T03:00:00.000Z', 'venue': 'Vancouver'},
        {'id': 86, 'next_match_id': 95, 'is_next_match_home': True, 'stage': 'LAST_32', 'date': '2026-07-03T22:00:00.000Z', 'venue': 'Miami (Miami Gardens)'},
        {'id': 87, 'next_match_id': 96, 'is_next_match_home': False, 'stage': 'LAST_32', 'date': '2026-07-04T01:30:00.000Z', 'venue': 'Kansas City'},
        {'id': 88, 'next_match_id': 95, 'is_next_match_home': False, 'stage': 'LAST_32', 'date': '2026-07-03T18:00:00.000Z', 'venue': 'Dallas (Arlington)'},
        {'id': 89, 'next_match_id': 97, 'is_next_match_home': True, 'stage': 'LAST_16', 'date': '2026-07-04T21:00:00.000Z', 'venue': 'Philadelphia'},
        {'id': 90, 'next_match_id': 97, 'is_next_match_home': False, 'stage': 'LAST_16', 'date': '2026-07-04T17:00:00.000Z', 'venue': 'Houston'},
        {'id': 91, 'next_match_id': 99, 'is_next_match_home': True, 'stage': 'LAST_16', 'date': '2026-07-05T20:00:00.000Z', 'venue': 'New York/New Jersey (East Rutherford)'},
        {'id': 92, 'next_match_id': 99, 'is_next_match_home': False, 'stage': 'LAST_16', 'date': '2026-07-06T00:00:00.000Z', 'venue': 'Mexico City'},
        {'id': 93, 'next_match_id': 98, 'is_next_match_home': True, 'stage': 'LAST_16', 'date': '2026-07-06T19:00:00.000Z', 'venue': 'Dallas (Arlington)'},
        {'id': 94, 'next_match_id': 98, 'is_next_match_home': False, 'stage': 'LAST_16', 'date': '2026-07-07T00:00:00.000Z', 'venue': 'Seattle'},
        {'id': 95, 'next_match_id': 100, 'is_next_match_home': True, 'stage': 'LAST_16', 'date': '2026-07-07T16:00:00.000Z', 'venue': 'Atlanta'},
        {'id': 96, 'next_match_id': 100, 'is_next_match_home': False, 'stage': 'LAST_16', 'date': '2026-07-07T20:00:00.000Z', 'venue': 'Vancouver'},
        {'id': 97, 'next_match_id': 101, 'is_next_match_home': True, 'stage': 'QUARTER_FINALS', 'date': '2026-07-09T20:00:00.000Z', 'venue': 'Boston (Foxborough)'},
        {'id': 98, 'next_match_id': 101, 'is_next_match_home': False, 'stage': 'QUARTER_FINALS', 'date': '2026-07-10T19:00:00.000Z', 'venue': 'Los Angeles (Inglewood)'},
        {'id': 99, 'next_match_id': 102, 'is_next_match_home': True, 'stage': 'QUARTER_FINALS', 'date': '2026-07-11T21:00:00.000Z', 'venue': 'Miami (Miami Gardens)'},
        {'id': 100, 'next_match_id': 102, 'is_next_match_home': False, 'stage': 'QUARTER_FINALS', 'date': '2026-07-12T01:00:00.000Z', 'venue': 'Kansas City'},
        {'id': 101, 'next_match_id': 104, 'is_next_match_home': True, 'stage': 'SEMI_FINALS', 'date': '2026-07-14T19:00:00.000Z', 'venue': 'Dallas (Arlington)'},
        {'id': 102, 'next_match_id': 104, 'is_next_match_home': False, 'stage': 'SEMI_FINALS', 'date': '2026-07-15T19:00:00.000Z', 'venue': 'Atlanta'},
        {'id': 103, 'next_match_id': None, 'is_next_match_home': True, 'stage': 'THIRD_PLACE', 'date': '2026-07-18T21:00:00.000Z', 'venue': 'Miami (Miami Gardens)'},
        {'id': 104, 'next_match_id': None, 'is_next_match_home': True, 'stage': 'FINAL', 'date': '2026-07-19T19:00:00.000Z', 'venue': 'New York/New Jersey (East Rutherford)'},
    ]
    for k in knockouts:
        m = models.Match(
            id=k['id'],
            tournament_id=t.id,
            home_team_id=None,
            away_team_id=None,
            is_knockout=True,
            next_match_id=k['next_match_id'],
            is_next_match_home=k['is_next_match_home'],
            stage_name=k['stage'],
            date=k['date'],
            venue=k['venue'],
            status="Scheduled"
        )
        db.add(m)
    
    db.commit()
    return {"msg": "Seeded 48 teams, 12 groups, group stage matches, and 32 knockout matches."}


def _get_standings_data(db: Session):
    matches = db.query(models.Match).filter(models.Match.is_knockout == False).all()
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

@app.get("/groups/third-place-assignments")
def get_third_place_assignments(db: Session = Depends(database.get_db)):
    unfinished_matches = db.query(models.Match).filter(models.Match.status != "Finished").count()
    if unfinished_matches > 0:
        return {}

    grouped = _get_standings_data(db)
    top_thirds = sorting_engine.get_top_third_place_teams(grouped, top_n=8)
    
    # Convert to dicts expected by sorting_engine
    top_thirds_dicts = [
        {
            'team_id': t['team_id'],
            'team_name': t['team_name'],
            'code': t['team_code'],
            'group_name': t['group_name']
        }
        for t in top_thirds
    ]
    
    assignments = sorting_engine.resolve_third_place_matchups(top_thirds_dicts)
    return assignments

def progress_knockout_match(db: Session, db_match: models.Match):
    if db_match.is_knockout and db_match.status == "Finished" and db_match.next_match_id:
        # Determine Winner
        winner_id = None
        loser_id = None
        
        h_goals = db_match.home_score or 0
        a_goals = db_match.away_score or 0
        h_pens = db_match.home_score_penalties or 0
        a_pens = db_match.away_score_penalties or 0
        
        if h_goals > a_goals:
            winner_id, loser_id = db_match.home_team_id, db_match.away_team_id
        elif a_goals > h_goals:
            winner_id, loser_id = db_match.away_team_id, db_match.home_team_id
        else:
            if h_pens > a_pens:
                winner_id, loser_id = db_match.home_team_id, db_match.away_team_id
            elif a_pens > h_pens:
                winner_id, loser_id = db_match.away_team_id, db_match.home_team_id
                
        if winner_id:
            next_m = db.query(models.Match).filter(models.Match.id == db_match.next_match_id).first()
            if next_m:
                if db_match.is_next_match_home:
                    next_m.home_team_id = winner_id
                else:
                    next_m.away_team_id = winner_id
                    
        # Third place edge case (if it's Semi Finals 101 or 102, loser goes to 103)
        if db_match.id in [101, 102] and loser_id:
            third_m = db.query(models.Match).filter(models.Match.id == 103).first()
            if third_m:
                if db_match.id == 101:
                    third_m.home_team_id = loser_id
                else:
                    third_m.away_team_id = loser_id


@app.post("/matches/{match_id}/result", response_model=schemas.Match)
def update_match_result(match_id: int, result: schemas.MatchResult, db: Session = Depends(database.get_db)):
    match = db.query(models.Match).filter(models.Match.id == match_id).first()
    if not match:
        raise HTTPException(status_code=404, detail="Match not found")
    
    match.home_score = result.home_score
    match.away_score = result.away_score
    match.home_score_penalties = result.home_score_penalties
    match.away_score_penalties = result.away_score_penalties
    match.status = "Finished"
    progress_knockout_match(db, match)
    db.commit()
    db.refresh(match)
    return match

@app.post("/update-real-teams")
def update_real_teams(db: Session = Depends(database.get_db)):
    real_teams = [
        {"name": "Mexico", "code": "MEX"}, {"name": "South Africa", "code": "RSA"}, {"name": "South Korea", "code": "KOR"}, {"name": "Czechia", "code": "CZE"},
        {"name": "Canada", "code": "CAN"}, {"name": "Bosnia-Herzegovina", "code": "BIH"}, {"name": "Qatar", "code": "QAT"}, {"name": "Switzerland", "code": "SUI"},
        {"name": "Brazil", "code": "BRA"}, {"name": "Morocco", "code": "MAR"}, {"name": "Haiti", "code": "HAI"}, {"name": "Scotland", "code": "SCO"},
        {"name": "United States", "code": "USA"}, {"name": "Paraguay", "code": "PAR"}, {"name": "Australia", "code": "AUS"}, {"name": "Turkey", "code": "TUR"},
        {"name": "Germany", "code": "GER"}, {"name": "Cura\u00e7ao", "code": "CUW"}, {"name": "Ivory Coast", "code": "CIV"}, {"name": "Ecuador", "code": "ECU"},
        {"name": "Netherlands", "code": "NED"}, {"name": "Japan", "code": "JPN"}, {"name": "Sweden", "code": "SWE"}, {"name": "Tunisia", "code": "TUN"},
        {"name": "Belgium", "code": "BEL"}, {"name": "Egypt", "code": "EGY"}, {"name": "Iran", "code": "IRN"}, {"name": "New Zealand", "code": "NZL"},
        {"name": "Spain", "code": "ESP"}, {"name": "Cape Verde Islands", "code": "CPV"}, {"name": "Saudi Arabia", "code": "KSA"}, {"name": "Uruguay", "code": "URU"},
        {"name": "France", "code": "FRA"}, {"name": "Senegal", "code": "SEN"}, {"name": "Iraq", "code": "IRQ"}, {"name": "Norway", "code": "NOR"},
        {"name": "Argentina", "code": "ARG"}, {"name": "Algeria", "code": "ALG"}, {"name": "Austria", "code": "AUT"}, {"name": "Jordan", "code": "JOR"},
        {"name": "Portugal", "code": "POR"}, {"name": "Congo DR", "code": "COD"}, {"name": "Uzbekistan", "code": "UZB"}, {"name": "Colombia", "code": "COL"},
        {"name": "England", "code": "ENG"}, {"name": "Croatia", "code": "CRO"}, {"name": "Ghana", "code": "GHA"}, {"name": "Panama", "code": "PAN"}
    ]
    teams = db.query(models.Team).order_by(models.Team.id).all()
    if not teams or len(teams) < 48:
        return {"error": "Not enough teams to update."}
    
    # Temporarily append a suffix to avoid UNIQUE constraint violations when swapping
    for t in teams:
        t.code = t.code + "_tmp"
    db.flush()

    for i, rt in enumerate(real_teams):
        teams[i].name = rt["name"]
        teams[i].code = rt["code"]
    db.commit()
    return {"msg": "Updated 48 teams to real names."}

from pydantic import BaseModel
class MatchDateData(BaseModel):
    home_code: str
    away_code: str
    date: str

@app.post("/restore-dates")
def restore_dates(data: list[MatchDateData], db: Session = Depends(database.get_db)):
    updated = 0
    for m in data:
        home = db.query(models.Team).filter(models.Team.code == m.home_code).first()
        away = db.query(models.Team).filter(models.Team.code == m.away_code).first()
        if not home or not away:
            continue
        match = db.query(models.Match).filter(
            ((models.Match.home_team_id == home.id) & (models.Match.away_team_id == away.id)) |
            ((models.Match.home_team_id == away.id) & (models.Match.away_team_id == home.id))
        ).first()
        if match:
            match.date = m.date
            updated += 1
    db.commit()
    return {"msg": f"Restored dates for {updated} matches."}

import random

@app.get("/reset-scores")
def reset_scores(db: Session = Depends(database.get_db)):
    """Resets all matches back to 'Scheduled' state without altering dates, venues, or team configurations."""
    matches = db.query(models.Match).all()
    updated = 0
    for m in matches:
        if m.status != 'Scheduled' or m.home_score is not None or m.away_score is not None:
            m.status = 'Scheduled'
            m.home_score = None
            m.away_score = None
            updated += 1
    db.commit()
    return {"msg": f"Reset {updated} matches back to Scheduled."}

@app.get("/simulate-match")
def simulate_match(db: Session = Depends(database.get_db)):
    """Simulates a live match by taking an 'In Progress' match and scoring a goal, or starting a new 'Scheduled' match."""
    match = db.query(models.Match).filter(models.Match.status == 'In Progress').first()
    
    if not match:
        match = db.query(models.Match).filter(models.Match.status == 'Scheduled').first()
        if not match:
            return {"msg": "No matches available to simulate."}
        match.status = 'In Progress'
        match.home_score = 0
        match.away_score = 0
    
    # Give a goal to either home or away randomly
    if random.choice([True, False]):
        match.home_score += 1
    else:
        match.away_score += 1
        
    db.commit()
    return {"msg": f"Simulated {match.home_team.name} {match.home_score} - {match.away_score} {match.away_team.name} (In Progress)"}

@app.get("/simulate-end-match")
def simulate_end_match(db: Session = Depends(database.get_db)):
    """Finds the current 'In Progress' match and sets it to 'Finished'."""
    match = db.query(models.Match).filter(models.Match.status == 'In Progress').first()
    if not match:
        return {"msg": "There are no matches currently in progress."}
        
    match.status = 'Finished'
    progress_knockout_match(db, match)
    db.commit()
    return {"msg": f"Match Finished! {match.home_team.name} {match.home_score} - {match.away_score} {match.away_team.name}"}

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
