import { getElements, scrollTo, isTruthy } from '../util';

/**
 * When editing an object, it is sometimes desirable to customize the form action *without*
 * overriding the form's `submit` event. For example, the 'Save & Continue' button. We don't want
 * to use the `formaction` attribute on that element because it will be included on the form even
 * if the button isn't clicked.
 *
 * @example
 * ```html
 * <button type="button" return-url="/special-url/">
 *   Save & Continue
 * </button>
 * ```
 *
 * @param event Click event.
 */
function handleSubmitWithReturnUrl(event: MouseEvent): void {
  const element = event.target as HTMLElement;
  if (element.tagName === 'BUTTON') {
    const button = element as HTMLButtonElement;
    const action = button.getAttribute('return-url');
    const form = button.form;
    if (form !== null && isTruthy(action)) {
      form.action = action;
      form.submit();
    }
  }
}

function handleFormSubmit(event: Event, form: HTMLFormElement): void {
  // Track the names of each invalid field.
  const invalids = new Set<string>();

  for (const element of form.querySelectorAll<FormControls>('*[name]')) {
    if (!element.validity.valid) {
      invalids.add(element.name);
      // If the field is invalid, but doesn't contain the .is-invalid class, add it.
      if (!element.classList.contains('is-invalid')) {
        element.classList.add('is-invalid');
      }
    } else {
      // If the field is valid, but contains the .is-invalid class, remove it.
      if (element.classList.contains('is-invalid')) {
        element.classList.remove('is-invalid');
      }
    }
  }

  if (invalids.size !== 0) {
    // If there are invalid fields, pick the first field and scroll to it.
    const firstInvalid = form.elements.namedItem(Array.from(invalids)[0]) as Element;
    scrollTo(firstInvalid);

    // If the form has invalid fields, don't submit it.
    event.preventDefault();
  }
}

/**
 * Attach event listeners to form buttons with the `return-url` attribute present.
 */
function initReturnUrlSubmitButtons(): void {
  for (const button of getElements<HTMLButtonElement>('button[return-url]')) {
    button.addEventListener('click', handleSubmitWithReturnUrl);
  }
}

/**
 * Attach an event listener to each form's submitter (button[type=submit]). When called, the
 * callback checks the validity of each form field and adds the appropriate Bootstrap CSS class
 * based on the field's validity.
 */
export function initFormElements(): void {
  for (const form of getElements('form')) {
    // Find each of the form's submitters. Most object edit forms have a "Create" and
    // a "Create & Add", so we need to add a listener to both.
    const submitters = form.querySelectorAll<HTMLButtonElement>('button[type=submit]');

    for (const submitter of submitters) {
      // Add the event listener to each submitter.
      submitter.addEventListener('click', (event: Event) => handleFormSubmit(event, form));
    }
  }
  initReturnUrlSubmitButtons();
}
