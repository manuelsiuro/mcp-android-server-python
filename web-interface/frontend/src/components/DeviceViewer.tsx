import { useState, useEffect, useRef } from 'react';
import { apiClient } from '../services/api';
import type { ClickEvent } from '../types';

interface DeviceViewerProps {
  deviceId: string | undefined;
  onClickCoordinates?: (x: number, y: number) => void;
}

export function DeviceViewer({ deviceId, onClickCoordinates }: DeviceViewerProps) {
  const [screenshotUrl, setScreenshotUrl] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [autoRefresh, setAutoRefresh] = useState(true);
  const [clickMarker, setClickMarker] = useState<ClickEvent | null>(null);
  const imageRef = useRef<HTMLImageElement>(null);
  const refreshIntervalRef = useRef<number | undefined>(undefined);

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

  useEffect(() => {
    if (deviceId) {
      captureScreenshot();
    }
  }, [deviceId]);

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

  const handleImageClick = (e: React.MouseEvent<HTMLImageElement>) => {
    if (!imageRef.current) return;

    const rect = imageRef.current.getBoundingClientRect();
    const x = Math.round(e.clientX - rect.left);
    const y = Math.round(e.clientY - rect.top);

    // Scale coordinates to actual device resolution
    const scaleX = imageRef.current.naturalWidth / rect.width;
    const scaleY = imageRef.current.naturalHeight / rect.height;
    const actualX = Math.round(x * scaleX);
    const actualY = Math.round(y * scaleY);

    // Show click marker
    setClickMarker({ x, y, timestamp: Date.now() });
    setTimeout(() => setClickMarker(null), 1000);

    onClickCoordinates?.(actualX, actualY);
  };

  if (!deviceId) {
    return (
      <div className="flex items-center justify-center h-full bg-gray-50 rounded-lg border-2 border-dashed border-gray-300">
        <p className="text-gray-500">Select a device to view screen</p>
      </div>
    );
  }

  return (
    <div className="flex flex-col h-full">
      {/* Controls */}
      <div className="flex items-center justify-between px-4 py-3 bg-gradient-to-r from-slate-50 to-slate-100 border-b border-slate-200">
        <div className="flex items-center gap-3">
          <button
            onClick={captureScreenshot}
            disabled={loading}
            className="px-4 py-2 bg-gradient-to-r from-blue-500 to-indigo-600 text-white rounded-lg hover:from-blue-600 hover:to-indigo-700 disabled:from-gray-300 disabled:to-gray-400 disabled:cursor-not-allowed transition-all shadow-sm font-medium text-sm flex items-center gap-2"
          >
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 9a2 2 0 012-2h.93a2 2 0 001.664-.89l.812-1.22A2 2 0 0110.07 4h3.86a2 2 0 011.664.89l.812 1.22A2 2 0 0018.07 7H19a2 2 0 012 2v9a2 2 0 01-2 2H5a2 2 0 01-2-2V9z" />
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 13a3 3 0 11-6 0 3 3 0 016 0z" />
            </svg>
            {loading ? 'Capturing...' : 'Capture'}
          </button>
          <label className="flex items-center gap-2 cursor-pointer select-none group">
            <input
              type="checkbox"
              checked={autoRefresh}
              onChange={(e) => setAutoRefresh(e.target.checked)}
              className="w-4 h-4 rounded border-slate-300 text-blue-600 focus:ring-2 focus:ring-blue-500 focus:ring-offset-0"
            />
            <span className="text-sm text-slate-700 group-hover:text-slate-900">Auto-refresh (2s)</span>
          </label>
        </div>
        {screenshotUrl && (
          <a
            href={screenshotUrl}
            download
            className="px-4 py-2 bg-white hover:bg-slate-50 border border-slate-200 rounded-lg text-sm font-medium text-slate-700 hover:text-slate-900 transition-colors flex items-center gap-2"
          >
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
            </svg>
            Download
          </a>
        )}
      </div>

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
    </div>
  );
}
