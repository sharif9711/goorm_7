export interface User {
  id: number;
  email: string;
  name: string;
  created_at: string;
}

export interface Channel {
  id: number;
  channel_id: string;
  title: string;
  description?: string;
  subscriber_count: number;
  video_count: number;
  view_count: number;
  growth_score: number;
  updated_at: string;
}

export interface Video {
  id: number;
  video_id: string;
  channel_id: string;
  title: string;
  description?: string;
  published_at?: string;
  view_count: number;
  like_count: number;
  comment_count: number;
  trend_score: number;
  thumbnail_url?: string;
}

export interface Keyword {
  id: number;
  keyword: string;
  frequency: number;
  growth_rate: number;
  competition_score: number;
  trend_score: number;
}

export interface Report {
  id: number;
  project_id?: number;
  user_id: number;
  title: string;
  summary?: string;
  markdown_content?: string;
  analysis_type: string;
  created_at: string;
}

export interface TrendOverview {
  top_keywords: Array<{ keyword: string; trend_score: number; frequency: number }>;
  rising_channels: Array<{ title: string; growth_score: number; subscribers: number }>;
  rising_videos: Array<{ title: string; views: number; trend_score: number }>;
  recent_analyses: Array<{ id: number; title: string; created_at: string }>;
  content_recommendations: string[];
}

export interface AnalyzeRequest {
  query: string;
  analysis_type?: string;
  channel_url?: string;
  competitor_urls?: string[];
  period?: string;
  project_id?: number;
}

export interface AnalyzeResponse {
  task_id: string;
  status: string;
  message: string;
}

export interface AnalysisResult {
  task_id: string;
  status: string;
  query: string;
  analysis_type: string;
  plan: string[];
  steps_completed?: string[];
  tool_calls?: Array<{ tool: string; arguments: Record<string, unknown> }>;
  data: Record<string, unknown>;
  insights: string[];
  content_ideas: Record<string, string[]>;
  quality_score: number;
  evaluation?: {
    overall_score: number;
    passed: boolean;
    recommendations: string[];
  };
  requires_human_review?: boolean;
  report_id?: number;
  created_at?: string;
}

export interface HumanReviewRequest {
  approved: boolean;
  feedback?: string;
}

export interface WorkflowStatus {
  task_id: string;
  status: string;
  current_step?: string;
  steps_completed: string[];
  requires_human_review: boolean;
  quality_score: number;
  evaluation: Record<string, unknown>;
  interrupt_payload?: {
    message: string;
    quality_score: number;
    insights_preview: string[];
  };
}
