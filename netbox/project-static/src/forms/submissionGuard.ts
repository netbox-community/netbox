const GUARD_ATTRIBUTE = 'data-disable-on-submit';

// Forms with a guarded submission in flight, mapped to the buttons the guard marked.
const pendingForms = new Map<HTMLFormElement, HTMLButtonElement[]>();

/**
 * Dim the form's enabled submit buttons for handleSubmit(). Class and ARIA only, since `disabled`
 * drops the submitter and survives a Firefox reload.
 */
function markButtons(form: HTMLFormElement): HTMLButtonElement[] {
  const marked: HTMLButtonElement[] = [];
  for (const button of form.querySelectorAll<HTMLButtonElement>('button[type="submit"]')) {
    if (button.disabled || button.classList.contains('disabled')) continue;
    button.classList.add('disabled');
    button.setAttribute('aria-disabled', 'true');
    marked.push(button);
  }
  return marked;
}

/** Undo markButtons() for a form and drop its lock. Used on a late cancel and a cache restore. */
function release(form: HTMLFormElement): void {
  for (const button of pendingForms.get(form) ?? []) {
    button.classList.remove('disabled');
    button.removeAttribute('aria-disabled');
  }
  pendingForms.delete(form);
}

/** Delegated submit listener: lock an opted-in form and cancel its repeat submits while locked. */
function handleSubmit(event: SubmitEvent): void {
  const form = event.target;
  if (!(form instanceof HTMLFormElement)) return;

  // The lock covers every submitter of the form, not only the opted-in one.
  if (pendingForms.has(form)) {
    event.preventDefault();
    return;
  }

  // Canceled by another handler, such as htmx, so no navigation follows.
  if (event.defaultPrevented) return;

  if (form.hasAttribute(GUARD_ATTRIBUTE) || event.submitter?.hasAttribute(GUARD_ATTRIBUTE)) {
    pendingForms.set(form, markButtons(form));
    // A listener that runs after this one can still cancel the submission.
    setTimeout(() => {
      if (event.defaultPrevented) release(form);
    });
  }
}

/** Release every lock when the page comes back from the back/forward cache. */
function handlePageShow(event: PageTransitionEvent): void {
  // A back/forward cache restore keeps both the marked buttons and this module's state.
  if (!event.persisted) return;

  for (const form of pendingForms.keys()) {
    release(form);
  }
}

/** Block repeat submits of a form marked data-disable-on-submit on itself or its submitter. */
export function initSubmissionGuard(): void {
  // htmx re-inits pass the same listeners again, which the DOM ignores.
  document.addEventListener('submit', handleSubmit);
  window.addEventListener('pageshow', handlePageShow);
}
