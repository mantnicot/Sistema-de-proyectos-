import { Injectable } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { map } from 'rxjs/operators';
import { environment } from '../../../environments/environment';
import {
  ApiMessage,
  FormField,
  FormFieldPayload,
  Project,
  WorkEvidence,
  WorkFolderCategory,
  WorkProject,
  WorkSubfolder,
} from '../models';

@Injectable({ providedIn: 'root' })
export class ApiService {
  constructor(private http: HttpClient) {}

  // Form fields
  getFormFields() {
    return this.http.get<FormField[]>(`${environment.apiUrl}/form-fields`).pipe(
      map((fields) => fields.map((f) => this.normalizeField(f)))
    );
  }

  private toBoolean(value: unknown): boolean {
    return value === true || value === 1 || value === '1' || value === 'true';
  }

  private normalizeField(f: FormField): FormField {
    const raw = f as unknown as Record<string, unknown>;
    return {
      ...f,
      list_multiple: this.toBoolean(raw['list_multiple']),
      list_options: Array.isArray(f.list_options) ? f.list_options : [],
    };
  }

  private mergeSavedField(saved: FormField, payload: FormFieldPayload): FormField {
    const raw = saved as unknown as Record<string, unknown>;
    const hasListMultipleKey = Object.prototype.hasOwnProperty.call(raw, 'list_multiple');
    return {
      ...saved,
      list_multiple: hasListMultipleKey ? this.toBoolean(raw['list_multiple']) : payload.list_multiple,
    };
  }

  private normalizeFields(fields: FormField[]): FormField[] {
    return fields.map((f) => this.normalizeField(f));
  }

  createFormField(field: FormFieldPayload) {
    return this.http
      .post<FormField>(`${environment.apiUrl}/form-fields`, field)
      .pipe(map((f) => this.normalizeField(f)));
  }

  updateFormField(id: number, field: FormFieldPayload) {
    return this.http
      .put<FormField>(`${environment.apiUrl}/form-fields/${id}`, field)
      .pipe(map((f) => this.mergeSavedField(this.normalizeField(f), field)));
  }

  deleteFormField(id: number) {
    return this.http.delete<ApiMessage>(`${environment.apiUrl}/form-fields/${id}`);
  }

  duplicateFormField(id: number) {
    return this.http
      .post<FormField>(`${environment.apiUrl}/form-fields/${id}/duplicate`, {})
      .pipe(map((f) => this.normalizeField(f)));
  }

  reorderFormFields(fieldIds: number[]) {
    return this.http
      .put<FormField[]>(`${environment.apiUrl}/form-fields/reorder`, { field_ids: fieldIds })
      .pipe(map((fields) => this.normalizeFields(fields)));
  }

  // Projects
  getProjects(search?: string, sortBy = 'name', sortDir = 'asc') {
    let params = new HttpParams().set('sort_by', sortBy).set('sort_dir', sortDir);
    if (search) params = params.set('search', search);
    return this.http.get<Project[]>(`${environment.apiUrl}/projects`, { params });
  }

  getProject(id: number) {
    return this.http.get<Project>(`${environment.apiUrl}/projects/${id}`);
  }

  createProject(project: Partial<Project>) {
    return this.http.post<Project>(`${environment.apiUrl}/projects`, project);
  }

  updateProject(id: number, project: Partial<Project>) {
    return this.http.put<Project>(`${environment.apiUrl}/projects/${id}`, project);
  }

  deleteProject(id: number) {
    return this.http.delete<ApiMessage>(`${environment.apiUrl}/projects/${id}`);
  }

  duplicateProject(id: number) {
    return this.http.post<Project>(`${environment.apiUrl}/projects/${id}/duplicate`, {});
  }

  exportPdf(id: number) {
    return this.http.get(`${environment.apiUrl}/projects/${id}/export/pdf`, { responseType: 'blob' });
  }

  exportWord(id: number) {
    return this.http.get(`${environment.apiUrl}/projects/${id}/export/word`, { responseType: 'blob' });
  }

  exportExcelAll() {
    return this.http.get(`${environment.apiUrl}/projects/export/excel`, { responseType: 'blob' });
  }

  // Proyectos en proceso
  getWorkProjects(folder: WorkFolderCategory) {
    return this.http.get<WorkProject[]>(`${environment.apiUrl}/work-projects`, {
      params: new HttpParams().set('folder', folder),
    });
  }

  createWorkProject(name: string, folder: WorkFolderCategory) {
    return this.http.post<WorkProject>(`${environment.apiUrl}/work-projects`, { name, folder });
  }

  updateWorkProject(id: number, data: { name?: string; folder?: WorkFolderCategory }) {
    return this.http.put<WorkProject>(`${environment.apiUrl}/work-projects/${id}`, data);
  }

  deleteWorkProject(id: number) {
    return this.http.delete<ApiMessage>(`${environment.apiUrl}/work-projects/${id}`);
  }

  uploadWorkProjectLogo(projectId: number, file: File) {
    const form = new FormData();
    form.append('file', file);
    return this.http.post<ApiMessage & { logo_url?: string }>(
      `${environment.apiUrl}/work-projects/${projectId}/logo`,
      form
    );
  }

  workProjectLogoUrl(logoPath?: string): string | null {
    if (!logoPath) return null;
    return `${environment.apiUrl}/${logoPath}`;
  }

  createWorkSubfolder(projectId: number, name: string) {
    return this.http.post<WorkSubfolder>(`${environment.apiUrl}/work-projects/${projectId}/subfolders`, { name });
  }

  updateWorkSubfolder(id: number, name: string) {
    return this.http.put<WorkSubfolder>(`${environment.apiUrl}/work-projects/subfolders/${id}`, { name });
  }

  deleteWorkSubfolder(id: number) {
    return this.http.delete<ApiMessage>(`${environment.apiUrl}/work-projects/subfolders/${id}`);
  }

  createWorkEvidenceDocument(subfolderId: number, name: string, progress: number, file: File) {
    const form = new FormData();
    form.append('evidence_type', 'document');
    form.append('name', name);
    form.append('progress_percent', String(progress));
    form.append('file', file);
    return this.http.post<WorkEvidence>(`${environment.apiUrl}/work-projects/subfolders/${subfolderId}/evidences`, form);
  }

  createWorkEvidenceUrl(subfolderId: number, name: string, url: string, progress: number) {
    const form = new FormData();
    form.append('evidence_type', 'url');
    form.append('name', name);
    form.append('progress_percent', String(progress));
    form.append('url', url);
    return this.http.post<WorkEvidence>(`${environment.apiUrl}/work-projects/subfolders/${subfolderId}/evidences`, form);
  }

  updateWorkEvidence(id: number, data: Partial<WorkEvidence>) {
    return this.http.put<WorkEvidence>(`${environment.apiUrl}/work-projects/evidences/${id}`, data);
  }

  deleteWorkEvidence(id: number) {
    return this.http.delete<ApiMessage>(`${environment.apiUrl}/work-projects/evidences/${id}`);
  }

  reorderWorkEvidences(items: { id: number; order_index: number; group_id?: number | null }[]) {
    return this.http.put<ApiMessage>(`${environment.apiUrl}/work-projects/evidences/reorder`, { items });
  }

  downloadWorkEvidenceFile(evidenceId: number) {
    return this.http.get(`${environment.apiUrl}/work-projects/evidences/${evidenceId}/file`, {
      responseType: 'blob',
    });
  }

  workEvidenceFileUrl(filePath?: string): string | null {
    if (!filePath) return null;
    return `${environment.apiUrl}/${filePath}`;
  }
}
