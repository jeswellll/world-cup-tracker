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
            
        from sqlalchemy import or_
        # Find the match in the local DB regardless of home/away orientation
        db_match = db.query(models.Match).filter(
            or_(
                (models.Match.home_team_id == home_team.id) & (models.Match.away_team_id == away_team.id),
                (models.Match.home_team_id == away_team.id) & (models.Match.away_team_id == home_team.id)
            )
        ).first()
        
        if db_match:
            score_data = m.get("score", {}).get("fullTime", {})
            api_h_score = score_data.get("home")
            api_a_score = score_data.get("away")
            venue_name = m.get("venue")
            
            updated = False
            # Update score if available
            if api_h_score is not None and api_a_score is not None:
                if db_match.home_team_id == home_team.id:
                    db_match.home_score = api_h_score
                    db_match.away_score = api_a_score
                else:
                    # The API flipped the teams, so flip the scores for our database
                    db_match.home_score = api_a_score
                    db_match.away_score = api_h_score
                    
                db_match.status = "Finished" if status in ["FINISHED", "AWARDED"] else "In Progress"
                updated = True
                
            # Update venue if available
            if venue_name and db_match.venue != venue_name:
                db_match.venue = venue_name
                updated = True
                
            if updated:
                updated_count += 1
                
    db.commit()
    return {"msg": f"Successfully synced {updated_count} matches from API."}
