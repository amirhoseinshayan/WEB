import type { KeyValuePair } from '../types/apiClient';

export function getEnabledHeaders(headers: KeyValuePair[]): KeyValuePair[] {
  return headers.filter((header) => header.enabled && header.key.trim() !== '');
}

export function buildHeadersObject(headers: KeyValuePair[]): Record<string, string> {
  return getEnabledHeaders(headers).reduce<Record<string, string>>(
    (result, header) => {
      // Trim header names, but keep values as the user entered them.
      result[header.key.trim()] = header.value;
      return result;
    },
    {}
  );
}

export function hasHeader(headers: KeyValuePair[], headerName: string): boolean {
  const normalizedHeaderName = headerName.trim().toLowerCase();

  return headers.some(
    (header) => header.key.trim().toLowerCase() === normalizedHeaderName
  );
}