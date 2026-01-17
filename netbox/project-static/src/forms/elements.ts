import TomSelect from 'tom-select';
import { getElements } from '../util';

function handleFormSubmit(): void {
  // Automatically select all options in any <select> with the "select-all" class. This is useful for
  // multi-select fields that are used to add/remove choices.
  for (const element of getElements<HTMLOptionElement>('select.select-all option')) {
    element.selected = true;
  }
}

/**
 * Initialize clear-field dependencies.
 * When a field with ts-clear-field attribute's parent field is cleared, this field will also be cleared.
 */
function initClearFieldDependencies(): void {
  // Find all fields with ts-clear-field attribute
  for (const field of getElements<HTMLSelectElement>('[ts-clear-field]')) {
    const parentFieldName = field.getAttribute('ts-clear-field');
    if (!parentFieldName) continue;

    // Find the parent field
    const parentField = document.querySelector<HTMLSelectElement>(`[name="${parentFieldName}"]`);
    if (!parentField) continue;

    // Listen for changes on the parent field
    parentField.addEventListener('change', () => {
      // If parent field is cleared, also clear this dependent field
      if (!parentField.value || parentField.value === '') {
        // Check if this field uses TomSelect
        const tomselect = (field as HTMLSelectElement & { tomselect?: TomSelect }).tomselect;
        if (tomselect) {
          tomselect.clear();
        } else {
          // Regular select field
          field.value = '';
        }
      }
    });
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

  // Initialize clear-field dependencies
  initClearFieldDependencies();
}
