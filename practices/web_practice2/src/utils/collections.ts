import type {
  BodyMode,
  Collection,
  HttpMethod,
  KeyValuePair,
  RequestConfig,
  SavedRequest
} from '../types/apiClient';
import { createId } from './id';

const HTTP_METHODS: HttpMethod[] = ['GET', 'POST', 'PUT', 'PATCH', 'DELETE'];
const BODY_MODES: BodyMode[] = ['raw', 'json'];

interface ImportResult {
  collections: Collection[];
  error: string | null;
}

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === 'object' && value !== null && !Array.isArray(value);
}

function isHttpMethod(value: unknown): value is HttpMethod {
  return typeof value === 'string' && HTTP_METHODS.includes(value as HttpMethod);
}

function isBodyMode(value: unknown): value is BodyMode {
  return typeof value === 'string' && BODY_MODES.includes(value as BodyMode);
}

function getString(value: unknown, fallback = ''): string {
  return typeof value === 'string' ? value : fallback;
}

function getDateString(value: unknown): string {
  const rawValue = getString(value);

  if (!rawValue) {
    return new Date().toISOString();
  }

  const date = new Date(rawValue);

  if (Number.isNaN(date.getTime())) {
    return new Date().toISOString();
  }

  return date.toISOString();
}

function normalizeKeyValuePair(value: unknown): KeyValuePair | null {
  if (!isRecord(value)) {
    return null;
  }

  return {
    id: createId('kv'),
    key: getString(value.key),
    value: getString(value.value),
    enabled: typeof value.enabled === 'boolean' ? value.enabled : true
  };
}

function normalizeKeyValueList(value: unknown): KeyValuePair[] {
  if (!Array.isArray(value)) {
    return [];
  }

  return value
    .map((item) => normalizeKeyValuePair(item))
    .filter((item): item is KeyValuePair => item !== null);
}

function normalizeRequestConfig(value: unknown): RequestConfig | null {
  if (!isRecord(value)) {
    return null;
  }

  return {
    method: isHttpMethod(value.method) ? value.method : 'GET',
    url: getString(value.url),
    params: normalizeKeyValueList(value.params),
    headers: normalizeKeyValueList(value.headers),
    body: getString(value.body),
    bodyMode: isBodyMode(value.bodyMode) ? value.bodyMode : 'json'
  };
}

function createFallbackRequestName(request: RequestConfig): string {
  const url = request.url.trim();

  if (!url) {
    return `${request.method} Untitled Request`;
  }

  return `${request.method} ${url.length > 60 ? `${url.slice(0, 57)}...` : url}`;
}

function normalizeSavedRequest(value: unknown): SavedRequest | null {
  if (!isRecord(value)) {
    return null;
  }

  const request = normalizeRequestConfig(value.request);

  if (!request) {
    return null;
  }

  const now = new Date().toISOString();

  return {
    id: createId('saved-request'),
    name: getString(value.name, createFallbackRequestName(request)),
    request,
    createdAt: getDateString(value.createdAt) || now,
    updatedAt: getDateString(value.updatedAt) || now
  };
}

function normalizeSavedRequestList(value: unknown): SavedRequest[] {
  if (!Array.isArray(value)) {
    return [];
  }

  return value
    .map((item) => normalizeSavedRequest(item))
    .filter((item): item is SavedRequest => item !== null);
}

function normalizeCollection(value: unknown): Collection | null {
  if (!isRecord(value)) {
    return null;
  }

  const now = new Date().toISOString();

  return {
    id: createId('collection'),
    name: getString(value.name, 'Imported Collection'),
    requests: normalizeSavedRequestList(value.requests),
    createdAt: getDateString(value.createdAt) || now,
    updatedAt: now
  };
}

function extractRawCollections(parsedValue: unknown): unknown[] | null {
  if (Array.isArray(parsedValue)) {
    return parsedValue;
  }

  if (!isRecord(parsedValue)) {
    return null;
  }

  if (Array.isArray(parsedValue.collections)) {
    return parsedValue.collections;
  }

  if ('name' in parsedValue && 'requests' in parsedValue) {
    return [parsedValue];
  }

  return null;
}

export function parseCollectionsJson(text: string): ImportResult {
  try {
    const parsedValue = JSON.parse(text) as unknown;
    const rawCollections = extractRawCollections(parsedValue);

    if (!rawCollections) {
      return {
        collections: [],
        error:
          'Invalid JSON structure. Expected a collection object, an array of collections, or an object with a collections array.'
      };
    }

    const collections = rawCollections
      .map((item) => normalizeCollection(item))
      .filter((item): item is Collection => item !== null);

    if (collections.length === 0) {
      return {
        collections: [],
        error: 'No valid collections were found in this file.'
      };
    }

    return {
      collections,
      error: null
    };
  } catch {
    return {
      collections: [],
      error: 'Invalid JSON file. Please choose a valid JSON export file.'
    };
  }
}

function safeFileName(value: string): string {
  const cleanedValue = value
    .trim()
    .toLowerCase()
    .replace(/[^a-z0-9-_]+/g, '-')
    .replace(/-+/g, '-')
    .replace(/^-|-$/g, '');

  return cleanedValue || 'collection';
}

export function createCollectionsExportPayload(collections: Collection[]) {
  return {
    version: 1,
    exportedAt: new Date().toISOString(),
    collections
  };
}

export function getCollectionExportFileName(collection: Collection): string {
  return `${safeFileName(collection.name)}.collection.json`;
}

export function getAllCollectionsExportFileName(): string {
  return 'api-client-collections.json';
}

export function downloadJsonFile(fileName: string, data: unknown): void {
  const json = JSON.stringify(data, null, 2);
  const blob = new Blob([json], {
    type: 'application/json'
  });
  const url = URL.createObjectURL(blob);
  const anchor = document.createElement('a');

  anchor.href = url;
  anchor.download = fileName;
  anchor.click();

  URL.revokeObjectURL(url);
}