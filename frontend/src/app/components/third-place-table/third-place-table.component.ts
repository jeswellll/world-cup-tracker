import { Component, Input } from '@angular/core';
import { CommonModule } from '@angular/common';
import { GroupStanding } from '../../models/group-standing';

@Component({
  selector: 'app-third-place-table',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './third-place-table.component.html',
  styleUrls: ['./third-place-table.component.css']
})
export class ThirdPlaceTableComponent {
  @Input() standings!: GroupStanding[];
}
