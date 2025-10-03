/**
 * TypeScript types for Claude CLI stream-json output
 * Based on Anthropic Messages API streaming format
 */

// Stream event types
export type ClaudeStreamEvent =
  | MessageStartEvent
  | ContentBlockStartEvent
  | ContentBlockDeltaEvent
  | ContentBlockStopEvent
  | MessageDeltaEvent
  | MessageStopEvent
  | ErrorEvent
  | ResultEvent;

export interface MessageStartEvent {
  type: 'message_start';
  message: {
    id: string;
    type: 'message';
    role: 'assistant';
    content: [];
    model: string;
    stop_reason: null;
    stop_sequence: null;
    usage: {
      input_tokens: number;
      output_tokens: number;
    };
  };
}

export interface ContentBlockStartEvent {
  type: 'content_block_start';
  index: number;
  content_block: {
    type: 'text' | 'tool_use';
    text?: string;
    id?: string;
    name?: string;
    input?: Record<string, unknown>;
  };
}

export interface ContentBlockDeltaEvent {
  type: 'content_block_delta';
  index: number;
  delta: {
    type: 'text_delta' | 'input_json_delta';
    text?: string;
    partial_json?: string;
  };
}

export interface ContentBlockStopEvent {
  type: 'content_block_stop';
  index: number;
}

export interface MessageDeltaEvent {
  type: 'message_delta';
  delta: {
    stop_reason: 'end_turn' | 'max_tokens' | 'stop_sequence' | 'tool_use' | null;
    stop_sequence: string | null;
  };
  usage: {
    output_tokens: number;
  };
}

export interface MessageStopEvent {
  type: 'message_stop';
}

export interface ErrorEvent {
  type: 'error';
  error: {
    type: string;
    message: string;
  };
}

export interface ResultEvent {
  type: 'result';
  subtype: 'success' | 'error';
  is_error: boolean;
  duration_ms: number;
  duration_api_ms?: number;
  num_turns?: number;
  result: string;
  session_id: string;
  total_cost_usd?: number;
  usage?: {
    input_tokens: number;
    cache_creation_input_tokens?: number;
    cache_read_input_tokens?: number;
    output_tokens: number;
  };
  modelUsage?: Record<string, any>;
  permission_denials?: Array<{
    tool_name: string;
    tool_use_id: string;
    tool_input: Record<string, any>;
  }>;
  uuid?: string;
}

// Content block types (assembled from stream events)
export type ContentBlock = TextBlock | ToolUseBlock;

export interface TextBlock {
  type: 'text';
  text: string;
}

export interface ToolUseBlock {
  type: 'tool_use';
  id: string;
  name: string;
  input: Record<string, unknown>;
  status?: 'pending' | 'executing' | 'complete' | 'error';
  result?: ToolResult;
  error?: string;
}

export interface ToolResult {
  tool_use_id: string;
  content: string | Record<string, unknown>;
  is_error?: boolean;
}

// Complete Claude message
export interface ClaudeMessageData {
  id: string;
  role: 'user' | 'assistant';
  content: ContentBlock[];
  model?: string;
  stop_reason?: 'end_turn' | 'max_tokens' | 'stop_sequence' | 'tool_use' | null;
  usage?: {
    input_tokens: number;
    output_tokens: number;
  };
  timestamp: number;
}
