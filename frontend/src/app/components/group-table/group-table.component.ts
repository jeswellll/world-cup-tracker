import { Component, Input, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { GroupStanding } from '../../models/group-standing';
import { TournamentState } from '../../state/tournament.state';
import { GroupMatches } from '../group-matches/group-matches';

@Component({
  selector: 'app-group-table',
  standalone: true,
  imports: [CommonModule, GroupMatches],
  templateUrl: './group-table.component.html',
  styleUrls: ['./group-table.component.css']
})
export class GroupTableComponent {
  @Input() groupName: string = '';
  @Input() standings: GroupStanding[] = [];
  
  state = inject(TournamentState);
}
