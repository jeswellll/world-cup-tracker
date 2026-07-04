from sqlalchemy.orm import Session
import models
import sorting_engine

def populate_round_of_32(db: Session):
    # Check if R32 is already populated
    r32_match = db.query(models.Match).filter(models.Match.stage_name == "LAST_32").first()
    if r32_match and r32_match.home_team_id is not None:
        return # Already populated

    # Get standings
    matches = db.query(models.Match).filter(models.Match.is_knockout == False).all()
    tournament_teams = db.query(models.TournamentTeam).all()
    
    # Ensure all group matches are finished
    if any(m.status != "Finished" for m in matches):
        return
        
    teams_dict = {}
    for tt in tournament_teams:
        team = db.query(models.Team).filter(models.Team.id == tt.team_id).first()
        teams_dict[team.id] = {
            'id': team.id, 'name': team.name, 'code': team.code, 'group_name': tt.group_name
        }
    
    matches_list = [{'home_team_id': m.home_team_id, 'away_team_id': m.away_team_id, 'home_score': m.home_score, 'away_score': m.away_score, 'status': m.status, 'group_name': m.group_name} for m in matches]
    
    standings_flat = sorting_engine.calculate_standings(matches_list, list(teams_dict.values()))
    grouped = sorting_engine.get_group_standings(standings_flat)
    
    # Map teams
    winners = {g: grouped[g][0]['team_id'] for g in grouped}
    runners_up = {g: grouped[g][1]['team_id'] for g in grouped}
    
    # 3rd place mapping (simplified for this script: just take top 8 3rd places)
    top_thirds = sorting_engine.get_top_third_place_teams(grouped, top_n=8)
    thirds_by_group = {t['group_name']: t['team_id'] for t in top_thirds}
    # For now, just assign the first 8 third place teams in order to the 8 slots
    thirds_list = list(thirds_by_group.values())

    # Map to M73-M88
    mapping = {
        73: (runners_up['A'], runners_up['B']),
        74: (winners['E'], thirds_list[0] if len(thirds_list) > 0 else None),
        75: (winners['C'], runners_up['F']),
        76: (winners['I'], thirds_list[1] if len(thirds_list) > 1 else None),
        77: (winners['H'], runners_up['J']),
        78: (runners_up['E'], runners_up['I']),
        79: (winners['D'], thirds_list[2] if len(thirds_list) > 2 else None),
        80: (winners['G'], thirds_list[3] if len(thirds_list) > 3 else None),
        81: (winners['A'], thirds_list[4] if len(thirds_list) > 4 else None),
        82: (winners['B'], thirds_list[5] if len(thirds_list) > 5 else None),
        83: (runners_up['K'], runners_up['L']),
        84: (winners['F'], runners_up['C']),
        85: (winners['L'], thirds_list[6] if len(thirds_list) > 6 else None),
        86: (winners['J'], runners_up['H']),
        87: (winners['K'], thirds_list[7] if len(thirds_list) > 7 else None),
        88: (runners_up['D'], runners_up['G']),
    }
    
    for m_id, (home_id, away_id) in mapping.items():
        if home_id and away_id:
            db_m = db.query(models.Match).filter(models.Match.id == m_id).first()
            if db_m:
                db_m.home_team_id = home_id
                db_m.away_team_id = away_id
    
    db.commit()
