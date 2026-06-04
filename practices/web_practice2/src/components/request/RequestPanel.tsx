import { useState, type ChangeEvent } from 'react';
import { createEmptyKeyValuePair } from '../../constants/defaults';
import { useAppState } from '../../store/AppContext';
import type { ApiTab, BodyMode, KeyValuePair } from '../../types/apiClient';
import {
  buildUrlWithQueryParams,
  extractQueryParamsFromUrl,
  hasQueryParams
} from '../../utils/queryParams';
import { KeyValueEditor } from './KeyValueEditor';

type RequestPanelTab = 'params' | 'headers' | 'body';

interface RequestPanelProps {
  activeTab: ApiTab;
}

export function RequestPanel({ activeTab }: RequestPanelProps) {
  const { dispatch } = useAppState();
  const [selectedTab, setSelectedTab] = useState<RequestPanelTab>('params');

  function updateParams(nextParams: KeyValuePair[]) {
    const nextUrl = buildUrlWithQueryParams(activeTab.request.url, nextParams);

    dispatch({
      type: 'UPDATE_ACTIVE_REQUEST',
      payload: {
        changes: {
          params: nextParams,
          url: nextUrl
        }
      }
    });
  }

  function handleAddParam() {
    dispatch({
      type: 'UPDATE_ACTIVE_REQUEST',
      payload: {
        changes: {
          params: [...activeTab.request.params, createEmptyKeyValuePair()]
        }
      }
    });
  }

  function handleUpdateParam(rowId: string, changes: Partial<KeyValuePair>) {
    const nextParams = activeTab.request.params.map((param) =>
      param.id === rowId
        ? {
            ...param,
            ...changes
          }
        : param
    );

    updateParams(nextParams);
  }

  function handleRemoveParam(rowId: string) {
    const nextParams = activeTab.request.params.filter(
      (param) => param.id !== rowId
    );

    updateParams(nextParams);
  }

  function handleClearParams() {
    updateParams([]);
  }

  function handleImportParamsFromUrl() {
    const importedParams = extractQueryParamsFromUrl(activeTab.request.url);

    dispatch({
      type: 'UPDATE_ACTIVE_REQUEST',
      payload: {
        changes: {
          params: importedParams
        }
      }
    });
  }

  function handleAddHeader() {
    dispatch({
      type: 'UPDATE_ACTIVE_REQUEST',
      payload: {
        changes: {
          headers: [...activeTab.request.headers, createEmptyKeyValuePair()]
        }
      }
    });
  }

  function handleUpdateHeader(rowId: string, changes: Partial<KeyValuePair>) {
    const nextHeaders = activeTab.request.headers.map((header) =>
      header.id === rowId
        ? {
            ...header,
            ...changes
          }
        : header
    );

    dispatch({
      type: 'UPDATE_ACTIVE_REQUEST',
      payload: {
        changes: {
          headers: nextHeaders
        }
      }
    });
  }

  function handleRemoveHeader(rowId: string) {
    const nextHeaders = activeTab.request.headers.filter(
      (header) => header.id !== rowId
    );

    dispatch({
      type: 'UPDATE_ACTIVE_REQUEST',
      payload: {
        changes: {
          headers: nextHeaders
        }
      }
    });
  }

  function handleClearHeaders() {
    dispatch({
      type: 'UPDATE_ACTIVE_REQUEST',
      payload: {
        changes: {
          headers: []
        }
      }
    });
  }

  function handleBodyModeChange(event: ChangeEvent<HTMLSelectElement>) {
    dispatch({
      type: 'UPDATE_ACTIVE_REQUEST',
      payload: {
        changes: {
          bodyMode: event.target.value as BodyMode
        }
      }
    });
  }

  function handleBodyChange(event: ChangeEvent<HTMLTextAreaElement>) {
    dispatch({
      type: 'UPDATE_ACTIVE_REQUEST',
      payload: {
        changes: {
          body: event.target.value
        }
      }
    });
  }

  return (
    <section className="panel-card request-panel">
      <div className="section-heading">
        <div>
          <p className="section-kicker">Request</p>
          <h2>Request Data</h2>
        </div>
      </div>

      <div className="request-panel-tabs">
        <button
          type="button"
          className={selectedTab === 'params' ? 'active' : ''}
          onClick={() => setSelectedTab('params')}
        >
          Params
        </button>

        <button
          type="button"
          className={selectedTab === 'headers' ? 'active' : ''}
          onClick={() => setSelectedTab('headers')}
        >
          Headers
        </button>

        <button
          type="button"
          className={selectedTab === 'body' ? 'active' : ''}
          onClick={() => setSelectedTab('body')}
        >
          Body
        </button>
      </div>

      <div className="request-panel-content">
        {selectedTab === 'params' && (
          <KeyValueEditor
            title="Query Parameters"
            description="Add, edit, disable, or remove query parameters. Enabled rows are reflected in the request URL automatically."
            rows={activeTab.request.params}
            emptyMessage="No query parameters yet"
            keyPlaceholder="page"
            valuePlaceholder="1"
            importButtonLabel={
              hasQueryParams(activeTab.request.url)
                ? 'Import from URL'
                : 'No URL Params'
            }
            onAddRow={handleAddParam}
            onUpdateRow={handleUpdateParam}
            onRemoveRow={handleRemoveParam}
            onClearRows={handleClearParams}
            onImportFromUrl={
              hasQueryParams(activeTab.request.url)
                ? handleImportParamsFromUrl
                : undefined
            }
          />
        )}

        {selectedTab === 'headers' && (
          <KeyValueEditor
            title="Headers"
            description="Add, edit, disable, or remove request headers. Enabled rows will be applied when sending the request."
            rows={activeTab.request.headers}
            emptyMessage="No headers yet"
            keyPlaceholder="Content-Type"
            valuePlaceholder="application/json"
            onAddRow={handleAddHeader}
            onUpdateRow={handleUpdateHeader}
            onRemoveRow={handleRemoveHeader}
            onClearRows={handleClearHeaders}
          />
        )}

        {selectedTab === 'body' && (
          <div className="body-editor-section">
            <div className="subsection-header">
              <div>
                <h3>Request Body</h3>
                <p>Raw and JSON body input is prepared for later sending.</p>
              </div>

              <label className="inline-field">
                <span>Mode</span>
                <select
                  value={activeTab.request.bodyMode}
                  onChange={handleBodyModeChange}
                >
                  <option value="json">JSON</option>
                  <option value="raw">Raw</option>
                </select>
              </label>
            </div>

            <textarea
              value={activeTab.request.body}
              placeholder={
                activeTab.request.bodyMode === 'json'
                  ? '{\n  "name": "John Doe"\n}'
                  : 'Write raw request body here...'
              }
              onChange={handleBodyChange}
            />
          </div>
        )}
      </div>
    </section>
  );
}