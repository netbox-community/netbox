import { readableColor } from 'color2k';

import type SlimSelect from 'slim-select';

/**
 * Add or remove a class to the SlimSelect element to match Bootstrap .form-select:disabled styles.
 *
 * @param action `enable` or `disable`
 * @param instance Instance of SlimSelect
 */
export function toggle(action: 'enable' | 'disable', instance: SlimSelect): void {
  if (action === 'enable') {
    if (instance.slim.singleSelected !== null) {
      if (instance.slim.singleSelected.container.hasAttribute('disabled')) {
        instance.slim.singleSelected.container.removeAttribute('disabled');
      }
    } else if (instance.slim.multiSelected !== null) {
      if (instance.slim.multiSelected.container.hasAttribute('disabled')) {
        instance.slim.multiSelected.container.removeAttribute('disabled');
      }
    }
  } else if (action === 'disable') {
    if (instance.slim.singleSelected !== null) {
      if (!instance.slim.singleSelected.container.hasAttribute('disabled')) {
        instance.slim.singleSelected.container.setAttribute('disabled', '');
      }
    } else if (instance.slim.multiSelected !== null) {
      if (!instance.slim.multiSelected.container.hasAttribute('disabled')) {
        instance.slim.multiSelected.container.setAttribute('disabled', '');
      }
    }
  }
}

/**
 * Add scoped style elements specific to each SlimSelect option, if the color property exists.
 * As of this writing, this attribute only exist on Tags. The color property is used as the
 * background color, and a foreground color is detected based on the luminosity of the background
 * color.
 *
 * @param instance SlimSelect instance with options already set.
 */
export function setOptionStyles(instance: SlimSelect): void {
  console.log('1', instance);
  const options = instance.data.data;
  for (const option of options) {
    // Only create style elements for options that contain a color attribute.
    if (
      'data' in option &&
      'id' in option &&
      typeof option.data !== 'undefined' &&
      typeof option.id !== 'undefined' &&
      'color' in option.data
    ) {
      const id = option.id as string;
      const data = option.data as { color: string };

      // Create the style element.
      const style = document.createElement('style');

      // Append hash to color to make it a valid hex color.
      const bg = `#${data.color}`;
      // Detect the foreground color.
      const fg = readableColor(bg);

      // Add a unique identifier to the style element.
      style.dataset.netbox = id;

      // Scope the CSS to apply both the list item and the selected item.
      style.innerHTML = `
div.ss-values div.ss-value[data-id="${id}"],
div.ss-list div.ss-option:not(.ss-disabled)[data-id="${id}"]
 {
  background-color: ${bg} !important;
  color: ${fg} !important;
}
            `
        .replaceAll('\n', '')
        .trim();

      // Add the style element to the DOM.
      document.head.appendChild(style);
    }
  }
}

/**
 * Determine if a select element should be filtered by the value of another select element.
 *
 * Looks for the DOM attribute `data-query-param-<name of other field>`, which would look like:
 * `["$<name>"]`
 *
 * If the attribute exists, parse out the raw value. In the above example, this would be `name`.
 *
 * @param element Element to scan
 * @returns Attribute name, or null if it was not found.
 */
export function getFilteredBy<T extends HTMLElement>(element: T): string[] {
  const pattern = new RegExp(/\[|\]|"|\$/g);
  const keys = Object.keys(element.dataset);
  const filteredBy = [] as string[];

  // Process the URL attribute in a separate loop so that it comes first.
  for (const key of keys) {
    if (key === 'url' && element.dataset.url?.includes(`{{`)) {
      /**
       * If the URL contains a Django/Jinja template variable tag we need to extract the variable
       * name and consider this a field to monitor for changes.
       */
      const value = element.dataset.url.match(/\{\{(.+)\}\}/);
      if (value !== null) {
        filteredBy.push(value[1]);
      }
    }
  }
  for (const key of keys) {
    if (key.includes('queryParam') && key !== 'queryParamExclude') {
      const value = element.dataset[key];
      if (typeof value !== 'undefined') {
        const parsed = JSON.parse(value) as string | string[];
        if (Array.isArray(parsed)) {
          filteredBy.push(parsed[0].replaceAll(pattern, ''));
        } else {
          filteredBy.push(value.replaceAll(pattern, ''));
        }
      }
    }
  }
  return filteredBy;
}
