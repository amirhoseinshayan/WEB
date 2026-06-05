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

function getStatusDescription(status: number): string {
  if (status >= 100 && status < 200) {
    return 'Informational response';
  }

  if (status >= 200 && status < 300) {
    return 'Successful response';
  }

  if (status >= 300 && status < 400) {
    return 'Redirection response';
  }

  if (status >= 400 && status < 500) {
    return 'Client-side error response';
  }

  if (status >= 500) {
    return 'Server-side error response';
  }

  return 'Unknown response status';
}

function formatReceivedAt(value: string): string {
  try {
    return new Date(value).toLocaleString();
  } catch {
    return value;
  }
}

function formatErrorType(value: string): string {
  return value
    .split('-')
    .map((part) => `${part.charAt(0).toUpperCase()}${part.slice(1)}`)
    .join(' ');
}

export function ResponsePanel({ activeTab }: ResponsePanelProps) {
  const response = activeTab.response;
  const statusClass = response ? getStatusClass(response.status) : '';
  const statusDescription = response
    ? getStatusDescription(response.status)
    : null;

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
        <div className="error-state detailed-error-state">
          <div className="error-meta-row">
            <span className="error-type-badge">
              {formatErrorType(activeTab.error.type)}
            </span>

            {activeTab.error.field && (
              <span className="error-field-badge">
                Field: {activeTab.error.field}
              </span>
            )}
          </div>

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
              <dt>Status Type</dt>
              <dd>{statusDescription}</dd>
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

          {response.status >= 400 && (
            <div className="status-warning">
              <strong>Request completed with an error status.</strong>
              <span>
                The server returned a response, but the status code indicates a
                client or server error.
              </span>
            </div>
          )}

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