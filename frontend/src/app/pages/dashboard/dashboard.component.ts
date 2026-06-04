import { Component, inject, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { GroupTableComponent } from '../../components/group-table/group-table.component';
import { ThirdPlaceTableComponent } from '../../components/third-place-table/third-place-table.component';
import { KnockoutBracketComponent } from '../../components/knockout-bracket/knockout-bracket.component';
import { Calendar } from '../../components/calendar/calendar';
import { TournamentState } from '../../state/tournament.state';

@Component({
  selector: 'app-dashboard',
  standalone: true,
  imports: [CommonModule, GroupTableComponent, ThirdPlaceTableComponent, KnockoutBracketComponent, Calendar],
  templateUrl: './dashboard.component.html',
  styleUrls: ['./dashboard.component.css']
})
export class DashboardComponent implements OnInit {
  state = inject(TournamentState);
  activeTab: string = 'standings'; // 'standings', 'bracket', 'calendar'

  // Helper to extract keys for the view
  get groupKeys() {
    return Object.keys(this.state.groups());
  }

  ngOnInit() {
    this.state.loadData();
  }

  setTab(tab: string) {
    this.activeTab = tab;
  }
}
