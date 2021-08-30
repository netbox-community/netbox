import { getElement, getElements, findFirstAdjacent } from '../util';

/**
 * If any PK checkbox is checked, uncheck the select all table checkbox and the select all
 * confirmation checkbox.
 *
 * @param event Change Event
 */
function handlePkCheck(event: Event): void {
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
 * Show the select all card when the select all checkbox is checked, and sync the checkbox state
 * with all the PK checkboxes in the table.
 *
 * @param event Change Event
 */
function handleSelectAllToggle(event: Event): void {
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
 * Synchronize the select all confirmation checkbox state with the select all confirmation button
 * disabled state. If the select all confirmation checkbox is checked, the buttons should be
 * enabled. If not, the buttons should be disabled.
 *
 * @param event Change Event
 */
function handleSelectAll(event: Event): void {
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
export function initSelectAll(): void {
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
