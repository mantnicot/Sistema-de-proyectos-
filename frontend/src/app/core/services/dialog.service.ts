import { Injectable, signal } from '@angular/core';

export type DialogType = 'confirm' | 'alert' | 'loading' | 'success' | 'error';

export interface DialogState {
  visible: boolean;
  type: DialogType;
  title: string;
  message: string;
  confirmText?: string;
  cancelText?: string;
  onConfirm?: () => void;
}

@Injectable({ providedIn: 'root' })
export class DialogService {
  readonly state = signal<DialogState>({
    visible: false,
    type: 'alert',
    title: '',
    message: '',
  });

  showLoading(message = 'Procesando...'): void {
    this.state.set({ visible: true, type: 'loading', title: 'Espere', message });
  }

  hideLoading(): void {
    this.state.update((s) => ({ ...s, visible: s.type === 'loading' ? false : s.visible }));
  }

  showSuccess(message: string, title = 'Éxito'): void {
    this.state.set({ visible: true, type: 'success', title, message, confirmText: 'Aceptar' });
  }

  showError(message: string, title = 'Error'): void {
    this.state.set({ visible: true, type: 'error', title, message, confirmText: 'Aceptar' });
  }

  showAlert(message: string, title = 'Información'): void {
    this.state.set({ visible: true, type: 'alert', title, message, confirmText: 'Aceptar' });
  }

  showConfirm(message: string, onConfirm: () => void, title = 'Confirmar'): void {
    this.state.set({
      visible: true,
      type: 'confirm',
      title,
      message,
      confirmText: 'Confirmar',
      cancelText: 'Cancelar',
      onConfirm,
    });
  }

  close(): void {
    this.state.update((s) => ({ ...s, visible: false }));
  }

  confirm(): void {
    const s = this.state();
    s.onConfirm?.();
    this.close();
  }
}
