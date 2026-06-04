import type { ApiTab } from '../../types/apiClient';

interface ResponsePanelProps {
  activeTab: ApiTab;
}

function getStatusClass(status: number): string {
  if (status >= 200 && status < 300) {
    return 'success';
  }

  if (status >= 400) {
    return 'error';
  }

  return 'neutral';
}

function formatReceivedAt(value: string): string {
  try {
    return new Date(value).toLocaleString();
  } catch {
    return value;
  }
}

export function ResponsePanel({ activeTab }: ResponsePanelProps) {
  const response = activeTab.response;
  const statusClass = response ? getStatusClass(response.status) : '';

  return (
    <section className="panel-card response-panel">
      <div className="section-heading">
        <div>
          <p className="section-kicker">Server</p>
          <h2>Response</h2>
        </div>

        {response && (
          <span className={`status-badge ${statusClass}`}>
            {response.status}
          </span>
        )}
      </div>

      {activeTab.isLoading && (
        <div className="loading-state">
          <span className="loader" />
          <strong>Sending request...</strong>
          <span>Please wait while the server responds.</span>
        </div>
      )}

      {!activeTab.isLoading && activeTab.error && (
        <div className="error-state">
          <strong>{activeTab.error.message}</strong>
          {activeTab.error.details && <span>{activeTab.error.details}</span>}
        </div>
      )}

      {!activeTab.isLoading && !activeTab.error && response && (
        <div className="response-content">
          <dl className="response-meta">
            <div>
              <dt>Status</dt>
              <dd>
                {response.status} {response.statusText}
              </dd>
            </div>

            <div>
              <dt>Duration</dt>
              <dd>{response.durationMs} ms</dd>
            </div>

            <div>
              <dt>Received</dt>
              <dd>{formatReceivedAt(response.receivedAt)}</dd>
            </div>

            <div>
              <dt>Headers</dt>
              <dd>{response.headers.length}</dd>
            </div>
          </dl>

          {response.headers.length > 0 && (
            <details className="response-headers">
              <summary>Response Headers</summary>

              <div className="response-headers-list">
                {response.headers.map((header) => (
                  <div key={`${header.key}-${header.value}`}>
                    <span>{header.key}</span>
                    <strong>{header.value}</strong>
                  </div>
                ))}
              </div>
            </details>
          )}

          <div className="response-body-block">
            <div className="response-body-heading">
              <h3>Response Body</h3>
            </div>

            {response.body ? (
              <pre>{response.body}</pre>
            ) : (
              <div className="empty-state compact">
                <strong>Empty response body</strong>
                <span>The server returned no body content.</span>
              </div>
            )}
          </div>
        </div>
      )}

      {!activeTab.isLoading && !activeTab.error && !response && (
        <div className="empty-state response-empty">
          <strong>No response yet</strong>
          <span>
            Send a request to see the status code, response body, and response
            headers here.
          </span>
        </div>
      )}
    </section>
  );
}