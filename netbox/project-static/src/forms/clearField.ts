import TomSelect from 'tom-select';
import { getElements } from '../util';

/**
 * Initialize clear-field dependencies.
 * When a required field is cleared, dependent fields with data-requires-fields attribute will also be cleared.
 */
export function initClearField(): void {
  // Find all fields with data-requires-fields attribute
  for (const field of getElements<HTMLSelectElement>('[data-requires-fields]')) {
    const requiredFieldsAttr = field.getAttribute('data-requires-fields');
    if (!requiredFieldsAttr) continue;

    // Parse the comma-separated list of required field names
    const requiredFields = requiredFieldsAttr.split(',').map(name => name.trim());

    // Set up listeners for each required field
    for (const requiredFieldName of requiredFields) {
      const requiredField = document.querySelector<HTMLSelectElement>(
        `[name="${requiredFieldName}"]`,
      );
      if (!requiredField) continue;

      // Listen for changes on the required field
      requiredField.addEventListener('change', () => {
        // If required field is cleared, also clear this dependent field
        if (!requiredField.value || requiredField.value === '') {
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
}
