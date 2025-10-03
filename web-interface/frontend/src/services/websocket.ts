import type { WebSocketMessage } from '../types';

const WS_URL = `ws://${window.location.hostname}:3001/ws/claude`;

export class ClaudeWebSocket {
  private ws: WebSocket | null = null;
  private messageHandlers: Set<(message: WebSocketMessage) => void> = new Set();
  private reconnectAttempts = 0;
  private maxReconnectAttempts = 5;
  private reconnectDelay = 1000;

  connect(): Promise<void> {
    return new Promise((resolve, reject) => {
      try {
        this.ws = new WebSocket(WS_URL);

        this.ws.onopen = () => {
          console.log('WebSocket connected');
          this.reconnectAttempts = 0;
          resolve();
        };

        this.ws.onmessage = (event) => {
          try {
            console.log('📥 Received raw WebSocket message:', event.data);
            const message: WebSocketMessage = JSON.parse(event.data);
            console.log('📥 Parsed WebSocket message:', message);
            this.messageHandlers.forEach((handler) => handler(message));
          } catch (error) {
            console.error('❌ Failed to parse WebSocket message:', error, event.data);
          }
        };

        this.ws.onerror = (error) => {
          console.error('WebSocket error:', error);
          reject(error);
        };

        this.ws.onclose = () => {
          console.log('WebSocket disconnected');
          this.attemptReconnect();
        };
      } catch (error) {
        reject(error);
      }
    });
  }

  private attemptReconnect() {
    if (this.reconnectAttempts < this.maxReconnectAttempts) {
      this.reconnectAttempts++;
      console.log(`Reconnecting... Attempt ${this.reconnectAttempts}`);
      setTimeout(() => {
        this.connect().catch(console.error);
      }, this.reconnectDelay * this.reconnectAttempts);
    }
  }

  sendPrompt(prompt: string, deviceId?: string): void {
    if (this.ws?.readyState === WebSocket.OPEN) {
      const payload = {
        prompt,
        device_id: deviceId,
      };
      console.log('📤 Sending to WebSocket:', payload);
      this.ws.send(JSON.stringify(payload));
    } else {
      console.error('❌ WebSocket not connected');
    }
  }

  onMessage(handler: (message: WebSocketMessage) => void): () => void {
    this.messageHandlers.add(handler);
    return () => {
      this.messageHandlers.delete(handler);
    };
  }

  disconnect(): void {
    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }
  }

  isConnected(): boolean {
    return this.ws?.readyState === WebSocket.OPEN;
  }
}

export const claudeWs = new ClaudeWebSocket();
