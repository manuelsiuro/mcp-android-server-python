import { useState, useEffect, useRef } from 'react';
import { claudeWs } from '../services/websocket';
import type { WebSocketMessage, ClaudeMessageData, ContentBlock, ClaudeStreamEvent } from '../types';
import { ContentBlockRenderer } from './ContentBlockRenderer';

interface ClaudeChatProps {
  deviceId: string | undefined;
}

export function ClaudeChat({ deviceId }: ClaudeChatProps) {
  const [messages, setMessages] = useState<ClaudeMessageData[]>([]);
  const [currentMessage, setCurrentMessage] = useState<ClaudeMessageData | null>(null);
  const [input, setInput] = useState('');
  const [isConnected, setIsConnected] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    // Connect WebSocket
    claudeWs
      .connect()
      .then(() => setIsConnected(true))
      .catch((err) => {
        console.error('Failed to connect WebSocket:', err);
        setIsConnected(false);
      });

    // Subscribe to messages
    const unsubscribe = claudeWs.onMessage((message: WebSocketMessage) => {
      handleWebSocketMessage(message);
    });

    return () => {
      unsubscribe();
    };
  }, []);

  useEffect(() => {
    // Auto-scroll to bottom
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, currentMessage]);

  const handleWebSocketMessage = (message: WebSocketMessage) => {
    console.log('📨 WebSocket message:', message);

    switch (message.type) {
      case 'start':
        setIsLoading(true);
        break;

      case 'content':
        // Parse Claude stream-json event
        if (message.data) {
          handleStreamEvent(message.data as ClaudeStreamEvent);
        }
        break;

      case 'end':
        // Finalize current message
        if (currentMessage) {
          setMessages((prev) => [...prev, currentMessage]);
          setCurrentMessage(null);
        }
        setIsLoading(false);
        break;

      case 'error':
        setIsLoading(false);
        setMessages((prev) => [
          ...prev,
          {
            id: `error-${Date.now()}`,
            role: 'assistant',
            content: [{
              type: 'text',
              text: `❌ Error: ${message.data || 'Unknown error'}`,
            }],
            timestamp: Date.now(),
          },
        ]);
        setCurrentMessage(null);
        break;
    }
  };

  const handleStreamEvent = (event: ClaudeStreamEvent) => {
    console.log('🔄 Stream event:', event);

    switch (event.type) {
      case 'result':
        // Handle Claude CLI result response
        if (event.result) {
          const resultMessage: ClaudeMessageData = {
            id: event.session_id || `result-${Date.now()}`,
            role: 'assistant',
            content: [{
              type: 'text',
              text: event.result,
            }],
            timestamp: Date.now(),
            usage: event.usage ? {
              input_tokens: event.usage.input_tokens || 0,
              output_tokens: event.usage.output_tokens || 0,
            } : undefined,
          };
          setMessages((prev) => [...prev, resultMessage]);
          setCurrentMessage(null);
        }
        break;

      case 'message_start':
        setCurrentMessage({
          id: event.message.id,
          role: 'assistant',
          content: [],
          model: event.message.model,
          usage: event.message.usage,
          timestamp: Date.now(),
        });
        break;

      case 'content_block_start':
        setCurrentMessage((prev) => {
          if (!prev) return null;

          const newBlock: ContentBlock = event.content_block.type === 'tool_use'
            ? {
                type: 'tool_use',
                id: event.content_block.id || '',
                name: event.content_block.name || '',
                input: event.content_block.input || {},
                status: 'executing',
              }
            : {
                type: 'text',
                text: event.content_block.text || '',
              };

          return {
            ...prev,
            content: [...prev.content, newBlock],
          };
        });
        break;

      case 'content_block_delta':
        setCurrentMessage((prev) => {
          if (!prev || prev.content.length === 0) return prev;

          const updatedContent = [...prev.content];
          const blockIndex = event.index;
          const currentBlock = updatedContent[blockIndex];

          if (event.delta.type === 'text_delta' && currentBlock.type === 'text') {
            updatedContent[blockIndex] = {
              ...currentBlock,
              text: currentBlock.text + (event.delta.text || ''),
            };
          } else if (event.delta.type === 'input_json_delta' && currentBlock.type === 'tool_use') {
            // Parse partial JSON for tool use
            try {
              const partialJson = event.delta.partial_json || '';
              const currentJson = JSON.stringify(currentBlock.input);
              const newInput = JSON.parse(currentJson + partialJson);
              updatedContent[blockIndex] = {
                ...currentBlock,
                input: newInput,
              };
            } catch (e) {
              // Ignore JSON parse errors during streaming
              console.warn('JSON parse error during streaming:', e);
            }
          }

          return {
            ...prev,
            content: updatedContent,
          };
        });
        break;

      case 'content_block_stop':
        setCurrentMessage((prev) => {
          if (!prev) return prev;

          const updatedContent = [...prev.content];
          const block = updatedContent[event.index];

          if (block && block.type === 'tool_use') {
            updatedContent[event.index] = {
              ...block,
              status: 'complete',
            };
          }

          return {
            ...prev,
            content: updatedContent,
          };
        });
        break;

      case 'message_delta':
        setCurrentMessage((prev) => {
          if (!prev) return prev;
          return {
            ...prev,
            stop_reason: event.delta.stop_reason,
            usage: prev.usage ? {
              input_tokens: prev.usage.input_tokens,
              output_tokens: event.usage.output_tokens,
            } : { input_tokens: 0, output_tokens: event.usage.output_tokens },
          };
        });
        break;

      case 'error':
        console.error('Stream error:', event.error);
        break;
    }
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || !isConnected || isLoading) return;

    // Add user message
    const userMessage: ClaudeMessageData = {
      id: `user-${Date.now()}`,
      role: 'user',
      content: [
        {
          type: 'text',
          text: input,
        },
      ],
      timestamp: Date.now(),
    };
    setMessages((prev) => [...prev, userMessage]);

    // Send to WebSocket
    claudeWs.sendPrompt(input, deviceId);

    // Clear input
    setInput('');
  };

  const clearChat = () => {
    setMessages([]);
    setCurrentMessage(null);
  };

  const allMessages = currentMessage ? [...messages, currentMessage] : messages;

  return (
    <div className="flex flex-col h-full bg-white rounded-xl shadow-xl border border-slate-200 overflow-hidden">
      {/* Header */}
      <div className="flex items-center justify-between px-4 py-3 bg-gradient-to-r from-indigo-50 to-purple-50 border-b border-indigo-100">
        <div className="flex items-center gap-3">
          <div className="flex items-center justify-center w-8 h-8 bg-gradient-to-br from-indigo-500 to-purple-600 rounded-lg shadow-sm">
            <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
            </svg>
          </div>
          <div>
            <h2 className="text-base font-semibold text-slate-800">Claude Assistant</h2>
            <div className="flex items-center gap-1.5 mt-0.5">
              <div
                className={`w-1.5 h-1.5 rounded-full ${
                  isConnected ? 'bg-green-500 animate-pulse' : 'bg-red-500'
                }`}
              />
              <span className="text-xs text-slate-600">
                {isConnected ? 'Connected' : 'Disconnected'}
              </span>
            </div>
          </div>
        </div>
        <button
          onClick={clearChat}
          className="px-3 py-1.5 text-sm font-medium bg-white hover:bg-slate-50 text-slate-700 border border-slate-200 rounded-lg transition-colors"
        >
          Clear
        </button>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-auto p-4 space-y-4 bg-gradient-to-br from-slate-50 to-slate-100">
        {allMessages.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-full text-center">
            <div className="mb-4 flex items-center justify-center w-16 h-16 bg-gradient-to-br from-indigo-100 to-purple-100 rounded-2xl">
              <svg className="w-8 h-8 text-indigo-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M14 10h4.764a2 2 0 011.789 2.894l-3.5 7A2 2 0 0115.263 21h-4.017c-.163 0-.326-.02-.485-.06L7 20m7-10V5a2 2 0 00-2-2h-.095c-.5 0-.905.405-.905.905 0 .714-.211 1.412-.608 2.006L7 11v9m7-10h-2M7 20H5a2 2 0 01-2-2v-6a2 2 0 012-2h2.5" />
              </svg>
            </div>
            <p className="text-lg font-semibold text-slate-800 mb-2">Hi! I'm Claude</p>
            <p className="text-sm text-slate-600 max-w-sm">
              Ask me to interact with the Android device or help with automation tasks.
            </p>
          </div>
        ) : (
          allMessages.map((message, index) => (
            <div
              key={message.id || index}
              className={`flex ${
                message.role === 'user' ? 'justify-end' : 'justify-start'
              }`}
            >
              <div
                className={`max-w-[85%] rounded-xl p-4 shadow-sm ${
                  message.role === 'user'
                    ? 'bg-gradient-to-br from-blue-500 to-indigo-600 text-white'
                    : 'bg-white text-slate-900 border border-slate-200'
                }`}
              >
                {/* Message Header */}
                <div className={`flex items-center gap-2 mb-2 text-xs ${message.role === 'user' ? 'text-blue-100' : 'text-slate-500'}`}>
                  <span className="font-medium">{message.role === 'user' ? 'You' : 'Claude'}</span>
                  {message.model && message.role === 'assistant' && (
                    <span className="opacity-75">({message.model})</span>
                  )}
                  <span className="opacity-50">·</span>
                  <span className="opacity-75">{new Date(message.timestamp).toLocaleTimeString()}</span>
                </div>

                {/* Content Blocks */}
                <div className="space-y-2">
                  {message.content.map((block, blockIndex) => (
                    <ContentBlockRenderer
                      key={blockIndex}
                      block={block}
                      isStreaming={message === currentMessage && blockIndex === message.content.length - 1}
                    />
                  ))}
                </div>

                {/* Usage Stats */}
                {message.usage && message.role === 'assistant' && (
                  <div className="mt-2 pt-2 border-t border-slate-200 text-xs text-slate-500">
                    📊 {message.usage.input_tokens} in · {message.usage.output_tokens} out
                  </div>
                )}
              </div>
            </div>
          ))
        )}
        {isLoading && (
          <div className="flex items-center gap-2 px-4">
            <div className="flex items-center gap-1.5">
              <div className="w-2 h-2 bg-indigo-400 rounded-full animate-bounce" />
              <div
                className="w-2 h-2 bg-indigo-400 rounded-full animate-bounce"
                style={{ animationDelay: '0.15s' }}
              />
              <div
                className="w-2 h-2 bg-indigo-400 rounded-full animate-bounce"
                style={{ animationDelay: '0.3s' }}
              />
            </div>
            <span className="text-sm text-slate-500">Claude is thinking...</span>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <form onSubmit={handleSubmit} className="p-4 border-t border-slate-200 bg-white">
        <div className="flex gap-2">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder={
              isConnected
                ? 'Ask Claude to interact with the device...'
                : 'Connecting...'
            }
            disabled={!isConnected || isLoading}
            className="flex-1 px-4 py-2.5 border border-slate-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent disabled:bg-slate-100 disabled:text-slate-400 text-sm"
          />
          <button
            type="submit"
            disabled={!isConnected || isLoading || !input.trim()}
            className="px-6 py-2.5 bg-gradient-to-r from-indigo-500 to-purple-600 text-white rounded-lg hover:from-indigo-600 hover:to-purple-700 disabled:from-gray-300 disabled:to-gray-400 disabled:cursor-not-allowed transition-all shadow-sm font-medium text-sm"
          >
            Send
          </button>
        </div>
      </form>
    </div>
  );
}
