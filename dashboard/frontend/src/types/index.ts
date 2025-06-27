// Type definitions for the dashboard

export type DocumentStatus =
  | "not_started"
  | "in_progress"
  | "generated"
  | "refining"
  | "refined"
  | "validating"
  | "validated"
  | "failed";

export interface DocumentInfo {
  id: string;
  title: string;
  status: DocumentStatus;
  file_size?: number;
  refined_count: number;
  generated_at?: string;
  elapsed_time?: number;
  error_message?: string;
  dependencies: string[];
}

export interface GenerationSummary {
  total_documents: number;
  completed: number;
  in_progress: number;
  failed: number;
  not_started: number;
  overall_progress: number;
  estimated_time_remaining?: number;
  average_document_time?: number;
  documents: Record<string, DocumentInfo>;
  generation_started_at?: string;
  generation_completed_at?: string;
}

export interface StatusUpdate {
  type: string;
  timestamp: string;
  document_id?: string;
  status?: DocumentStatus;
  progress?: number;
  message?: string;
  summary?: GenerationSummary;
}

export interface LogEntry {
  timestamp: string;
  level: string;
  message: string;
  document_id?: string;
}