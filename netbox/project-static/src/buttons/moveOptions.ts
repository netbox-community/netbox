import { getElements } from '../util';

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
 * Initialize move up/down buttons.
 */
export function initMoveButtons(): void {
  for (const button of getElements<HTMLButtonElement>('#move-option-up')) {
    const target = button.getAttribute('data-target');
    if (target !== null) {
      for (const select of getElements<HTMLSelectElement>(`#${target}`)) {
        button.addEventListener('click', () => moveOptionUp(select));
      }
    }
  }
  for (const button of getElements<HTMLButtonElement>('#move-option-down')) {
    const target = button.getAttribute('data-target');
    if (target !== null) {
      for (const select of getElements<HTMLSelectElement>(`#${target}`)) {
        button.addEventListener('click', () => moveOptionDown(select));
      }
    }
  }
}
