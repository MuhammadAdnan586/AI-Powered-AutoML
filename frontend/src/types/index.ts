// ─── Auth Types ───────────────────────────────────────────────────────────────

export type UserRole = "admin" | "user" | "viewer";

export interface User {
  id: number;
  full_name: string;
  email: string;
  role: UserRole;
  is_active: boolean;
  is_verified: boolean;
  avatar_url?: string;
  bio?: string;
  created_at: string;
  last_login?: string;
}

export interface AuthTokens {
  access_token: string;
  refresh_token: string;
  token_type: string;
  expires_in: number;
}

export interface LoginPayload {
  email: string;
  password: string;
}

export interface RegisterPayload {
  full_name: string;
  email: string;
  password: string;
}

// ─── Dataset Types ────────────────────────────────────────────────────────────

export type DatasetStatus = "uploading" | "processing" | "ready" | "error";

export interface DatasetVersion {
  id: number;
  dataset_id: number;
  version_number: number;
  version_label?: string;
  notes?: string;
  file_size_bytes?: number;
  row_count?: number;
  column_count?: number;
  is_active: boolean;
  created_at: string;
}

export interface Dataset {
  id: number;
  owner_id: number;
  name: string;
  description?: string;
  status: DatasetStatus;
  original_filename: string;
  file_extension: string;
  file_size_bytes?: number;
  row_count?: number;
  column_count?: number;
  column_names?: string[];
  dtypes_info?: Record<string, string>;
  missing_values_info?: Record<string, number>;
  preview_data?: Record<string, unknown>[];
  created_at: string;
  updated_at?: string;
  versions?: DatasetVersion[];
}

export interface DatasetListItem {
  id: number;
  name: string;
  description?: string;
  status: DatasetStatus;
  original_filename: string;
  file_size_bytes?: number;
  row_count?: number;
  column_count?: number;
  created_at: string;
}

// ─── Dashboard Types ──────────────────────────────────────────────────────────

export interface DashboardStats {
  total_datasets: number;
  ready_datasets: number;
  processing_datasets: number;
  error_datasets: number;
  total_storage_bytes: number;
  total_rows: number;
  recent_datasets: RecentDataset[];
  user_since_days: number;
}

export interface RecentDataset {
  id: number;
  name: string;
  status: DatasetStatus;
  row_count?: number;
  column_count?: number;
  created_at: string;
}

// ─── API Error ────────────────────────────────────────────────────────────────

export interface ApiError {
  detail: string;
  errors?: { field: string; message: string }[];
}
