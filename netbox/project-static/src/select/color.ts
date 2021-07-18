import SlimSelect from 'slim-select';
import { readableColor } from 'color2k';
import { getElements } from '../util';

import type { Option } from 'slim-select/dist/data';

/**
 * Determine if the option has a valid value (i.e., is not the placeholder).
 */
function canChangeColor(option: Option | HTMLOptionElement): boolean {
  return typeof option.value === 'string' && option.value !== '';
}

/**
 * Initialize color selection widget. Dynamically change the style of the select container to match
 * the selected option.
 */
export function initColorSelect(): void {
  for (const select of getElements<HTMLSelectElement>('select.netbox-color-select')) {
    for (const option of select.options) {
      if (canChangeColor(option)) {
        // Get the background color from the option's value.
        const bg = `#${option.value}`;
        // Determine an accessible foreground color based on the background color.
        const fg = readableColor(bg);

        // Set the option's style attributes.
        option.style.backgroundColor = bg;
        option.style.color = fg;
      }
    }

    const instance = new SlimSelect({
      select,
      allowDeselect: true,
      // Inherit the calculated color on the deselect icon.
      deselectLabel: `<i class="mdi mdi-close-circle" style="color: currentColor;"></i>`,
    });

    // Style the select container to match any pre-selectd options.
    for (const option of instance.data.data) {
      if ('selected' in option && option.selected) {
        styleContainer(option);
        break;
      }
    }

    // Don't inherit the select element's classes.
    for (const className of select.classList) {
      instance.slim.container.classList.remove(className);
    }

    function styleContainer(option: Option | HTMLOptionElement): void {
      if (instance.slim.singleSelected !== null) {
        if (canChangeColor(option)) {
          // Get the background color from the selected option's value.
          const bg = `#${option.value}`;
          // Determine an accessible foreground color based on the background color.
          const fg = readableColor(bg);

          // Set the container's style attributes.
          instance.slim.singleSelected.container.style.backgroundColor = bg;
          instance.slim.singleSelected.container.style.color = fg;

          // Find this element's label.
          const label = document.querySelector<HTMLLabelElement>(`label[for=${select.id}]`);

          if (label !== null) {
            // Set the field's label color to match (Bootstrap sets the opacity to 0.65 as well).
            label.style.color = fg;
          }
        } else {
          // If the color cannot be set (i.e., the placeholder), remove any inline styles.
          instance.slim.singleSelected.container.removeAttribute('style');
        }
      }
    }

    // Change the SlimSelect container's style based on the selected option.
    instance.onChange = styleContainer;
  }
}
