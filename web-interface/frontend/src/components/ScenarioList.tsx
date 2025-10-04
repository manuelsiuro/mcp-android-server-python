import { useState, useEffect } from 'react';
import { apiClient } from '../services/api';
import type { ScenarioInfo, ReplayResult } from '../types';

export function ScenarioList() {
  const [scenarios, setScenarios] = useState<ScenarioInfo[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [autoRefresh, setAutoRefresh] = useState(true);
  const [replayingScenario, setReplayingScenario] = useState<string | null>(null);
  const [replayResult, setReplayResult] = useState<ReplayResult | null>(null);
  const [showReplayModal, setShowReplayModal] = useState(false);

  const loadScenarios = async () => {
    try {
      setLoading(true);
      setError(null);
      const scenarioList = await apiClient.getScenarios();
      setScenarios(scenarioList);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load scenarios');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadScenarios();
  }, []);

  useEffect(() => {
    if (autoRefresh) {
      const interval = setInterval(loadScenarios, 5000);
      return () => clearInterval(interval);
    }
  }, [autoRefresh]);

  const handleReplay = async (scenario: ScenarioInfo) => {
    if (replayingScenario) return;

    try {
      setReplayingScenario(scenario.name);
      setReplayResult(null);
      setShowReplayModal(false);

      const result = await apiClient.replayScenario(scenario.name, {
        speed_multiplier: 1.0,
        retry_attempts: 3,
        capture_screenshots: false,
        stop_on_error: false,
      });

      setReplayResult(result);
      setShowReplayModal(true);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Replay failed');
    } finally {
      setReplayingScenario(null);
    }
  };

  const handleDelete = async (scenario: ScenarioInfo) => {
    if (!confirm(`Are you sure you want to delete scenario "${scenario.description}"?`)) {
      return;
    }

    try {
      await apiClient.deleteScenario(scenario.name);
      await loadScenarios();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to delete scenario');
    }
  };

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleString();
  };

  const formatDuration = (ms: number) => {
    const seconds = Math.floor(ms / 1000);
    if (seconds < 60) return `${seconds}s`;
    const minutes = Math.floor(seconds / 60);
    const remainingSeconds = seconds % 60;
    return `${minutes}m ${remainingSeconds}s`;
  };

  const closeReplayModal = () => {
    setShowReplayModal(false);
    setReplayResult(null);
  };

  return (
    <div className="flex flex-col h-full bg-white rounded-xl shadow-xl border border-slate-200 overflow-hidden">
      {/* Header */}
      <div className="flex items-center justify-between px-4 py-3 bg-gradient-to-r from-emerald-50 to-teal-50 border-b border-emerald-100">
        <div className="flex items-center gap-3">
          <div className="flex items-center justify-center w-8 h-8 bg-gradient-to-br from-emerald-500 to-teal-600 rounded-lg shadow-sm">
            <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M14.752 11.168l-3.197-2.132A1 1 0 0010 9.87v4.263a1 1 0 001.555.832l3.197-2.132a1 1 0 000-1.664z" />
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          </div>
          <h2 className="text-base font-semibold text-slate-800">Recorded Scenarios</h2>
          <div className="group relative">
            <svg className="w-4 h-4 text-slate-400 hover:text-slate-600 cursor-help" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <div className="absolute left-0 top-6 w-64 p-3 bg-slate-800 text-white text-xs rounded-lg shadow-xl opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all duration-200 z-50">
              <p className="font-semibold mb-1">About Scenarios</p>
              <p className="text-slate-300 leading-relaxed">
                Scenarios are recorded sequences of Android interactions that can be replayed automatically.
                Use the recording engine to capture new scenarios.
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
            onClick={loadScenarios}
            disabled={loading}
            className="p-1.5 text-sm bg-white hover:bg-slate-50 border border-slate-200 rounded-lg disabled:opacity-50 transition-colors"
          >
            <svg className="w-4 h-4 text-slate-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
            </svg>
          </button>
        </div>
      </div>

      {/* Scenario List */}
      <div className="flex-1 overflow-auto p-4 bg-gradient-to-br from-slate-50 to-slate-100">
        {loading && scenarios.length === 0 ? (
          <div className="flex items-center justify-center h-full">
            <div className="w-8 h-8 border-4 border-emerald-500 border-t-transparent rounded-full animate-spin" />
          </div>
        ) : error ? (
          <div className="p-4 bg-red-50 border border-red-200 rounded-lg text-red-700 shadow-sm">
            {error}
          </div>
        ) : scenarios.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-full text-center px-6">
            <svg className="w-12 h-12 text-slate-400 mb-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M14.752 11.168l-3.197-2.132A1 1 0 0010 9.87v4.263a1 1 0 001.555.832l3.197-2.132a1 1 0 000-1.664z" />
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <p className="text-sm font-semibold text-slate-700 mb-2">No scenarios recorded yet</p>
            <p className="text-xs text-slate-500 max-w-sm leading-relaxed">
              Use the MCP recording tools to capture Android interaction sequences.
              Recorded scenarios will appear here and can be replayed automatically.
            </p>
            <div className="mt-4 p-3 bg-blue-50 rounded-lg border border-blue-200">
              <div className="flex items-start gap-2">
                <svg className="w-4 h-4 text-blue-600 mt-0.5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                <div className="text-xs text-blue-700">
                  <span className="font-semibold">Tip:</span> Start recording with the start_recording MCP tool,
                  perform your interactions, then stop_recording to save a replayable scenario.
                </div>
              </div>
            </div>
          </div>
        ) : (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-3">
            {scenarios.map((scenario) => (
              <div
                key={scenario.name}
                className="p-4 bg-white rounded-lg border border-slate-200 hover:border-emerald-300 hover:shadow-md transition-all"
              >
                {/* Scenario Header */}
                <div className="flex items-start justify-between mb-3">
                  <div className="flex-1">
                    <h3 className="text-sm font-semibold text-slate-800 mb-1">
                      {scenario.description || scenario.name}
                    </h3>
                    <p className="text-xs text-slate-500 font-mono">
                      {scenario.name}
                    </p>
                    <p className="text-xs text-slate-400">
                      {formatDate(scenario.created_at)}
                    </p>
                  </div>
                  <button
                    onClick={() => handleDelete(scenario)}
                    className="p-1.5 text-red-600 hover:bg-red-50 rounded-lg transition-colors"
                    title="Delete scenario"
                  >
                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                    </svg>
                  </button>
                </div>

                {/* Scenario Stats */}
                <div className="grid grid-cols-3 gap-2 mb-3">
                  <div className="text-center p-2 bg-emerald-50 rounded-lg">
                    <div className="text-xs text-emerald-600 font-medium">Actions</div>
                    <div className="text-lg font-bold text-emerald-700">{scenario.action_count}</div>
                  </div>
                  <div className="text-center p-2 bg-blue-50 rounded-lg">
                    <div className="text-xs text-blue-600 font-medium">Duration</div>
                    <div className="text-lg font-bold text-blue-700">{formatDuration(scenario.duration_ms)}</div>
                  </div>
                  <div className="text-center p-2 bg-purple-50 rounded-lg">
                    <div className="text-xs text-purple-600 font-medium">Screenshots</div>
                    <div className="text-lg font-bold text-purple-700">{scenario.screenshot_count}</div>
                  </div>
                </div>

                {/* Replay Button */}
                <button
                  onClick={() => handleReplay(scenario)}
                  disabled={replayingScenario === scenario.name}
                  className="w-full px-4 py-2.5 bg-gradient-to-r from-emerald-500 to-teal-600 hover:from-emerald-600 hover:to-teal-700 text-white font-medium rounded-lg shadow-sm disabled:opacity-50 disabled:cursor-not-allowed transition-all flex items-center justify-center gap-2"
                >
                  {replayingScenario === scenario.name ? (
                    <>
                      <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                      <span>Replaying...</span>
                    </>
                  ) : (
                    <>
                      <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M14.752 11.168l-3.197-2.132A1 1 0 0010 9.87v4.263a1 1 0 001.555.832l3.197-2.132a1 1 0 000-1.664z" />
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                      </svg>
                      <span>Replay Scenario</span>
                    </>
                  )}
                </button>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Footer */}
      <div className="px-4 py-2 border-t bg-gradient-to-r from-emerald-50 to-teal-50 text-xs text-slate-600 text-center font-medium">
        {scenarios.length} scenario{scenarios.length !== 1 ? 's' : ''} available
      </div>

      {/* Replay Result Modal */}
      {showReplayModal && replayResult && replayResult.execution && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-xl shadow-2xl max-w-2xl w-full max-h-[80vh] overflow-hidden flex flex-col">
            {/* Modal Header */}
            <div className="flex items-center justify-between px-6 py-4 border-b bg-gradient-to-r from-emerald-50 to-teal-50">
              <div className="flex items-center gap-3">
                <div className={`flex items-center justify-center w-10 h-10 rounded-lg shadow-sm ${
                  replayResult.success
                    ? 'bg-gradient-to-br from-green-500 to-emerald-600'
                    : 'bg-gradient-to-br from-red-500 to-rose-600'
                }`}>
                  {replayResult.success ? (
                    <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                    </svg>
                  ) : (
                    <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                    </svg>
                  )}
                </div>
                <div>
                  <h3 className="text-lg font-semibold text-slate-800">Replay Results</h3>
                  <p className="text-sm text-slate-600">
                    {replayResult.execution?.success_rate?.toFixed(0) || 0}% success rate
                  </p>
                </div>
              </div>
              <button
                onClick={closeReplayModal}
                className="p-2 hover:bg-slate-100 rounded-lg transition-colors"
              >
                <svg className="w-5 h-5 text-slate-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>

            {/* Modal Content */}
            <div className="flex-1 overflow-auto p-6">
              {/* Summary Stats */}
              <div className="grid grid-cols-4 gap-3 mb-6">
                <div className="text-center p-3 bg-blue-50 rounded-lg border border-blue-200">
                  <div className="text-xs text-blue-600 font-medium mb-1">Total</div>
                  <div className="text-2xl font-bold text-blue-700">{replayResult.execution.total_actions}</div>
                </div>
                <div className="text-center p-3 bg-green-50 rounded-lg border border-green-200">
                  <div className="text-xs text-green-600 font-medium mb-1">Success</div>
                  <div className="text-2xl font-bold text-green-700">{replayResult.execution.successful_actions}</div>
                </div>
                <div className="text-center p-3 bg-red-50 rounded-lg border border-red-200">
                  <div className="text-xs text-red-600 font-medium mb-1">Failed</div>
                  <div className="text-2xl font-bold text-red-700">{replayResult.execution.failed_actions}</div>
                </div>
                <div className="text-center p-3 bg-slate-50 rounded-lg border border-slate-200">
                  <div className="text-xs text-slate-600 font-medium mb-1">Skipped</div>
                  <div className="text-2xl font-bold text-slate-700">{replayResult.execution.skipped_actions}</div>
                </div>
              </div>

              {/* Action Details */}
              <div className="space-y-2">
                <h4 className="text-sm font-semibold text-slate-800 mb-3">Action Results</h4>
                {replayResult.action_results.map((action) => (
                  <div
                    key={action.action_index}
                    className="p-3 bg-slate-50 rounded-lg border border-slate-200"
                  >
                    <div className="flex items-center justify-between mb-1">
                      <div className="flex items-center gap-2">
                        <span className="text-xs font-mono text-slate-500">#{action.action_index}</span>
                        <span className="px-2 py-1 text-xs font-semibold bg-emerald-100 text-emerald-700 rounded">
                          {action.tool_name}
                        </span>
                      </div>
                      <div className="flex items-center gap-2">
                        <span className="text-xs text-slate-500">
                          {action.duration_ms.toFixed(0)}ms
                        </span>
                        <span
                          className={`text-xs px-2 py-1 rounded font-medium ${
                            action.status === 'success'
                              ? 'bg-green-100 text-green-700'
                              : action.status === 'failed'
                              ? 'bg-red-100 text-red-700'
                              : 'bg-slate-100 text-slate-700'
                          }`}
                        >
                          {action.status === 'success' ? '✓' : action.status === 'failed' ? '✗' : '⊘'} {action.status}
                        </span>
                      </div>
                    </div>
                    {action.error && (
                      <div className="mt-2 p-2 bg-red-50 border border-red-200 rounded text-xs text-red-700">
                        {action.error}
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </div>

            {/* Modal Footer */}
            <div className="px-6 py-4 border-t bg-slate-50">
              <button
                onClick={closeReplayModal}
                className="w-full px-4 py-2.5 bg-slate-200 hover:bg-slate-300 text-slate-800 font-medium rounded-lg transition-colors"
              >
                Close
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
