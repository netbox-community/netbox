import { initForms } from './forms';
import { initButtons } from './buttons';
import { initClipboard } from './clipboard';
import { initSelects } from './select';
import { initObjectSelector } from './objectSelector';
import { initBootstrap } from './bs';
import { initMessages } from './messages';
import { initQuickAdd } from './quickAdd';
import { focusFirstFormError } from './forms/errors';

type HtmxConfigRequestDetail = {
  elt: Element;
  verb: string;
  formData: FormData;
};

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
 * On an object edit form refresh (see HTMXSelect), send each cleared multiple select as an empty
 * value, so the server does not render its saved selection again.
 */
function includeClearedMultipleSelects(event: Event): void {
  const { elt, verb, formData } = (event as CustomEvent<HtmxConfigRequestDetail>).detail;
  const include = elt.getAttribute('hx-include');
  if (verb !== 'get' || !include?.startsWith('#') || !elt.closest('form.object-edit')) return;

  // htmx applies hx-params before this event, so leave filtered requests as they are
  const params = elt.closest('[hx-params], [data-hx-params]');
  const filter = params?.getAttribute('hx-params') ?? params?.getAttribute('data-hx-params');
  if (params && filter !== '*') return;

  const container = document.getElementById(include.slice(1));
  const selects = container?.querySelectorAll<HTMLSelectElement>('select[multiple]');
  for (const select of selects ?? []) {
    const empty = !select.selectedOptions.length;
    if (select.name && empty && !select.matches(':disabled') && !formData.has(select.name)) {
      formData.append(select.name, '');
    }
  }
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
 * Hook into HTMX's event system to complete object edit form refreshes, and to reinitialize specific
 * native event listeners when HTMX swaps elements.
 */
export function initHtmx(): void {
  document.addEventListener('htmx:configRequest', includeClearedMultipleSelects);
  document.addEventListener('htmx:afterSettle', event => {
    initDepedencies();
    revealSubmissionErrors(event);
  });
}
