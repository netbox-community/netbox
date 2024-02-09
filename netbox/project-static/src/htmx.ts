import { getElements, isTruthy } from './util';
import { initButtons } from './buttons';
import { initSelects } from './select';
import { initObjectSelector } from './objectSelector';
import { initBootstrap } from './bs';

function initDepedencies(): void {
  for (const init of [initButtons, initSelects, initObjectSelector, initBootstrap]) {
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

  for (const element of getElements('[hx-trigger=load]')) {
    element.addEventListener('htmx:afterSettle', initDepedencies);
  }
}
