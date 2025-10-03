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
