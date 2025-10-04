import { type ReactNode, useState } from 'react';

export interface Tab {
  id: string;
  label: string;
  icon?: ReactNode;
  content: ReactNode;
}

interface TabbedPanelProps {
  tabs: Tab[];
  defaultTabId?: string;
}

export function TabbedPanel({ tabs, defaultTabId }: TabbedPanelProps) {
  const [activeTabId, setActiveTabId] = useState(defaultTabId || tabs[0]?.id);

  const activeTab = tabs.find(tab => tab.id === activeTabId);

  return (
    <div className="flex flex-col h-full bg-white rounded-xl shadow-xl border border-slate-200 overflow-hidden">
      {/* Tab Headers */}
      <div className="flex border-b border-slate-200 bg-gradient-to-r from-slate-50 to-slate-100">
        {tabs.map((tab) => (
          <button
            key={tab.id}
            onClick={() => setActiveTabId(tab.id)}
            className={`
              flex items-center gap-2 px-6 py-3 font-medium text-sm transition-all relative
              ${activeTabId === tab.id
                ? 'text-blue-600 bg-white border-b-2 border-blue-600'
                : 'text-slate-600 hover:text-slate-900 hover:bg-slate-50'
              }
            `}
          >
            {tab.icon && <span className="flex-shrink-0">{tab.icon}</span>}
            <span>{tab.label}</span>
            {activeTabId === tab.id && (
              <div className="absolute bottom-0 left-0 right-0 h-0.5 bg-blue-600" />
            )}
          </button>
        ))}
      </div>

      {/* Tab Content */}
      <div className="flex-1 overflow-hidden">
        {activeTab?.content}
      </div>
    </div>
  );
}
