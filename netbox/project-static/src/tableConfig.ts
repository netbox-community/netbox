import { createToast } from './bs';
import { getElements, apiPatch, hasError, getSelectedOptions } from './util';

/**
 * Mark each option element in the selected columns element as 'selected' so they are submitted to
 * the API.
 */
function saveTableConfig(): void {
  for (const element of getElements<HTMLOptionElement>('select[name="columns"] option')) {
    element.selected = true;
  }
}

/**
 * Delete all selected columns, which reverts the user's preferences to the default column set.
 */
function resetTableConfig(): void {
  for (const element of getElements<HTMLSelectElement>('select[name="columns"]')) {
    element.value = '';
  }
}

/**
 * Add columns to the table config select element.
 */
function addColumns(event: Event): void {
  for (const selectedOption of getElements<HTMLOptionElement>('#id_available_columns > option')) {
    if (selectedOption.selected) {
      for (const selected of getElements<HTMLSelectElement>('#id_columns')) {
        selected.appendChild(selectedOption.cloneNode(true));
      }
      selectedOption.remove();
    }
  }
  event.preventDefault();
}

/**
 * Remove columns from the table config select element.
 */
function removeColumns(event: Event): void {
  for (const selectedOption of getElements<HTMLOptionElement>('#id_columns > option')) {
    if (selectedOption.selected) {
      for (const available of getElements<HTMLSelectElement>('#id_available_columns')) {
        available.appendChild(selectedOption.cloneNode(true));
      }
      selectedOption.remove();
    }
  }
  event.preventDefault();
}

/**
 * Submit form configuration to the NetBox API.
 */
async function submitFormConfig(url: string, formConfig: Dict<Dict>): Promise<APIResponse<APIUserConfig>> {
  return await apiPatch<APIUserConfig>(url, formConfig);
}

/**
 * Handle table config form submission. Sends the selected columns to the NetBox API to update
 * the user's table configuration preferences.
 */
function handleSubmit(event: Event): void {
  event.preventDefault();

  const element = event.currentTarget as HTMLFormElement;

  // Get the API URL for submitting the form
  const url = element.getAttribute('data-url');
  if (url == null) {
    const toast = createToast(
        'danger',
        'Error Updating Table Configuration',
        'No API path defined for configuration form.'
    );
    toast.show();
    return;
  }

  // Get all the selected options from any select element in the form.
  const options = getSelectedOptions(element);

  // Create an object mapping the select element's name to all selected options for that element.
  const formData: Dict<Dict<string>> = Object.assign(
    {},
    ...options.map(opt => ({ [opt.name]: opt.options })),
  );
  // Create an array from the dot-separated config path. E.g. tables.DevicePowerOutletTable becomes
  // ['tables', 'DevicePowerOutletTable']
  const path = element.getAttribute('data-config-root')?.split('.') ?? [];

  // Create an object mapping the configuration path to the select element names, which contain the
  // selection options. E.g. {tables: {DevicePowerOutletTable: {columns: ['label', 'type']}}}
  const data = path.reduceRight<Dict<Dict>>((value, key) => ({ [key]: value }), formData);

  // Submit the resulting object to the API to update the user's preferences for this table.
  submitFormConfig(url, data).then(res => {
    if (hasError(res)) {
      const toast = createToast('danger', 'Error Updating Table Configuration', res.error);
      toast.show();
    } else {
      location.reload();
    }
  });
}

/**
 * Initialize table configuration elements.
 */
export function initTableConfig(): void {
  for (const element of getElements<HTMLButtonElement>('#save_tableconfig')) {
    element.addEventListener('click', saveTableConfig);
  }
  for (const element of getElements<HTMLButtonElement>('#reset_tableconfig')) {
    element.addEventListener('click', resetTableConfig);
  }
  for (const element of getElements<HTMLButtonElement>('#add_columns')) {
    element.addEventListener('click', addColumns);
  }
  for (const element of getElements<HTMLButtonElement>('#remove_columns')) {
    element.addEventListener('click', removeColumns);
  }
  for (const element of getElements<HTMLFormElement>('form.userconfigform')) {
    element.addEventListener('submit', handleSubmit);
  }
}
