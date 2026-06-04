import type { ChangeEvent } from 'react';
import { HTTP_METHODS } from '../../constants/http';
import { useAppState } from '../../store/AppContext';
import type { ApiTab, HttpMethod } from '../../types/apiClient';

interface RequestLineProps {
  activeTab: ApiTab;
}

export function RequestLine({ activeTab }: RequestLineProps) {
  const { dispatch } = useAppState();

  function handleMethodChange(event: ChangeEvent<HTMLSelectElement>) {
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
    dispatch({
      type: 'UPDATE_ACTIVE_REQUEST',
      payload: {
        changes: {
          url: event.target.value
        }
      }
    });
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
      </label>

      <button
        type="button"
        className="primary-button"
        disabled
        title="Request sending will be implemented in a later phase."
      >
        Send
      </button>

      <button
        type="button"
        onClick={() => dispatch({ type: 'RESET_ACTIVE_REQUEST' })}
      >
        Clear
      </button>
    </section>
  );
}