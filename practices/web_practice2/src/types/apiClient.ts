export type HttpMethod = 'GET' | 'POST' | 'PUT' | 'PATCH' | 'DELETE';

export type BodyMode = 'raw' | 'json';

export type ThemeMode = 'light' | 'dark';

export type RequestErrorType =
  | 'validation'
  | 'network'
  | 'timeout'
  | 'server'
  | 'unknown';

export type RequestErrorField =
  | 'url'
  | 'params'
  | 'headers'
  | 'body'
  | 'request';

export interface KeyValuePair {
  id: string;
  key: string;
  value: string;
  enabled: boolean;
}

export interface RequestConfig {
  method: HttpMethod;
  url: string;
  params: KeyValuePair[];
  headers: KeyValuePair[];
  body: string;
  bodyMode: BodyMode;
}

export interface ResponseHeader {
  key: string;
  value: string;
}

export interface ResponseData {
  status: number;
  statusText: string;
  body: string;
  headers: ResponseHeader[];
  durationMs: number;
  receivedAt: string;
}

export interface RequestError {
  type: RequestErrorType;
  field?: RequestErrorField;
  message: string;
  details?: string;
}

export interface ApiTab {
  id: string;
  title: string;
  request: RequestConfig;
  response: ResponseData | null;
  error: RequestError | null;
  isLoading: boolean;
}

export interface HistoryItem {
  id: string;
  request: RequestConfig;
  responseStatus: number | null;
  createdAt: string;
}

export interface SavedRequest {
  id: string;
  name: string;
  request: RequestConfig;
  createdAt: string;
  updatedAt: string;
}

export interface Collection {
  id: string;
  name: string;
  requests: SavedRequest[];
  createdAt: string;
  updatedAt: string;
}

export interface AppState {
  version: number;
  tabs: ApiTab[];
  activeTabId: string;
  history: HistoryItem[];
  collections: Collection[];
  theme: ThemeMode;
}