import { useState } from 'react';
import type { ToolUseBlock as ToolUseBlockType } from '../types/claude';

interface ToolUseBlockProps {
  toolUse: ToolUseBlockType;
}

export function ToolUseBlock({ toolUse }: ToolUseBlockProps) {
  const [showParams, setShowParams] = useState(false);
  const [showResult, setShowResult] = useState(false);

  const statusColors = {
    pending: 'bg-yellow-50 border-yellow-300 text-yellow-800',
    executing: 'bg-blue-50 border-blue-300 text-blue-800',
    complete: 'bg-green-50 border-green-300 text-green-800',
    error: 'bg-red-50 border-red-300 text-red-800',
  };

  const statusIcons = {
    pending: '⏳',
    executing: '⚙️',
    complete: '✅',
    error: '❌',
  };

  const status = toolUse.status || 'complete';

  return (
    <div className={`border-2 rounded-lg p-4 my-2 ${statusColors[status]}`}>
      {/* Header */}
      <div className="flex items-center justify-between mb-2">
        <div className="flex items-center gap-2">
          <span className="text-xl">{statusIcons[status]}</span>
          <span className="font-semibold">Tool: {toolUse.name}</span>
        </div>
        <span className="text-sm font-medium">
          {status.charAt(0).toUpperCase() + status.slice(1)}
        </span>
      </div>

      {/* Parameters */}
      <div className="mt-2">
        <button
          onClick={() => setShowParams(!showParams)}
          className="text-sm font-medium flex items-center gap-1 hover:underline"
        >
          Parameters {showParams ? '▲' : '▼'}
        </button>
        {showParams && (
          <pre className="mt-2 p-3 bg-gray-900 text-gray-100 rounded text-xs overflow-x-auto">
            {JSON.stringify(toolUse.input, null, 2)}
          </pre>
        )}
      </div>

      {/* Result */}
      {toolUse.result && (
        <div className="mt-2">
          <button
            onClick={() => setShowResult(!showResult)}
            className="text-sm font-medium flex items-center gap-1 hover:underline"
          >
            Result {showResult ? '▲' : '▼'}
          </button>
          {showResult && (
            <pre className="mt-2 p-3 bg-gray-900 text-gray-100 rounded text-xs overflow-x-auto max-h-64">
              {typeof toolUse.result.content === 'string'
                ? toolUse.result.content
                : JSON.stringify(toolUse.result.content, null, 2)}
            </pre>
          )}
        </div>
      )}

      {/* Error */}
      {toolUse.error && (
        <div className="mt-2 p-2 bg-red-100 border border-red-300 rounded text-sm">
          <strong>Error:</strong> {toolUse.error}
        </div>
      )}
    </div>
  );
}
