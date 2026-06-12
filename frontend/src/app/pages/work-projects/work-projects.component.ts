import { Component, inject, OnInit, signal } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { MatIconModule } from '@angular/material/icon';
import { MatTooltipModule } from '@angular/material/tooltip';
import { CdkDragDrop, DragDropModule, moveItemInArray } from '@angular/cdk/drag-drop';
import { ApiService } from '../../core/services/api.service';
import { AuthService } from '../../core/services/auth.service';
import { DialogService } from '../../core/services/dialog.service';
import {
  WorkEvidence,
  WorkEvidenceType,
  WorkFolder,
  WorkProject,
  WorkSubfolder,
} from '../../core/models';

@Component({
  selector: 'app-work-projects',
  standalone: true,
  imports: [FormsModule, MatIconModule, MatTooltipModule, DragDropModule],
  templateUrl: './work-projects.component.html',
  styleUrl: './work-projects.component.scss',
})
export class WorkProjectsComponent implements OnInit {
  private api = inject(ApiService);
  private dialog = inject(DialogService);
  auth = inject(AuthService);

  folders = signal<WorkFolder[]>([]);
  activeFolderId = signal<number | null>(null);
  projects = signal<WorkProject[]>([]);
  expandedProjectId = signal<number | null>(null);

  showFolderModal = false;
  editingFolder: WorkFolder | null = null;
  folderName = '';

  showProjectModal = false;
  editingProject: WorkProject | null = null;
  projectName = '';

  showSubfolderModal = false;
  subfolderName = '';
  subfolderProjectId: number | null = null;
  editingSubfolder: WorkSubfolder | null = null;

  showEvidenceModal = false;
  evidenceSubfolderId: number | null = null;
  editingEvidence: WorkEvidence | null = null;
  evidenceName = '';
  evidenceType: WorkEvidenceType = 'url';
  evidenceUrl = '';
  evidenceProgress = 0;
  evidenceFile: File | null = null;

  ngOnInit(): void {
    this.loadFolders();
  }

  activeFolderName(): string {
    const id = this.activeFolderId();
    return this.folders().find((f) => f.id === id)?.name ?? '';
  }

  loadFolders(): void {
    this.dialog.showLoading('Cargando carpetas...');
    this.api.getWorkFolders().subscribe({
      next: (data) => {
        this.dialog.hideLoading();
        this.folders.set(data);
        if (data.length && !this.activeFolderId()) {
          this.activeFolderId.set(data[0].id);
        }
        if (this.activeFolderId()) {
          this.loadProjects();
        } else {
          this.projects.set([]);
        }
      },
      error: () => {
        this.dialog.hideLoading();
        this.dialog.showError('No se pudieron cargar las carpetas.');
      },
    });
  }

  loadProjects(): void {
    const folderId = this.activeFolderId();
    if (!folderId) return;
    this.dialog.showLoading('Cargando proyectos en proceso...');
    this.api.getWorkProjects(folderId).subscribe({
      next: (data) => {
        this.dialog.hideLoading();
        this.projects.set(data);
      },
      error: () => {
        this.dialog.hideLoading();
        this.dialog.showError('No se pudieron cargar los proyectos.');
      },
    });
  }

  selectFolder(folderId: number): void {
    this.activeFolderId.set(folderId);
    this.expandedProjectId.set(null);
    this.loadProjects();
  }

  openCreateFolder(): void {
    this.editingFolder = null;
    this.folderName = '';
    this.showFolderModal = true;
  }

  openEditFolder(folder: WorkFolder): void {
    this.editingFolder = folder;
    this.folderName = folder.name;
    this.showFolderModal = true;
  }

  saveFolder(): void {
    if (!this.folderName.trim()) {
      this.dialog.showError('Ingrese el nombre de la carpeta.');
      return;
    }
    this.dialog.showLoading('Guardando...');
    const req = this.editingFolder
      ? this.api.updateWorkFolder(this.editingFolder.id, this.folderName)
      : this.api.createWorkFolder(this.folderName);
    req.subscribe({
      next: (folder) => {
        this.dialog.hideLoading();
        this.showFolderModal = false;
        this.dialog.showSuccess('Carpeta guardada.');
        this.loadFolders();
        if (!this.editingFolder) {
          this.activeFolderId.set(folder.id);
          this.loadProjects();
        }
      },
      error: () => {
        this.dialog.hideLoading();
        this.dialog.showError('Error al guardar la carpeta.');
      },
    });
  }

  deleteFolder(folder: WorkFolder): void {
    this.dialog.showConfirm(`¿Eliminar la carpeta "${folder.name}"?`, () => {
      this.api.deleteWorkFolder(folder.id).subscribe({
        next: () => {
          this.dialog.showSuccess('Carpeta eliminada.');
          if (this.activeFolderId() === folder.id) {
            this.activeFolderId.set(null);
          }
          this.loadFolders();
        },
        error: () => this.dialog.showError('No se puede eliminar: la carpeta tiene proyectos o hubo un error.'),
      });
    });
  }

  logoUrl(project: WorkProject): string | null {
    return this.api.workProjectLogoUrl(project.logo_url);
  }

  toggleProject(id: number): void {
    this.expandedProjectId.set(this.expandedProjectId() === id ? null : id);
  }

  openCreateProject(): void {
    if (!this.activeFolderId()) {
      this.dialog.showError('Cree una carpeta antes de agregar proyectos.');
      return;
    }
    this.editingProject = null;
    this.projectName = '';
    this.showProjectModal = true;
  }

  openEditProject(p: WorkProject): void {
    this.editingProject = p;
    this.projectName = p.name;
    this.showProjectModal = true;
  }

  saveProject(): void {
    if (!this.projectName.trim()) {
      this.dialog.showError('Ingrese el nombre del proyecto.');
      return;
    }
    this.dialog.showLoading('Guardando...');
    const req = this.editingProject
      ? this.api.updateWorkProject(this.editingProject.id, { name: this.projectName })
      : this.api.createWorkProject(this.projectName, this.activeFolderId()!);
    req.subscribe({
      next: () => {
        this.dialog.hideLoading();
        this.showProjectModal = false;
        this.dialog.showSuccess('Proyecto guardado.');
        this.loadProjects();
      },
      error: () => {
        this.dialog.hideLoading();
        this.dialog.showError('Error al guardar.');
      },
    });
  }

  deleteProject(p: WorkProject): void {
    this.dialog.showConfirm(`¿Eliminar el proyecto "${p.name}"?`, () => {
      this.dialog.showLoading('Eliminando...');
      this.api.deleteWorkProject(p.id).subscribe({
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

  onLogoSelected(project: WorkProject, event: Event): void {
    const input = event.target as HTMLInputElement;
    const file = input.files?.[0];
    if (!file) return;
    this.dialog.showLoading('Subiendo logo...');
    this.api.uploadWorkProjectLogo(project.id, file).subscribe({
      next: () => {
        this.dialog.hideLoading();
        this.dialog.showSuccess('Logo actualizado.');
        this.loadProjects();
      },
      error: () => {
        this.dialog.hideLoading();
        this.dialog.showError('Error al subir logo.');
      },
    });
    input.value = '';
  }

  openCreateSubfolder(projectId: number): void {
    this.subfolderProjectId = projectId;
    this.editingSubfolder = null;
    this.subfolderName = '';
    this.showSubfolderModal = true;
  }

  openEditSubfolder(sf: WorkSubfolder): void {
    this.editingSubfolder = sf;
    this.subfolderProjectId = sf.project_id;
    this.subfolderName = sf.name;
    this.showSubfolderModal = true;
  }

  saveSubfolder(): void {
    if (!this.subfolderName.trim() || !this.subfolderProjectId) return;
    this.dialog.showLoading('Guardando...');
    const req = this.editingSubfolder
      ? this.api.updateWorkSubfolder(this.editingSubfolder.id, this.subfolderName)
      : this.api.createWorkSubfolder(this.subfolderProjectId, this.subfolderName);
    req.subscribe({
      next: () => {
        this.dialog.hideLoading();
        this.showSubfolderModal = false;
        this.dialog.showSuccess('Subcarpeta guardada.');
        this.loadProjects();
      },
      error: () => {
        this.dialog.hideLoading();
        this.dialog.showError('Error al guardar subcarpeta.');
      },
    });
  }

  deleteSubfolder(sf: WorkSubfolder): void {
    this.dialog.showConfirm(`¿Eliminar subcarpeta "${sf.name}"?`, () => {
      this.api.deleteWorkSubfolder(sf.id).subscribe({
        next: () => {
          this.dialog.showSuccess('Subcarpeta eliminada.');
          this.loadProjects();
        },
        error: () => this.dialog.showError('Error al eliminar.'),
      });
    });
  }

  openCreateEvidence(subfolderId: number): void {
    this.evidenceSubfolderId = subfolderId;
    this.editingEvidence = null;
    this.evidenceName = '';
    this.evidenceType = 'url';
    this.evidenceUrl = '';
    this.evidenceProgress = 0;
    this.evidenceFile = null;
    this.showEvidenceModal = true;
  }

  openEditEvidence(ev: WorkEvidence): void {
    this.editingEvidence = ev;
    this.evidenceSubfolderId = ev.subfolder_id;
    this.evidenceName = ev.name;
    this.evidenceType = ev.evidence_type;
    this.evidenceUrl = ev.url || '';
    this.evidenceProgress = ev.progress_percent;
    this.evidenceFile = null;
    this.showEvidenceModal = true;
  }

  onEvidenceFileChange(event: Event): void {
    this.evidenceFile = (event.target as HTMLInputElement).files?.[0] || null;
  }

  saveEvidence(): void {
    if (!this.evidenceName.trim() || !this.evidenceSubfolderId) return;
    this.dialog.showLoading('Guardando evidencia...');
    if (this.editingEvidence) {
      this.api
        .updateWorkEvidence(this.editingEvidence.id, {
          name: this.evidenceName,
          progress_percent: this.evidenceProgress,
          url: this.evidenceType === 'url' ? this.evidenceUrl : undefined,
        })
        .subscribe({
          next: () => this.afterEvidenceSave(),
          error: () => this.evidenceError(),
        });
      return;
    }
    if (this.evidenceType === 'url') {
      if (!this.evidenceUrl.trim()) {
        this.dialog.hideLoading();
        this.dialog.showError('Ingrese la URL.');
        return;
      }
      this.api
        .createWorkEvidenceUrl(
          this.evidenceSubfolderId,
          this.evidenceName,
          this.evidenceUrl,
          this.evidenceProgress
        )
        .subscribe({
          next: () => this.afterEvidenceSave(),
          error: () => this.evidenceError(),
        });
    } else {
      if (!this.evidenceFile) {
        this.dialog.hideLoading();
        this.dialog.showError('Seleccione un archivo.');
        return;
      }
      this.api
        .createWorkEvidenceDocument(
          this.evidenceSubfolderId,
          this.evidenceName,
          this.evidenceProgress,
          this.evidenceFile
        )
        .subscribe({
          next: () => this.afterEvidenceSave(),
          error: () => this.evidenceError(),
        });
    }
  }

  private afterEvidenceSave(): void {
    this.dialog.hideLoading();
    this.showEvidenceModal = false;
    this.dialog.showSuccess('Evidencia guardada.');
    this.loadProjects();
  }

  private evidenceError(): void {
    this.dialog.hideLoading();
    this.dialog.showError('Error al guardar evidencia.');
  }

  deleteEvidence(ev: WorkEvidence): void {
    this.dialog.showConfirm(`¿Eliminar "${ev.name}"?`, () => {
      this.api.deleteWorkEvidence(ev.id).subscribe({
        next: () => {
          this.dialog.showSuccess('Evidencia eliminada.');
          this.loadProjects();
        },
        error: () => this.dialog.showError('Error al eliminar.'),
      });
    });
  }

  openUrl(ev: WorkEvidence): void {
    if (ev.url) window.open(ev.url, '_blank', 'noopener,noreferrer');
  }

  downloadDocument(ev: WorkEvidence): void {
    this.dialog.showLoading('Descargando...');
    this.api.downloadWorkEvidenceFile(ev.id).subscribe({
      next: (blob) => {
        this.dialog.hideLoading();
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = ev.file_name || 'documento';
        a.click();
        URL.revokeObjectURL(url);
      },
      error: () => {
        this.dialog.hideLoading();
        this.dialog.showError('Error al descargar.');
      },
    });
  }

  dropEvidence(sf: WorkSubfolder, event: CdkDragDrop<WorkEvidence[]>): void {
    if (!this.auth.isAdmin()) return;
    const list = [...sf.evidences].sort((a, b) => a.order_index - b.order_index);
    const moved = list[event.previousIndex];
    moveItemInArray(list, event.previousIndex, event.currentIndex);
    const newIndex = event.currentIndex;
    if (newIndex > 0) {
      const prev = list[newIndex - 1];
      moved.group_id = prev.group_id ?? prev.id;
    } else {
      moved.group_id = null;
    }
    const items = list.map((e, i) => ({
      id: e.id,
      order_index: i,
      group_id: e.id === moved.id ? moved.group_id : e.group_id,
    }));
    this.api.reorderWorkEvidences(items).subscribe({
      next: () => this.loadProjects(),
      error: () => this.dialog.showError('Error al reordenar.'),
    });
  }

  ungroupEvidence(ev: WorkEvidence): void {
    if (!this.auth.isAdmin()) return;
    this.api.updateWorkEvidence(ev.id, { group_id: null }).subscribe({
      next: () => this.loadProjects(),
      error: () => this.dialog.showError('Error al desagrupar.'),
    });
  }

  isInGroup(ev: WorkEvidence): boolean {
    return ev.group_id != null && ev.group_id > 0;
  }

  groupClass(ev: WorkEvidence): string {
    if (!this.isInGroup(ev)) return '';
    return `group-${ev.group_id}`;
  }
}
