import { DEFAULT_HTTP_METHOD, STORAGE_VERSION } from './http';
import type {
  ApiTab,
  AppState,
  KeyValuePair,
  RequestConfig
} from '../types/apiClient';
import { createId } from '../utils/id';

export function createEmptyKeyValuePair(): KeyValuePair {
  return {
    id: createId('kv'),
    key: '',
    value: '',
    enabled: true
  };
}

export function createDefaultRequestConfig(): RequestConfig {
  return {
    method: DEFAULT_HTTP_METHOD,
    url: '',
    params: [],
    headers: [],
    body: '',
    bodyMode: 'json'
  };
}

export function createDefaultTab(title = 'Request 1'): ApiTab {
  return {
    id: createId('tab'),
    title,
    request: createDefaultRequestConfig(),
    response: null,
    error: null,
    isLoading: false
  };
}

export function createInitialAppState(): AppState {
  const firstTab = createDefaultTab('Request 1');

  return {
    version: STORAGE_VERSION,
    tabs: [firstTab],
    activeTabId: firstTab.id,
    history: [],
    collections: [],
    theme: 'light',
    notifications: []
  };
}