import { getElements, findFirstAdjacent, isTruthy } from './util';

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

export function initSearch(): void {
  for (const func of [initSearchBar]) {
    func();
  }
}
