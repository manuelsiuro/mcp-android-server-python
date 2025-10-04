import { useState, useEffect, useRef } from 'react';
import { apiClient } from '../services/api';
import type { ClickEvent } from '../types';

interface DeviceViewerProps {
  deviceId: string | undefined;
  onClickCoordinates?: (x: number, y: number) => void;
}

// Recording state interface
interface RecordingState {
  status: 'idle' | 'recording' | 'stopping' | 'error';
  sessionName: string | null;
  startTime: number | null;
  actionCount: number;
  screenshotCount: number;
  lastAction: string | null;
  error: string | null;
}

export function DeviceViewer({ deviceId, onClickCoordinates }: DeviceViewerProps) {
  // Existing state
  const [screenshotUrl, setScreenshotUrl] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [autoRefresh, setAutoRefresh] = useState(true);
  const [clickMarker, setClickMarker] = useState<ClickEvent | null>(null);
  const imageRef = useRef<HTMLImageElement>(null);
  const refreshIntervalRef = useRef<number | undefined>(undefined);

  // Recording state
  const [recordingState, setRecordingState] = useState<RecordingState>({
    status: 'idle',
    sessionName: null,
    startTime: null,
    actionCount: 0,
    screenshotCount: 0,
    lastAction: null,
    error: null
  });
  const [showSessionModal, setShowSessionModal] = useState(false);
  const [sessionNameInput, setSessionNameInput] = useState('');
  const [captureScreenshots, setCaptureScreenshots] = useState(true);

  // Helper functions for recording
  const isRecording = recordingState.status === 'recording';
  const recordingDuration = recordingState.startTime
    ? Date.now() - recordingState.startTime
    : 0;

  const formatDuration = (ms: number): string => {
    const seconds = Math.floor(ms / 1000);
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  // Recording functions
  const handleStartRecording = async () => {
    if (!sessionNameInput.trim()) return;

    try {
      const result = await apiClient.startRecording(sessionNameInput, {
        capture_screenshots: captureScreenshots,
        device_id: deviceId
      });

      setRecordingState({
        status: 'recording',
        sessionName: result.recording_id,
        startTime: Date.now(),
        actionCount: 0,
        screenshotCount: 0,
        lastAction: null,
        error: null
      });

      setShowSessionModal(false);
      setSessionNameInput('');
    } catch (error) {
      setRecordingState(prev => ({
        ...prev,
        status: 'error',
        error: error instanceof Error ? error.message : 'Failed to start recording'
      }));
    }
  };

  const handleStopRecording = async () => {
    setRecordingState(prev => ({ ...prev, status: 'stopping' }));

    try {
      await apiClient.stopRecording();
      setRecordingState({
        status: 'idle',
        sessionName: null,
        startTime: null,
        actionCount: 0,
        screenshotCount: 0,
        lastAction: null,
        error: null
      });
    } catch (error) {
      setRecordingState(prev => ({
        ...prev,
        status: 'error',
        error: error instanceof Error ? error.message : 'Failed to stop recording'
      }));
    }
  };

  // Existing screenshot capture function
  const captureScreenshot = async () => {
    if (!deviceId) return;

    try {
      setLoading(true);
      setError(null);
      const response = await apiClient.takeScreenshot(deviceId);
      const url = apiClient.getScreenshotUrl(response.filename);
      setScreenshotUrl(url + '?t=' + Date.now()); // Cache bust
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to capture screenshot');
    } finally {
      setLoading(false);
    }
  };

  // Initial screenshot capture
  useEffect(() => {
    if (deviceId) {
      captureScreenshot();
    }
  }, [deviceId]);

  // Auto-refresh for screenshots
  useEffect(() => {
    if (autoRefresh && deviceId) {
      refreshIntervalRef.current = window.setInterval(() => {
        captureScreenshot();
      }, 2000);

      return () => {
        if (refreshIntervalRef.current) {
          clearInterval(refreshIntervalRef.current);
        }
      };
    }
  }, [autoRefresh, deviceId]);

  // Poll recording status to update action count, screenshot count, and last action
  useEffect(() => {
    if (recordingState.status === 'recording') {
      const pollInterval = setInterval(async () => {
        try {
          const status = await apiClient.getRecordingStatus();
          if (status.active && status.action_count !== undefined) {
            setRecordingState(prev => ({
              ...prev,
              actionCount: status.action_count!,
              screenshotCount: status.screenshot_count || 0,
              lastAction: status.last_action || null
            }));
          }
        } catch (err) {
          console.error('Failed to poll recording status:', err);
        }
      }, 2000);

      return () => clearInterval(pollInterval);
    }
  }, [recordingState.status]);

  // Update duration timer
  useEffect(() => {
    if (recordingState.status === 'recording' && recordingState.startTime) {
      const timerId = setInterval(() => {
        // Force re-render to update duration display
        setRecordingState(prev => ({ ...prev }));
      }, 1000);

      return () => clearInterval(timerId);
    }
  }, [recordingState.status, recordingState.startTime]);

  // Click handler with proper coordinate calculation
  const handleImageClick = (e: React.MouseEvent<HTMLImageElement>) => {
    if (!imageRef.current) return;

    // Get the image's bounding rectangle
    const rect = imageRef.current.getBoundingClientRect();

    // Get the parent container's bounding rectangle for marker positioning
    const parentRect = imageRef.current.parentElement?.getBoundingClientRect();
    if (!parentRect) return;

    // Calculate relative click position within the image
    // e.clientX/Y are viewport coordinates, rect.left/top is image position
    const x = Math.round(e.clientX - rect.left);
    const y = Math.round(e.clientY - rect.top);

    // Validate click is within image bounds
    if (x < 0 || y < 0 || x > rect.width || y > rect.height) {
      console.warn('Click outside image bounds', { x, y, width: rect.width, height: rect.height });
      return;
    }

    // Scale coordinates to actual device resolution
    const scaleX = imageRef.current.naturalWidth / rect.width;
    const scaleY = imageRef.current.naturalHeight / rect.height;
    const actualX = Math.round(x * scaleX);
    const actualY = Math.round(y * scaleY);

    // Calculate marker position relative to parent container
    // This accounts for the image being centered in its parent with flexbox
    const markerX = Math.round(rect.left - parentRect.left + x);
    const markerY = Math.round(rect.top - parentRect.top + y);

    // Show click marker at the correct position relative to parent
    setClickMarker({ x: markerX, y: markerY, timestamp: Date.now() });
    setTimeout(() => setClickMarker(null), 1000);

    // Send coordinates to parent
    onClickCoordinates?.(actualX, actualY);
  };

  if (!deviceId) {
    return (
      <div className="flex items-center justify-center h-full bg-gray-50 rounded-lg border-2 border-dashed border-gray-300">
        <p className="text-gray-500">Select a device to view screen</p>
      </div>
    );
  }

  // Session Name Modal Component
  const SessionNameModal = () => (
    <div
      className="fixed inset-0 bg-black/50 flex items-center justify-center z-50"
      onClick={(e) => {
        if (e.target === e.currentTarget) {
          setShowSessionModal(false);
          setSessionNameInput('');
        }
      }}
    >
      <div className="bg-white rounded-xl shadow-2xl p-6 w-[450px]">
        <h2 className="text-xl font-bold text-slate-900 mb-4">Start Recording Session</h2>

        <div className="space-y-4">
          <div>
            <label htmlFor="sessionName" className="block text-sm font-medium text-slate-700 mb-2">
              Session Name
            </label>
            <input
              id="sessionName"
              type="text"
              value={sessionNameInput}
              onChange={(e) => setSessionNameInput(e.target.value)}
              placeholder="e.g., login-flow, search-contacts"
              className="w-full px-4 py-2.5 border border-slate-300 rounded-lg focus:ring-2 focus:ring-red-500 focus:border-red-500 outline-none transition-all"
              autoFocus
              onKeyDown={(e) => {
                if (e.key === 'Enter' && sessionNameInput.trim()) {
                  handleStartRecording();
                } else if (e.key === 'Escape') {
                  setShowSessionModal(false);
                  setSessionNameInput('');
                }
              }}
            />
            <p className="mt-1.5 text-xs text-slate-500">
              Use lowercase letters, numbers, hyphens, and underscores
            </p>
          </div>

          <div className="flex items-start gap-3 p-3 bg-slate-50 rounded-lg">
            <input
              type="checkbox"
              id="captureScreenshots"
              checked={captureScreenshots}
              onChange={(e) => setCaptureScreenshots(e.target.checked)}
              className="w-4 h-4 mt-0.5 rounded border-slate-300 text-red-600 focus:ring-2 focus:ring-red-500 focus:ring-offset-0"
            />
            <label htmlFor="captureScreenshots" className="flex-1 cursor-pointer select-none">
              <div className="text-sm font-medium text-slate-900">Capture screenshots</div>
              <div className="text-xs text-slate-600 mt-0.5">
                Automatically capture screenshots for each action (recommended)
              </div>
            </label>
          </div>
        </div>

        <div className="flex items-center gap-3 mt-6">
          <button
            onClick={() => {
              setShowSessionModal(false);
              setSessionNameInput('');
            }}
            className="flex-1 px-4 py-2.5 bg-white hover:bg-slate-50 border border-slate-300 text-slate-700 rounded-lg transition-colors font-medium text-sm"
          >
            Cancel
          </button>
          <button
            onClick={handleStartRecording}
            disabled={!sessionNameInput.trim()}
            className="flex-1 px-4 py-2.5 bg-gradient-to-r from-red-500 to-rose-600 hover:from-red-600 hover:to-rose-700 disabled:from-slate-300 disabled:to-slate-400 disabled:cursor-not-allowed text-white rounded-lg transition-all font-medium text-sm shadow-sm"
          >
            Start Recording
          </button>
        </div>
      </div>
    </div>
  );

  return (
    <div className={`flex flex-col h-full ${isRecording ? 'border-4 border-red-500' : 'border border-slate-200'} rounded-lg transition-all`}>
      {/* Controls - Redesigned with Grouped Layout */}
      <div className="flex items-center justify-between px-3 py-2 bg-gradient-to-r from-slate-50 to-slate-100 border-b border-slate-200">
        <div className="flex items-center gap-2">
          {/* Recording Group */}
          <div className="flex items-center gap-2 pr-3 border-r border-slate-300">
            {recordingState.status === 'idle' && (
              <button
                onClick={() => setShowSessionModal(true)}
                className="px-3 py-1.5 bg-gradient-to-r from-red-500 to-rose-600 hover:from-red-600 hover:to-rose-700 text-white rounded-md transition-all shadow-sm font-medium text-sm flex items-center gap-1.5"
              >
                <svg className="w-3.5 h-3.5" fill="currentColor" viewBox="0 0 24 24">
                  <circle cx="12" cy="12" r="8" />
                </svg>
                <span>Record</span>
              </button>
            )}

            {recordingState.status === 'recording' && (
              <button
                disabled
                className="px-3 py-1.5 bg-gradient-to-r from-red-500 to-rose-600 text-white rounded-md cursor-not-allowed shadow-sm font-medium text-sm flex items-center gap-1.5 relative"
              >
                <span className="relative flex h-2.5 w-2.5">
                  <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-white opacity-75"></span>
                  <span className="relative inline-flex rounded-full h-2.5 w-2.5 bg-white"></span>
                </span>
                <span>Recording</span>
              </button>
            )}

            {(recordingState.status === 'recording' || recordingState.status === 'stopping') && (
              <button
                onClick={handleStopRecording}
                disabled={recordingState.status === 'stopping'}
                className="px-3 py-1.5 bg-white hover:bg-red-50 border-2 border-red-500 text-red-600 hover:text-red-700 disabled:bg-slate-50 disabled:border-slate-300 disabled:text-slate-400 disabled:cursor-not-allowed rounded-md transition-all font-medium text-sm flex items-center gap-1.5"
              >
                {recordingState.status === 'stopping' ? (
                  <>
                    <svg className="w-3.5 h-3.5 animate-spin" fill="none" viewBox="0 0 24 24">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                    </svg>
                    <span>Stopping</span>
                  </>
                ) : (
                  <>
                    <svg className="w-3.5 h-3.5" fill="currentColor" viewBox="0 0 24 24">
                      <rect x="6" y="6" width="12" height="12" rx="1" />
                    </svg>
                    <span>Stop</span>
                  </>
                )}
              </button>
            )}
          </div>

          {/* View Controls Group */}
          <div className="flex items-center gap-2 pr-3 border-r border-slate-300">
            <button
              onClick={captureScreenshot}
              disabled={loading}
              className="px-3 py-1.5 bg-gradient-to-r from-blue-500 to-indigo-600 text-white rounded-md hover:from-blue-600 hover:to-indigo-700 disabled:from-blue-400 disabled:to-indigo-500 disabled:cursor-not-allowed transition-all shadow-sm font-medium text-sm flex items-center gap-1.5 relative overflow-hidden"
            >
              {loading ? (
                <svg className="w-3.5 h-3.5 animate-spin" fill="none" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
              ) : (
                <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 9a2 2 0 012-2h.93a2 2 0 001.664-.89l.812-1.22A2 2 0 0110.07 4h3.86a2 2 0 011.664.89l.812 1.22A2 2 0 0018.07 7H19a2 2 0 012 2v9a2 2 0 01-2 2H5a2 2 0 01-2-2V9z" />
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 13a3 3 0 11-6 0 3 3 0 016 0z" />
                </svg>
              )}
              <span className="transition-opacity duration-200">Capture</span>
            </button>

            <label className="flex items-center gap-1.5 cursor-pointer select-none group">
              <input
                type="checkbox"
                checked={autoRefresh}
                onChange={(e) => setAutoRefresh(e.target.checked)}
                className="w-3.5 h-3.5 rounded border-slate-300 text-blue-600 focus:ring-2 focus:ring-blue-500 focus:ring-offset-0"
              />
              <span className="text-xs text-slate-700 group-hover:text-slate-900 font-medium">Auto-refresh (2s)</span>
            </label>
          </div>
        </div>

        {/* Download Button */}
        {screenshotUrl && (
          <a
            href={screenshotUrl}
            download
            className="px-3 py-1.5 bg-white hover:bg-slate-50 border border-slate-200 rounded-md text-xs font-medium text-slate-700 hover:text-slate-900 transition-colors flex items-center gap-1.5"
          >
            <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
            </svg>
            Download
          </a>
        )}
      </div>

      {/* Recording Status Banner - Clean Professional Design */}
      {recordingState.status === 'recording' && (
        <div className="px-4 py-2.5 bg-gradient-to-r from-red-500 to-rose-600 text-white border-b border-red-600">
          <div className="flex items-center justify-center gap-6">
            {/* Pulsing indicator */}
            <span className="relative flex h-3 w-3">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-white opacity-75"></span>
              <span className="relative inline-flex rounded-full h-3 w-3 bg-white"></span>
            </span>

            {/* Duration */}
            <div className="flex items-center gap-2">
              <span className="text-red-100 text-xs font-medium uppercase tracking-wide">Duration</span>
              <span className="font-mono font-bold text-lg">
                {formatDuration(recordingDuration)}
              </span>
            </div>

            <div className="w-px h-6 bg-red-400/50"></div>

            {/* Actions */}
            <div className="flex items-center gap-2">
              <span className="text-red-100 text-xs font-medium uppercase tracking-wide">Actions</span>
              <span className="font-mono font-bold text-lg">
                {recordingState.actionCount}
              </span>
            </div>

            <div className="w-px h-6 bg-red-400/50"></div>

            {/* Screenshots */}
            <div className="flex items-center gap-2">
              <span className="text-red-100 text-xs font-medium uppercase tracking-wide">Screenshots</span>
              <span className="font-mono font-bold text-lg">
                {recordingState.screenshotCount}
              </span>
            </div>

            {/* Last Action - Only show if exists */}
            {recordingState.lastAction && (
              <>
                <div className="w-px h-6 bg-red-400/50"></div>
                <div className="flex items-center gap-2 max-w-md">
                  <span className="text-red-100 text-xs font-medium uppercase tracking-wide">Last</span>
                  <span className="font-mono text-sm truncate">
                    {recordingState.lastAction}
                  </span>
                </div>
              </>
            )}
          </div>
        </div>
      )}

      {/* Error Banner */}
      {recordingState.status === 'error' && recordingState.error && (
        <div className="px-4 py-2.5 bg-red-50 border-b border-red-200 flex items-center justify-between">
          <div className="flex items-center gap-2 text-sm text-red-700">
            <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
            </svg>
            <span className="font-medium">{recordingState.error}</span>
          </div>
          <button
            onClick={() => setRecordingState(prev => ({ ...prev, status: 'idle', error: null }))}
            className="text-red-600 hover:text-red-700 text-sm font-medium"
          >
            Dismiss
          </button>
        </div>
      )}

      {/* Screenshot Display */}
      <div className="flex-1 overflow-hidden bg-gradient-to-br from-slate-100 to-slate-200 flex items-center justify-center p-4">
        {error && (
          <div className="absolute top-20 left-4 right-4 p-4 bg-red-50 border border-red-200 rounded-lg text-red-700 shadow-lg z-10">
            {error}
          </div>
        )}

        {screenshotUrl ? (
          <div className="relative max-w-full max-h-full flex items-center justify-center">
            <img
              ref={imageRef}
              src={screenshotUrl}
              alt="Device screenshot"
              onClick={handleImageClick}
              className="max-w-full max-h-full object-contain shadow-2xl rounded-lg cursor-crosshair border-4 border-white/50"
              style={{ maxHeight: 'calc(100vh - 200px)' }}
            />
            {clickMarker && (
              <div
                className="absolute pointer-events-none"
                style={{
                  left: clickMarker.x,
                  top: clickMarker.y,
                }}
              >
                <div className="absolute w-6 h-6 -translate-x-1/2 -translate-y-1/2 bg-red-500 rounded-full animate-ping opacity-75" />
                <div className="absolute w-3 h-3 -translate-x-1/2 -translate-y-1/2 bg-red-600 rounded-full" />
              </div>
            )}
          </div>
        ) : (
          <div className="flex flex-col items-center justify-center gap-3 text-slate-500">
            <svg className="w-16 h-16 opacity-50" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
            </svg>
            <p className="text-sm font-medium">No screenshot available</p>
          </div>
        )}
      </div>

      {/* Session Name Modal */}
      {showSessionModal && <SessionNameModal />}
    </div>
  );
}
