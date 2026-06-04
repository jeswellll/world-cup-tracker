import { Component, Input, inject, computed } from '@angular/core';
import { CommonModule } from '@angular/common';
import { TournamentState } from '../../state/tournament.state';
import { Match } from '../../models/match';

@Component({
  selector: 'app-group-matches',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './group-matches.html',
  styleUrls: ['./group-matches.css']
})
export class GroupMatches {
  @Input({ required: true }) groupName!: string;
  state = inject(TournamentState);

  groupMatches = computed<Match[]>(() => {
    return this.state.matches()
      .filter(m => m.group_name === this.groupName)
      .sort((a, b) => {
        const da = a.date ? new Date(a.date).getTime() : 0;
        const db = b.date ? new Date(b.date).getTime() : 0;
        return da - db;
      });
  });
}
