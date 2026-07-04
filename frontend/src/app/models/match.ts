export interface Match {
  id: number;
  tournament_id: number;
  home_team_id?: number;
  away_team_id?: number;
  home_team_name: string;
  away_team_name: string;
  home_team_code?: string | null;
  away_team_code?: string | null;
  home_score: number | null;
  away_score: number | null;
  home_score_penalties?: number | null;
  away_score_penalties?: number | null;
  status: string;
  group_name: string;
  date: string | null;
  venue: string | null;
  type?: string;
}
