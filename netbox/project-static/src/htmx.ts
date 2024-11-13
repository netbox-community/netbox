import { initButtons } from './buttons';
import { initClipboard } from './clipboard'
import { initSelects } from './select';
import { initObjectSelector } from './objectSelector';
import { initBootstrap } from './bs';
import { initMessages } from './messages';
import { initQuickAdd } from './quickAdd';

function initDepedencies(): void {
  initButtons();
  initClipboard();
  initSelects();
  initObjectSelector();
  initQuickAdd();
  initBootstrap();
  initMessages();
}

/**
 * Hook into HTMX's event system to reinitialize specific native event listeners when HTMX swaps
 * elements.
 */
export function initHtmx(): void {
  document.addEventListener('htmx:afterSettle', initDepedencies);
}
