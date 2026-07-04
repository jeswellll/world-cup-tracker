import pandas as pd
from typing import List, Dict, Any

def calculate_standings(matches: List[Dict[str, Any]], teams: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Calculate standings from a list of match dictionaries and team dictionaries.
    matches = [{'home_team_id': 1, 'away_team_id': 2, 'home_score': 2, 'away_score': 1, 'status': 'Finished', 'group_name': 'A'}, ...]
    teams = [{'id': 1, 'name': 'USA', 'code': 'USA', 'group_name': 'A'}, ...]
    """
    if not teams:
        return []

    df_teams = pd.DataFrame(teams)
    
    # Initialize stats
    stats = []
    for _, team in df_teams.iterrows():
        stats.append({
            'team_id': team['id'],
            'team_name': team['name'],
            'team_code': team['code'],
            'group_name': team.get('group_name', ''),
            'played': 0, 'won': 0, 'drawn': 0, 'lost': 0,
            'goals_for': 0, 'goals_against': 0, 'goal_difference': 0, 'points': 0
        })
    
    df_stats = pd.DataFrame(stats).set_index('team_id')

    # Process matches
    df_matches = pd.DataFrame(matches)
    if not df_matches.empty:
        finished_matches = df_matches[df_matches['status'].isin(['Finished', 'In Progress'])]
        for _, match in finished_matches.iterrows():
            h_id = match['home_team_id']
            a_id = match['away_team_id']
            h_score = match['home_score']
            a_score = match['away_score']

            if pd.isna(h_score) or pd.isna(a_score):
                continue
                
            # Update played
            df_stats.loc[h_id, 'played'] += 1
            df_stats.loc[a_id, 'played'] += 1
            
            # Update goals
            df_stats.loc[h_id, 'goals_for'] += h_score
            df_stats.loc[h_id, 'goals_against'] += a_score
            df_stats.loc[a_id, 'goals_for'] += a_score
            df_stats.loc[a_id, 'goals_against'] += h_score
            
            # Update results and points
            if h_score > a_score:
                df_stats.loc[h_id, 'won'] += 1
                df_stats.loc[h_id, 'points'] += 3
                df_stats.loc[a_id, 'lost'] += 1
            elif a_score > h_score:
                df_stats.loc[a_id, 'won'] += 1
                df_stats.loc[a_id, 'points'] += 3
                df_stats.loc[h_id, 'lost'] += 1
            else:
                df_stats.loc[h_id, 'drawn'] += 1
                df_stats.loc[a_id, 'drawn'] += 1
                df_stats.loc[h_id, 'points'] += 1
                df_stats.loc[a_id, 'points'] += 1

    # Calculate goal difference
    df_stats['goal_difference'] = df_stats['goals_for'] - df_stats['goals_against']

    df_stats = df_stats.reset_index()

    from functools import cmp_to_key

    standings = df_stats.to_dict('records')

    def compare_teams(t1, t2):
        if t1['points'] != t2['points']:
            return t1['points'] - t2['points']
        
        # Tie breaker 1: Head-to-Head
        match = df_matches[
            ((df_matches['home_team_id'] == t1['team_id']) & (df_matches['away_team_id'] == t2['team_id'])) |
            ((df_matches['home_team_id'] == t2['team_id']) & (df_matches['away_team_id'] == t1['team_id']))
        ]
        if not match.empty:
            m = match.iloc[0]
            if m['status'] in ['Finished', 'In Progress']:
                if m['home_team_id'] == t1['team_id']:
                    if m['home_score'] > m['away_score']: return 1
                    if m['home_score'] < m['away_score']: return -1
                else:
                    if m['away_score'] > m['home_score']: return 1
                    if m['away_score'] < m['home_score']: return -1
        
        # Tie breaker 2: Goal Difference
        if t1['goal_difference'] != t2['goal_difference']:
            return t1['goal_difference'] - t2['goal_difference']
            
        # Tie breaker 3: Goals For
        return t1['goals_for'] - t2['goals_for']

    standings = sorted(standings, key=cmp_to_key(compare_teams), reverse=True)

    # Mathematical Qualification Engine
    # Group the standings and matches by group
    from itertools import product

    # Set default
    for row in standings:
        row['locked_rank'] = None

    grouped = {}
    for row in standings:
        g = row['group_name']
        if g not in grouped:
            grouped[g] = []
        grouped[g].append(row)

    for g, g_teams in grouped.items():
        # Get scheduled matches for this group
        g_scheduled = [m for m in matches if m.get('group_name') == g and m.get('status') != 'Finished']
        
        # If no scheduled matches, ranks are perfectly locked by definition
        if not g_scheduled:
            for i, team in enumerate(g_teams):
                team['locked_rank'] = i + 1
            continue

        # Extract base points
        base_points = {t['team_id']: t['points'] for t in g_teams}
        team_ids = list(base_points.keys())

        absolute_best = {tid: 4 for tid in team_ids}
        absolute_worst = {tid: 1 for tid in team_ids}

        # Simulate all 3^N scenarios
        # Outcome tuples: (home_pts, away_pts)
        outcomes = [(3, 0), (1, 1), (0, 3)]
        
        # Generator for all combinations of outcomes
        # e.g. product(outcomes, repeat=2) gives all 9 combinations for 2 matches
        # Limit to 6 matches max (729 scenarios) to prevent infinite loops if data is bad
        if len(g_scheduled) <= 6:
            for combo in product(outcomes, repeat=len(g_scheduled)):
                scenario_points = base_points.copy()
                for match, outcome in zip(g_scheduled, combo):
                    h_id = match['home_team_id']
                    a_id = match['away_team_id']
                    if h_id in scenario_points: scenario_points[h_id] += outcome[0]
                    if a_id in scenario_points: scenario_points[a_id] += outcome[1]

                # Find best and worst rank for each team in this scenario based strictly on points
                for tid in team_ids:
                    pts = scenario_points[tid]
                    # Best rank: 1 + number of teams with strictly more points
                    better_count = sum(1 for other_pts in scenario_points.values() if other_pts > pts)
                    best_rank = better_count + 1
                    
                    # Worst rank: number of teams with greater or equal points
                    equal_or_better_count = sum(1 for other_pts in scenario_points.values() if other_pts >= pts)
                    worst_rank = equal_or_better_count
                    
                    if best_rank < absolute_best[tid]: absolute_best[tid] = best_rank
                    if worst_rank > absolute_worst[tid]: absolute_worst[tid] = worst_rank

            # Assign locked rank if best == worst
            for i, team in enumerate(g_teams):
                tid = team['team_id']
                if absolute_best[tid] == absolute_worst[tid]:
                    team['locked_rank'] = absolute_best[tid]

    return standings

def get_group_standings(standings: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
    """Group the overall sorted standings by group_name."""
    groups = {}
    for row in standings:
        g = row['group_name']
        if g not in groups:
            groups[g] = []
        groups[g].append(row)
    return groups

def get_top_third_place_teams(grouped_standings: Dict[str, List[Dict[str, Any]]], top_n: int = 8) -> List[Dict[str, Any]]:
    """Extract third place teams from each group, sort them, and return the top N."""
    third_place_teams = []
    
    for group_name, teams in grouped_standings.items():
        if len(teams) >= 3:
            # The list is already sorted by the tie-breakers within the group since calculate_standings sorts everything
            # Wait, calculate_standings sorted ALL teams globally. 
            # We need to sort within group first to find the 3rd place team.
            # Let's ensure the teams are sorted correctly within the group
            sorted_group = sorted(teams, key=lambda x: (x['points'], x['goal_difference'], x['goals_for']), reverse=True)
            third_place_teams.append(sorted_group[2])

    # Now sort the third place teams globally
    sorted_thirds = sorted(third_place_teams, key=lambda x: (x['points'], x['goal_difference'], x['goals_for']), reverse=True)
    
    return sorted_thirds[:top_n]

def resolve_third_place_matchups(third_place_teams: List[Dict[str, Any]]) -> Dict[int, Dict[str, Any]]:
    """
    Given the top 8 third-place teams (each should have a 'group_name' and 'team_id'),
    assign them to the 8 designated Match IDs.
    Returns a dictionary mapping Match ID -> Team dictionary.
    """
    if len(third_place_teams) != 8:
        return {}
        
    # The 8 knockout slots and their allowed source groups for 3rd place teams
    slots = {
        74: ['A', 'B', 'C', 'D', 'F'],
        77: ['C', 'D', 'F', 'G', 'H'],
        79: ['C', 'E', 'F', 'H', 'I'],
        80: ['E', 'H', 'I', 'J', 'K'],
        81: ['B', 'E', 'F', 'I', 'J'],
        82: ['A', 'E', 'H', 'I', 'J'],
        85: ['E', 'F', 'G', 'I', 'J'],
        87: ['D', 'E', 'I', 'J', 'L']
    }
    
    match_ids = list(slots.keys())
    assignments = {} # Match ID -> Team
    used_teams = set()
    
    def backtrack(slot_idx: int) -> bool:
        if slot_idx == len(match_ids):
            return True # All assigned successfully!
            
        current_match_id = match_ids[slot_idx]
        allowed_groups = slots[current_match_id]
        
        for team in third_place_teams:
            team_id = team['team_id']
            group = team['group_name']
            
            if team_id not in used_teams and group in allowed_groups:
                # Try assigning this team
                assignments[current_match_id] = team
                used_teams.add(team_id)
                
                # Recurse
                if backtrack(slot_idx + 1):
                    return True
                    
                # Backtrack
                used_teams.remove(team_id)
                del assignments[current_match_id]
                
        return False
        
    # Start the matching algorithm
    success = backtrack(0)
    
    if success:
        return assignments
    else:
        return {}
