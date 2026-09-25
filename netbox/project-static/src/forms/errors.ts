import type TomSelect from 'tom-select';

type TomSelectElement = HTMLSelectElement & { tomselect?: TomSelect };

const INVALID_SELECTOR = '[aria-invalid="true"]';
const CONTROL_SELECTOR = 'input:not([type="hidden"]), select, textarea';
// Matched by attribute because a control named "method" shadows the property.
const POST_FORM_SELECTOR = 'form[method="post" i]';

/**
 * Focus the control the server flagged. Tom Select hides the native <select> and overrides
 * focus(), so its instance owns focus for enhanced fields.
 */
function focusControl(element: HTMLElement): void {
  const instance = (element as TomSelectElement).tomselect;
  if (instance) {
    instance.focus();
    return;
  }

  // A disabled control still gets its row revealed, it just cannot take focus.
  if (element.matches(CONTROL_SELECTOR)) {
    const control = element as FormControls;
    if (!control.disabled) control.focus({ preventScroll: true });
    return;
  }

  // Grouped widgets (radios, checkbox lists) carry the attribute on their wrapper.
  for (const control of element.querySelectorAll<FormControls>(CONTROL_SELECTOR)) {
    if (!control.disabled) {
      control.focus({ preventScroll: true });
      return;
    }
  }
}

/**
 * Reveal the first field within `root` that the server marked invalid. Returns true once one
 * has been revealed.
 */
export function focusFirstFormError(root: ParentNode): boolean {
  for (const invalid of root.querySelectorAll<HTMLElement>(INVALID_SELECTOR)) {
    const row = invalid.closest<HTMLElement>('.row') ?? invalid;

    // A row in a collapsed tab pane or any display:none container has no box to reveal.
    if (row.getClientRects().length === 0) continue;

    focusControl(invalid);
    // Scroll last so it wins over the browser's own scroll-on-focus.
    row.scrollIntoView({ block: 'center', inline: 'nearest', behavior: 'instant' });
    return true;
  }

  return false;
}

/**
 * Reveal the first invalid field in a submitting form on the page. GET forms are skipped so a
 * rejected list filter cannot take focus away from the page content.
 */
export function focusFirstPageFormError(): boolean {
  for (const form of document.querySelectorAll<HTMLFormElement>(POST_FORM_SELECTOR)) {
    if (focusFirstFormError(form)) {
      return true;
    }
  }

  return false;
}
