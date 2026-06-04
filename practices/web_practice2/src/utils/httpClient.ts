import type {
  RequestConfig,
  RequestError,
  ResponseData,
  ResponseHeader
} from '../types/apiClient';
import { buildHeadersObject, hasHeader } from './requestHeaders';
import { methodSupportsRequestBody } from './requestBody';

function extractResponseHeaders(headers: Headers): ResponseHeader[] {
  const result: ResponseHeader[] = [];

  // Convert browser Headers into our app-friendly structure.
  headers.forEach((value, key) => {
    result.push({
      key,
      value
    });
  });

  return result;
}

async function readResponseBody(response: Response): Promise<string> {
  const contentType = response.headers.get('content-type') ?? '';
  const rawText = await response.text();

  if (!rawText.trim()) {
    return '';
  }

  if (contentType.toLowerCase().includes('application/json')) {
    try {
      return JSON.stringify(JSON.parse(rawText), null, 2);
    } catch {
      return rawText;
    }
  }

  return rawText;
}

function createRequestInit(request: RequestConfig): RequestInit {
  const headers = buildHeadersObject(request.headers);
  const shouldSendBody =
    methodSupportsRequestBody(request.method) && request.body.trim() !== '';

  if (
    shouldSendBody &&
    request.bodyMode === 'json' &&
    !hasHeader(request.headers, 'Content-Type')
  ) {
    headers['Content-Type'] = 'application/json';
  }

  return {
    method: request.method,
    headers,
    body: shouldSendBody ? request.body : undefined
  };
}

export async function sendHttpRequest(
  request: RequestConfig
): Promise<ResponseData> {
  const startedAt = performance.now();
  const response = await fetch(request.url.trim(), createRequestInit(request));
  const body = await readResponseBody(response);
  const finishedAt = performance.now();

  return {
    status: response.status,
    statusText: response.statusText,
    body,
    headers: extractResponseHeaders(response.headers),
    durationMs: Math.round(finishedAt - startedAt),
    receivedAt: new Date().toISOString()
  };
}

export function normalizeFetchError(error: unknown): RequestError {
  if (error instanceof TypeError) {
    return {
      type: 'network',
      field: 'request',
      message: 'Network request failed.',
      details:
        'The server may be unreachable, the browser may have blocked the request, or CORS may not allow this request.'
    };
  }

  if (error instanceof Error) {
    return {
      type: 'unknown',
      field: 'request',
      message: 'Request failed.',
      details: error.message
    };
  }

  return {
    type: 'unknown',
    field: 'request',
    message: 'Request failed.',
    details: 'An unknown error occurred while sending the request.'
  };
}