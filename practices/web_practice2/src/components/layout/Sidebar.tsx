import type { HistoryItem } from '../../types/apiClient';
import { useAppState } from '../../store/AppContext';

function formatHistoryDate(value: string): string {
  try {
    return new Date(value).toLocaleString();
  } catch {
    return value;
  }
}

function getShortUrl(url: string): string {
  if (url.length <= 70) {
    return url;
  }

  return `${url.slice(0, 67)}...`;
}

function HistoryStatus({ item }: { item: HistoryItem }) {
  if (item.responseStatus === null) {
    return <span className="history-status failed">Failed</span>;
  }

  if (item.responseStatus >= 200 && item.responseStatus < 300) {
    return <span className="history-status success">{item.responseStatus}</span>;
  }

  if (item.responseStatus >= 400) {
    return <span className="history-status error">{item.responseStatus}</span>;
  }

  return <span className="history-status neutral">{item.responseStatus}</span>;
}

export function Sidebar() {
  const { state, dispatch } = useAppState();

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
          <span>Collections will be implemented in a later phase.</span>
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

        {state.history.length === 0 ? (
          <div className="empty-state compact">
            <strong>No requests sent yet</strong>
            <span>Request history will appear here after sending requests.</span>
          </div>
        ) : (
          <>
            <div className="history-list">
              {state.history.map((item) => (
                <article key={item.id} className="history-item">
                  <button
                    type="button"
                    className="history-load-button"
                    onClick={() =>
                      dispatch({
                        type: 'LOAD_HISTORY_ITEM',
                        payload: {
                          request: item.request
                        }
                      })
                    }
                  >
                    <div className="history-item-top">
                      <span className="history-method">
                        {item.request.method}
                      </span>
                      <HistoryStatus item={item} />
                    </div>

                    <strong title={item.request.url}>
                      {getShortUrl(item.request.url)}
                    </strong>

                    <span>{formatHistoryDate(item.createdAt)}</span>
                  </button>

                  <button
                    type="button"
                    className="history-remove-button"
                    aria-label="Remove history item"
                    onClick={() =>
                      dispatch({
                        type: 'REMOVE_HISTORY_ITEM',
                        payload: {
                          historyItemId: item.id
                        }
                      })
                    }
                  >
                    ×
                  </button>
                </article>
              ))}
            </div>

            <button
              type="button"
              className="clear-history-button"
              onClick={() => dispatch({ type: 'CLEAR_HISTORY' })}
            >
              Clear History
            </button>
          </>
        )}
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