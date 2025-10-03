import { useState } from 'react';
import { DeviceSelector } from './components/DeviceSelector';
import { DeviceViewer } from './components/DeviceViewer';
import { ClaudeChat } from './components/ClaudeChat';
import { ActionHistory } from './components/ActionHistory';
import { ScenarioList } from './components/ScenarioList';

function App() {
  const [selectedDevice, setSelectedDevice] = useState<string | undefined>();
  const [clickedCoordinates, setClickedCoordinates] = useState<{ x: number; y: number } | null>(
    null
  );
  const [showActionHistory, setShowActionHistory] = useState(false);
  const [showScenarios, setShowScenarios] = useState(false);

  const handleClickCoordinates = (x: number, y: number) => {
    setClickedCoordinates({ x, y });
    console.log(`Device clicked at: (${x}, ${y})`);
    // Could auto-populate Claude chat with click_at command
  };

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
              <button
                onClick={() => setShowScenarios(!showScenarios)}
                className="px-4 py-2 text-sm font-medium text-slate-700 hover:text-slate-900 bg-purple-100 hover:bg-purple-200 rounded-lg transition-colors"
              >
                {showScenarios ? 'Hide Scenarios' : 'Show Scenarios'}
              </button>
              <button
                onClick={() => setShowActionHistory(!showActionHistory)}
                className="px-4 py-2 text-sm font-medium text-slate-700 hover:text-slate-900 bg-slate-100 hover:bg-slate-200 rounded-lg transition-colors"
              >
                {showActionHistory ? 'Hide History' : 'Show History'}
              </button>
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
                <div className="px-4 py-2 bg-gradient-to-r from-blue-50 to-indigo-50 border-t border-blue-100 text-sm font-medium text-blue-700">
                  Last click: <span className="font-mono">({clickedCoordinates.x}, {clickedCoordinates.y})</span>
                </div>
              )}
            </div>
          </div>

          {/* Right Panel - Claude Chat (60%) */}
          <div className="w-[60%] h-full flex flex-col gap-4">
            {/* Determine height based on what panels are shown */}
            <div className={
              showScenarios && showActionHistory ? 'h-[40%]' :
              showScenarios || showActionHistory ? 'h-[65%]' :
              'h-full'
            }>
              <ClaudeChat deviceId={selectedDevice} />
            </div>

            {/* Scenarios (Collapsible) */}
            {showScenarios && (
              <div className={showActionHistory ? 'h-[30%]' : 'h-[35%]'}>
                <ScenarioList />
              </div>
            )}

            {/* Action History (Collapsible) */}
            {showActionHistory && (
              <div className={showScenarios ? 'h-[30%]' : 'h-[35%]'}>
                <ActionHistory />
              </div>
            )}
          </div>
        </div>
      </main>
    </div>
  );
}

export default App;
