import SlimSelect from 'slim-select';
import queryString from 'query-string';
import { getApiData, isApiError } from '../util';
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

const PLACEHOLDER = {
  value: '',
  text: '',
  placeholder: true,
} as Option;

export function initApiSelect() {
  const elements = document.querySelectorAll<HTMLSelectElement>('.netbox-select2-api');
  for (const select of elements) {
    // Get all non-placeholder (empty) options' values. If any exist, it means we're editing an
    // existing object. When we fetch options from the API later, we can set any of the options
    // contained in this array to `selected`.
    const selectOptions = Array.from(select.options)
      .filter(option => option.value !== '')
      .map(option => option.value);

    const filteredBy = getFilteredBy(select);
    const filterMap = new Map<string, string>();

    if (isCustomSelect(select)) {
      let { url } = select.dataset;
      const displayField = select.getAttribute('display-field') ?? 'name';

      // Set the placeholder text to the label value, if it exists.
      let placeholder;
      if (select.id) {
        const label = document.querySelector(`label[for=${select.id}]`) as HTMLLabelElement;

        if (label !== null) {
          placeholder = `Select ${label.innerText.trim()}`;
        }
      }
      let disabledOptions = [] as string[];
      if (hasExclusions(select)) {
        disabledOptions = JSON.parse(select.dataset.queryParamExclude) as string[];
      }

      const instance = new SlimSelect({
        select,
        allowDeselect: true,
        deselectLabel: `<i class="bi bi-x-circle" style="color:currentColor;"></i>`,
        placeholder,
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

      // Don't copy classes from select element to SlimSelect instance.
      for (const className of select.classList) {
        instance.slim.container.classList.remove(className);
      }

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

      /**
       * Retrieve all objects for this object type.
       *
       * @param choiceUrl Optionally override the URL for filtering. If not set, the URL
       *                  from the DOM attributes is used.
       * @returns Data parsed into Choices.JS Choices.
       */
      async function getChoices(choiceUrl: string = url): Promise<Option[]> {
        if (choiceUrl.includes(`{{`)) {
          return [PLACEHOLDER];
        }
        return getApiData(choiceUrl).then(data => {
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
              let style, selected;
              for (const [k, v] of Object.entries(result)) {
                if (
                  !['id', 'slug'].includes(k) &&
                  ['string', 'number', 'boolean'].includes(typeof v)
                ) {
                  const key = k.replaceAll('_', '-');
                  data[key] = String(v);
                }
              }
              if (selectOptions.includes(value)) {
                selected = true;
              }

              const choice = {
                value,
                text: result[displayField],
                data,
                style,
                selected,
              } as Option;

              options.push(choice);
            }
          }
          return options;
        });
      }

      if (filteredBy.length !== 0) {
        for (const filter of filteredBy) {
          // Find element with the `name` attribute matching this element's filtered-by attribute.
          const groupElem = document.querySelector(`[name=${filter}]`) as HTMLSelectElement;

          if (groupElem !== null) {
            // Add the group's value to the filtered-by map.
            filterMap.set(filter, groupElem.value);
            // If the URL contains a Django/Jinja template variable tag, we need to replace the tag
            // with the event's value.
            if (url.includes(`{{`)) {
              url = url.replaceAll(new RegExp(`{{${filter}}}`, 'g'), groupElem.value);
              select.setAttribute('data-url', url);
            }
            /**
             * When the group's selection changes, re-query the dependant element's options, but
             * filtered to results matching the group's ID.
             *
             * @param event Group's DOM event.
             */
            function handleEvent(event: Event) {
              let filterUrl: string | undefined;

              const target = event.target as HTMLSelectElement;

              if (target.value) {
                let filterValue = filterMap.get(target.value);
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
                filterUrl = queryString.stringifyUrl({
                  url,
                  query: { [`${queryKey}_id`]: groupElem.value },
                });
              }

              getChoices(filterUrl).then(data => instance.setData(data));
            }

            groupElem.addEventListener('change', handleEvent);
            groupElem.addEventListener('change', handleEvent);
          }
        }
      }

      getChoices()
        .then(data => instance.setData(data))
        .finally(() => setOptionStyles(instance));
    }
  }
}
