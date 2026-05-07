// Only target selection-driven sticky bars; 'always' bars are pure CSS
const stickyActionsSelector = '.sticky-actions[data-sticky-position][data-sticky-when="selection"]';
const selectionInputSelector = [
  'input[type="checkbox"][name="pk"]',
  'table tr th > input[type="checkbox"].toggle',
  '#select-all',
].join(', ');
const checkedSelectionSelector = [
  'input[type="checkbox"][name="pk"]:checked',
  'table tr th > input[type="checkbox"].toggle:checked',
  '#select-all:checked',
].join(', ');
const selectionControlSelector = [
  '.bulk-action-buttons .btn',
  '.bulk-action-buttons input:not([type="hidden"])',
  '.bulk-action-buttons select',
  '.bulk-action-buttons textarea',
].join(', ');

// Module-scoped guard: assumes this module is loaded exactly once per page.
let listenersBound = false;

/**
 * Determine whether a sticky action group has an active selection in scope.
 */
function hasSelection(scope: ParentNode): boolean {
  return scope.querySelector<HTMLInputElement>(checkedSelectionSelector) !== null;
}

/**
 * Enable or disable controls that require a selection.
 */
function setSelectionControlsDisabled(stickyActions: HTMLElement, disabled: boolean): void {
  for (const control of stickyActions.querySelectorAll(selectionControlSelector)) {
    if (
      control instanceof HTMLButtonElement ||
      control instanceof HTMLInputElement ||
      control instanceof HTMLSelectElement ||
      control instanceof HTMLTextAreaElement
    ) {
      control.disabled = disabled;
    } else if (control instanceof HTMLAnchorElement) {
      control.classList.toggle('disabled', disabled);
      control.setAttribute('aria-disabled', String(disabled));

      if (disabled) {
        control.tabIndex = -1;
      } else {
        control.removeAttribute('tabindex');
      }
    }
  }
}

/**
 * Update the state of a sticky action group.
 */
function updateStickyActions(stickyActions: HTMLElement): void {
  const scope = stickyActions.closest('form') ?? document;
  const isActive = hasSelection(scope);

  stickyActions.classList.toggle('is-sticky-active', isActive);
  setSelectionControlsDisabled(stickyActions, !isActive);
}

/**
 * Update all sticky action groups on the page.
 */
function syncStickyActions(): void {
  for (const stickyActions of document.querySelectorAll<HTMLElement>(stickyActionsSelector)) {
    updateStickyActions(stickyActions);
  }
}

/**
 * Initialize sticky action groups.
 */
export function initFloatBulk(): void {
  if (!listenersBound) {
    document.addEventListener('change', (event: Event) => {
      const target = event.target;
      if (target instanceof HTMLInputElement && target.matches(selectionInputSelector)) {
        syncStickyActions();
      }
    });

    for (const eventName of ['htmx:afterSwap', 'htmx:oobAfterSwap']) {
      document.body.addEventListener(eventName, syncStickyActions);
    }

    listenersBound = true;
  }

  syncStickyActions();
}
