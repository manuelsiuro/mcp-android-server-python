export interface Device {
  id: string;
  info: {
    brand?: string;
    model?: string;
    version?: string;
  };
  connected: boolean;
}

export interface ActionRecord {
  id: string;
  timestamp: string;
  type: string;
  tool: string;
  params: Record<string, any>;
  result: any;
}

export interface ClaudeMessage {
  role: 'user' | 'assistant';
  content: string;
  timestamp: string;
}

export interface WebSocketMessage {
  type: 'start' | 'content' | 'end' | 'error';
  data?: any;
}

// Re-export Claude types
export type { ClaudeMessageData, ContentBlock, ClaudeStreamEvent, ToolUseBlock, TextBlock } from './claude';

export interface ScreenshotResponse {
  filename: string;
  url: string;
}

export interface ClickEvent {
  x: number;
  y: number;
  timestamp: number;
}

export interface ScenarioInfo {
  name: string;
  description: string;
  created_at: string;
  duration_ms: number;
  action_count: number;
  screenshot_count: number;
  device: Record<string, any>;
  file_path: string;
}

export interface ReplayOptions {
  speed_multiplier?: number;
  retry_attempts?: number;
  capture_screenshots?: boolean;
  stop_on_error?: boolean;
  device_id?: string;
}

export interface ReplayResult {
  success: boolean;
  scenario: {
    session_name: string;
    device_id: string;
    recorded_at: string | null;
    total_actions: number;
  };
  execution: {
    duration_seconds: number;
    total_actions: number;
    successful_actions: number;
    failed_actions: number;
    skipped_actions: number;
    success_rate: number;
    total_retries: number;
    avg_action_duration_ms: number;
  };
  action_results: Array<{
    action_index: number;
    tool_name: string;
    parameters: Record<string, any>;
    status: string;
    result: any;
    error: string | null;
    duration_ms: number;
    retry_count: number;
    screenshot_before: string | null;
    screenshot_after: string | null;
    screenshot_diff: string | null;
  }>;
  errors: string[];
  failed_actions: Array<{
    action_index: number;
    tool_name: string;
    error: string;
  }>;
}
