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
    
    import populate_knockouts
    populate_knockouts.populate_round_of_32(db)
    
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
            score_data = m.get("score", {})
            ft = score_data.get("fullTime", {})
            api_h_score = ft.get("home")
            api_a_score = ft.get("away")
            
            penalties = score_data.get("penalties", {})
            api_h_pen = penalties.get("home")
            api_a_pen = penalties.get("away")
            
            venue_name = m.get("venue")
            
            updated = False
            # Update score if available
            if api_h_score is not None and api_a_score is not None:
                if db_match.home_team_id == home_team.id:
                    db_match.home_score = api_h_score
                    db_match.away_score = api_a_score
                    db_match.home_score_penalties = api_h_pen
                    db_match.away_score_penalties = api_a_pen
                else:
                    # The API flipped the teams, so flip the scores for our database
                    db_match.home_score = api_a_score
                    db_match.away_score = api_h_score
                    db_match.home_score_penalties = api_a_pen
                    db_match.away_score_penalties = api_h_pen
                    
                db_match.status = "Finished" if status in ["FINISHED", "AWARDED"] else "In Progress"
                updated = True
                
            # Update venue if available
            if venue_name and db_match.venue != venue_name:
                db_match.venue = venue_name
                updated = True
                
            # Bracket Progression
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

            if updated:
                updated_count += 1
                
    db.commit()
    return {"msg": f"Successfully synced {updated_count} matches from API."}
