import { isTruthy } from '../util';

/**
 * Handle saved filter change event.
 *
 * @param event "change" event for the saved filter select
 */
function handleSavedFilterChange(event: Event): void {
  const savedFilter = event.currentTarget as HTMLSelectElement;
  let baseUrl = savedFilter.baseURI.split('?')[0];
  const preFilter = '?';

  const selectedOptions = Array.from(savedFilter.options)
    .filter(option => option.selected)
    .map(option => `filter_id=${option.value}`)
    .join('&');

  baseUrl += `${preFilter}${selectedOptions}`;
  document.location.href = baseUrl;
}

export function initSavedFilterSelect(): void {
  const divResults = document.getElementById('results');
  if (isTruthy(divResults)) {
    const savedFilterSelect = document.getElementById('id_filter_id');
    if (isTruthy(savedFilterSelect)) {
      savedFilterSelect.addEventListener('change', handleSavedFilterChange);
    }
  }
}
