import { getElements, fadeIn } from '../util';
				
/**
 * Conditionally add and remove a class that will float the button group
 * based on whether or not items in the list are checked
 */
function toggleFloat(): void {
  const checkedCheckboxes = document.querySelector<HTMLInputElement>('input[type="checkbox"][name="pk"]:checked');
  const buttonGroup = document.querySelector<HTMLDivElement>('div.form.form-horizontal div.btn-list');
  const isFloating = buttonGroup.classList.contains('btn-float-group-left');
  if (checkedCheckboxes !== null && !isFloating) {
    buttonGroup.classList.add('btn-float-group-left');
  }
  else if (checkedCheckboxes === null && isFloating) {
    buttonGroup.classList.remove('btn-float-group-left');
  }
}


/**
 * Initialize floating bulk buttons.
 */
export function initFloatBulk(): void {
  for (const element of getElements<HTMLInputElement>('input[type="checkbox"][name="pk"]')) {
    element.addEventListener('change', event => {
      toggleFloat();
    });
  }
  // Handle the select-all checkbox
  for (const element of getElements<HTMLInputElement>('table tr th > input[type="checkbox"].toggle')) {
    element.addEventListener('change', event => {
      toggleFloat();
    });
  }
}
