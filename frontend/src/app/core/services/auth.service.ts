import { Injectable, signal } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Router } from '@angular/router';
import { tap } from 'rxjs/operators';
import { environment } from '../../../environments/environment';
import { LoginResponse, User, UserRole } from '../models';

@Injectable({ providedIn: 'root' })
export class AuthService {
  private readonly tokenKey = 'oati_token';
  private readonly roleKey = 'oati_role';
  private readonly usernameKey = 'oati_username';

  readonly isAuthenticated = signal(false);
  readonly role = signal<UserRole | null>(null);
  readonly username = signal<string>('');

  constructor(
    private http: HttpClient,
    private router: Router
  ) {
    this.loadFromStorage();
  }

  private loadFromStorage(): void {
    const token = localStorage.getItem(this.tokenKey);
    const role = localStorage.getItem(this.roleKey) as UserRole | null;
    const username = localStorage.getItem(this.usernameKey) || '';
    if (token && role) {
      this.isAuthenticated.set(true);
      this.role.set(role);
      this.username.set(username);
    }
  }

  login(username: string, password: string) {
    return this.http
      .post<LoginResponse>(`${environment.apiUrl}/auth/login`, { username, password })
      .pipe(
        tap((res) => {
          localStorage.setItem(this.tokenKey, res.access_token);
          localStorage.setItem(this.roleKey, res.role);
          localStorage.setItem(this.usernameKey, res.username);
          this.isAuthenticated.set(true);
          this.role.set(res.role);
          this.username.set(res.username);
        })
      );
  }

  logout(): void {
    localStorage.removeItem(this.tokenKey);
    localStorage.removeItem(this.roleKey);
    localStorage.removeItem(this.usernameKey);
    this.isAuthenticated.set(false);
    this.role.set(null);
    this.username.set('');
    this.router.navigate(['/']);
  }

  getToken(): string | null {
    return localStorage.getItem(this.tokenKey);
  }

  isAdmin(): boolean {
    return this.role() === 'admin';
  }

  me() {
    return this.http.get<User>(`${environment.apiUrl}/auth/me`);
  }
}
