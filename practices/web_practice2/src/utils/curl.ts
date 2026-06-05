import type { RequestConfig } from '../types/apiClient';
import { buildHeadersObject } from './requestHeaders';
import { methodSupportsRequestBody } from './requestBody';

function quoteForShell(value: string): string {
  return `"${value
    .replace(/\\/g, '\\\\')
    .replace(/"/g, '\\"')
    .replace(/\r?\n/g, '\\n')}"`;
}

export function generateCurlCommand(request: RequestConfig): string {
  const url = request.url.trim() || 'https://api.example.com';
  const headers = buildHeadersObject(request.headers);
  const shouldSendBody =
    methodSupportsRequestBody(request.method) && request.body.trim() !== '';

  const commandParts: string[] = [
    `curl -X ${request.method} ${quoteForShell(url)}`
  ];

  Object.entries(headers).forEach(([key, value]) => {
    commandParts.push(`-H ${quoteForShell(`${key}: ${value}`)}`);
  });

  if (shouldSendBody) {
    commandParts.push(`--data ${quoteForShell(request.body)}`);
  }

  if (commandParts.length === 1) {
    return commandParts[0];
  }

  return commandParts
    .map((part, index) => (index === 0 ? part : `  ${part}`))
    .join(' \\\n');
}