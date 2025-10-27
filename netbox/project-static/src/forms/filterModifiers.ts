import { getElements } from '../util';

// Modifier codes for empty/null checking
// These map to Django's 'empty' lookup: field__empty=true/false
const MODIFIER_EMPTY_TRUE = 'empty_true';
const MODIFIER_EMPTY_FALSE = 'empty_false';

/**
 * Initialize filter modifier functionality.
 *
 * Handles transformation of field names based on modifier selection
 * at form submission time using the FormData API.
 */
export function initFilterModifiers(): void {
  for (const form of getElements<HTMLFormElement>('form')) {
    // Only process forms with modifier selects
    const modifierSelects = form.querySelectorAll<HTMLSelectElement>('.modifier-select');
    if (modifierSelects.length === 0) continue;

    // Initialize form state from URL parameters
    initializeFromURL(form);

    // Add change listeners to modifier dropdowns to handle isnull
    modifierSelects.forEach(select => {
      select.addEventListener('change', () => handleModifierChange(select));
      // Trigger initial state
      handleModifierChange(select);
    });

    // Handle form submission - must use submit event for GET forms
    form.addEventListener('submit', e => {
      e.preventDefault();

      // Build FormData to get all form values
      const formData = new FormData(form);

      // Transform field names
      handleFormDataTransform(form, formData);

      // Build URL with transformed parameters
      const params = new URLSearchParams();
      for (const [key, value] of formData.entries()) {
        if (value && String(value).trim()) {
          params.append(key, String(value));
        }
      }

      // Navigate to new URL
      window.location.href = `${form.action}?${params.toString()}`;
    });
  }
}

/**
 * Handle modifier dropdown changes - disable/enable value input for empty lookups.
 */
function handleModifierChange(modifierSelect: HTMLSelectElement): void {
  const group = modifierSelect.closest('.filter-modifier-group');
  if (!group) return;

  const wrapper = group.querySelector('.filter-value-container');
  if (!wrapper) return;

  const valueInput = wrapper.querySelector<
    HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement
  >('input, select, textarea');

  if (!valueInput) return;

  const modifier = modifierSelect.value;

  // Disable and add placeholder for empty modifiers
  if (modifier === MODIFIER_EMPTY_TRUE || modifier === MODIFIER_EMPTY_FALSE) {
    valueInput.disabled = true;
    valueInput.value = '';
    // Get translatable placeholder from modifier dropdown's data attribute
    const placeholder = modifierSelect.dataset.emptyPlaceholder || '(automatically set)';
    valueInput.setAttribute('placeholder', placeholder);
  } else {
    valueInput.disabled = false;
    valueInput.removeAttribute('placeholder');
  }
}

/**
 * Transform field names in FormData based on modifier selection.
 */
function handleFormDataTransform(form: HTMLFormElement, formData: FormData): void {
  const modifierGroups = form.querySelectorAll('.filter-modifier-group');

  for (const group of modifierGroups) {
    const modifierSelect = group.querySelector<HTMLSelectElement>('.modifier-select');
    // Find input in the wrapper div (more specific selector)
    const wrapper = group.querySelector('.filter-value-container');
    if (!wrapper) continue;

    const valueInput = wrapper.querySelector<
      HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement
    >('input, select, textarea');

    if (!modifierSelect || !valueInput) continue;

    const currentName = valueInput.name;
    const modifier = modifierSelect.value;

    // Handle empty special case
    if (modifier === MODIFIER_EMPTY_TRUE || modifier === MODIFIER_EMPTY_FALSE) {
      formData.delete(currentName);
      const boolValue = modifier === MODIFIER_EMPTY_TRUE ? 'true' : 'false';
      formData.set(`${currentName}__empty`, boolValue);
    } else {
      // Get all values (handles multi-select)
      const values = formData.getAll(currentName);

      if (values.length > 0 && values.some(v => String(v).trim())) {
        formData.delete(currentName);
        const newName = modifier === 'exact' ? currentName : `${currentName}__${modifier}`;

        // Set all values with the new name
        for (const value of values) {
          if (String(value).trim()) {
            formData.append(newName, value);
          }
        }
      } else {
        formData.delete(currentName);
      }
    }
  }
}

/**
 * Initialize form state from URL parameters.
 * Restores modifier selection and values from query string.
 *
 * Process:
 * 1. Parse URL parameters
 * 2. For each modifier group, check which lookup variant exists in URL
 * 3. Set modifier dropdown to match
 * 4. Populate value field with parameter value
 */
function initializeFromURL(form: HTMLFormElement): void {
  const urlParams = new URLSearchParams(window.location.search);

  // Find all modifier groups
  const modifierGroups = form.querySelectorAll('.filter-modifier-group');

  for (const group of modifierGroups) {
    const modifierSelect = group.querySelector<HTMLSelectElement>('.modifier-select');
    // Find input in the wrapper div (more specific selector)
    const wrapper = group.querySelector('.filter-value-container');
    if (!wrapper) continue;

    const valueInput = wrapper.querySelector<
      HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement
    >('input, select, textarea');

    if (!modifierSelect || !valueInput) continue;

    const baseFieldName = valueInput.name; // e.g., "serial"

    // Special handling for empty - check if field__empty exists in URL
    const emptyParam = `${baseFieldName}__empty`;
    if (urlParams.has(emptyParam)) {
      const emptyValue = urlParams.get(emptyParam);
      const modifier = emptyValue === 'true' ? MODIFIER_EMPTY_TRUE : MODIFIER_EMPTY_FALSE;
      modifierSelect.value = modifier;
      continue; // Don't set value input for empty
    }

    // Check each possible lookup in URL
    for (const option of modifierSelect.options) {
      const lookup = option.value;

      // Skip empty_true/false as they're handled above
      if (lookup === MODIFIER_EMPTY_TRUE || lookup === MODIFIER_EMPTY_FALSE) continue;

      const paramName = lookup === 'exact' ? baseFieldName : `${baseFieldName}__${lookup}`;

      if (urlParams.has(paramName)) {
        modifierSelect.value = lookup;

        // Handle multi-select vs single-value inputs
        if (valueInput instanceof HTMLSelectElement && valueInput.multiple) {
          // For multi-select, set selected on matching options
          const values = urlParams.getAll(paramName);
          for (const option of valueInput.options) {
            option.selected = values.includes(option.value);
          }
        } else {
          // For single-value inputs, set value directly
          valueInput.value = urlParams.get(paramName) || '';
        }
        break;
      }
    }
  }
}
