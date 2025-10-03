import { useState, useEffect } from 'react';
import { apiClient } from '../services/api';
import type { ActionRecord } from '../types';

export function ActionHistory() {
  const [actions, setActions] = useState<ActionRecord[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [autoRefresh, setAutoRefresh] = useState(true);

  const loadHistory = async () => {
    try {
      setLoading(true);
      setError(null);
      const history = await apiClient.getActionHistory();
      setActions(history);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load history');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadHistory();
  }, []);

  useEffect(() => {
    if (autoRefresh) {
      const interval = setInterval(loadHistory, 3000);
      return () => clearInterval(interval);
    }
  }, [autoRefresh]);

  const clearHistory = async () => {
    if (confirm('Are you sure you want to clear all action history?')) {
      // Note: This would need a backend endpoint
      setActions([]);
    }
  };

  const formatTimestamp = (timestamp: string) => {
    const date = new Date(timestamp);
    return date.toLocaleTimeString();
  };

  const formatParams = (params: Record<string, any>) => {
    return JSON.stringify(params, null, 2);
  };

  return (
    <div className="flex flex-col h-full bg-white rounded-xl shadow-xl border border-slate-200 overflow-hidden">
      {/* Header */}
      <div className="flex items-center justify-between px-4 py-3 bg-gradient-to-r from-emerald-50 to-teal-50 border-b border-emerald-100">
        <div className="flex items-center gap-3">
          <div className="flex items-center justify-center w-8 h-8 bg-gradient-to-br from-emerald-500 to-teal-600 rounded-lg shadow-sm">
            <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
          </div>
          <h2 className="text-base font-semibold text-slate-800">Action History</h2>
          <div className="group relative">
            <svg className="w-4 h-4 text-slate-400 hover:text-slate-600 cursor-help" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <div className="absolute left-0 top-6 w-64 p-3 bg-slate-800 text-white text-xs rounded-lg shadow-xl opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all duration-200 z-50">
              <p className="font-semibold mb-1">About Action History</p>
              <p className="text-slate-300 leading-relaxed">
                Automatically tracks all MCP Android tool executions initiated by Claude.
                View parameters, results, and execution times for debugging and workflow analysis.
              </p>
            </div>
          </div>
        </div>
        <div className="flex items-center gap-2">
          <label className="flex items-center gap-2 cursor-pointer text-sm select-none group">
            <input
              type="checkbox"
              checked={autoRefresh}
              onChange={(e) => setAutoRefresh(e.target.checked)}
              className="w-4 h-4 rounded border-slate-300 text-emerald-600 focus:ring-2 focus:ring-emerald-500 focus:ring-offset-0"
            />
            <span className="text-slate-600 group-hover:text-slate-800">Auto</span>
          </label>
          <button
            onClick={loadHistory}
            disabled={loading}
            className="p-1.5 text-sm bg-white hover:bg-slate-50 border border-slate-200 rounded-lg disabled:opacity-50 transition-colors"
          >
            <svg className="w-4 h-4 text-slate-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
            </svg>
          </button>
          <button
            onClick={clearHistory}
            className="px-3 py-1.5 text-sm bg-red-50 hover:bg-red-100 text-red-700 border border-red-200 rounded-lg transition-colors font-medium"
          >
            Clear
          </button>
        </div>
      </div>

      {/* Action List */}
      <div className="flex-1 overflow-auto p-4 bg-gradient-to-br from-slate-50 to-slate-100">
        {loading && actions.length === 0 ? (
          <div className="flex items-center justify-center h-full">
            <div className="w-8 h-8 border-4 border-emerald-500 border-t-transparent rounded-full animate-spin" />
          </div>
        ) : error ? (
          <div className="p-4 bg-red-50 border border-red-200 rounded-lg text-red-700 shadow-sm">
            {error}
          </div>
        ) : actions.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-full text-center px-6">
            <svg className="w-12 h-12 text-slate-400 mb-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
            <p className="text-sm font-semibold text-slate-700 mb-2">No actions recorded yet</p>
            <p className="text-xs text-slate-500 max-w-sm leading-relaxed">
              Actions will appear here automatically when Claude uses MCP Android tools.
              Try asking Claude to interact with your device (e.g., "take a screenshot" or "click on the login button").
            </p>
            <div className="mt-4 p-3 bg-blue-50 rounded-lg border border-blue-200">
              <div className="flex items-start gap-2">
                <svg className="w-4 h-4 text-blue-600 mt-0.5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                <div className="text-xs text-blue-700">
                  <span className="font-semibold">Tip:</span> This history tracks all MCP tool calls made through Claude,
                  including click, send_text, screenshot, and 60+ other Android automation tools.
                </div>
              </div>
            </div>
          </div>
        ) : (
          <div className="space-y-2">
            {actions.map((action) => (
              <div
                key={action.id}
                className="p-3 bg-white rounded-lg border border-slate-200 hover:border-emerald-300 hover:shadow-sm transition-all"
              >
                <div className="flex items-start justify-between mb-2">
                  <div className="flex items-center gap-2">
                    <span className="px-2 py-1 text-xs font-semibold bg-emerald-100 text-emerald-700 rounded">
                      {action.tool}
                    </span>
                    <span className="text-xs text-slate-500">
                      {formatTimestamp(action.timestamp)}
                    </span>
                  </div>
                  <span
                    className={`text-xs px-2 py-1 rounded font-medium ${
                      action.result?.success === false
                        ? 'bg-red-100 text-red-700'
                        : 'bg-green-100 text-green-700'
                    }`}
                  >
                    {action.result?.success === false ? '✗ Failed' : '✓ Success'}
                  </span>
                </div>

                {/* Parameters */}
                {Object.keys(action.params).length > 0 && (
                  <details className="mt-2">
                    <summary className="text-xs font-medium text-slate-700 cursor-pointer hover:text-emerald-600 transition-colors">
                      Parameters
                    </summary>
                    <pre className="mt-2 p-2 bg-slate-50 border border-slate-200 rounded text-xs overflow-x-auto">
                      {formatParams(action.params)}
                    </pre>
                  </details>
                )}

                {/* Result */}
                {action.result && (
                  <details className="mt-2">
                    <summary className="text-xs font-medium text-slate-700 cursor-pointer hover:text-emerald-600 transition-colors">
                      Result
                    </summary>
                    <pre className="mt-2 p-2 bg-slate-50 border border-slate-200 rounded text-xs overflow-x-auto">
                      {JSON.stringify(action.result, null, 2)}
                    </pre>
                  </details>
                )}
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Footer */}
      <div className="px-4 py-2 border-t bg-gradient-to-r from-emerald-50 to-teal-50 text-xs text-slate-600 text-center font-medium">
        {actions.length} action{actions.length !== 1 ? 's' : ''} recorded
      </div>
    </div>
  );
}
