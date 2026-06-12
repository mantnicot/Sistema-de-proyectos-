export type UserRole = 'admin' | 'general';

export type FieldType =
  | 'text'
  | 'textarea'
  | 'integer'
  | 'decimal'
  | 'percentage'
  | 'time'
  | 'list'
  | 'image'
  | 'hyperlink';

export interface User {
  id: number;
  username: string;
  email: string;
  role: UserRole;
}

export interface LoginResponse {
  access_token: string;
  token_type: string;
  role: UserRole;
  username: string;
}

export interface FormFieldPayload {
  name: string;
  label: string;
  field_type: FieldType;
  placeholder?: string;
  required: boolean;
  order_index: number;
  width: number;
  height: number;
  min_value?: number;
  max_value?: number;
  max_length?: number;
  list_options: string[];
  list_multiple: boolean;
  section: string;
}

export interface FormField {
  id: number;
  name: string;
  label: string;
  field_type: FieldType;
  placeholder?: string;
  required: boolean;
  order_index: number;
  width: number;
  height: number;
  min_value?: number;
  max_value?: number;
  max_length?: number;
  list_options: string[];
  list_multiple: boolean;
  section: string;
}

export interface Project {
  id: number;
  name: string;
  description?: string;
  data: Record<string, unknown>;
  created_at?: string;
  updated_at?: string;
}

export interface ApiMessage {
  message: string;
  success: boolean;
}

export type WorkEvidenceType = 'document' | 'url';

export interface WorkFolder {
  id: number;
  name: string;
  order_index: number;
}

export interface WorkEvidence {
  id: number;
  subfolder_id: number;
  evidence_type: WorkEvidenceType;
  name: string;
  progress_percent: number;
  url?: string;
  file_name?: string;
  file_url?: string;
  order_index: number;
  group_id?: number | null;
}

export interface WorkSubfolder {
  id: number;
  project_id: number;
  name: string;
  order_index: number;
  progress_percent: number;
  evidences: WorkEvidence[];
}

export interface WorkProject {
  id: number;
  name: string;
  folder_id: number;
  folder_name: string;
  logo_url?: string;
  order_index: number;
  subfolders: WorkSubfolder[];
}
