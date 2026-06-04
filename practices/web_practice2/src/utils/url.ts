import type { RequestError } from '../types/apiClient';

export interface UrlValidationResult {
  isValid: boolean;
  normalizedUrl: string;
  error: RequestError | null;
}

export function validateRequestUrl(url: string): UrlValidationResult {
  const trimmedUrl = url.trim();

  if (!trimmedUrl) {
    return {
      isValid: false,
      normalizedUrl: '',
      error: {
        type: 'validation',
        message: 'Request URL is required.',
        details: 'Please enter a URL that starts with http:// or https://.'
      }
    };
  }

  if (!/^https?:\/\//i.test(trimmedUrl)) {
    return {
      isValid: false,
      normalizedUrl: trimmedUrl,
      error: {
        type: 'validation',
        message: 'Invalid URL protocol.',
        details: 'The URL must start with http:// or https://.'
      }
    };
  }

  try {
    const parsedUrl = new URL(trimmedUrl);

    if (parsedUrl.protocol !== 'http:' && parsedUrl.protocol !== 'https:') {
      return {
        isValid: false,
        normalizedUrl: trimmedUrl,
        error: {
          type: 'validation',
          message: 'Unsupported URL protocol.',
          details: 'Only HTTP and HTTPS URLs are supported.'
        }
      };
    }

    if (!parsedUrl.hostname) {
      return {
        isValid: false,
        normalizedUrl: trimmedUrl,
        error: {
          type: 'validation',
          message: 'Invalid URL host.',
          details: 'Please enter a valid host name.'
        }
      };
    }

    return {
      isValid: true,
      normalizedUrl: trimmedUrl,
      error: null
    };
  } catch {
    return {
      isValid: false,
      normalizedUrl: trimmedUrl,
      error: {
        type: 'validation',
        message: 'Invalid URL format.',
        details: 'Please enter a complete and valid HTTP or HTTPS URL.'
      }
    };
  }
}