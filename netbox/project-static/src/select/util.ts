import { readableColor } from 'color2k';
import { findFirstAdjacent, getElements } from '../util';

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
      style.setAttribute('data-netbox', id);

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
 * @returns Map of attributes to values. An empty value indicates a dynamic property that will
 *          be updated later.
 */
export function getFilteredBy<T extends HTMLElement>(element: T): Map<string, string> {
  const pattern = new RegExp(/\[|\]|"|\$/g);
  const keyPattern = new RegExp(/data-query-param-/g);

  // Extract data attributes.
  const keys = Object.values(element.attributes)
    .map(v => v.name)
    .filter(v => v.includes('data'));

  const filterMap = new Map<string, string>();

  // Process the URL attribute in a separate loop so that it comes first.
  for (const key of keys) {
    const url = element.getAttribute('data-url');
    if (key === 'data-url' && url !== null && url.includes(`{{`)) {
      // If the URL contains a Django/Jinja template variable tag we need to extract the variable
      // name and consider this a field to monitor for changes.
      const value = url.match(/\{\{(.+)\}\}/);
      if (value !== null) {
        filterMap.set(value[1], '');
      }
    }
  }
  for (const key of keys) {
    if (key.match(keyPattern) && key !== 'data-query-param-exclude') {
      const value = element.getAttribute(key);
      if (value !== null) {
        try {
          const parsed = JSON.parse(value) as string | string[];
          if (Array.isArray(parsed)) {
            for (const item of parsed) {
              if (item.match(/^\$.+$/g)) {
                const replaced = item.replaceAll(pattern, '');
                filterMap.set(replaced, '');
              } else {
                filterMap.set(key.replaceAll(keyPattern, ''), item);
              }
            }
          } else {
            if (parsed.match(/^\$.+$/g)) {
              const replaced = parsed.replaceAll(pattern, '');
              filterMap.set(replaced, '');
            } else {
              filterMap.set(key.replaceAll(keyPattern, ''), parsed);
            }
          }
        } catch (err) {
          console.warn(err);
          if (value.match(/^\$.+$/g)) {
            const replaced = value.replaceAll(pattern, '');
            filterMap.set(replaced, '');
          } else {
            filterMap.set(key.replaceAll(keyPattern, ''), value);
          }
        }
      }
    }
  }
  return filterMap;
}

function* getAllDependencyIds<E extends HTMLElement>(element: Nullable<E>): Generator<string> {
  const keyPattern = new RegExp(/data-query-param-/g);
  if (element !== null) {
    for (const attr of element.attributes) {
      if (attr.name.startsWith('data-query-param') && attr.name !== 'data-query-param-exclude') {
        const dep = attr.name.replaceAll(keyPattern, '');
        yield dep;
        for (const depNext of getAllDependencyIds(document.getElementById(`id_${dep}`))) {
          yield depNext;
        }
      } else if (attr.name === 'data-url' && attr.value.includes(`{{`)) {
        const value = attr.value.match(/\{\{(.+)\}\}/);
        if (value !== null) {
          const dep = value[1];
          yield dep;
          for (const depNext of getAllDependencyIds(document.getElementById(`id_${dep}`))) {
            yield depNext;
          }
        }
      }
    }
  }
}

export function getDependencyIds<E extends HTMLElement>(element: Nullable<E>): string[] {
  const ids = new Set<string>(getAllDependencyIds(element));
  return Array.from(ids).map(i => i.replaceAll('_id', ''));
}

/**
 * Initialize any adjacent reset buttons so that when clicked, the instance's selected value is cleared.
 *
 * @param select Select Element
 * @param instance SlimSelect Instance
 */
export function initResetButton(select: HTMLSelectElement, instance: SlimSelect) {
  const resetButton = findFirstAdjacent<HTMLButtonElement>(select, 'button[data-reset-select');
  if (resetButton !== null) {
    resetButton.addEventListener('click', () => {
      select.value = '';
      if (select.multiple) {
        instance.setSelected([]);
      } else {
        instance.setSelected('');
      }
    });
  }
}
