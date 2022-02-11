import { getElements, isTruthy } from './util';
import { initButtons } from './buttons';

function initDepedencies(): void {
  for (const init of [initButtons]) {
    init();
  }
}

/**
 * Hook into HTMX's event system to reinitialize specific native event listeners when HTMX swaps
 * elements.
 */
export function initHtmx(): void {
  for (const element of getElements('[hx-target]')) {
    const targetSelector = element.getAttribute('hx-target');
    if (isTruthy(targetSelector)) {
      for (const target of getElements(targetSelector)) {
        target.addEventListener('htmx:afterSettle', initDepedencies);
      }
    }
  }
}
