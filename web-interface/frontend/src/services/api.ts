import type { Device, ActionRecord, ScreenshotResponse, ScenarioInfo, ReplayOptions, ReplayResult } from '../types';

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
      body: JSON.stringify({ tool_name: tool, parameters: params }),
    });
  }

  // Scenario management endpoints
  async getScenarios(): Promise<ScenarioInfo[]> {
    const response = await this.request<{ scenarios: ScenarioInfo[]; count: number }>('/api/scenarios');
    return response.scenarios;
  }

  async replayScenario(
    scenarioName: string,
    options: ReplayOptions = {}
  ): Promise<ReplayResult> {
    return this.request<ReplayResult>(`/api/scenarios/${encodeURIComponent(scenarioName)}/replay`, {
      method: 'POST',
      body: JSON.stringify(options),
    });
  }

  async deleteScenario(scenarioName: string): Promise<{ success: boolean; message: string }> {
    return this.request<{ success: boolean; message: string }>(
      `/api/scenarios/${encodeURIComponent(scenarioName)}`,
      {
        method: 'DELETE',
      }
    );
  }

  async getScenarioScreenshots(scenarioName: string): Promise<{
    screenshots: Array<{ filename: string; url: string; size: number }>;
    count: number;
  }> {
    return this.request<{ screenshots: Array<{ filename: string; url: string; size: number }>; count: number }>(
      `/api/scenarios/${encodeURIComponent(scenarioName)}/screenshots`
    );
  }

  getScenarioScreenshotUrl(scenarioName: string, filename: string): string {
    return `${this.baseUrl}/api/scenarios/${encodeURIComponent(scenarioName)}/screenshots/${filename}`;
  }

  // Recording control endpoints
  async startRecording(
    sessionName: string,
    options: {
      description?: string;
      capture_screenshots?: boolean;
      device_id?: string;
    } = {}
  ): Promise<{
    recording_id: string;
    status: string;
    start_time: string;
    capture_screenshots: boolean;
  }> {
    return this.request('/api/recording/start', {
      method: 'POST',
      body: JSON.stringify({
        session_name: sessionName,
        description: options.description,
        capture_screenshots: options.capture_screenshots ?? true,
        device_id: options.device_id
      }),
    });
  }

  async stopRecording(): Promise<{
    scenario_file: string;
    screenshot_folder?: string;
    action_count: number;
    duration_ms: number;
    status: string;
  }> {
    return this.request('/api/recording/stop', {
      method: 'POST',
    });
  }

  async getRecordingStatus(): Promise<{
    active: boolean;
    session_name?: string;
    action_count?: number;
    screenshot_count?: number;
    last_action?: string;
    duration_ms?: number;
    capture_screenshots?: boolean;
    message?: string;
  }> {
    return this.request('/api/recording/status');
  }
}

export const apiClient = new ApiClient();
