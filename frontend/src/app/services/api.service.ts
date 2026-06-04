import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { map } from 'rxjs/operators';
import { GroupStanding } from '../models/group-standing';
import { Match } from '../models/match';

const FIFA_TO_ISO: Record<string, string> = {
  'MEX':'mx', 'RSA':'za', 'KOR':'kr', 'CZE':'cz', 'CAN':'ca', 'BIH':'ba',
  'QAT':'qa', 'SUI':'ch', 'BRA':'br', 'MAR':'ma', 'HAI':'ht', 'SCO':'gb-sct',
  'USA':'us', 'PAR':'py', 'AUS':'au', 'TUR':'tr', 'GER':'de', 'CUW':'cw',
  'CIV':'ci', 'ECU':'ec', 'NED':'nl', 'JPN':'jp', 'SWE':'se', 'TUN':'tn',
  'BEL':'be', 'EGY':'eg', 'IRN':'ir', 'NZL':'nz', 'ESP':'es', 'CPV':'cv',
  'KSA':'sa', 'URY':'uy', 'FRA':'fr', 'SEN':'sn', 'IRQ':'iq', 'NOR':'no',
  'ARG':'ar', 'ALG':'dz', 'AUT':'at', 'JOR':'jo', 'POR':'pt', 'COD':'cd',
  'UZB':'uz', 'COL':'co', 'ENG':'gb-eng', 'CRO':'hr', 'GHA':'gh', 'PAN':'pa',
  'URU':'uy' // Just in case
};

@Injectable({
  providedIn: 'root'
})
export class ApiService {
  private baseUrl = 'http://127.0.0.1:8000';

  constructor(private http: HttpClient) {}

  getGroups(): Observable<Record<string, GroupStanding[]>> {
    return this.http.get<any[]>(`${this.baseUrl}/groups`).pipe(
      map(data => {
        const record: Record<string, GroupStanding[]> = {};
        data.forEach(g => {
          record[g.group_name] = g.standings.map((s: any) => ({
            team: s.team_name,
            group: s.group_name,
            played: s.played,
            won: s.won,
            drawn: s.drawn,
            lost: s.lost,
            gf: s.goals_for,
            ga: s.goals_against,
            gd: s.goal_difference,
            points: s.points,
            locked_rank: s.locked_rank,
            code: FIFA_TO_ISO[s.team_code] || s.team_code
          }));
        });
        return record;
      })
    );
  }

  getThirdPlace(): Observable<GroupStanding[]> {
    return this.http.get<any[]>(`${this.baseUrl}/groups/third-place`).pipe(
      map(data => data.map((s: any) => ({
        team: s.team_name,
        group: s.group_name,
        played: s.played,
        won: s.won,
        drawn: s.drawn,
        lost: s.lost,
        gf: s.goals_for,
        ga: s.goals_against,
        gd: s.goal_difference,
        points: s.points,
        locked_rank: s.locked_rank,
        code: FIFA_TO_ISO[s.team_code] || s.team_code
      })))
    );
  }

  getMatches(): Observable<Match[]> {
    return this.http.get<Match[]>(`${this.baseUrl}/matches`);
  }

  updateMatch(matchId: number, homeScore: number, awayScore: number): Observable<any> {
    return this.http.post(`${this.baseUrl}/matches/${matchId}/result`, { home_score: homeScore, away_score: awayScore });
  }
}
