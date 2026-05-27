import { Routes } from '@angular/router';
import { authGuard, adminGuard } from './core/guards/auth.guard';

export const routes: Routes = [
  {
    path: '',
    loadComponent: () => import('./pages/landing/landing.component').then((m) => m.LandingComponent),
  },
  {
    path: 'dashboard',
    canActivate: [authGuard],
    loadComponent: () =>
      import('./layout/dashboard-layout/dashboard-layout.component').then((m) => m.DashboardLayoutComponent),
    children: [
      {
        path: '',
        loadComponent: () => import('./pages/home/home.component').then((m) => m.HomeComponent),
      },
      {
        path: 'proyectos',
        loadComponent: () =>
          import('./pages/projects-list/projects-list.component').then((m) => m.ProjectsListComponent),
      },
      {
        path: 'gestion',
        canActivate: [adminGuard],
        loadComponent: () =>
          import('./pages/project-management/project-management.component').then((m) => m.ProjectManagementComponent),
      },
      {
        path: 'formulario',
        canActivate: [adminGuard],
        loadComponent: () =>
          import('./pages/form-builder/form-builder.component').then((m) => m.FormBuilderComponent),
      },
    ],
  },
  { path: '**', redirectTo: '' },
];
