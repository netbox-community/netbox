import SlimSelect from 'slim-select';
import queryString from 'query-string';
import { getApiData, isApiError, getElements } from '../util';
import { createToast } from '../toast';
import { setOptionStyles, getFilteredBy } from './util';

import type { Option } from 'slim-select/dist/data';

type WithUrl = {
  url: string;
};

type WithExclude = {
  queryParamExclude: string;
};

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
async function getChoices(
  url: string,
  displayField: string,
  selectOptions: string[],
  disabledOptions: string[],
): Promise<Option[]> {
  if (url.includes(`{{`)) {
    return [PLACEHOLDER];
  }
  return getApiData(url).then(data => {
    if (isApiError(data)) {
      const toast = createToast('danger', data.exception, data.error);
      toast.show();
      return [PLACEHOLDER];
    }

    const { results } = data;
    const options = [PLACEHOLDER] as Option[];

    if (results.length !== 0) {
      for (const result of results) {
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

        const choice = {
          value,
          text: result[displayField],
          data,
          style,
          selected,
          disabled,
        } as Option;

        options.push(choice);
      }
    }
    return options;
  });
}

export function initApiSelect() {
  for (const select of getElements<HTMLSelectElement>('.netbox-select2-api')) {
    // Get all non-placeholder (empty) options' values. If any exist, it means we're editing an
    // existing object. When we fetch options from the API later, we can set any of the options
    // contained in this array to `selected`.
    const selectOptions = Array.from(select.options)
      .filter(option => option.value !== '')
      .map(option => option.value);

    const filteredBy = getFilteredBy(select);
    const filterMap = new Map<string, string>();
    const event = new Event(`netbox.select.load.${select.name}`);

    if (isCustomSelect(select)) {
      let { url } = select.dataset;
      const displayField = select.getAttribute('display-field') ?? 'name';

      let placeholder: string = select.name;
      if (select.id) {
        const label = document.querySelector(`label[for=${select.id}]`) as HTMLLabelElement;

        // Set the placeholder text to the label value, if it exists.
        if (label !== null) {
          placeholder = `Select ${label.innerText.trim()}`;
        }
      }

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
      });

      // Disable the element while data has not been loaded.
      instance.disable();

      // Don't copy classes from select element to SlimSelect instance.
      for (const className of select.classList) {
        instance.slim.container.classList.remove(className);
      }

      // Load data.
      getChoices(url, displayField, selectOptions, disabledOptions)
        .then(options => instance.setData(options))
        .finally(() => {
          // Inform any event listeners that data has updated.
          select.dispatchEvent(event);
          // Enable the element after data has loaded.
          instance.enable();
          // Set option styles, if the field calls for it (color selectors). Note: this must be
          // done after instance.enable() since instance.enable() changes the element style.
          setOptionStyles(instance);
        });

      // Reset validity classes if the field was invalid.
      instance.onChange = () => {
        const element = instance.slim.container ?? null;
        if (element !== null) {
          if (element.classList.contains('is-invalid') || select.classList.contains('is-invalid')) {
            select.classList.remove('is-invalid');
            element.classList.remove('is-invalid');
          }
        }
      };

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

      for (const filter of filteredBy) {
        // Find element with the `name` attribute matching this element's filtered-by attribute.
        const groupElem = document.querySelector(`[name=${filter}]`) as HTMLSelectElement;

        if (groupElem !== null) {
          if (groupElem.value) {
            // Add the group's value to the filtered-by map.
            filterMap.set(filter, groupElem.value);
            // If the URL contains a Django/Jinja template variable tag, we need to replace the tag
            // with the event's value.
            if (url.includes(`{{`)) {
              url = url.replaceAll(new RegExp(`{{${filter}}}`, 'g'), groupElem.value);
              select.setAttribute('data-url', url);
            }
          }
          /**
           * When the group's selection changes, re-query the dependant element's options, but
           * filtered to results matching the group's ID.
           *
           * @param event Group's DOM event.
           */
          function handleEvent(event: Event) {
            let filterUrl = url;

            const target = event.target as HTMLSelectElement;

            if (target.value) {
              let filterValue = target.name;

              if (typeof filterValue === 'undefined') {
                filterMap.set(target.name, target.value);
              }

              if (url.includes(`{{`) && typeof filterValue !== 'undefined') {
                // If the URL contains a Django/Jinja template variable tag, we need to replace
                // the tag with the event's value.
                url = url.replaceAll(new RegExp(`{{${filter}}}`, 'g'), filterValue);
                select.setAttribute('data-url', url);
              }

              let queryKey = filterValue;
              if (filter?.includes('_group')) {
                // For example, a tenant's group relationship field is `group`, but the field
                // name is `tenant_group`.
                queryKey = 'group';
              }

              if (typeof queryKey !== 'undefined') {
                filterUrl = queryString.stringifyUrl({
                  url,
                  query: { [`${queryKey}_id`]: groupElem.value },
                });
              }
            }

            // Disable the element while data is loading.
            instance.disable();
            // Load new data.
            getChoices(filterUrl, displayField, selectOptions, disabledOptions)
              .then(data => instance.setData(data))
              .finally(() => {
                // Re-enable the element after data has loaded.
                instance.enable();
                // Set option styles, if the field calls for it (color selectors). Note: this must
                // be done after instance.enable() since instance.enable() changes the element
                // style.
                setOptionStyles(instance);
              });
          }
          // Re-fetch data when the group changes.
          groupElem.addEventListener('change', handleEvent);

          // Subscribe this instance (the child that relies on groupElem) to any changes of the
          // group's value, so we can re-render options.
          select.addEventListener(`netbox.select.onload.${groupElem.name}`, handleEvent);
        }
      }
    }
  }
}
