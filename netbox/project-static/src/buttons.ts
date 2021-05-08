import { createToast } from './bs';
import { setColorMode } from './colorMode';
import {
  slugify,
  isTruthy,
  apiPatch,
  hasError,
  getElement,
  getElements,
  findFirstAdjacent,
} from './util';

/**
 * Toggle the visibility of device images and update the toggle button style.
 */
function handleRackImageToggle(event: Event) {
  const target = event.target as HTMLButtonElement;
  const selected = target.getAttribute('selected');

  if (isTruthy(selected)) {
    for (const elevation of getElements<HTMLObjectElement>('.rack_elevation')) {
      const images = elevation.contentDocument?.querySelectorAll('image.device-image') ?? [];
      for (const image of images) {
        if (image !== null && !image.classList.contains('hidden')) {
          image.classList.add('hidden');
        }
      }
    }
    target.innerHTML = `<i class="mdi mdi-file-image-outline"></i>&nbsp;Show Images`;
    target.setAttribute('selected', '');
  } else {
    for (const elevation of getElements<HTMLObjectElement>('.rack_elevation')) {
      const images = elevation.contentDocument?.querySelectorAll('image.device-image') ?? [];
      for (const image of images) {
        if (image !== null) {
          image.classList.remove('hidden');
        }
      }
    }
    target.innerHTML = `<i class="mdi mdi-file-image-outline"></i>&nbsp;Hide Images`;
    target.setAttribute('selected', 'selected');
  }
  return;
}
/**
 * Add onClick callback for toggling rack elevation images.
 */
function initRackElevation() {
  for (const button of getElements<HTMLButtonElement>('button.toggle-images')) {
    button.addEventListener('click', handleRackImageToggle);
  }
}

/**
 * When the toggle button is clicked, swap the connection status via the API and toggle CSS
 * classes to reflect the connection status.
 *
 * @param element Connection Toggle Button Element
 */
function toggleConnection(element: HTMLButtonElement) {
  const id = element.getAttribute('data');
  const connected = element.classList.contains('connected');
  const status = connected ? 'planned' : 'connected';

  if (isTruthy(id)) {
    apiPatch(`/api/dcim/cables/${id}/`, { status }).then(res => {
      if (hasError(res)) {
        // If the API responds with an error, show it to the user.
        createToast('danger', 'Error', res.error).show();
        return;
      } else {
        // Get the button's row to change its styles.
        const row = element.parentElement?.parentElement as HTMLTableRowElement;
        // Get the button's icon to change its CSS class.
        const icon = element.querySelector('i.mdi, span.mdi') as HTMLSpanElement;
        if (connected) {
          row.classList.remove('success');
          row.classList.add('info');
          element.classList.remove('connected', 'btn-warning');
          element.classList.add('btn-info');
          element.title = 'Mark Installed';
          icon.classList.remove('mdi-lan-disconnect');
          icon.classList.add('mdi-lan-connect');
        } else {
          row.classList.remove('info');
          row.classList.add('success');
          element.classList.remove('btn-success');
          element.classList.add('connected', 'btn-warning');
          element.title = 'Mark Installed';
          icon.classList.remove('mdi-lan-connect');
          icon.classList.add('mdi-lan-disconnect');
        }
      }
    });
  }
}

function initConnectionToggle() {
  for (const element of getElements<HTMLButtonElement>('button.cable-toggle')) {
    element.addEventListener('click', () => toggleConnection(element));
  }
}

/**
 * If a slug field exists, add event listeners to handle automatically generating its value.
 */
function initReslug(): void {
  const slugField = document.getElementById('id_slug') as HTMLInputElement;
  const slugButton = document.getElementById('reslug') as HTMLButtonElement;
  if (slugField === null || slugButton === null) {
    return;
  }
  const sourceId = slugField.getAttribute('slug-source');
  const sourceField = document.getElementById(`id_${sourceId}`) as HTMLInputElement;

  if (sourceField === null) {
    console.error('Unable to find field for slug field.');
    return;
  }

  const slugLengthAttr = slugField.getAttribute('maxlength');
  let slugLength = 50;

  if (slugLengthAttr) {
    slugLength = Number(slugLengthAttr);
  }
  sourceField.addEventListener('blur', () => {
    slugField.value = slugify(sourceField.value, slugLength);
  });
  slugButton.addEventListener('click', () => {
    slugField.value = slugify(sourceField.value, slugLength);
  });
}

/**
 * Perform actions in the UI based on the value of user profile updates.
 *
 * @param event Form Submit
 */
function handlePreferenceSave(event: Event): void {
  // Create a FormData instance to access the form values.
  const form = event.currentTarget as HTMLFormElement;
  const formData = new FormData(form);

  // Update the UI color mode immediately when the user preference changes.
  if (formData.get('ui.colormode') === 'dark') {
    setColorMode('dark');
  } else if (formData.get('ui.colormode') === 'light') {
    setColorMode('light');
  }
}

/**
 * Initialize handlers for user profile updates.
 */
function initPreferenceUpdate() {
  const form = getElement<HTMLFormElement>('preferences-update');
  if (form !== null) {
    form.addEventListener('submit', handlePreferenceSave);
  }
}

/**
 * Show the select all card when the select all checkbox is checked, and sync the checkbox state
 * with all the PK checkboxes in the table.
 *
 * @param event Change Event
 */
function handleSelectAllToggle(event: Event) {
  // Select all checkbox in header row.
  const tableSelectAll = event.currentTarget as HTMLInputElement;
  // Nearest table to the select all checkbox.
  const table = findFirstAdjacent<HTMLInputElement>(tableSelectAll, 'table');
  // Select all confirmation card.
  const confirmCard = document.getElementById('select-all-box');
  // Checkbox in confirmation card to signal if all objects should be selected.
  const confirmCheckbox = document.getElementById('select-all') as Nullable<HTMLInputElement>;

  if (table !== null) {
    for (const element of table.querySelectorAll<HTMLInputElement>(
      'input[type="checkbox"][name="pk"]',
    )) {
      if (tableSelectAll.checked) {
        // Check all PK checkboxes if the select all checkbox is checked.
        element.checked = true;
      } else {
        // Uncheck all PK checkboxes if the select all checkbox is unchecked.
        element.checked = false;
      }
    }
    if (confirmCard !== null) {
      if (tableSelectAll.checked) {
        // Unhide the select all confirmation card if the select all checkbox is checked.
        confirmCard.classList.remove('d-none');
      } else {
        // Hide the select all confirmation card if the select all checkbox is unchecked.
        confirmCard.classList.add('d-none');
        if (confirmCheckbox !== null) {
          // Uncheck the confirmation checkbox when the table checkbox is unchecked (after which
          // the confirmation card will be hidden).
          confirmCheckbox.checked = false;
        }
      }
    }
  }
}

/**
 * If any PK checkbox is checked, uncheck the select all table checkbox and the select all
 * confirmation checkbox.
 *
 * @param event Change Event
 */
function handlePkCheck(event: Event) {
  const target = event.currentTarget as HTMLInputElement;
  if (!target.checked) {
    for (const element of getElements<HTMLInputElement>(
      'input[type="checkbox"].toggle',
      'input#select-all',
    )) {
      element.checked = false;
    }
  }
}

/**
 * Synchronize the select all confirmation checkbox state with the select all confirmation button
 * disabled state. If the select all confirmation checkbox is checked, the buttons should be
 * enabled. If not, the buttons should be disabled.
 *
 * @param event Change Event
 */
function handleSelectAll(event: Event) {
  const target = event.currentTarget as HTMLInputElement;
  const selectAllBox = getElement<HTMLDivElement>('select-all-box');
  if (selectAllBox !== null) {
    for (const button of selectAllBox.querySelectorAll<HTMLButtonElement>(
      'button[type="submit"]',
    )) {
      if (target.checked) {
        button.disabled = false;
      } else {
        button.disabled = true;
      }
    }
  }
}

/**
 * Initialize table select all elements.
 */
function initSelectAll() {
  for (const element of getElements<HTMLInputElement>(
    'table tr th > input[type="checkbox"].toggle',
  )) {
    element.addEventListener('change', handleSelectAllToggle);
  }
  for (const element of getElements<HTMLInputElement>('input[type="checkbox"][name="pk"]')) {
    element.addEventListener('change', handlePkCheck);
  }
  const selectAll = getElement<HTMLInputElement>('select-all');

  if (selectAll !== null) {
    selectAll.addEventListener('change', handleSelectAll);
  }
}

function handlePerPageSelect(event: Event) {
  const select = event.currentTarget as HTMLSelectElement;
  if (select.form !== null) {
    select.form.submit();
  }
}

function initPerPage() {
  for (const element of getElements<HTMLSelectElement>('select.per-page')) {
    element.addEventListener('change', handlePerPageSelect);
  }
}

export function initButtons() {
  for (const func of [
    initRackElevation,
    initConnectionToggle,
    initReslug,
    initSelectAll,
    initPreferenceUpdate,
    initPerPage,
  ]) {
    func();
  }
}
