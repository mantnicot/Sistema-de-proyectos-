import { Component, Input } from '@angular/core';
import { FormField } from '../../../core/models';
import { formatFieldDisplay } from '../../utils/field-utils';

@Component({
  selector: 'app-document-preview',
  standalone: true,
  templateUrl: './document-preview.component.html',
  styleUrl: './document-preview.component.scss',
})
export class DocumentPreviewComponent {
  @Input() projectName = '';
  @Input() projectDescription = '';
  @Input() fields: FormField[] = [];
  @Input() data: Record<string, unknown> = {};

  get introduction(): string {
    const desc = (this.projectDescription || '').trim();
    return desc || 'N/A';
  }

  getValue(field: FormField): string {
    return formatFieldDisplay(this.data[field.name]);
  }
}
