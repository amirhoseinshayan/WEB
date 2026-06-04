import { useEffect, useState, type ChangeEvent } from 'react';
import { HTTP_METHODS } from '../../constants/http';
import { useAppState } from '../../store/AppContext';
import type {
  ApiTab,
  HistoryItem,
  HttpMethod,
  RequestConfig
} from '../../types/apiClient';
import { normalizeFetchError, sendHttpRequest } from '../../utils/httpClient';
import { createId } from '../../utils/id';
import { validateRequestBody } from '../../utils/requestBody';
import { validateRequestUrl } from '../../utils/url';

interface RequestLineProps {
  activeTab: ApiTab;
}

function cloneRequestForHistory(request: RequestConfig): RequestConfig {
  return {
    ...request,
    params: request.params.map((param) => ({ ...param })),
    headers: request.headers.map((header) => ({ ...header }))
  };
}

function createHistoryItem(
  request: RequestConfig,
  responseStatus: number | null
): HistoryItem {
  return {
    id: createId('history'),
    request: cloneRequestForHistory(request),
    responseStatus,
    createdAt: new Date().toISOString()
  };
}

export function RequestLine({ activeTab }: RequestLineProps) {
  const { dispatch } = useAppState();
  const [validationMessage, setValidationMessage] = useState<string | null>(
    null
  );

  const validationError =
    activeTab.error?.type === 'validation' &&
    (activeTab.error.field === 'url' || !activeTab.error.field)
      ? activeTab.error
      : null;

  useEffect(() => {
    // Reset local validation message when the active tab changes.
    setValidationMessage(null);
  }, [activeTab.id]);

  function handleMethodChange(event: ChangeEvent<HTMLSelectElement>) {
    setValidationMessage(null);

    dispatch({
      type: 'UPDATE_ACTIVE_REQUEST',
      payload: {
        changes: {
          method: event.target.value as HttpMethod
        }
      }
    });
  }

  function handleUrlChange(event: ChangeEvent<HTMLInputElement>) {
    setValidationMessage(null);

    dispatch({
      type: 'UPDATE_ACTIVE_REQUEST',
      payload: {
        changes: {
          url: event.target.value
        }
      }
    });
  }

  async function handleSendRequest() {
    const tabId = activeTab.id;
    const urlResult = validateRequestUrl(activeTab.request.url);

    if (!urlResult.isValid) {
      setValidationMessage(null);

      dispatch({
        type: 'SET_TAB_ERROR',
        payload: {
          tabId,
          error: urlResult.error
        }
      });

      return;
    }

    const bodyError = validateRequestBody(
      activeTab.request.body,
      activeTab.request.bodyMode
    );

    if (bodyError) {
      setValidationMessage(null);

      dispatch({
        type: 'SET_TAB_ERROR',
        payload: {
          tabId,
          error: bodyError
        }
      });

      return;
    }

    const requestToSend: RequestConfig = {
      ...activeTab.request,
      url: urlResult.normalizedUrl
    };

    setValidationMessage(null);

    dispatch({
      type: 'SET_TAB_LOADING',
      payload: {
        tabId,
        isLoading: true
      }
    });

    try {
      const response = await sendHttpRequest(requestToSend);

      dispatch({
        type: 'SET_TAB_RESPONSE',
        payload: {
          tabId,
          response
        }
      });

      dispatch({
        type: 'ADD_HISTORY_ITEM',
        payload: {
          item: createHistoryItem(requestToSend, response.status)
        }
      });

      setValidationMessage(
        `Response received: ${response.status} ${response.statusText}`
      );
    } catch (error) {
      dispatch({
        type: 'SET_TAB_ERROR',
        payload: {
          tabId,
          error: normalizeFetchError(error)
        }
      });

      dispatch({
        type: 'ADD_HISTORY_ITEM',
        payload: {
          item: createHistoryItem(requestToSend, null)
        }
      });
    }
  }

  function handleClearRequest() {
    setValidationMessage(null);
    dispatch({ type: 'RESET_ACTIVE_REQUEST' });
  }

  return (
    <section className="request-line panel-card">
      <label className="field-group method-field">
        <span>Method</span>

        <select
          value={activeTab.request.method}
          disabled={activeTab.isLoading}
          onChange={handleMethodChange}
        >
          {HTTP_METHODS.map((method) => (
            <option key={method} value={method}>
              {method}
            </option>
          ))}
        </select>
      </label>

      <label className="field-group url-field">
        <span>Request URL</span>

        <input
          type="url"
          value={activeTab.request.url}
          disabled={activeTab.isLoading}
          placeholder="https://api.example.com/users"
          onChange={handleUrlChange}
        />

        {validationError && (
          <p className="field-error">
            {validationError.message}
            {validationError.details && (
              <span> {validationError.details}</span>
            )}
          </p>
        )}

        {!validationError && validationMessage && (
          <p className="field-success">{validationMessage}</p>
        )}
      </label>

      <button
        type="button"
        className="primary-button"
        disabled={activeTab.isLoading}
        onClick={handleSendRequest}
      >
        {activeTab.isLoading ? 'Sending...' : 'Send'}
      </button>

      <button
        type="button"
        disabled={activeTab.isLoading}
        onClick={handleClearRequest}
      >
        Clear
      </button>
    </section>
  );
}