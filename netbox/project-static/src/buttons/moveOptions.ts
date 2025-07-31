import { getElements } from '../util';

/**
 * Move selected options from one select element to another.
 *
 * @param source Select Element
 * @param target Select Element
 */
function moveOption(source: HTMLSelectElement, target: HTMLSelectElement): void {
  for (const option of Array.from(source.options)) {
    if (option.selected) {
      target.appendChild(option.cloneNode(true));
      option.remove();
    }
  }
}

/**
 * Move selected options of a select element up in order.
 *
 * Adapted from:
 * @see https://www.tomred.net/css-html-js/reorder-option-elements-of-an-html-select.html
 * @param element Select Element
 */
function moveOptionUp(element: HTMLSelectElement): void {
  const options = Array.from(element.options);
  for (let i = 1; i < options.length; i++) {
    const option = options[i];
    if (option.selected) {
      element.removeChild(option);
      element.insertBefore(option, element.options[i - 1]);
    }
  }
}

/**
 * Move selected options of a select element down in order.
 *
 * Adapted from:
 * @see https://www.tomred.net/css-html-js/reorder-option-elements-of-an-html-select.html
 * @param element Select Element
 */
function moveOptionDown(element: HTMLSelectElement): void {
  const options = Array.from(element.options);
  for (let i = options.length - 2; i >= 0; i--) {
    let option = options[i];
    if (option.selected) {
      let next = element.options[i + 1];
      option = element.removeChild(option);
      next = element.replaceChild(option, next);
      element.insertBefore(next, option);
    }
  }
}

/**
 * Initialize select/move buttons.
 */
export function initMoveButtons(): void {
  // Move selected option(s) between lists
  for (const button of getElements<HTMLButtonElement>('.move-option')) {
    const source = button.getAttribute('data-source');
    const target = button.getAttribute('data-target');
    const source_select = document.getElementById(`id_${source}`) as HTMLSelectElement;
    const target_select = document.getElementById(`id_${target}`) as HTMLSelectElement;
    if (source_select !== null && target_select !== null) {
      button.addEventListener('click', () => moveOption(source_select, target_select));
    }
  }

  // Move selected option(s) up in current list
  for (const button of getElements<HTMLButtonElement>('.move-option-up')) {
    const target = button.getAttribute('data-target');
    const target_select = document.getElementById(`id_${target}`) as HTMLSelectElement;
    if (target_select !== null) {
      button.addEventListener('click', () => moveOptionUp(target_select));
    }
  }

  // Move selected option(s) down in current list
  for (const button of getElements<HTMLButtonElement>('.move-option-down')) {
    const target = button.getAttribute('data-target');
    const target_select = document.getElementById(`id_${target}`) as HTMLSelectElement;
    if (target_select !== null) {
      button.addEventListener('click', () => moveOptionDown(target_select));
    }
  }
}
