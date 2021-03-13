interface SearchFilterButton extends EventTarget {
  dataset: { searchValue: string };
}

function isSearchButton(el: any): el is SearchFilterButton {
  return el?.dataset?.searchValue ?? null !== null;
}

export function initSearchBar() {
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
