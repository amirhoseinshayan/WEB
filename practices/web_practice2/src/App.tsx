import { useEffect } from 'react';
import { TopBar } from './components/layout/TopBar';
import { Sidebar } from './components/layout/Sidebar';
import { RequestLine } from './components/request/RequestLine';
import { RequestPanel } from './components/request/RequestPanel';
import { RequestTabs } from './components/request/RequestTabs';
import { ResponsePanel } from './components/response/ResponsePanel';
import { AppProvider, useAppState } from './store/AppContext';
import './styles/global.css';

function AppContent() {
  const { state } = useAppState();

  const activeTab =
    state.tabs.find((tab) => tab.id === state.activeTabId) ?? state.tabs[0];

  useEffect(() => {
    // Sync theme with the root HTML element.
    document.documentElement.dataset.theme = state.theme;
  }, [state.theme]);

  if (!activeTab) {
    return (
      <main className="app-shell">
        <div className="empty-state">
          <strong>No active tab found</strong>
          <span>Please create a new request tab.</span>
        </div>
      </main>
    );
  }

  return (
    <main className="app-shell">
      <TopBar />

      <div className="workspace-layout">
        <Sidebar />

        <section className="workspace-main">
          <RequestTabs />
          <RequestLine activeTab={activeTab} />

          <div className="request-response-grid">
            <RequestPanel activeTab={activeTab} />
            <ResponsePanel activeTab={activeTab} />
          </div>
        </section>
      </div>
    </main>
  );
}

export default function App() {
  return (
    <AppProvider>
      <AppContent />
    </AppProvider>
  );
}