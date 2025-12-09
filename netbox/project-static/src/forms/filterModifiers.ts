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
    const modifierSelects = form.querySelectorAll<HTMLSelectElement>('.modifier-select');
    if (modifierSelects.length === 0) continue;

    initializeFromURL(form);

    modifierSelects.forEach(select => {
      select.addEventListener('change', () => handleModifierChange(select));
      handleModifierChange(select);
    });

    // Must use submit event for GET forms
    form.addEventListener('submit', e => {
      e.preventDefault();

      const formData = new FormData(form);
      handleFormDataTransform(form, formData);

      const params = new URLSearchParams();
      for (const [key, value] of formData.entries()) {
        if (value && String(value).trim()) {
          params.append(key, String(value));
        }
      }

      // Use getAttribute to avoid collision with form fields named 'action'
      const actionUrl = form.getAttribute('action') || form.action;
      window.location.href = `${actionUrl}?${params.toString()}`;
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

  if (modifier === MODIFIER_EMPTY_TRUE || modifier === MODIFIER_EMPTY_FALSE) {
    valueInput.disabled = true;
    valueInput.value = '';
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
    const wrapper = group.querySelector('.filter-value-container');
    if (!wrapper) continue;

    const valueInput = wrapper.querySelector<
      HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement
    >('input, select, textarea');

    if (!modifierSelect || !valueInput) continue;

    const currentName = valueInput.name;
    const modifier = modifierSelect.value;

    if (modifier === MODIFIER_EMPTY_TRUE || modifier === MODIFIER_EMPTY_FALSE) {
      formData.delete(currentName);
      const boolValue = modifier === MODIFIER_EMPTY_TRUE ? 'true' : 'false';
      formData.set(`${currentName}__empty`, boolValue);
    } else {
      const values = formData.getAll(currentName);

      if (values.length > 0 && values.some(v => String(v).trim())) {
        formData.delete(currentName);
        const newName = modifier === 'exact' ? currentName : `${currentName}__${modifier}`;

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

  const modifierGroups = form.querySelectorAll('.filter-modifier-group');

  for (const group of modifierGroups) {
    const modifierSelect = group.querySelector<HTMLSelectElement>('.modifier-select');
    const wrapper = group.querySelector('.filter-value-container');
    if (!wrapper) continue;

    const valueInput = wrapper.querySelector<
      HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement
    >('input, select, textarea');

    if (!modifierSelect || !valueInput) continue;

    const baseFieldName = valueInput.name;

    // Special handling for empty - check if field__empty exists in URL
    const emptyParam = `${baseFieldName}__empty`;
    if (urlParams.has(emptyParam)) {
      const emptyValue = urlParams.get(emptyParam);
      const modifier = emptyValue === 'true' ? MODIFIER_EMPTY_TRUE : MODIFIER_EMPTY_FALSE;
      modifierSelect.value = modifier;
      continue; // Don't set value input for empty
    }

    for (const option of modifierSelect.options) {
      const lookup = option.value;

      // Skip empty_true/false as they're handled above
      if (lookup === MODIFIER_EMPTY_TRUE || lookup === MODIFIER_EMPTY_FALSE) continue;

      const paramName = lookup === 'exact' ? baseFieldName : `${baseFieldName}__${lookup}`;

      if (urlParams.has(paramName)) {
        modifierSelect.value = lookup;

        if (valueInput instanceof HTMLSelectElement && valueInput.multiple) {
          const values = urlParams.getAll(paramName);
          for (const option of valueInput.options) {
            option.selected = values.includes(option.value);
          }
        } else {
          valueInput.value = urlParams.get(paramName) || '';
        }
        break;
      }
    }
  }
}
