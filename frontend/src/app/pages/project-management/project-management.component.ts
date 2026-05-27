import { Component, inject, OnInit, signal } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { MatIconModule } from '@angular/material/icon';
import { MatTooltipModule } from '@angular/material/tooltip';
import { ApiService } from '../../core/services/api.service';
import { DialogService } from '../../core/services/dialog.service';
import { FormField, Project } from '../../core/models';
import { DynamicFieldComponent } from '../../shared/components/dynamic-field/dynamic-field.component';
import { DocumentPreviewComponent } from '../../shared/components/document-preview/document-preview.component';

@Component({
  selector: 'app-project-management',
  standalone: true,
  imports: [FormsModule, MatIconModule, MatTooltipModule, DynamicFieldComponent, DocumentPreviewComponent],
  templateUrl: './project-management.component.html',
  styleUrl: './project-management.component.scss',
})
export class ProjectManagementComponent implements OnInit {
  private api = inject(ApiService);
  private dialog = inject(DialogService);

  projects = signal<Project[]>([]);
  fields = signal<FormField[]>([]);
  showForm = false;
  editingId: number | null = null;
  projectName = '';
  projectDescription = '';
  projectData: Record<string, unknown> = {};

  ngOnInit(): void {
    this.loadProjects();
    this.loadFields();
  }

  loadProjects(): void {
    this.api.getProjects().subscribe({
      next: (data) => this.projects.set(data),
      error: () => this.dialog.showError('Error al cargar proyectos.'),
    });
  }

  loadFields(): void {
    this.api.getFormFields().subscribe({
      next: (data) => this.fields.set(data),
      error: () => this.dialog.showError('Error al cargar campos.'),
    });
  }

  openCreate(): void {
    this.editingId = null;
    this.projectName = '';
    this.projectDescription = '';
    this.projectData = this.emptyProjectData();
    this.showForm = true;
  }

  openEdit(p: Project): void {
    this.editingId = p.id;
    this.projectName = p.name;
    this.projectDescription = p.description || '';
    this.projectData = this.normalizeProjectData({ ...this.emptyProjectData(), ...p.data });
    this.showForm = true;
  }

  private normalizeProjectData(data: Record<string, unknown>): Record<string, unknown> {
    const normalized = { ...data };
    for (const f of this.fields()) {
      if (f.field_type === 'list' && f.list_multiple) {
        const val = normalized[f.name];
        if (typeof val === 'string' && val.trim()) {
          normalized[f.name] = [val.trim()];
        } else if (!Array.isArray(val)) {
          normalized[f.name] = [];
        }
      }
    }
    return normalized;
  }

  private emptyProjectData(): Record<string, unknown> {
    const data: Record<string, unknown> = {};
    for (const f of this.fields()) {
      data[f.name] = f.field_type === 'list' && f.list_multiple ? [] : '';
    }
    return data;
  }

  closeForm(): void {
    this.showForm = false;
  }

  setFieldValue(name: string, value: unknown): void {
    this.projectData = { ...this.projectData, [name]: value };
  }

  save(): void {
    if (!this.projectName.trim()) {
      this.dialog.showError('El nombre del proyecto es obligatorio.');
      return;
    }
    this.dialog.showConfirm(
      this.editingId ? '¿Confirmar modificación del proyecto?' : '¿Confirmar creación del proyecto?',
      () => {
        this.dialog.showLoading('Guardando...');
        const payload = {
          name: this.projectName,
          description: this.projectDescription,
          data: this.normalizeProjectData(this.projectData),
        };
        const req = this.editingId
          ? this.api.updateProject(this.editingId, payload)
          : this.api.createProject(payload);
        req.subscribe({
          next: () => {
            this.dialog.hideLoading();
            this.dialog.showSuccess('Proyecto guardado correctamente.');
            this.closeForm();
            this.loadProjects();
          },
          error: (err) => {
            this.dialog.hideLoading();
            const detail = err.error?.detail;
            if (detail?.errors) {
              this.dialog.showError(detail.errors.join('\n'));
            } else {
              this.dialog.showError(typeof detail === 'string' ? detail : 'Error al guardar.');
            }
          },
        });
      }
    );
  }

  deleteProject(p: Project): void {
    this.dialog.showConfirm(`¿Eliminar el proyecto "${p.name}"?`, () => {
      this.dialog.showLoading('Eliminando...');
      this.api.deleteProject(p.id).subscribe({
        next: () => {
          this.dialog.hideLoading();
          this.dialog.showSuccess('Proyecto eliminado.');
          this.loadProjects();
        },
        error: () => {
          this.dialog.hideLoading();
          this.dialog.showError('Error al eliminar.');
        },
      });
    });
  }

  duplicateProject(p: Project): void {
    this.dialog.showConfirm(`¿Duplicar el proyecto "${p.name}"?`, () => {
      this.dialog.showLoading('Duplicando...');
      this.api.duplicateProject(p.id).subscribe({
        next: () => {
          this.dialog.hideLoading();
          this.dialog.showSuccess('Proyecto duplicado.');
          this.loadProjects();
        },
        error: () => {
          this.dialog.hideLoading();
          this.dialog.showError('Error al duplicar.');
        },
      });
    });
  }
}
