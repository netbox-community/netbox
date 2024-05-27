import { isTruthy } from './util';

/**
 * Initialize the applied filter display.
 *
 */
export function initAppliedFilter(): void {
  const appliedFilter = document.getElementById('appliedfilters');
  if (isTruthy(appliedFilter)) {
    const divResults = document.getElementById('results');
    if (isTruthy(divResults)) {
      const savedFilterSelect = divResults.getElementsByTagName('select')[0];
      if (savedFilterSelect.selectedOptions.length > 0) {
        appliedFilter.hidden = true;
      }
    }
  }
}
