import { useMemo, useState } from 'react';
import type { ApiTab } from '../../types/apiClient';
import { useAppState } from '../../store/AppContext';
import { copyTextToClipboard } from '../../utils/clipboard';
import { generateCurlCommand } from '../../utils/curl';
import { createId } from '../../utils/id';
import { getEnabledQueryParams } from '../../utils/queryParams';
import { getEnabledHeaders } from '../../utils/requestHeaders';
import { methodSupportsRequestBody } from '../../utils/requestBody';

interface RequestSummaryProps {
  activeTab: ApiTab;
}

type CopyTarget = 'url' | 'curl' | null;

function getBodyLabel(activeTab: ApiTab): string {
  const body = activeTab.request.body.trim();

  if (!body) {
    return 'No body';
  }

  if (!methodSupportsRequestBody(activeTab.request.method)) {
    return `${activeTab.request.bodyMode.toUpperCase()} body saved, usually not sent for ${activeTab.request.method}`;
  }

  return `${activeTab.request.bodyMode.toUpperCase()} body, ${body.length} characters`;
}

export function RequestSummary({ activeTab }: RequestSummaryProps) {
  const { dispatch } = useAppState();
  const [copyTarget, setCopyTarget] = useState<CopyTarget>(null);

  const enabledParams = getEnabledQueryParams(activeTab.request.params);
  const enabledHeaders = getEnabledHeaders(activeTab.request.headers);

  const finalUrl = activeTab.request.url.trim() || 'No URL entered yet';

  const curlCommand = useMemo(
    () => generateCurlCommand(activeTab.request),
    [activeTab.request]
  );

  async function handleCopy(target: Exclude<CopyTarget, null>, value: string) {
    const copied = await copyTextToClipboard(value);

    if (!copied) {
      setCopyTarget(null);

      dispatch({
        type: 'ADD_NOTIFICATION',
        payload: {
          notification: {
            id: createId('notification'),
            type: 'error',
            title: 'Copy failed',
            message: 'Please copy the text manually.'
          }
        }
      });

      return;
    }

    setCopyTarget(target);

    dispatch({
      type: 'ADD_NOTIFICATION',
      payload: {
        notification: {
          id: createId('notification'),
          type: 'success',
          title: target === 'url' ? 'URL copied' : 'cURL copied',
          message:
            target === 'url'
              ? 'The request URL was copied to your clipboard.'
              : 'The generated cURL command was copied to your clipboard.'
        }
      }
    });

    window.setTimeout(() => {
      setCopyTarget(null);
    }, 1800);
  }

  return (
    <section className="request-summary panel-card">
      <div className="request-summary-header">
        <div>
          <p className="section-kicker">Overview</p>
          <h2>Request Summary</h2>
        </div>

        <div className="request-summary-actions">
          <button
            type="button"
            disabled={!activeTab.request.url.trim()}
            onClick={() => handleCopy('url', activeTab.request.url.trim())}
          >
            {copyTarget === 'url' ? 'URL Copied' : 'Copy URL'}
          </button>

          <button
            type="button"
            onClick={() => handleCopy('curl', curlCommand)}
          >
            {copyTarget === 'curl' ? 'cURL Copied' : 'Copy cURL'}
          </button>
        </div>
      </div>

      <dl className="request-summary-grid">
        <div>
          <dt>Method</dt>
          <dd>{activeTab.request.method}</dd>
        </div>

        <div>
          <dt>Enabled Params</dt>
          <dd>{enabledParams.length}</dd>
        </div>

        <div>
          <dt>Enabled Headers</dt>
          <dd>{enabledHeaders.length}</dd>
        </div>

        <div>
          <dt>Body</dt>
          <dd>{getBodyLabel(activeTab)}</dd>
        </div>
      </dl>

      <div className="request-summary-url">
        <span>Final URL</span>
        <code>{finalUrl}</code>
      </div>

      <details className="curl-preview">
        <summary>cURL Preview</summary>
        <pre>{curlCommand}</pre>
      </details>
    </section>
  );
}