import { Component, inject } from '@angular/core';
import { DialogService } from '../../../core/services/dialog.service';

@Component({
  selector: 'app-dialog',
  standalone: true,
  templateUrl: './app-dialog.component.html',
  styleUrl: './app-dialog.component.scss',
})
export class AppDialogComponent {
  dialog = inject(DialogService);

  close(): void {
    this.dialog.close();
  }

  confirm(): void {
    this.dialog.confirm();
  }
}
