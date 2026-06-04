import { Component, inject, computed } from '@angular/core';
import { CommonModule } from '@angular/common';
import { TournamentState } from '../../state/tournament.state';
import { Match } from '../../models/match';

interface DaySchedule {
  date: string;
  dateObj: Date;
  matches: Match[];
}

@Component({
  selector: 'app-calendar',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './calendar.html',
  styleUrls: ['./calendar.css']
})
export class Calendar {
  state = inject(TournamentState);

  scheduleByDay = computed<DaySchedule[]>(() => {
    const getCode = (team: string, groupName: string) => {
      if (!team || !groupName) return null;
      const g = this.state.groups()[groupName];
      return g ? g.find(t => t.team === team)?.code || null : null;
    };

    // Collect group matches
    const allMatches: any[] = [...this.state.matches().map(m => ({
      ...m,
      type: 'group',
      home_team_code: getCode(m.home_team_name, m.group_name),
      away_team_code: getCode(m.away_team_name, m.group_name)
    }))];

    // Collect knockout matches
    this.state.allKnockoutMatches().forEach(m => {
      allMatches.push({
        id: `ko-${m.id}`,
        date: m.date ? new Date(m.date).toISOString() : new Date().toISOString(),
        venue: m.venue || 'TBD',
        group_name: 'Knockouts',
        home_team_name: m.teamA || 'TBD',
        away_team_name: m.teamB || 'TBD',
        home_team_code: m.teamACode || null,
        away_team_code: m.teamBCode || null,
        home_score: null,
        away_score: null,
        status: 'Scheduled',
        type: 'knockout'
      });
    });

    const grouped: Record<string, DaySchedule> = {};

    allMatches.forEach(m => {
      // Create a display date string "Jun 11, 2026"
      const d = m.date ? new Date(m.date) : new Date();
      // Remove time for grouping, use LOCAL time!
      const dateKey = `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}`;

      if (!grouped[dateKey]) {
        // Create a normalized Date object at midnight local time to avoid timezone shifts when sorting
        const midnightLocal = new Date(d.getFullYear(), d.getMonth(), d.getDate());
        grouped[dateKey] = {
          date: midnightLocal.toLocaleDateString('en-US', { weekday: 'short', month: 'short', day: 'numeric', year: 'numeric' }),
          dateObj: midnightLocal,
          matches: []
        };
      }
      grouped[dateKey].matches.push(m);
    });

    // Sort days chronologically
    const days = Object.values(grouped).sort((a, b) => a.dateObj.getTime() - b.dateObj.getTime());
    
    // Sort matches within each day chronologically
    days.forEach(day => {
      day.matches.sort((a, b) => {
        const da = a.date ? new Date(a.date).getTime() : 0;
        const db = b.date ? new Date(b.date).getTime() : 0;
        return da - db;
      });
    });

    return days;
  });
}
