import type { Trigger } from './api';

/**
 * Determine if an element has the `data-url` attribute set.
 */
export function hasUrl(el: HTMLSelectElement): el is HTMLSelectElement & { 'data-url': string } {
  const value = el.getAttribute('data-url');
  return typeof value === 'string' && value !== '';
}

/**
 * Determine if an element has the `data-query-param-exclude` attribute set.
 */
export function hasExclusions(
  el: HTMLSelectElement,
): el is HTMLSelectElement & { 'data-query-param-exclude': string } {
  const exclude = el.getAttribute('data-query-param-exclude');
  return typeof exclude === 'string' && exclude !== '';
}

/**
 * Determine if a trigger value is valid.
 */
export function isTrigger(value: unknown): value is Trigger {
  return typeof value === 'string' && ['load', 'open', 'collapse'].includes(value);
}
