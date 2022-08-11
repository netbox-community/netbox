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
 * Show/hide quicksearch clear button.
 *
 * @param event "keyup" or "search" event for the quicksearch input
 */
function quickSearchEventHandler(event: Event): void {
  const quicksearch = event.currentTarget as HTMLInputElement;
  const inputgroup = quicksearch.parentElement as HTMLDivElement;
  if (isTruthy(inputgroup)) {
    if (quicksearch.value === "") {
      inputgroup.classList.add("hide-last-child");
    } else {
      inputgroup.classList.remove("hide-last-child");
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
 * Initialize Quicksearch Event listener/handlers.
 */
function initQuickSearch(): void {
  const quicksearch = document.getElementById("quicksearch") as HTMLInputElement;
  const clearbtn = document.getElementById("quicksearch_clear") as HTMLButtonElement;
  if (isTruthy(quicksearch)) {
    quicksearch.addEventListener("keyup", quickSearchEventHandler, {
      passive: true
    })
    quicksearch.addEventListener("search", quickSearchEventHandler, {
      passive: true
    })
    if (isTruthy(clearbtn)) {
      clearbtn.addEventListener("click", async () => {
        const search = new Event('search');
        quicksearch.value = '';
        await new Promise(f => setTimeout(f, 100));
        quicksearch.dispatchEvent(search);
      }, {
        passive: true
      })
    }
  }
}

export function initSearch(): void {
  for (const func of [initSearchBar]) {
    func();
  }
  initQuickSearch();
}
