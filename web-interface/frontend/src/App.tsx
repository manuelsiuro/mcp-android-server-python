import { useState } from 'react';
import { DeviceSelector } from './components/DeviceSelector';
import { DeviceViewer } from './components/DeviceViewer';
import { ClaudeChat } from './components/ClaudeChat';
import { ActionHistory } from './components/ActionHistory';
import { ScenarioList } from './components/ScenarioList';
import { TabbedPanel, type Tab } from './components/TabbedPanel';
import { apiClient } from './services/api';

function App() {
  const [selectedDevice, setSelectedDevice] = useState<string | undefined>();
  const [clickedCoordinates, setClickedCoordinates] = useState<{ x: number; y: number } | null>(
    null
  );
  const [isExecutingClick, setIsExecutingClick] = useState(false);

  const handleClickCoordinates = async (x: number, y: number) => {
    setClickedCoordinates({ x, y });
    console.log(`Executing click at: (${x}, ${y})`);

    setIsExecutingClick(true);
    try {
      const result = await apiClient.executeMcpTool('click_at', {
        x,
        y,
        device_id: selectedDevice
      });

      if (result) {
        console.log('Click executed successfully on device');
      } else {
        console.error('Click execution failed');
      }
    } catch (error) {
      console.error('Click action error:', error);
    } finally {
      setIsExecutingClick(false);
    }
  };

  // Define tabs for the right panel
  const tabs: Tab[] = [
    {
      id: 'claude',
      label: 'Claude Assistant',
      icon: (
        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z" />
        </svg>
      ),
      content: <ClaudeChat deviceId={selectedDevice} />,
    },
    {
      id: 'scenarios',
      label: 'Recorded Scenarios',
      icon: (
        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M14.752 11.168l-3.197-2.132A1 1 0 0010 9.87v4.263a1 1 0 001.555.832l3.197-2.132a1 1 0 000-1.664z" />
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
      ),
      content: <ScenarioList />,
    },
    {
      id: 'history',
      label: 'Action History',
      icon: (
        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
      ),
      content: <ActionHistory />,
    },
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-slate-100">
      {/* Header */}
      <header className="bg-white/80 backdrop-blur-sm shadow-sm border-b border-slate-200 sticky top-0 z-10">
        <div className="max-w-full mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <div className="flex items-center justify-center w-10 h-10 bg-gradient-to-br from-blue-500 to-indigo-600 rounded-lg shadow-lg">
                <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 18h.01M8 21h8a2 2 0 002-2V5a2 2 0 00-2-2H8a2 2 0 00-2 2v14a2 2 0 002 2z" />
                </svg>
              </div>
              <div>
                <h1 className="text-2xl font-bold bg-gradient-to-r from-slate-800 to-slate-600 bg-clip-text text-transparent">
                  MCP Android Interface
                </h1>
                <p className="text-sm text-slate-600 mt-0.5">
                  Claude-powered device automation
                </p>
              </div>
            </div>
            <div className="flex items-center gap-4">
              <DeviceSelector
                selectedDevice={selectedDevice}
                onDeviceChange={setSelectedDevice}
              />
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="h-[calc(100vh-88px)] p-4">
        <div className="h-full max-w-full mx-auto flex gap-4">
          {/* Left Panel - Device Viewer (40%) */}
          <div className="w-[40%] h-full">
            <div className="bg-white rounded-xl shadow-xl border border-slate-200 h-full overflow-hidden">
              <DeviceViewer
                deviceId={selectedDevice}
                onClickCoordinates={handleClickCoordinates}
              />
              {clickedCoordinates && (
                <div className="px-4 py-2 bg-gradient-to-r from-blue-50 to-indigo-50 border-t border-blue-100 text-sm font-medium text-blue-700 flex items-center justify-between">
                  <span>
                    Last click: <span className="font-mono">({clickedCoordinates.x}, {clickedCoordinates.y})</span>
                  </span>
                  {isExecutingClick && (
                    <span className="text-xs text-indigo-600 animate-pulse">Executing...</span>
                  )}
                </div>
              )}
            </div>
          </div>

          {/* Right Panel - Tabbed Interface (60%) */}
          <div className="w-[60%] h-full">
            <TabbedPanel tabs={tabs} defaultTabId="claude" />
          </div>
        </div>
      </main>
    </div>
  );
}

export default App;
