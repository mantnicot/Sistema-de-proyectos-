import { Component, inject, OnInit, signal } from '@angular/core';

import { FormsModule } from '@angular/forms';

import { MatIconModule } from '@angular/material/icon';

import { MatTooltipModule } from '@angular/material/tooltip';

import { CdkDragDrop, DragDropModule, moveItemInArray } from '@angular/cdk/drag-drop';

import { ApiService } from '../../core/services/api.service';

import { DialogService } from '../../core/services/dialog.service';

import { FieldType, FormField, FormFieldPayload } from '../../core/models';

import { DynamicFieldComponent } from '../../shared/components/dynamic-field/dynamic-field.component';



const FIELD_TYPES: { value: FieldType; label: string }[] = [

  { value: 'text', label: 'Texto' },

  { value: 'textarea', label: 'Texto largo' },

  { value: 'integer', label: 'Entero' },

  { value: 'decimal', label: 'Decimal' },

  { value: 'percentage', label: 'Porcentual' },

  { value: 'time', label: 'Tiempo' },

  { value: 'list', label: 'Lista' },

  { value: 'image', label: 'Imagen' },

  { value: 'hyperlink', label: 'Hipervínculo' },

];



@Component({

  selector: 'app-form-builder',

  standalone: true,

  imports: [FormsModule, MatIconModule, MatTooltipModule, DragDropModule, DynamicFieldComponent],

  templateUrl: './form-builder.component.html',

  styleUrl: './form-builder.component.scss',

})

export class FormBuilderComponent implements OnInit {

  private api = inject(ApiService);

  private dialog = inject(DialogService);



  fields = signal<FormField[]>([]);

  fieldTypes = FIELD_TYPES;

  showEditor = false;

  editingField: Partial<FormField> = {};

  listMultipleChecked = false;

  listOptionInput = '';

  previewData: Record<string, unknown> = {};

  activeMenuId: number | null = null;

  private resizeTimers = new Map<number, ReturnType<typeof setTimeout>>();



  ngOnInit(): void {

    this.load();

  }



  load(): void {

    this.api.getFormFields().subscribe({

      next: (data) => {

        this.fields.set(data);

        const preview: Record<string, unknown> = { ...this.previewData };

        data.forEach((f) => {

          if (f.field_type === 'list' && f.list_multiple) {

            preview[f.name] = Array.isArray(preview[f.name]) ? preview[f.name] : [];

          } else if (!(f.name in preview)) {

            preview[f.name] = '';

          }

        });

        this.previewData = preview;

      },

      error: () => this.dialog.showError('Error al cargar formulario.'),

    });

  }



  openCreate(): void {

    this.editingField = {

      name: '',

      label: '',

      field_type: 'text',

      placeholder: '',

      required: false,

      order_index: this.fields().length,

      width: 100,

      height: 1,

      list_options: [],

      list_multiple: false,

      section: 'general',

    };

    this.listMultipleChecked = false;

    this.showEditor = true;

  }



  openEdit(field: FormField): void {

    const fresh = this.fields().find((f) => f.id === field.id) ?? field;

    this.editingField = {

      ...fresh,

      list_options: [...fresh.list_options],

      list_multiple: fresh.list_multiple,

      required: fresh.required,

    };

    this.listMultipleChecked = fresh.list_multiple;

    this.showEditor = true;

    this.activeMenuId = null;

  }



  closeEditor(): void {

    this.showEditor = false;

    this.editingField = {};

    this.listMultipleChecked = false;

  }



  addListOption(): void {

    if (!this.listOptionInput.trim()) return;

    this.editingField.list_options = [...(this.editingField.list_options || []), this.listOptionInput.trim()];

    this.listOptionInput = '';

  }



  removeListOption(i: number): void {

    const opts = [...(this.editingField.list_options || [])];

    opts.splice(i, 1);

    this.editingField.list_options = opts;

  }



  saveField(): void {

    if (!this.editingField.name || !this.editingField.label) {

      this.dialog.showError('Nombre y etiqueta son obligatorios.');

      return;

    }



    const payload = this.buildFieldPayload();

    const fieldId = this.editingField.id;



    this.dialog.showConfirm('¿Guardar campo?', () => {

      this.dialog.showLoading('Guardando...');

      const req = fieldId

        ? this.api.updateFormField(fieldId, payload)

        : this.api.createFormField(payload);

      req.subscribe({

        next: (saved) => {

          this.dialog.hideLoading();

          this.fields.update((items) =>

            fieldId ? items.map((f) => (f.id === saved.id ? saved : f)) : [...items, saved]

          );

          this.dialog.showSuccess('Campo guardado.');

          this.closeEditor();

          this.load();

        },

        error: (err) => {

          this.dialog.hideLoading();

          this.dialog.showError(err.error?.detail || 'Error al guardar.');

        },

      });

    });

  }



  private buildFieldPayload(): FormFieldPayload {

    const e = this.editingField;

    const isList = e.field_type === 'list';

    return {

      name: e.name!.trim(),

      label: e.label!.trim(),

      field_type: e.field_type || 'text',

      placeholder: e.placeholder || '',

      required: Boolean(e.required),

      order_index: e.order_index ?? 0,

      width: e.width ?? 100,

      height: e.height ?? 1,

      min_value: e.min_value,

      max_value: e.max_value,

      max_length: e.max_length,

      list_options: [...(e.list_options || [])],

      list_multiple: isList ? this.listMultipleChecked : false,

      section: e.section || 'general',

    };

  }



  private fieldToPayload(field: FormField, overrides: Partial<FormFieldPayload> = {}): FormFieldPayload {

    return {

      name: field.name,

      label: field.label,

      field_type: field.field_type,

      placeholder: field.placeholder || '',

      required: field.required,

      order_index: field.order_index,

      width: field.width,

      height: field.height,

      min_value: field.min_value,

      max_value: field.max_value,

      max_length: field.max_length,

      list_options: [...field.list_options],

      list_multiple: field.field_type === 'list' ? field.list_multiple : false,

      section: field.section || 'general',

      ...overrides,

    };

  }



  deleteField(field: FormField): void {

    this.activeMenuId = null;

    this.dialog.showConfirm(`¿Eliminar el campo "${field.label}"?`, () => {

      this.api.deleteFormField(field.id).subscribe({

        next: () => {

          this.dialog.showSuccess('Campo eliminado.');

          this.load();

        },

        error: () => this.dialog.showError('Error al eliminar.'),

      });

    });

  }



  duplicateField(field: FormField): void {

    this.activeMenuId = null;

    this.api.duplicateFormField(field.id).subscribe({

      next: () => {

        this.dialog.showSuccess('Campo duplicado.');

        this.load();

      },

      error: () => this.dialog.showError('Error al duplicar.'),

    });

  }



  toggleMenu(id: number, event: Event): void {

    event.stopPropagation();

    this.activeMenuId = this.activeMenuId === id ? null : id;

  }



  onDrop(event: CdkDragDrop<FormField[]>): void {

    const items = [...this.fields()];

    moveItemInArray(items, event.previousIndex, event.currentIndex);

    this.fields.set(items);

    this.api.reorderFormFields(items.map((f) => f.id)).subscribe({

      error: () => this.dialog.showError('Error al reordenar.'),

    });

  }



  setPreviewValue(name: string, value: unknown): void {

    this.previewData = { ...this.previewData, [name]: value };

  }



  resizeFieldWidth(field: FormField, width: number): void {

    this.fields.update((items) => items.map((f) => (f.id === field.id ? { ...f, width } : f)));

    const current = this.fields().find((f) => f.id === field.id);

    if (!current) return;



    const prev = this.resizeTimers.get(field.id);

    if (prev) clearTimeout(prev);



    this.resizeTimers.set(

      field.id,

      setTimeout(() => {

        this.api.updateFormField(field.id, this.fieldToPayload(current, { width })).subscribe({

          error: () => this.dialog.showError('Error al redimensionar campo.'),

        });

        this.resizeTimers.delete(field.id);

      }, 400)

    );

  }

}


