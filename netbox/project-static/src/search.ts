import { getElements } from './util';

interface SearchFilterButton extends EventTarget {
  dataset: { searchValue: string };
}

function isSearchButton(el: any): el is SearchFilterButton {
  return el?.dataset?.searchValue ?? null !== null;
}

function initSearchBar() {
  const dropdown = document.getElementById('object-type-selector');
  const selectedValue = document.getElementById('selected-value') as HTMLSpanElement;
  const selectedType = document.getElementById('search-obj-type') as HTMLInputElement;
  let selected = '';

  if (dropdown !== null) {
    const buttons = dropdown.querySelectorAll('li > button.dropdown-item');
    for (const button of buttons) {
      if (button !== null) {
        function handleClick(event: Event) {
          if (isSearchButton(event.target)) {
            const objectType = event.target.dataset.searchValue;
            if (objectType !== '' && selected !== objectType) {
              selected = objectType;
              selectedValue.innerHTML = button.textContent ?? 'Error';
              selectedType.value = objectType;
            } else {
              selected = '';
              selectedType.innerHTML = 'All Objects';
              selectedType.value = '';
            }
          }
        }
        button.addEventListener('click', handleClick);
      }
    }
  }
}

/**
 * Initialize Interface Table Filter Elements.
 */
function initInterfaceFilter() {
  for (const element of getElements<HTMLInputElement>('input.interface-filter')) {
    /**
     * Filter on-page table by input text.
     */
    function handleInput(event: Event) {
      const target = event.target as HTMLInputElement;
      // Create a regex pattern from the input search text to match against.
      const filter = new RegExp(target.value);

      // Each row represents an interface and its attributes.
      for (const row of getElements<HTMLTableRowElement>('table > tbody > tr')) {
        // The data-name attribute's value contains the interface name.
        const name = row.getAttribute('data-name');

        // Find the row's checkbox and deselect it, so that it is not accidentally included in form
        // submissions.
        const checkBox = row.querySelector<HTMLInputElement>('input[type="checkbox"][name="pk"]');
        if (checkBox !== null) {
          checkBox.checked = false;
        }

        if (typeof name === 'string') {
          if (filter.test(name)) {
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
    element.addEventListener('keyup', handleInput);
  }
}

export function initSearch() {
  for (const func of [initSearchBar, initInterfaceFilter]) {
    func();
  }
}
