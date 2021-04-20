import { getElements, scrollTo } from './util';

/**
 * Get form data from a form element and transform it into a body usable by fetch.
 *
 * @param element Form element
 * @returns Fetch body
 */
export function getFormData(element: HTMLFormElement): URLSearchParams {
  const formData = new FormData(element);
  const body = new URLSearchParams();
  for (const [k, v] of formData) {
    body.append(k, v as string);
  }
  return body;
}

/**
 * Set the value of the number input field based on the selection of the dropdown.
 */
export function initSpeedSelector(): void {
  for (const element of getElements<HTMLAnchorElement>('a.set_speed')) {
    if (element !== null) {
      function handleClick(event: Event) {
        // Don't reload the page (due to href="#").
        event.preventDefault();
        // Get the value of the `data` attribute on the dropdown option.
        const value = element.getAttribute('data');
        // Find the input element referenced by the dropdown element.
        const input = document.getElementById(element.target) as Nullable<HTMLInputElement>;
        if (input !== null && value !== null) {
          // Set the value of the input field to the `data` attribute's value.
          input.value = value;
        }
      }
      element.addEventListener('click', handleClick);
    }
  }
}

/**
 * Attach an event listener to each form's submitter (button[type=submit]). When called, the
 * callback checks the validity of each form field and adds the appropriate Bootstrap CSS class
 * based on the field's validity.
 */
function initFormElements() {
  for (const form of getElements('form')) {
    const { elements } = form;
    // Find each of the form's submitters. Most object edit forms have a "Create" and
    // a "Create & Add", so we need to add a listener to both.
    const submitters = form.querySelectorAll('button[type=submit]');

    function callback(event: Event): void {
      // Track the names of each invalid field.
      const invalids = new Set<string>();

      for (const el of elements) {
        const element = (el as unknown) as FormControls;

        if (!element.validity.valid) {
          invalids.add(element.name);

          // If the field is invalid, but contains the .is-valid class, remove it.
          if (element.classList.contains('is-valid')) {
            element.classList.remove('is-valid');
          }
          // If the field is invalid, but doesn't contain the .is-invalid class, add it.
          if (!element.classList.contains('is-invalid')) {
            element.classList.add('is-invalid');
          }
        } else {
          // If the field is valid, but contains the .is-invalid class, remove it.
          if (element.classList.contains('is-invalid')) {
            element.classList.remove('is-invalid');
          }
          // If the field is valid, but doesn't contain the .is-valid class, add it.
          if (!element.classList.contains('is-valid')) {
            element.classList.add('is-valid');
          }
        }
      }

      if (invalids.size !== 0) {
        // If there are invalid fields, pick the first field and scroll to it.
        const firstInvalid = elements.namedItem(Array.from(invalids)[0]) as Element;
        scrollTo(firstInvalid);

        // If the form has invalid fields, don't submit it.
        event.preventDefault();
      }
    }
    for (const submitter of submitters) {
      // Add the event listener to each submitter.
      submitter.addEventListener('click', callback);
    }
  }
}

/**
 * Move selected options of a select element up in order.
 *
 * Adapted from:
 * @see https://www.tomred.net/css-html-js/reorder-option-elements-of-an-html-select.html
 * @param element Select Element
 */
function moveOptionUp(element: HTMLSelectElement): void {
  const options = Array.from(element.options);
  for (let i = 1; i < options.length; i++) {
    let option = options[i];
    if (option.selected) {
      element.removeChild(option);
      element.insertBefore(option, element.options[i - 1]);
    }
  }
}

/**
 * Move selected options of a select element down in order.
 *
 * Adapted from:
 * @see https://www.tomred.net/css-html-js/reorder-option-elements-of-an-html-select.html
 * @param element Select Element
 */
function moveOptionDown(element: HTMLSelectElement): void {
  const options = Array.from(element.options);
  for (let i = options.length - 2; i >= 0; i--) {
    let option = options[i];
    if (option.selected) {
      let next = element.options[i + 1];
      option = element.removeChild(option);
      next = element.replaceChild(option, next);
      element.insertBefore(next, option);
    }
  }
}

/**
 * Initialize move up/down buttons.
 */
function initMoveButtons() {
  for (const button of getElements<HTMLButtonElement>('#move-option-up')) {
    const target = button.getAttribute('data-target');
    if (target !== null) {
      for (const select of getElements<HTMLSelectElement>(`#${target}`)) {
        button.addEventListener('click', () => moveOptionUp(select));
      }
    }
  }
  for (const button of getElements<HTMLButtonElement>('#move-option-down')) {
    const target = button.getAttribute('data-target');
    if (target !== null) {
      for (const select of getElements<HTMLSelectElement>(`#${target}`)) {
        button.addEventListener('click', () => moveOptionDown(select));
      }
    }
  }
}

export function initForms() {
  for (const func of [initFormElements, initMoveButtons]) {
    func();
  }
}
