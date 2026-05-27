import { Component, Input, Output, EventEmitter } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { MatIconModule } from '@angular/material/icon';
import { MatTooltipModule } from '@angular/material/tooltip';
import { FormField } from '../../../core/models';
import { asStringArray, groupSelections } from '../../utils/field-utils';

@Component({
  selector: 'app-dynamic-field',
  standalone: true,
  imports: [FormsModule, MatIconModule, MatTooltipModule],
  templateUrl: './dynamic-field.component.html',
  styleUrl: './dynamic-field.component.scss',
})
export class DynamicFieldComponent {
  @Input({ required: true }) field!: FormField;
  @Input() value: unknown = '';
  @Input() showHelp = true;
  @Output() valueChange = new EventEmitter<unknown>();

  listPicker = '';

  onChange(val: unknown): void {
    this.valueChange.emit(val);
  }

  isListMultiple(): boolean {
    return this.field.field_type === 'list' && Boolean(this.field.list_multiple);
  }

  isListSingle(): boolean {
    return this.field.field_type === 'list' && !this.isListMultiple();
  }

  selectionGroups(): { label: string; count: number }[] {
    if (typeof this.value === 'string' && this.value.trim()) {
      return [{ label: this.value.trim(), count: 1 }];
    }
    return groupSelections(this.value);
  }

  currentListValues(): string[] {
    if (Array.isArray(this.value)) {
      return this.value.map(String);
    }
    if (typeof this.value === 'string' && this.value.trim()) {
      return [this.value.trim()];
    }
    return [];
  }

  onListPick(option: string): void {
    if (!option) return;
    const current = this.currentListValues();
    this.valueChange.emit([...current, option]);
    this.listPicker = '';
  }

  removeOneInstance(label: string): void {
    const current = [...this.currentListValues()];
    const idx = current.indexOf(label);
    if (idx >= 0) {
      current.splice(idx, 1);
      this.valueChange.emit(current);
    }
  }

  fieldHelp(): string {
    const hints: Record<string, string> = {
      text: 'Campo de texto corto.',
      textarea: 'Campo de texto largo, múltiples líneas.',
      integer: 'Solo números enteros.',
      decimal: 'Números con decimales.',
      percentage: 'Valor porcentual entre 0 y 100.',
      time: 'Duración o cantidad de tiempo.',
      list: this.isListMultiple()
        ? 'Seleccione opciones del listado. Cada elección aparece abajo; puede repetir la misma.'
        : 'Selección única de una opción de la lista.',
      image: 'Adjunte una imagen referencial.',
      hyperlink: 'Ingrese una URL válida.',
    };
    return hints[this.field.field_type] ?? '';
  }
}
