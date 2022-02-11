import { getElements } from '../util';

/**
 * Set the value of the number input field based on the selection of the dropdown.
 */
export function initSpeedSelector(): void {
  for (const element of getElements<HTMLAnchorElement>('a.set_speed')) {
    if (element !== null) {
      function handleClick(event: Event) {
        // Don't reload the page (due to href="#").
        event.preventDefault();
        // Get the value of the `data` attribute on the dropdown option.
        const value = element.getAttribute('data');
        // Find the input element referenced by the dropdown element.
        const input = document.getElementById(element.target) as Nullable<HTMLInputElement>;
        if (input !== null && value !== null) {
          // Set the value of the input field to the `data` attribute's value.
          input.value = value;
        }
      }
      element.addEventListener('click', handleClick);
    }
  }
}
