import { useAppState } from '../../store/AppContext';

export function Sidebar() {
  const { state } = useAppState();

  const activeTab =
    state.tabs.find((tab) => tab.id === state.activeTabId) ?? state.tabs[0];

  return (
    <aside className="sidebar">
      <section className="sidebar-card">
        <div className="section-heading">
          <div>
            <p className="section-kicker">Saved</p>
            <h2>Collections</h2>
          </div>

          <span className="counter-badge">{state.collections.length}</span>
        </div>

        <div className="empty-state compact">
          <strong>No collections yet</strong>
          <span>Saving requests into collections will be added later.</span>
        </div>

        <div className="sidebar-actions">
          <button type="button" disabled>
            Import JSON
          </button>
          <button type="button" disabled>
            Export JSON
          </button>
        </div>
      </section>

      <section className="sidebar-card">
        <div className="section-heading">
          <div>
            <p className="section-kicker">Recent</p>
            <h2>History</h2>
          </div>

          <span className="counter-badge">{state.history.length}</span>
        </div>

        <div className="empty-state compact">
          <strong>No requests sent yet</strong>
          <span>Request history will appear here after sending requests.</span>
        </div>
      </section>

      <section className="sidebar-card">
        <div className="section-heading">
          <div>
            <p className="section-kicker">Current</p>
            <h2>Active Tab</h2>
          </div>
        </div>

        <dl className="sidebar-summary">
          <div>
            <dt>Tab</dt>
            <dd>{activeTab?.title ?? 'None'}</dd>
          </div>

          <div>
            <dt>Method</dt>
            <dd>{activeTab?.request.method ?? '-'}</dd>
          </div>

          <div>
            <dt>URL</dt>
            <dd>{activeTab?.request.url || 'Empty'}</dd>
          </div>
        </dl>
      </section>
    </aside>
  );
}