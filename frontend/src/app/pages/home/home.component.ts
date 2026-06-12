import { Component, inject } from '@angular/core';
import { RouterLink } from '@angular/router';
import { AuthService } from '../../core/services/auth.service';

@Component({
  selector: 'app-home',
  standalone: true,
  imports: [RouterLink],
  template: `
    <div class="oati-card">
      <div class="card-header">BIENVENIDO AL SISTEMA</div>
      <div class="card-body welcome">
        <p>Bienvenido, <strong>{{ auth.username() }}</strong>.</p>
        <p>Rol: <strong>{{ auth.role() }}</strong></p>
        <div class="quick-links">
          <a routerLink="/dashboard/proyectos" class="btn-oati">Ver proyectos existentes</a>
          <a routerLink="/dashboard/proyectos-en-proceso" class="btn-neutral">Proyectos en proceso</a>
          @if (auth.isAdmin()) {
            <a routerLink="/dashboard/gestion" class="btn-neutral">Gestión de proyectos</a>
            <a routerLink="/dashboard/formulario" class="btn-neutral">Gestión de formulario</a>
          }
        </div>
      </div>
    </div>
  `,
  styles: `
    .welcome { padding: 2rem; }
    .quick-links { display: flex; gap: 1rem; flex-wrap: wrap; margin-top: 1.5rem; }
  `,
})
export class HomeComponent {
  auth = inject(AuthService);
}
