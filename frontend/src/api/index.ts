import { apiClient } from './client';
import type {
  AnalyzeRequest,
  AnalyzeResponse,
  AnalysisResult,
  Channel,
  Keyword,
  Report,
  TrendOverview,
  User,
  Video,
  WorkflowStatus,
  HumanReviewRequest,
} from '@/types';

export const authApi = {
  login: (email: string, password: string) =>
    apiClient.post<{ access_token: string; user: User }>('/auth/login', { email, password }),
  register: (email: string, name: string, password: string) =>
    apiClient.post<{ access_token: string; user: User }>('/auth/register', { email, name, password }),
  googleAuth: (token: string) =>
    apiClient.post<{ access_token: string; user: User }>('/auth/google', { token }),
  me: () => apiClient.get<User>('/auth/me'),
};

export const trendsApi = {
  getOverview: () => apiClient.get<TrendOverview>('/trends'),
};

export const analysisApi = {
  analyze: (data: AnalyzeRequest) => apiClient.post<AnalyzeResponse>('/analyze', data),
  getResult: (taskId: string) => apiClient.get<AnalysisResult>(`/analyze/${taskId}`),
  resume: (taskId: string, data: HumanReviewRequest) =>
    apiClient.post<AnalyzeResponse>(`/analyze/${taskId}/resume`, data),
  getWorkflowStatus: (taskId: string) =>
    apiClient.get<WorkflowStatus>(`/workflow/${taskId}`),
};

export const channelsApi = {
  list: (params?: { limit?: number; sort_by?: string }) =>
    apiClient.get<Channel[]>('/channels', { params }),
};

export const videosApi = {
  list: (params?: { limit?: number; sort_by?: string }) =>
    apiClient.get<Video[]>('/videos', { params }),
};

export const keywordsApi = {
  list: (params?: { limit?: number }) =>
    apiClient.get<Keyword[]>('/keywords', { params }),
};

export const reportsApi = {
  list: () => apiClient.get<Report[]>('/reports'),
  get: (id: number) => apiClient.get<Report>(`/reports/${id}`),
  downloadPdf: (id: number) =>
    apiClient.get(`/reports/${id}/pdf`, { responseType: 'blob' }),
};
