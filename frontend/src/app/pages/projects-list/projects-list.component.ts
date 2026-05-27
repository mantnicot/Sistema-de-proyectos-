import { Component, inject, OnInit, signal } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { MatIconModule } from '@angular/material/icon';
import { MatTooltipModule } from '@angular/material/tooltip';
import { ApiService } from '../../core/services/api.service';
import { DialogService } from '../../core/services/dialog.service';
import { FormField, Project } from '../../core/models';
import { DocumentPreviewComponent } from '../../shared/components/document-preview/document-preview.component';
import { formatFieldDisplay } from '../../shared/utils/field-utils';

@Component({
  selector: 'app-projects-list',
  standalone: true,
  imports: [FormsModule, MatIconModule, MatTooltipModule, DocumentPreviewComponent],
  templateUrl: './projects-list.component.html',
  styleUrl: './projects-list.component.scss',
})
export class ProjectsListComponent implements OnInit {
  private api = inject(ApiService);
  private dialog = inject(DialogService);

  projects = signal<Project[]>([]);
  fields = signal<FormField[]>([]);
  search = '';
  sortBy = 'name';
  sortDir: 'asc' | 'desc' = 'asc';
  selectedProject = signal<Project | null>(null);
  showDetail = false;
  showDocPreview = false;
  previewProject = signal<Project | null>(null);

  ngOnInit(): void {
    this.load();
    this.api.getFormFields().subscribe({
      next: (data) => this.fields.set(data),
    });
  }

  load(): void {
    this.dialog.showLoading('Cargando proyectos...');
    this.api.getProjects(this.search || undefined, this.sortBy, this.sortDir).subscribe({
      next: (data) => {
        this.projects.set(data);
        this.dialog.hideLoading();
      },
      error: () => {
        this.dialog.hideLoading();
        this.dialog.showError('No se pudieron cargar los proyectos.');
      },
    });
  }

  searchProjects(): void {
    this.load();
  }

  sort(column: string): void {
    if (this.sortBy === column) {
      this.sortDir = this.sortDir === 'asc' ? 'desc' : 'asc';
    } else {
      this.sortBy = column;
      this.sortDir = 'asc';
    }
    this.load();
  }

  fieldLabel(key: string): string {
    return this.fields().find((f) => f.name === key)?.label ?? key;
  }

  displayValue(key: string, val: unknown): string {
    return formatFieldDisplay(val);
  }

  viewProject(p: Project): void {
    this.selectedProject.set(p);
    this.showDetail = true;
  }

  closeDetail(): void {
    this.showDetail = false;
    this.selectedProject.set(null);
  }

  openDocPreview(p: Project): void {
    this.previewProject.set(p);
    this.showDocPreview = true;
  }

  closeDocPreview(): void {
    this.showDocPreview = false;
    this.previewProject.set(null);
  }

  downloadPdf(p: Project): void {
    this.dialog.showConfirm(`¿Generar PDF del proyecto "${p.name}"?`, () => {
      this.dialog.showLoading('Generando PDF...');
      this.api.exportPdf(p.id).subscribe({
        next: (blob) => {
          this.dialog.hideLoading();
          this.saveBlob(blob, `proyecto_${p.id}.pdf`);
          this.dialog.showSuccess('PDF generado correctamente.');
        },
        error: () => {
          this.dialog.hideLoading();
          this.dialog.showError('Error al generar PDF.');
        },
      });
    });
  }

  downloadWord(p: Project): void {
    this.dialog.showConfirm(`¿Generar Word del proyecto "${p.name}"?`, () => {
      this.dialog.showLoading('Generando Word...');
      this.api.exportWord(p.id).subscribe({
        next: (blob) => {
          this.dialog.hideLoading();
          this.saveBlob(blob, `proyecto_${p.id}.docx`);
          this.dialog.showSuccess('Word generado correctamente.');
        },
        error: () => {
          this.dialog.hideLoading();
          this.dialog.showError('Error al generar Word.');
        },
      });
    });
  }

  exportExcel(): void {
    this.dialog.showConfirm('¿Generar Excel con todos los proyectos?', () => {
      this.dialog.showLoading('Generando Excel...');
      this.api.exportExcelAll().subscribe({
        next: (blob) => {
          this.dialog.hideLoading();
          this.saveBlob(blob, 'proyectos_oati.xlsx');
          this.dialog.showSuccess('Excel generado correctamente.');
        },
        error: () => {
          this.dialog.hideLoading();
          this.dialog.showError('Error al generar Excel.');
        },
      });
    });
  }

  private saveBlob(blob: Blob, filename: string): void {
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    a.click();
    URL.revokeObjectURL(url);
  }
}
