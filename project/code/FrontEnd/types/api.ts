// API Types for Frontend
export interface ApiResponse<T> {
  success: boolean;
  message: string;
  data?: T;
  errors?: string[];
  timestamp: string;
}

export interface PagedResult<T> {
  items: T[];
  totalCount: number;
  page: number;
  pageSize: number;
  totalPages: number;
  hasNextPage: boolean;
  hasPreviousPage: boolean;
}

export interface LeadDto {
  id: number;
  name: string;
  email: string;
  phone?: string;
  company?: string;
  source: string;
  status: string;
  score?: number;
  isEnriched: boolean;
  isVetted: boolean;
  isUpsertedToZoho: boolean;
  workflowInstanceId?: string;
  createdDate: string;
  modifiedDate: string;
}

export interface CreateLeadRequest {
  name: string;
  email: string;
  phone?: string;
  company?: string;
  source?: string;
}

export interface UpdateLeadRequest {
  name?: string;
  email?: string;
  phone?: string;
  company?: string;
  status?: string;
}

export interface WorkflowResult {
  workflowInstanceId: string;
  status: string;
  message: string;
}

export interface DashboardMetrics {
  totalLeads: number;
  todayLeads: number;
  weekLeads: number;
  statusCounts: Record<string, number>;
  sourceCounts: Record<string, number>;
  enrichedLeads: number;
  vettedLeads: number;
  zohoLeads: number;
  averageScore: number;
  lastUpdated: string;
}

export interface FilterOptions {
  sources: string[];
  statuses: string[];
}

export interface LoginRequest {
  email: string;
  password: string;
  rememberMe?: boolean;
}

export interface RegisterRequest {
  email: string;
  password: string;
  confirmPassword: string;
}

export interface RefreshTokenRequest {
  accessToken: string;
  refreshToken: string;
}

export interface LoginResult {
  accessToken: string;
  refreshToken: string;
  expiresIn: number;
  tokenType: string;
  user: UserDto;
}

export interface UserDto {
  id: string;
  email: string;
  userName: string;
}

export interface LeadFilters {
  page?: number;
  pageSize?: number;
  search?: string;
  source?: string;
  status?: string;
  sortBy?: string;
  sortOrder?: 'asc' | 'desc';
}