import { initForms } from './forms';
import { initButtons } from './buttons';
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
 * Dispatch `netbox:search-input` on an input once its value reaches the length in
 * `data-search-min-length`. The input's `hx-trigger` listens for this event instead of using a
 * `keyup[...]` filter, which htmx compiles with runtime eval.
 */
function dispatchSearchInput(event: KeyboardEvent): void {
  const input = event.target;
  if (!(input instanceof HTMLInputElement)) return;
  const rawMinLength = input.dataset.searchMinLength;
  if (!rawMinLength) return;
  const minLength = Number(rawMinLength);
  if (Number.isNaN(minLength)) return;
  if (input.value.length >= minLength) {
    input.dispatchEvent(new CustomEvent('netbox:search-input', { bubbles: true }));
  }
}

/**
 * Blank the request parameter named by `data-htmx-clear-param` on the requesting element. The
 * generic object selector uses this so a stale object ID can't cross content types. It replaces
 * an `hx-on::config-request` attribute, which htmx evaluates at runtime.
 */
function clearConfiguredParam(event: HTMLElementEventMap['htmx:configRequest']): void {
  const { elt, parameters } = event.detail;
  const param = elt.getAttribute('data-htmx-clear-param');
  if (param) {
    parameters[param] = '';
  }
}

/**
 * Hook into HTMX's event system to reinitialize specific native event listeners when HTMX swaps
 * elements.
 */
export function initHtmx(): void {
  // htmx.config.allowEval stays at its default: a CSP without 'unsafe-eval' already blocks eval,
  // and disabling it would break plugins that use hx-on or trigger filters. See #23503.
  document.addEventListener('keyup', dispatchSearchInput);
  document.addEventListener('htmx:configRequest', clearConfiguredParam);

  document.addEventListener('htmx:afterSettle', event => {
    initDepedencies();
    revealSubmissionErrors(event);
  });
}
