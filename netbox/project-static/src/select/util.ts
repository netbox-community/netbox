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
