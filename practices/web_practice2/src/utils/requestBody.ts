import type { BodyMode, HttpMethod, RequestError } from '../types/apiClient';

const METHODS_WITH_BODY: HttpMethod[] = ['POST', 'PUT', 'PATCH'];

export function methodSupportsRequestBody(method: HttpMethod): boolean {
  return METHODS_WITH_BODY.includes(method);
}

export function getBodyUsageMessage(method: HttpMethod): string {
  if (methodSupportsRequestBody(method)) {
    return `${method} requests can include a request body.`;
  }

  return `${method} requests usually do not include a request body. The body will be kept in the editor, but it may not be sent later.`;
}

export function validateJsonBody(body: string): RequestError | null {
  const trimmedBody = body.trim();

  if (!trimmedBody) {
    return null;
  }

  try {
    JSON.parse(trimmedBody);
    return null;
  } catch {
    return {
      type: 'validation',
      field: 'body',
      message: 'Invalid JSON body.',
      details: 'Please enter valid JSON or switch the body mode to Raw.'
    };
  }
}

export function validateRequestBody(
  body: string,
  bodyMode: BodyMode
): RequestError | null {
  const trimmedBody = body.trim();

  if (!trimmedBody) {
    return null;
  }

  if (bodyMode === 'json') {
    return validateJsonBody(trimmedBody);
  }

  // Raw body does not need JSON validation.
  return null;
}

export function formatJsonBody(body: string): {
  formattedBody: string | null;
  error: RequestError | null;
} {
  const trimmedBody = body.trim();

  if (!trimmedBody) {
    return {
      formattedBody: '',
      error: null
    };
  }

  try {
    const parsedBody = JSON.parse(trimmedBody);

    return {
      formattedBody: JSON.stringify(parsedBody, null, 2),
      error: null
    };
  } catch {
    return {
      formattedBody: null,
      error: {
        type: 'validation',
        field: 'body',
        message: 'Cannot format invalid JSON.',
        details: 'Fix the JSON syntax first, then try formatting again.'
      }
    };
  }
}