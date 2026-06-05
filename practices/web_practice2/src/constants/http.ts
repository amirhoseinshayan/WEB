import type { HttpMethod } from '../types/apiClient';

export const HTTP_METHODS: HttpMethod[] = [
  'GET',
  'POST',
  'PUT',
  'PATCH',
  'DELETE'
];

export const DEFAULT_HTTP_METHOD: HttpMethod = 'GET';

export const STORAGE_VERSION = 1;

export const HTTP_REQUEST_TIMEOUT_MS = 30000;