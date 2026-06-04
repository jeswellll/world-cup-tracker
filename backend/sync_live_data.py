import os
import requests
from sqlalchemy.orm import Session
import database, models
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("SPORTS_API_KEY")
URL = "http://api.football-data.org/v4/competitions/2000/matches"

def sync_matches_from_api(db: Session):
    if not API_KEY:
        print("No API Key found. Sync aborted.")
        return {"error": "Missing SPORTS_API_KEY"}
        
    headers = {"X-Auth-Token": API_KEY}
    response = requests.get(URL, headers=headers)
    
    if response.status_code != 200:
        print(f"Failed to fetch data: {response.text}")
        return {"error": f"API returned {response.status_code}"}
        
    data = response.json()
    matches_data = data.get("matches", [])
    
    updated_count = 0
    for m in matches_data:
        status = m.get("status")
        # We only care about matches that have started or finished
        if status not in ["IN_PLAY", "PAUSED", "FINISHED", "AWARDED", "TIMED"]:
            continue
            
        home_tla = m.get("homeTeam", {}).get("tla")
        away_tla = m.get("awayTeam", {}).get("tla")
        
        if not home_tla or not away_tla:
            continue
            
        # Find the local teams
        home_team = db.query(models.Team).filter(models.Team.code == home_tla).first()
        away_team = db.query(models.Team).filter(models.Team.code == away_tla).first()
        
        if not home_team or not away_team:
            continue
            
        # Find the match in the local DB
        db_match = db.query(models.Match).filter(
            models.Match.home_team_id == home_team.id,
            models.Match.away_team_id == away_team.id
        ).first()
        
        if db_match:
            score_data = m.get("score", {}).get("fullTime", {})
            h_score = score_data.get("home")
            a_score = score_data.get("away")
            
            # Update score if available
            if h_score is not None and a_score is not None:
                db_match.home_score = h_score
                db_match.away_score = a_score
                db_match.status = "Finished" if status in ["FINISHED", "AWARDED"] else "In Progress"
                updated_count += 1
                
    db.commit()
    return {"msg": f"Successfully synced {updated_count} matches from API."}
