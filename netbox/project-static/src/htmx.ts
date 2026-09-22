import { initForms } from './forms';
import { initButtons } from './buttons';
import { initClipboard } from './clipboard';
import { initSelects } from './select';
import { initObjectSelector } from './objectSelector';
import { initBootstrap } from './bs';
import { initMessages } from './messages';
import { initQuickAdd } from './quickAdd';
import { focusFirstFormError } from './forms/errors';

type HtmxSettleDetail = {
  elt?: Element;
  target?: Element;
  requestConfig?: {
    verb?: string;
    triggeringEvent?: Event;
  };
};

function initDepedencies(): void {
  initButtons();
  initClipboard();
  initForms();
  initSelects();
  initObjectSelector();
  initQuickAdd();
  initBootstrap();
  initMessages();
}

/**
 * Reveal validation errors only for a swapped-in form submission, scoped to the swapped content.
 * Dependent-field refreshes post on `change` and re-render a bound form, so gating on the verb
 * alone would drag focus away from the field the user is editing.
 */
function revealSubmissionErrors(event: Event): void {
  const { detail } = event as CustomEvent<HtmxSettleDetail>;
  const trigger = detail?.requestConfig?.triggeringEvent?.type;
  const verb = detail?.requestConfig?.verb;

  if (trigger !== 'submit' || verb === 'get') return;

  // An outerHTML swap detaches the original target, so fall back to the settled element.
  const root = detail.target?.isConnected ? detail.target : detail.elt;
  if (root?.isConnected) {
    focusFirstFormError(root);
  }
}

/**
 * Hook into HTMX's event system to reinitialize specific native event listeners when HTMX swaps
 * elements.
 */
export function initHtmx(): void {
  document.addEventListener('htmx:afterSettle', event => {
    initDepedencies();
    revealSubmissionErrors(event);
  });
}
