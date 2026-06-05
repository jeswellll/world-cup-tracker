import { Injectable, signal, computed } from '@angular/core';
import { GroupStanding } from '../models/group-standing';
import { Match } from '../models/match';
import { ApiService } from '../services/api.service';

export interface MatchNode {
  id: number;
  name: string;
  date: string;
  venue?: string;
  sourceGroupA?: string | null;
  sourceGroupB?: string | null;
  teamACode?: string | null;
  teamBCode?: string | null;
  teamA?: string;
  teamB?: string;
}

export interface Round {
  name: string;
  matches: MatchNode[];
}

@Injectable({
  providedIn: 'root'
})
export class TournamentState {
  groups = signal<Record<string, GroupStanding[]>>({});
  thirdPlace = signal<GroupStanding[]>([]);
  matches = signal<Match[]>([]);
  thirdPlaceAssignments = signal<Record<string, any>>({});

  allKnockoutMatches = computed<MatchNode[]>(() => {
    const groups = this.groups();
    
    const resolveTeam = (desc: string | undefined, groupName: string | null | undefined, matchId?: number): string => {
      if (!desc) return 'TBD';
      if (!groupName) return desc;
      if (desc.startsWith('1st Group')) {
        const team = groups[groupName]?.find(t => t.locked_rank === 1);
        return team ? team.team : desc;
      }
      if (desc.startsWith('2nd Group')) {
        const team = groups[groupName]?.find(t => t.locked_rank === 2);
        return team ? team.team : desc;
      }
      if (desc.startsWith('3rd Group') && matchId) {
        const assignment = this.thirdPlaceAssignments()[matchId];
        return assignment ? assignment.team_name : desc;
      }
      return desc; // 3rd Group A/B/C/D/F stays as is until backend resolves
    };

    const getCode = (desc: string | undefined, groupName: string | null | undefined, matchId?: number): string | null => {
      if (!desc || !groupName) return null;
      if (desc.startsWith('1st Group')) {
        const team = groups[groupName]?.find(t => t.locked_rank === 1);
        return team ? (team.code || null) : null;
      }
      if (desc.startsWith('2nd Group')) {
        const team = groups[groupName]?.find(t => t.locked_rank === 2);
        return team ? (team.code || null) : null;
      }
      if (desc.startsWith('3rd Group') && matchId) {
        const assignment = this.thirdPlaceAssignments()[matchId];
        return assignment ? (assignment.code || null) : null;
      }
      return null;
    };

    const hardcoded: any[] = [
      { id: 73, name: "M73", date: "2026-06-28T19:00:00.000Z", venue: "Los Angeles", teamA: "2nd Group A", teamB: "2nd Group B", sourceGroupA: "A", sourceGroupB: "B" },
      { id: 74, name: "M74", date: "2026-06-28T20:30:00.000Z", venue: "Boston", teamA: "1st Group E", teamB: "3rd Group A/B/C/D/F", sourceGroupA: "E", sourceGroupB: "ABCDF" },
      { id: 75, name: "M75", date: "2026-06-30T01:00:00.000Z", venue: "Monterrey", teamA: "1st Group C", teamB: "2nd Group F", sourceGroupA: "C", sourceGroupB: "F" },
      { id: 76, name: "M76", date: "2026-06-29T17:00:00.000Z", venue: "Houston", teamA: "1st Group I", teamB: "3rd Group C/D/F/G/H", sourceGroupA: "I", sourceGroupB: "CDFGH" },
      { id: 77, name: "M77", date: "2026-06-29T21:00:00.000Z", venue: "New York New Jersey", teamA: "1st Group H", teamB: "2nd Group J", sourceGroupA: "H", sourceGroupB: "J" },
      { id: 78, name: "M78", date: "2026-06-29T17:00:00.000Z", venue: "Dallas", teamA: "2nd Group E", teamB: "2nd Group I", sourceGroupA: "E", sourceGroupB: "I" },
      { id: 79, name: "M79", date: "2026-07-01T01:00:00.000Z", venue: "Mexico City", teamA: "1st Group D", teamB: "3rd Group B/E/F/I/J", sourceGroupA: "D", sourceGroupB: "BEFIJ" },
      { id: 80, name: "M80", date: "2026-06-30T16:00:00.000Z", venue: "Atlanta", teamA: "1st Group G", teamB: "3rd Group A/E/H/I/J", sourceGroupA: "G", sourceGroupB: "AEHIJ" },
      { id: 81, name: "M81", date: "2026-07-01T00:00:00.000Z", venue: "San Francisco Bay Area", teamA: "1st Group A", teamB: "3rd Group C/E/F/H/I", sourceGroupA: "A", sourceGroupB: "CEFHI" },
      { id: 82, name: "M82", date: "2026-06-30T20:00:00.000Z", venue: "Seattle", teamA: "1st Group B", teamB: "3rd Group E/F/G/I/J", sourceGroupA: "B", sourceGroupB: "EFGIJ" },
      { id: 83, name: "M83", date: "2026-07-01T23:00:00.000Z", venue: "Toronto", teamA: "2nd Group K", teamB: "2nd Group L", sourceGroupA: "K", sourceGroupB: "L" },
      { id: 84, name: "M84", date: "2026-07-01T19:00:00.000Z", venue: "Los Angeles", teamA: "1st Group F", teamB: "2nd Group C", sourceGroupA: "F", sourceGroupB: "C" },
      { id: 85, name: "M85", date: "2026-07-02T03:00:00.000Z", venue: "Vancouver", teamA: "1st Group L", teamB: "3rd Group E/H/I/J/K", sourceGroupA: "L", sourceGroupB: "EHIJK" },
      { id: 86, name: "M86", date: "2026-07-01T22:00:00.000Z", venue: "Miami", teamA: "1st Group J", teamB: "2nd Group H", sourceGroupA: "J", sourceGroupB: "H" },
      { id: 87, name: "M87", date: "2026-07-03T01:30:00.000Z", venue: "Kansas City", teamA: "1st Group K", teamB: "3rd Group D/E/I/J/L", sourceGroupA: "K", sourceGroupB: "DEIJL" },
      { id: 88, name: "M88", date: "2026-07-02T18:00:00.000Z", venue: "Dallas", teamA: "2nd Group D", teamB: "2nd Group G", sourceGroupA: "D", sourceGroupB: "G" },
      { id: 89, name: "M89", date: "2026-07-04T21:00:00.000Z", venue: "Philadelphia", teamA: "Winner Match 74", teamB: "Winner Match 77" },
      { id: 90, name: "M90", date: "2026-07-04T17:00:00.000Z", venue: "Houston", teamA: "Winner Match 73", teamB: "Winner Match 75" },
      { id: 91, name: "M91", date: "2026-07-05T20:00:00.000Z", venue: "New York New Jersey", teamA: "Winner Match 76", teamB: "Winner Match 78" },
      { id: 92, name: "M92", date: "2026-07-06T00:00:00.000Z", venue: "Mexico City", teamA: "Winner Match 79", teamB: "Winner Match 80" },
      { id: 93, name: "M93", date: "2026-07-06T19:00:00.000Z", venue: "Dallas", teamA: "Winner Match 83", teamB: "Winner Match 84" },
      { id: 94, name: "M94", date: "2026-07-07T00:00:00.000Z", venue: "Seattle", teamA: "Winner Match 81", teamB: "Winner Match 82" },
      { id: 95, name: "M95", date: "2026-07-07T16:00:00.000Z", venue: "Atlanta", teamA: "Winner Match 86", teamB: "Winner Match 88" },
      { id: 96, name: "M96", date: "2026-07-08T00:00:00.000Z", venue: "Vancouver", teamA: "Winner Match 85", teamB: "Winner Match 87" },
      { id: 97, name: "M97", date: "2026-07-09T20:00:00.000Z", venue: "Boston", teamA: "Winner Match 89", teamB: "Winner Match 90" },
      { id: 98, name: "M98", date: "2026-07-10T19:00:00.000Z", venue: "Los Angeles", teamA: "Winner Match 93", teamB: "Winner Match 94" },
      { id: 99, name: "M99", date: "2026-07-11T21:00:00.000Z", venue: "Miami", teamA: "Winner Match 91", teamB: "Winner Match 92" },
      { id: 100, name: "M100", date: "2026-07-12T01:00:00.000Z", venue: "Kansas City", teamA: "Winner Match 95", teamB: "Winner Match 96" },
      { id: 101, name: "M101", date: "2026-07-14T19:00:00.000Z", venue: "Dallas", teamA: "Winner Match 97", teamB: "Winner Match 98" },
      { id: 102, name: "M102", date: "2026-07-15T19:00:00.000Z", venue: "Atlanta", teamA: "Winner Match 99", teamB: "Winner Match 100" },
      { id: 103, name: "M103", date: "2026-07-18T21:00:00.000Z", venue: "Miami", teamA: "Runner-up Match 101", teamB: "Runner-up Match 102" },
      { id: 104, name: "M104", date: "2026-07-19T19:00:00.000Z", venue: "New York New Jersey", teamA: "Winner Match 101", teamB: "Winner Match 102" }
    ];

    const matchNodes = hardcoded.map(m => ({
      ...m,
      teamA: resolveTeam(m.teamA, m.sourceGroupA, m.id),
      teamB: resolveTeam(m.teamB, m.sourceGroupB, m.id),
      teamACode: getCode(m.teamA, m.sourceGroupA, m.id),
      teamBCode: getCode(m.teamB, m.sourceGroupB, m.id)
    }));

    return matchNodes;
  });

  leftWingRounds = computed<Round[]>(() => {
    const matchNodes = this.allKnockoutMatches();
    if (!matchNodes.length) return [];
    
    return [
      { name: 'Round of 32', matches: [matchNodes[1], matchNodes[4], matchNodes[0], matchNodes[2], matchNodes[10], matchNodes[11], matchNodes[8], matchNodes[9]] },
      { name: 'Round of 16', matches: [matchNodes[16], matchNodes[17], matchNodes[20], matchNodes[21]] },
      { name: 'Quarterfinals', matches: [matchNodes[24], matchNodes[25]] },
      { name: 'Semifinals', matches: [matchNodes[28]] }
    ];
  });

  rightWingRounds = computed<Round[]>(() => {
    const matchNodes = this.allKnockoutMatches();
    if (!matchNodes.length) return [];
    
    // In the HTML, we will iterate these columns from Semis outward to R32, but for logic consistency we'll define them here
    return [
      { name: 'Semifinals', matches: [matchNodes[29]] },
      { name: 'Quarterfinals', matches: [matchNodes[26], matchNodes[27]] },
      { name: 'Round of 16', matches: [matchNodes[18], matchNodes[19], matchNodes[22], matchNodes[23]] },
      { name: 'Round of 32', matches: [matchNodes[3], matchNodes[5], matchNodes[6], matchNodes[7], matchNodes[13], matchNodes[15], matchNodes[12], matchNodes[14]] }
    ];
  });

  centerFinal = computed<MatchNode | null>(() => {
    const matchNodes = this.allKnockoutMatches();
    if (!matchNodes.length) return null;
    return matchNodes[31]; // M104
  });

  bronzeMatch = computed<MatchNode | null>(() => {
    const matchNodes = this.allKnockoutMatches();
    if (!matchNodes.length) return null;
    return matchNodes[30]; // M103
  });

  constructor(private apiService: ApiService) {}

  loadData() {
    this.apiService.getGroups().subscribe(data => this.groups.set(data));
    this.apiService.getThirdPlace().subscribe(data => this.thirdPlace.set(data));
    this.apiService.getMatches().subscribe(data => this.matches.set(data));
    this.apiService.getThirdPlaceAssignments().subscribe(data => this.thirdPlaceAssignments.set(data));
  }
}
