import { DEFAULT_HTTP_METHOD } from '../constants/http';
import type { ApiTab, RequestConfig } from '../types/apiClient';

export function isRequestConfigEmpty(request: RequestConfig): boolean {
  return (
    request.method === DEFAULT_HTTP_METHOD &&
    request.url.trim() === '' &&
    request.params.length === 0 &&
    request.headers.length === 0 &&
    request.body.trim() === '' &&
    request.bodyMode === 'json'
  );
}

export function hasRuntimeTabData(tab: ApiTab): boolean {
  return Boolean(tab.response || tab.error || tab.isLoading);
}

export function shouldConfirmClearRequest(tab: ApiTab): boolean {
  return !isRequestConfigEmpty(tab.request) || hasRuntimeTabData(tab);
}