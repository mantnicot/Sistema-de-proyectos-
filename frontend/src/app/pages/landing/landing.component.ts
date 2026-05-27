import { Component, inject } from '@angular/core';
import { Router } from '@angular/router';
import { FormsModule } from '@angular/forms';
import { MatIconModule } from '@angular/material/icon';
import { AuthService } from '../../core/services/auth.service';
import { DialogService } from '../../core/services/dialog.service';
import { InstitutionalFooterComponent } from '../../shared/components/institutional-footer/institutional-footer.component';
import { AppDialogComponent } from '../../shared/components/app-dialog/app-dialog.component';

@Component({
  selector: 'app-landing',
  standalone: true,
  imports: [FormsModule, MatIconModule, InstitutionalFooterComponent, AppDialogComponent],
  templateUrl: './landing.component.html',
  styleUrl: './landing.component.scss',
})
export class LandingComponent {
  private auth = inject(AuthService);
  private dialog = inject(DialogService);
  private router = inject(Router);

  showLogin = false;
  username = '';
  password = '';

  openLogin(): void {
    this.showLogin = true;
  }

  closeLogin(): void {
    this.showLogin = false;
    this.username = '';
    this.password = '';
  }

  login(): void {
    if (!this.username || !this.password) {
      this.dialog.showError('Ingrese usuario y contraseña.');
      return;
    }
    this.dialog.showLoading('Validando identidad...');
    this.auth.login(this.username, this.password).subscribe({
      next: () => {
        this.dialog.hideLoading();
        this.closeLogin();
        this.router.navigate(['/dashboard']);
      },
      error: (err) => {
        this.dialog.hideLoading();
        this.dialog.showError(err.error?.detail || 'Credenciales inválidas.');
      },
    });
  }
}
