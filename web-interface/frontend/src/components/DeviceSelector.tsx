import { useState, useEffect } from 'react';
import { apiClient } from '../services/api';
import type { Device } from '../types';

interface DeviceSelectorProps {
  selectedDevice: string | undefined;
  onDeviceChange: (deviceId: string | undefined) => void;
}

export function DeviceSelector({ selectedDevice, onDeviceChange }: DeviceSelectorProps) {
  const [devices, setDevices] = useState<Device[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadDevices();
  }, []);

  const loadDevices = async () => {
    try {
      setLoading(true);
      setError(null);
      const deviceList = await apiClient.getDevices();
      setDevices(deviceList);

      // Auto-select first device if none selected
      if (!selectedDevice && deviceList.length > 0) {
        onDeviceChange(deviceList[0].id);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load devices');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center gap-2">
        <div className="w-4 h-4 border-2 border-blue-500 border-t-transparent rounded-full animate-spin" />
        <span className="text-sm text-gray-600">Loading devices...</span>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex items-center gap-2">
        <span className="text-sm text-red-600">{error}</span>
        <button
          onClick={loadDevices}
          className="px-3 py-1 text-sm bg-blue-500 text-white rounded hover:bg-blue-600"
        >
          Retry
        </button>
      </div>
    );
  }

  if (devices.length === 0) {
    return (
      <div className="text-sm text-gray-600">
        No devices connected. Please connect an Android device.
      </div>
    );
  }

  return (
    <div className="flex items-center gap-3">
      <label htmlFor="device-select" className="text-sm font-medium text-slate-700">
        Device:
      </label>
      <select
        id="device-select"
        value={selectedDevice || ''}
        onChange={(e) => onDeviceChange(e.target.value || undefined)}
        className="px-4 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-white text-slate-900 text-sm font-medium shadow-sm hover:border-slate-400 transition-colors"
      >
        <option value="">Select device...</option>
        {devices.map((device) => (
          <option key={device.id} value={device.id}>
            {device.id} - {device.info.model || 'Unknown Model'}
            {device.connected ? ' ✓' : ' (disconnected)'}
          </option>
        ))}
      </select>
      <button
        onClick={loadDevices}
        className="p-2 text-sm bg-white hover:bg-slate-50 border border-slate-300 rounded-lg transition-colors shadow-sm"
        title="Refresh devices"
      >
        <svg className="w-4 h-4 text-slate-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
        </svg>
      </button>
    </div>
  );
}
