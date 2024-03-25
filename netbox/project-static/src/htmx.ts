import { initButtons } from './buttons';
import { initClipboard } from './clipboard'
import { initSelects } from './select';
import { initObjectSelector } from './objectSelector';
import { initBootstrap } from './bs';
import { initMessages } from './messages';

function initDepedencies(): void {
  for (const init of [initButtons, initClipboard, initSelects, initObjectSelector, initBootstrap, initMessages]) {
    init();
  }
}

/**
 * Hook into HTMX's event system to reinitialize specific native event listeners when HTMX swaps
 * elements.
 */
export function initHtmx(): void {
  document.addEventListener('htmx:afterSettle', initDepedencies);
}
