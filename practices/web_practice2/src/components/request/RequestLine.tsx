import { useEffect, useState, type ChangeEvent } from 'react';
import { HTTP_METHODS } from '../../constants/http';
import { useAppState } from '../../store/AppContext';
import type { ApiTab, HttpMethod } from '../../types/apiClient';
import { validateRequestBody } from '../../utils/requestBody';
import { validateRequestUrl } from '../../utils/url';

interface RequestLineProps {
  activeTab: ApiTab;
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

  function handleValidateRequest() {
    const urlResult = validateRequestUrl(activeTab.request.url);

    if (!urlResult.isValid) {
      setValidationMessage(null);

      dispatch({
        type: 'SET_ACTIVE_ERROR',
        payload: {
          error: urlResult.error
        }
      });

      return;
    }

    const bodyError = validateRequestBody(
      activeTab.request.method,
      activeTab.request.bodyMode
    );

    if (bodyError) {
      setValidationMessage(null);

      dispatch({
        type: 'SET_ACTIVE_ERROR',
        payload: {
          error: bodyError
        }
      });

      return;
    }

    dispatch({
      type: 'CLEAR_ACTIVE_ERROR'
    });

    setValidationMessage(
      'Request configuration looks valid. HTTP sending will be implemented in the next phase.'
    );
  }

  function handleClearRequest() {
    setValidationMessage(null);
    dispatch({ type: 'RESET_ACTIVE_REQUEST' });
  }

  return (
    <section className="request-line panel-card">
      <label className="field-group method-field">
        <span>Method</span>

        <select value={activeTab.request.method} onChange={handleMethodChange}>
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
        title="This phase validates the request configuration. HTTP sending comes later."
        onClick={handleValidateRequest}
      >
        Send
      </button>

      <button type="button" onClick={handleClearRequest}>
        Clear
      </button>
    </section>
  );
}