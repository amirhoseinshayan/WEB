import { useEffect } from 'react';
import { HTTP_METHODS } from './constants/http';
import { AppProvider, useAppState } from './store/AppContext';
import './styles/global.css';

function AppContent() {
  const { state, dispatch } = useAppState();

  const activeTab =
    state.tabs.find((tab) => tab.id === state.activeTabId) ?? state.tabs[0];

  useEffect(() => {
    // Sync theme with the root HTML element.
    document.documentElement.dataset.theme = state.theme;
  }, [state.theme]);

  function handleToggleTheme() {
    dispatch({
      type: 'SET_THEME',
      payload: {
        theme: state.theme === 'dark' ? 'light' : 'dark'
      }
    });
  }

  return (
    <main className="app-shell">
      <header className="topbar">
        <div>
          <p className="eyebrow">Web Programming HW2</p>
          <h1>API Client</h1>
        </div>

        <div className="topbar-actions">
          <button type="button" onClick={handleToggleTheme}>
            Toggle Theme
          </button>

          <button type="button" onClick={() => dispatch({ type: 'CREATE_TAB' })}>
            New Tab
          </button>
        </div>
      </header>

      <section className="layout-grid">
        <aside className="panel">
          <h2>Project Base</h2>

          <p>
            Phase 1 is focused on project setup, types, global state, and base
            layout.
          </p>

          <div className="placeholder-list">
            <span>Collections will be added later.</span>
            <span>History will be added later.</span>
            <span>Local Storage is prepared.</span>
          </div>
        </aside>

        <section className="panel main-panel">
          <div className="tabs-row">
            {state.tabs.map((tab) => (
              <button
                key={tab.id}
                type="button"
                className={tab.id === state.activeTabId ? 'tab active' : 'tab'}
                onClick={() =>
                  dispatch({
                    type: 'SET_ACTIVE_TAB',
                    payload: { tabId: tab.id }
                  })
                }
              >
                {tab.title}
              </button>
            ))}

            <button type="button" onClick={() => dispatch({ type: 'CREATE_TAB' })}>
              +
            </button>
          </div>

          <div className="info-card">
            <h2>Active Request State</h2>

            <dl className="state-list">
              <div>
                <dt>Active tab</dt>
                <dd>{activeTab.title}</dd>
              </div>

              <div>
                <dt>Method</dt>
                <dd>{activeTab.request.method}</dd>
              </div>

              <div>
                <dt>URL</dt>
                <dd>{activeTab.request.url || 'Empty'}</dd>
              </div>

              <div>
                <dt>Theme</dt>
                <dd>{state.theme}</dd>
              </div>
            </dl>
          </div>

          <div className="info-card">
            <h2>Supported HTTP Methods</h2>

            <div className="badge-row">
              {HTTP_METHODS.map((method) => (
                <span key={method} className="badge">
                  {method}
                </span>
              ))}
            </div>
          </div>

          <div className="info-card">
            <h2>Phase 1 Checklist</h2>

            <ul className="check-list">
              <li>React and TypeScript are ready.</li>
              <li>Core data models are defined.</li>
              <li>Global state is prepared.</li>
              <li>Reducer and context are connected.</li>
              <li>Base layout and theme variables are ready.</li>
            </ul>
          </div>

          <div className="danger-zone">
            <button
              type="button"
              onClick={() =>
                dispatch({
                  type: 'CLOSE_TAB',
                  payload: { tabId: state.activeTabId }
                })
              }
            >
              Close Active Tab
            </button>

            <button
              type="button"
              onClick={() => dispatch({ type: 'RESET_ACTIVE_REQUEST' })}
            >
              Reset Active Request
            </button>
          </div>
        </section>
      </section>
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