import type { Device, ActionRecord, ScreenshotResponse } from '../types';

const API_BASE = '';

class ApiClient {
  private baseUrl: string;

  constructor(baseUrl: string = API_BASE) {
    this.baseUrl = baseUrl;
  }

  private async request<T>(
    endpoint: string,
    options?: RequestInit
  ): Promise<T> {
    const response = await fetch(`${this.baseUrl}${endpoint}`, {
      ...options,
      headers: {
        'Content-Type': 'application/json',
        ...options?.headers,
      },
    });

    if (!response.ok) {
      throw new Error(`API error: ${response.statusText}`);
    }

    return response.json();
  }

  // Device endpoints
  async getDevices(): Promise<Device[]> {
    const response = await this.request<{
      devices: Array<{
        device_id: string;
        status: string;
        model: string;
        product: string;
      }>;
      count: number;
    }>('/api/devices');

    // Transform backend format to frontend format
    return response.devices.map(device => ({
      id: device.device_id,
      info: {
        model: device.model.replace(/_/g, ' '), // SM_S921B -> SM S921B
        brand: 'Unknown',
        version: device.product
      },
      connected: device.status === 'device'
    }));
  }

  // Screenshot endpoints
  async takeScreenshot(deviceId?: string): Promise<ScreenshotResponse> {
    return this.request<ScreenshotResponse>('/api/screenshot', {
      method: 'POST',
      body: JSON.stringify({ device_id: deviceId }),
    });
  }

  getScreenshotUrl(filename: string): string {
    return `${this.baseUrl}/api/screenshot/${filename}`;
  }

  // Action history endpoints
  async getActionHistory(): Promise<ActionRecord[]> {
    const response = await this.request<{ actions: ActionRecord[] }>('/api/actions/history');
    return response.actions;
  }

  async recordAction(action: Partial<ActionRecord>): Promise<void> {
    await this.request('/api/actions/record', {
      method: 'POST',
      body: JSON.stringify(action),
    });
  }

  // MCP tool execution
  async executeMcpTool(
    tool: string,
    params: Record<string, any>
  ): Promise<any> {
    return this.request('/api/mcp/tool', {
      method: 'POST',
      body: JSON.stringify({ tool, params }),
    });
  }
}

export const apiClient = new ApiClient();
