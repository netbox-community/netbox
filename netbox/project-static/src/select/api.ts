import SlimSelect from 'slim-select';
import queryString from 'query-string';
import {
  getApiData,
  isApiError,
  getElements,
  isTruthy,
  hasError,
  findFirstAdjacent,
} from '../util';
import { createToast } from '../bs';
import { setOptionStyles, toggle, getDependencyIds, initResetButton } from './util';

import type { Option } from 'slim-select/dist/data';

type WithUrl = {
  'data-url': string;
};

type WithExclude = {
  queryParamExclude: string;
};

type ReplaceTuple = [RegExp, string];

type CustomSelect<T extends Record<string, string>> = HTMLSelectElement & T;

function hasUrl(el: HTMLSelectElement): el is CustomSelect<WithUrl> {
  const value = el.getAttribute('data-url');
  return typeof value === 'string' && value !== '';
}

function hasExclusions(el: HTMLSelectElement): el is CustomSelect<WithExclude> {
  const exclude = el.getAttribute('data-query-param-exclude');
  return typeof exclude === 'string' && exclude !== '';
}

const DISABLED_ATTRIBUTES = ['occupied'] as string[];

// Various one-off patterns to replace in query param keys.
const REPLACE_PATTERNS = [
  // Don't query `termination_a_device=1`, but rather `device=1`.
  [new RegExp(/termination_(a|b)_(.+)/g), '$2_id'],
  // A tenant's group relationship field is `group`, but the field name is `tenant_group`.
  [new RegExp(/tenant_(group)/g), '$1_id'],
  // Append `_id` to any fields
  [new RegExp(/^([A-Za-z0-9]+)(_id)?$/g), '$1_id'],
] as ReplaceTuple[];

const PLACEHOLDER = {
  value: '',
  text: '',
  placeholder: true,
} as Option;

/**
 * Retrieve all objects for this object type.
 *
 * @param url API endpoint to query.
 *
 * @returns Data parsed into SlimSelect options.
 */
async function getOptions(
  url: string,
  select: HTMLSelectElement,
  disabledOptions: string[],
): Promise<Option[]> {
  if (url.includes(`{{`)) {
    return [PLACEHOLDER];
  }

  // Get all non-placeholder (empty) options' values. If any exist, it means we're editing an
  // existing object. When we fetch options from the API later, we can set any of the options
  // contained in this array to `selected`.
  const selectOptions = Array.from(select.options)
    .map(option => option.getAttribute('value'))
    .filter(isTruthy);

  const data = await getApiData(url);
  if (hasError(data)) {
    if (isApiError(data)) {
      createToast('danger', data.exception, data.error).show();
      return [PLACEHOLDER];
    }
    createToast('danger', `Error Fetching Options for field ${select.name}`, data.error).show();
    return [PLACEHOLDER];
  }

  const { results } = data;
  const options = [PLACEHOLDER] as Option[];

  for (const result of results) {
    const text = getDisplayName(result, select);
    const data = {} as Record<string, string>;
    const value = result.id.toString();
    let style, selected, disabled;

    // Set any primitive k/v pairs as data attributes on each option.
    for (const [k, v] of Object.entries(result)) {
      if (!['id', 'slug'].includes(k) && ['string', 'number', 'boolean'].includes(typeof v)) {
        const key = k.replaceAll('_', '-');
        data[key] = String(v);
      }
      // Set option to disabled if the result contains a matching key and is truthy.
      if (DISABLED_ATTRIBUTES.some(key => key.toLowerCase() === k.toLowerCase())) {
        if (typeof v === 'string' && v.toLowerCase() !== 'false') {
          disabled = true;
        } else if (typeof v === 'boolean' && v === true) {
          disabled = true;
        } else if (typeof v === 'number' && v > 0) {
          disabled = true;
        }
      }
    }

    // Set option to disabled if it is contained within the disabled array.
    if (selectOptions.some(option => disabledOptions.includes(option))) {
      disabled = true;
    }

    // Set pre-selected options.
    if (selectOptions.includes(value)) {
      selected = true;
      // If an option is selected, it can't be disabled. Otherwise, it won't be submitted with
      // the rest of the form, resulting in that field's value being deleting from the object.
      disabled = false;
    }

    const option = {
      value,
      text,
      data,
      style,
      selected,
      disabled,
    } as Option;

    options.push(option);
  }
  return options;
}

/**
 * Find the select element's placeholder text/label.
 */
function getPlaceholder(select: HTMLSelectElement): string {
  let placeholder = select.name;
  if (select.id) {
    const label = document.querySelector(`label[for=${select.id}]`) as HTMLLabelElement;

    // Set the placeholder text to the label value, if it exists.
    if (label !== null) {
      placeholder = `Select ${label.innerText.trim()}`;
    }
  }
  return placeholder;
}

/**
 * Find this field's display name.
 * @param select
 * @returns
 */
function getDisplayName(result: APIObjectBase, select: HTMLSelectElement): string {
  let displayName = result.display;

  const legacyDisplayProperty = select.getAttribute('display-field');

  if (
    typeof displayName === 'undefined' &&
    legacyDisplayProperty !== null &&
    legacyDisplayProperty in result
  ) {
    displayName = result[legacyDisplayProperty] as string;
  }

  if (!displayName) {
    displayName = result.name;
  }

  return displayName;
}

/**
 * Initialize select elements that rely on the NetBox API to build their options.
 */
export function initApiSelect() {
  for (const select of getElements<HTMLSelectElement>('.netbox-api-select')) {
    const dependencies = getDependencyIds(select);
    // Initialize an event, so other elements relying on this element can subscribe to this
    // element's value.
    const event = new Event(`netbox.select.onload.${select.name}`);
    // Query Parameters - will have attributes added below.
    const query = { limit: 0 } as Record<string, string | number>;

    if (hasUrl(select)) {
      // Store the original URL, so it can be referred back to as filter-by elements change.
      // const originalUrl = select.getAttribute('data-url') as string;
      // Get the original URL with the intent of reassigning it as context updates.
      let url = select.getAttribute('data-url') ?? '';

      const placeholder = getPlaceholder(select);

      let disabledOptions = [] as string[];
      if (hasExclusions(select)) {
        try {
          const exclusions = JSON.parse(
            select.getAttribute('data-query-param-exclude') ?? '[]',
          ) as string[];
          disabledOptions = [...disabledOptions, ...exclusions];
        } catch (err) {
          console.warn(
            `Unable to parse data-query-param-exclude value on select element '${select.name}': ${err}`,
          );
        }
      }

      const instance = new SlimSelect({
        select,
        allowDeselect: true,
        deselectLabel: `<i class="mdi mdi-close-circle" style="color:currentColor;"></i>`,
        placeholder,
        onChange() {
          const element = instance.slim.container ?? null;
          if (element !== null) {
            // Reset validity classes if the field was invalid.
            if (
              element.classList.contains('is-invalid') ||
              select.classList.contains('is-invalid')
            ) {
              select.classList.remove('is-invalid');
              element.classList.remove('is-invalid');
            }
          }
          select.dispatchEvent(event);
        },
      });

      // Disable the element while data has not been loaded.
      toggle('disable', instance);

      // Don't copy classes from select element to SlimSelect instance.
      for (const className of select.classList) {
        instance.slim.container.classList.remove(className);
      }

      /**
       * Update an element's API URL based on the value of another element upon which this element
       * relies.
       *
       * @param id DOM ID of the other element.
       */
      function updateQuery(id: string) {
        let key = id;
        // Find the element dependency.
        const element = document.getElementById(`id_${id}`) as Nullable<HTMLSelectElement>;
        if (element !== null) {
          if (element.value !== '') {
            // If the dependency has a value, parse the dependency's name (form key) for any
            // required replacements.
            for (const [pattern, replacement] of REPLACE_PATTERNS) {
              if (id.match(pattern)) {
                key = id.replaceAll(pattern, replacement);
                break;
              }
            }
            // If this element's URL contains Django template tags ({{), replace the template tag
            // with the the dependency's value. For example, if the dependency is the `rack` field,
            // and the `rack` field's value is `1`, this element's URL would change from
            // `/dcim/racks/{{rack}}/` to `/dcim/racks/1/`.
            if (url.includes(`{{`)) {
              for (const test of url.matchAll(new RegExp(`({{(${id}|${key})}})`, 'g'))) {
                // The template tag may contain the original element name or the post-parsed value.
                url = url.replaceAll(test[1], element.value);
              }
              // Set the DOM attribute to reflect the change.
              select.setAttribute('data-url', url);
            }
          }
          if (isTruthy(element.value)) {
            // Add the dependency's value to the URL query.
            query[key] = element.value;
          }
        }
      }
      // Process each of the dependencies, updating this element's URL or other attributes as
      // needed.
      for (const dep of dependencies) {
        updateQuery(dep);
      }

      // Create a valid encoded URL with all query params.
      url = queryString.stringifyUrl({ url, query });

      /**
       * When the group's selection changes, re-query the dependant element's options, but
       * filtered to results matching the group's ID.
       *
       * @param event Group's DOM event.
       */
      function handleEvent(event: Event) {
        const target = event.target as HTMLSelectElement;
        // Update the element's URL after any changes to a dependency.
        updateQuery(target.id);

        // Disable the element while data is loading.
        toggle('disable', instance);
        // Load new data.
        getOptions(url, select, disabledOptions)
          .then(data => instance.setData(data))
          .catch(console.error)
          .finally(() => {
            // Re-enable the element after data has loaded.
            toggle('enable', instance);
            // Inform any event listeners that data has updated.
            select.dispatchEvent(event);
          });
      }

      for (const dep of dependencies) {
        const element = document.getElementById(`id_${dep}`);
        if (element !== null) {
          element.addEventListener('change', handleEvent);
        }
        select.addEventListener(`netbox.select.onload.${dep}`, handleEvent);
      }

      /**
       * Load this element's options from the NetBox API.
       */
      async function loadData(): Promise<void> {
        try {
          const options = await getOptions(url, select, disabledOptions);
          instance.setData(options);
        } catch (err) {
          console.error(err);
        } finally {
          setOptionStyles(instance);
          toggle('enable', instance);
          select.dispatchEvent(event);
        }
      }

      /**
       * Delete this element's options.
       */
      function clearData(): void {
        return instance.setData([]);
      }

      // Determine if this element is part of collapsible element.
      const collapse = findFirstAdjacent(select, '.collapse', '.content-container');
      if (collapse !== null) {
        // If this element is part of a collapsible element, only load the data when the
        // collapsible element is shown.
        // See: https://getbootstrap.com/docs/5.0/components/collapse/#events
        collapse.addEventListener('show.bs.collapse', loadData);
        collapse.addEventListener('hide.bs.collapse', clearData);
      } else {
        // Otherwise, load the data on render.
        Promise.all([loadData()]);
      }

      // Bind event listener to
      initResetButton(select, instance);

      // Set the underlying select element to the same size as the SlimSelect instance.
      // This is primarily for built-in HTML form validation, which doesn't really work,
      // but it also makes things seem cleaner in the DOM.
      const { width, height } = instance.slim.container.getBoundingClientRect();
      select.style.opacity = '0';
      select.style.width = `${width}px`;
      select.style.height = `${height}px`;
      select.style.display = 'block';
      select.style.position = 'absolute';
      select.style.pointerEvents = 'none';
    }
  }
}
