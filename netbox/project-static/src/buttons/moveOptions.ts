import { getElements } from '../util';

/**
 * Move selected options from one select element to another, preserving optgroup structure.
 *
 * @param source Select Element
 * @param target Select Element
 */
function moveOption(source: HTMLSelectElement, target: HTMLSelectElement): void {
  for (const option of Array.from(source.options)) {
    if (option.selected) {
      // Check if option is inside an optgroup
      const parentOptgroup = option.parentElement as HTMLElement;

      if (parentOptgroup.tagName === 'OPTGROUP') {
        // Find or create matching optgroup in target
        const groupLabel = parentOptgroup.getAttribute('label');
        let targetOptgroup = Array.from(target.children).find(
          child => child.tagName === 'OPTGROUP' && child.getAttribute('label') === groupLabel,
        ) as HTMLOptGroupElement;

        if (!targetOptgroup) {
          // Create new optgroup in target
          targetOptgroup = document.createElement('optgroup');
          targetOptgroup.setAttribute('label', groupLabel!);
          target.appendChild(targetOptgroup);
        }

        // Move option to target optgroup
        targetOptgroup.appendChild(option.cloneNode(true));
      } else {
        // Option is not in an optgroup, append directly
        target.appendChild(option.cloneNode(true));
      }

      option.remove();

      // Clean up empty optgroups in source
      if (parentOptgroup.tagName === 'OPTGROUP' && parentOptgroup.children.length === 0) {
        parentOptgroup.remove();
      }
    }
  }
}

/**
 * Move selected options of a select element up in order, respecting optgroup boundaries.
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
      const parent = option.parentElement as HTMLElement;
      const previousOption = element.options[i - 1];
      const previousParent = previousOption.parentElement as HTMLElement;

      // Only move if previous option is in the same parent (optgroup or select)
      if (parent === previousParent) {
        parent.removeChild(option);
        parent.insertBefore(option, previousOption);
      }
    }
  }
}

/**
 * Move selected options of a select element down in order, respecting optgroup boundaries.
 *
 * Adapted from:
 * @see https://www.tomred.net/css-html-js/reorder-option-elements-of-an-html-select.html
 * @param element Select Element
 */
function moveOptionDown(element: HTMLSelectElement): void {
  const options = Array.from(element.options);
  for (let i = options.length - 2; i >= 0; i--) {
    const option = options[i];
    if (option.selected) {
      const parent = option.parentElement as HTMLElement;
      const nextOption = element.options[i + 1];
      const nextParent = nextOption.parentElement as HTMLElement;

      // Only move if next option is in the same parent (optgroup or select)
      if (parent === nextParent) {
        const optionClone = parent.removeChild(option);
        const nextClone = parent.replaceChild(optionClone, nextOption);
        parent.insertBefore(nextClone, optionClone);
      }
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
