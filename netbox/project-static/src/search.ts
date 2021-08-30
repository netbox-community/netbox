import debounce from 'just-debounce-it';
import { getElements, getRowValues, findFirstAdjacent, isTruthy } from './util';

/**
 * Change the display value and hidden input values of the search filter based on dropdown
 * selection.
 *
 * @param event "click" event for each dropdown item.
 * @param button Each dropdown item element.
 */
function handleSearchDropdownClick(event: Event, button: HTMLButtonElement): void {
  const dropdown = event.currentTarget as HTMLButtonElement;
  const selectedValue = findFirstAdjacent<HTMLSpanElement>(dropdown, 'span.search-obj-selected');
  const selectedType = findFirstAdjacent<HTMLInputElement>(dropdown, 'input.search-obj-type');
  const searchValue = dropdown.getAttribute('data-search-value');
  let selected = '' as string;

  if (selectedValue !== null && selectedType !== null) {
    if (isTruthy(searchValue) && selected !== searchValue) {
      selected = searchValue;
      selectedValue.innerHTML = button.textContent ?? 'Error';
      selectedType.value = searchValue;
    } else {
      selected = '';
      selectedValue.innerHTML = 'All Objects';
      selectedType.value = '';
    }
  }
}

/**
 * Initialize Search Bar Elements.
 */
function initSearchBar(): void {
  for (const dropdown of getElements<HTMLUListElement>('.search-obj-selector')) {
    for (const button of dropdown.querySelectorAll<HTMLButtonElement>(
      'li > button.dropdown-item',
    )) {
      button.addEventListener('click', event => handleSearchDropdownClick(event, button));
    }
  }
}

/**
 * Initialize Interface Table Filter Elements.
 */
function initInterfaceFilter(): void {
  for (const input of getElements<HTMLInputElement>('input.interface-filter')) {
    const table = findFirstAdjacent<HTMLTableElement>(input, 'table');
    const rows = Array.from(
      table?.querySelectorAll<HTMLTableRowElement>('tbody > tr') ?? [],
    ).filter(r => r !== null);
    /**
     * Filter on-page table by input text.
     */
    function handleInput(event: Event): void {
      const target = event.target as HTMLInputElement;
      // Create a regex pattern from the input search text to match against.
      const filter = new RegExp(target.value.toLowerCase().trim());

      // Each row represents an interface and its attributes.
      for (const row of rows) {
        // Find the row's checkbox and deselect it, so that it is not accidentally included in form
        // submissions.
        const checkBox = row.querySelector<HTMLInputElement>('input[type="checkbox"][name="pk"]');
        if (checkBox !== null) {
          checkBox.checked = false;
        }

        // The data-name attribute's value contains the interface name.
        const name = row.getAttribute('data-name');

        if (typeof name === 'string') {
          if (filter.test(name.toLowerCase().trim())) {
            // If this row matches the search pattern, but is already hidden, unhide it.
            if (row.classList.contains('d-none')) {
              row.classList.remove('d-none');
            }
          } else {
            // If this row doesn't match the search pattern, hide it.
            row.classList.add('d-none');
          }
        }
      }
    }
    input.addEventListener('keyup', debounce(handleInput, 300));
  }
}

function initTableFilter(): void {
  for (const input of getElements<HTMLInputElement>('input.object-filter')) {
    // Find the first adjacent table element.
    const table = findFirstAdjacent<HTMLTableElement>(input, 'table');

    // Build a valid array of <tr/> elements that are children of the adjacent table.
    const rows = Array.from(
      table?.querySelectorAll<HTMLTableRowElement>('tbody > tr') ?? [],
    ).filter(r => r !== null);

    /**
     * Filter table rows by matched input text.
     * @param event
     */
    function handleInput(event: Event): void {
      const target = event.target as HTMLInputElement;

      // Create a regex pattern from the input search text to match against.
      const filter = new RegExp(target.value.toLowerCase().trim());

      for (const row of rows) {
        // Find the row's checkbox and deselect it, so that it is not accidentally included in form
        // submissions.
        const checkBox = row.querySelector<HTMLInputElement>('input[type="checkbox"][name="pk"]');
        if (checkBox !== null) {
          checkBox.checked = false;
        }
        // Iterate through each row's cell values
        for (const value of getRowValues(row)) {
          if (filter.test(value.toLowerCase())) {
            // If this row matches the search pattern, but is already hidden, unhide it and stop
            // iterating through the rest of the cells.
            row.classList.remove('d-none');
            break;
          } else {
            // If none of the cells in this row match the search pattern, hide the row.
            row.classList.add('d-none');
          }
        }
      }
    }
    input.addEventListener('keyup', debounce(handleInput, 300));
  }
}

export function initSearch(): void {
  for (const func of [initSearchBar, initTableFilter, initInterfaceFilter]) {
    func();
  }
}
