import SlimSelect from 'slim-select';
import queryString from 'query-string';
import { getApiData, isApiError, getElements, isTruthy } from '../util';
import { createToast } from '../toast';
import { setOptionStyles, getFilteredBy, toggle } from './util';

import type { Option } from 'slim-select/dist/data';

type WithUrl = {
  url: string;
};

type WithExclude = {
  queryParamExclude: string;
};

type ReplaceTuple = [RegExp, string];

interface CustomSelect<T extends Record<string, string>> extends HTMLSelectElement {
  dataset: T;
}

function isCustomSelect(el: HTMLSelectElement): el is CustomSelect<WithUrl> {
  return typeof el?.dataset?.url === 'string';
}

function hasExclusions(el: HTMLSelectElement): el is CustomSelect<WithExclude> {
  return (
    typeof el?.dataset?.queryParamExclude === 'string' && el?.dataset?.queryParamExclude !== ''
  );
}

const DISABLED_ATTRIBUTES = ['occupied'] as string[];

// Various one-off patterns to replace in query param keys.
const REPLACE_PATTERNS = [
  // Don't query `termination_a_device=1`, but rather `device=1`.
  [new RegExp(/termination_(a|b)_(.+)/g), '$2_id'],
  // For example, a tenant's group relationship field is `group`, but the field name
  // is `tenant_group`.
  [new RegExp(/.+_(group)/g), '$1_id'],
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
    .filter(option => option.value !== '')
    .map(option => option.value);

  return getApiData(url).then(data => {
    if (isApiError(data)) {
      const toast = createToast('danger', data.exception, data.error);
      toast.show();
      return [PLACEHOLDER];
    }

    const { results } = data;
    const options = [PLACEHOLDER] as Option[];

    for (const result of results) {
      const text = getDisplayName(result, select);
      const data = {} as Record<string, string>;
      const value = result.id.toString();

      // Set any primitive k/v pairs as data attributes on each option.
      for (const [k, v] of Object.entries(result)) {
        if (!['id', 'slug'].includes(k) && ['string', 'number', 'boolean'].includes(typeof v)) {
          const key = k.replaceAll('_', '-');
          data[key] = String(v);
        }
      }

      let style, selected, disabled;

      // Set pre-selected options.
      if (selectOptions.includes(value)) {
        selected = true;
      }

      // Set option to disabled if it is contained within the disabled array.
      if (selectOptions.some(option => disabledOptions.includes(option))) {
        disabled = true;
      }

      // Set option to disabled if the result contains a matching key and is truthy.
      if (DISABLED_ATTRIBUTES.some(key => Object.keys(result).includes(key) && result[key])) {
        disabled = true;
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
  });
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
  for (const select of getElements<HTMLSelectElement>('.netbox-select2-api')) {
    const filterMap = getFilteredBy(select);
    // Initialize an event, so other elements relying on this element can subscribe to this
    // element's value.
    const event = new Event(`netbox.select.onload.${select.name}`);
    // Query Parameters - will have attributes added below.
    const query = {} as Record<string, string>;
    // List of OTHER elements THIS element relies on for query filtering.
    const groupBy = [] as HTMLSelectElement[];

    if (isCustomSelect(select)) {
      // Store the original URL, so it can be referred back to as filter-by elements change.
      const originalUrl = JSON.parse(JSON.stringify(select.dataset.url)) as string;
      // Unpack the original URL with the intent of reassigning it as context updates.
      let { url } = select.dataset;

      const placeholder = getPlaceholder(select);

      let disabledOptions = [] as string[];
      if (hasExclusions(select)) {
        try {
          const exclusions = JSON.parse(select.dataset.queryParamExclude) as string[];
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
        deselectLabel: `<i class="bi bi-x-circle" style="color:currentColor;"></i>`,
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

      for (let [key, value] of filterMap) {
        if (value === '') {
          // An empty value is set if the key contains a `$`, indicating reliance on another field.
          const elem = document.querySelector(`[name=${key}]`) as HTMLSelectElement;
          if (elem !== null) {
            groupBy.push(elem);
            if (elem.value !== '') {
              // If the element's form value exists, add it to the map.
              value = elem.value;
              filterMap.set(key, elem.value);
            }
          }
        }

        // A non-empty value indicates a static query parameter.
        for (const [pattern, replacement] of REPLACE_PATTERNS) {
          // Check the query param key to see if we should modify it.
          if (key.match(pattern)) {
            key = key.replaceAll(pattern, replacement);
          }
        }

        if (url.includes(`{{`) && value !== '') {
          // If the URL contains a Django/Jinja template variable, we need to replace the
          // tag with the event's value.
          url = url.replaceAll(new RegExp(`{{${key}}}`, 'g'), value);
          select.setAttribute('data-url', url);
        }

        // Add post-replaced key/value pairs to the query object.
        if (isTruthy(value)) {
          query[key] = value;
        }
      }

      url = queryString.stringifyUrl({ url, query });

      /**
       * When the group's selection changes, re-query the dependant element's options, but
       * filtered to results matching the group's ID.
       *
       * @param event Group's DOM event.
       */
      function handleEvent(event: Event) {
        const target = event.target as HTMLSelectElement;

        if (isTruthy(target.value)) {
          let name = target.name;

          for (const [pattern, replacement] of REPLACE_PATTERNS) {
            // Check the query param key to see if we should modify it.
            if (name.match(pattern)) {
              name = name.replaceAll(pattern, replacement);
            }
          }

          if (url.includes(`{{`) && target.name && target.value) {
            // If the URL (still) contains a Django/Jinja template variable, we need to replace
            // the tag with the event's value.
            url = url.replaceAll(new RegExp(`{{${target.name}}}`, 'g'), target.value);
            select.setAttribute('data-url', url);
          }

          if (filterMap.get(target.name) === '') {
            // Update empty filter map values now that there is a value.
            filterMap.set(target.name, target.value);
          }
          // Add post-replaced key/value pairs to the query object.
          query[name] = target.value;
          // Create a URL with all relevant query parameters.
          url = queryString.stringifyUrl({ url, query });
        } else {
          url = originalUrl;
        }

        // Disable the element while data is loading.
        toggle('disable', instance);
        // Load new data.
        getOptions(url, select, disabledOptions)
          .then(data => instance.setData(data))
          .finally(() => {
            // Re-enable the element after data has loaded.
            toggle('enable', instance);
            // Inform any event listeners that data has updated.
            select.dispatchEvent(event);
          });
        // Stop event bubbling.
        event.preventDefault();
      }

      for (const group of groupBy) {
        // Re-fetch data when the group changes.
        group.addEventListener('change', handleEvent);

        // Subscribe this instance (the child that relies on `group`) to any changes of the
        // group's value, so we can re-render options.
        select.addEventListener(`netbox.select.onload.${group.name}`, handleEvent);
      }

      // Load data.
      getOptions(url, select, disabledOptions)
        .then(options => instance.setData(options))
        .finally(() => {
          // Set option styles, if the field calls for it (color selectors).
          setOptionStyles(instance);
          // Enable the element after data has loaded.
          toggle('enable', instance);
          // Inform any event listeners that data has updated.
          select.dispatchEvent(event);
        });

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
