import type { KeyValuePair } from '../types/apiClient';
import { createId } from './id';

function splitUrlParts(url: string): {
  baseUrl: string;
  hashPart: string;
} {
  const hashIndex = url.indexOf('#');

  if (hashIndex === -1) {
    return {
      baseUrl: url,
      hashPart: ''
    };
  }

  return {
    baseUrl: url.slice(0, hashIndex),
    hashPart: url.slice(hashIndex)
  };
}

function convertSearchParamsToRows(searchParams: URLSearchParams): KeyValuePair[] {
  const rows: KeyValuePair[] = [];

  // Use forEach instead of entries for better TypeScript compatibility.
  searchParams.forEach((value, key) => {
    rows.push({
      id: createId('kv'),
      key,
      value,
      enabled: true
    });
  });

  return rows;
}

export function getEnabledQueryParams(params: KeyValuePair[]): KeyValuePair[] {
  return params.filter((param) => param.enabled && param.key.trim() !== '');
}

export function buildUrlWithQueryParams(
  currentUrl: string,
  params: KeyValuePair[]
): string {
  const trimmedUrl = currentUrl.trim();

  if (!trimmedUrl) {
    return currentUrl;
  }

  const { baseUrl, hashPart } = splitUrlParts(trimmedUrl);
  const queryStartIndex = baseUrl.indexOf('?');
  const urlWithoutQuery =
    queryStartIndex === -1 ? baseUrl : baseUrl.slice(0, queryStartIndex);

  const searchParams = new URLSearchParams();

  getEnabledQueryParams(params).forEach((param) => {
    searchParams.append(param.key.trim(), param.value);
  });

  const queryString = searchParams.toString();

  return `${urlWithoutQuery}${queryString ? `?${queryString}` : ''}${hashPart}`;
}

export function extractQueryParamsFromUrl(url: string): KeyValuePair[] {
  const trimmedUrl = url.trim();

  if (!trimmedUrl || !trimmedUrl.includes('?')) {
    return [];
  }

  try {
    const parsedUrl = new URL(trimmedUrl);

    return convertSearchParamsToRows(parsedUrl.searchParams);
  } catch {
    const queryStartIndex = trimmedUrl.indexOf('?');
    const hashStartIndex = trimmedUrl.indexOf('#');
    const queryEndIndex =
      hashStartIndex === -1 ? trimmedUrl.length : hashStartIndex;

    const rawQuery = trimmedUrl.slice(queryStartIndex + 1, queryEndIndex);
    const searchParams = new URLSearchParams(rawQuery);

    return convertSearchParamsToRows(searchParams);
  }
}

export function hasQueryParams(url: string): boolean {
  return extractQueryParamsFromUrl(url).length > 0;
}