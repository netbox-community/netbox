import { getElements } from '../util';

function handleFormSubmit(): void {
  // Automatically select all options in any <select> with the "select-all" class. This is useful for
  // multi-select fields that are used to add/remove choices.
  for (const element of getElements<HTMLOptionElement>('select.select-all option')) {
    element.selected = true;
  }
}

/**
 * Attach event listeners to each form's submit/reset buttons.
 */
export function initFormElements(): void {
  for (const form of getElements('form')) {
    // Find each of the form's submit buttons.
    const submitters = form.querySelectorAll<HTMLButtonElement>('button[type=submit]');
    for (const submitter of submitters) {
      // Add the event listener to each submitter.
      submitter.addEventListener('click', () => handleFormSubmit());
    }

    // Initialize any reset buttons so that when clicked, the page is reloaded without query parameters.
    const resetButton = document.querySelector<HTMLButtonElement>('button[data-reset-select]');
    if (resetButton !== null) {
      resetButton.addEventListener('click', () => {
        window.location.assign(window.location.origin + window.location.pathname);
      });
    }
  }
}
