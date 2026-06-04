export function createId(prefix = 'id'): string {
  // Use browser UUID when available.
  if (typeof crypto !== 'undefined' && 'randomUUID' in crypto) {
    return `${prefix}-${crypto.randomUUID()}`;
  }

  // Fallback for older browsers.
  return `${prefix}-${Date.now()}-${Math.random().toString(16).slice(2)}`;
}