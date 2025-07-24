export interface JobScheduleViewModel {
  jobName: string;
  displayName: string;
  cronExpression: string;
  description: string;
  isEnabled: boolean;
  friendlySchedule: string;
  lastModified: string;
  modifiedBy?: string;
}

export interface JobScheduleUpdateRequest {
  cronExpression: string;
  isEnabled: boolean;
  notes?: string;
}

export interface JobEnabledUpdateRequest {
  isEnabled: boolean;
}

export interface ApiResponse<T> {
  success: boolean;
  data?: T;
  message: string;
  errors?: string[];
}

export interface CronDescriptionResponse {
  cronExpression: string;
  description: string;
}