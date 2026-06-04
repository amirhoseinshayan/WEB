import type { ApiTab } from '../../types/apiClient';

interface ResponsePanelProps {
  activeTab: ApiTab;
}

export function ResponsePanel({ activeTab }: ResponsePanelProps) {
  return (
    <section className="panel-card response-panel">
      <div className="section-heading">
        <div>
          <p className="section-kicker">Server</p>
          <h2>Response</h2>
        </div>

        {activeTab.response && (
          <span className="status-badge">{activeTab.response.status}</span>
        )}
      </div>

      {activeTab.isLoading && (
        <div className="loading-state">
          <span className="loader" />
          <strong>Sending request...</strong>
        </div>
      )}

      {!activeTab.isLoading && activeTab.error && (
        <div className="error-state">
          <strong>{activeTab.error.message}</strong>
          {activeTab.error.details && <span>{activeTab.error.details}</span>}
        </div>
      )}

      {!activeTab.isLoading && !activeTab.error && activeTab.response && (
        <div className="response-content">
          <dl className="response-meta">
            <div>
              <dt>Status</dt>
              <dd>
                {activeTab.response.status} {activeTab.response.statusText}
              </dd>
            </div>

            <div>
              <dt>Duration</dt>
              <dd>{activeTab.response.durationMs} ms</dd>
            </div>
          </dl>

          <pre>{activeTab.response.body}</pre>
        </div>
      )}

      {!activeTab.isLoading && !activeTab.error && !activeTab.response && (
        <div className="empty-state response-empty">
          <strong>No response yet</strong>
          <span>
            After request sending is implemented, status code and response body
            will appear here.
          </span>
        </div>
      )}
    </section>
  );
}