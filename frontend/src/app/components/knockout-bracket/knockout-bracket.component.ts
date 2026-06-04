import { Component, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { TournamentState } from '../../state/tournament.state';

@Component({
  selector: 'app-knockout-bracket',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './knockout-bracket.component.html',
  styleUrls: ['./knockout-bracket.component.css']
})
export class KnockoutBracketComponent {
  state = inject(TournamentState);
  
  get leftWingRounds() { return this.state.leftWingRounds(); }
  get rightWingRounds() { return this.state.rightWingRounds(); }
  get centerFinal() { return this.state.centerFinal(); }

  get bronzeMatch() {
    return this.state.bronzeMatch();
  }

  getTooltipTeams(sourceGroup: string | null | undefined): {group: string, team: string}[] {
    if (!sourceGroup) return [];
    if (sourceGroup.length === 1) {
      // Return the whole group standing
      const group = this.state.groups()[sourceGroup];
      if (!group) return [];
      return group.map(t => ({ group: sourceGroup, team: t.team }));
    } else {
      // It's a combination like 'ABCDF'
      const teams = [];
      for (const char of sourceGroup) {
        const group = this.state.groups()[char];
        if (group && group.length >= 3) {
           teams.push({ group: char, team: group[2].team });
        }
      }
      return teams;
    }
  }
}
