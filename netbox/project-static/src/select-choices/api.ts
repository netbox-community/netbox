import Choices from "choices.js";
import queryString from "query-string";
import { getApiData, isApiError } from "../util";
import { createToast } from "../toast";

import type { Choices as TChoices } from "choices.js";

interface CustomSelect extends HTMLSelectElement {
  dataset: {
    url: string;
  };
}

function isCustomSelect(el: HTMLSelectElement): el is CustomSelect {
  return typeof el?.dataset?.url === "string";
}

/**
 * Determine if a select element should be filtered by the value of another select element.
 *
 * Looks for the DOM attribute `data-query-param-<name of other field>`, which would look like:
 * `["$<name>"]`
 *
 * If the attribute exists, parse out the raw value. In the above example, this would be `name`.
 * @param element Element to scan
 * @returns Attribute name, or null if it was not found.
 */
function getFilteredBy<T extends HTMLElement>(element: T): string[] {
  const pattern = new RegExp(/\[|\]|"|\$/g);
  const keys = Object.keys(element.dataset);
  const filteredBy = [] as string[];
  for (const key of keys) {
    if (key.includes("queryParam")) {
      const value = element.dataset[key];
      if (typeof value !== "undefined") {
        const parsed = JSON.parse(value) as string | string[];
        if (Array.isArray(parsed)) {
          filteredBy.push(parsed[0].replaceAll(pattern, ""));
        } else {
          filteredBy.push(value.replaceAll(pattern, ""));
        }
      }
    }
    if (key === "url" && element.dataset.url?.includes(`{{`)) {
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
  return filteredBy;
}

export function initApiSelect() {
  const elements = document.querySelectorAll(
    ".netbox-select2-api"
  ) as NodeListOf<HTMLSelectElement>;

  for (const element of elements) {
    if (isCustomSelect(element)) {
      let { url } = element.dataset;

      const instance = new Choices(element, {
        noChoicesText: "No Options Available",
        itemSelectText: "",
      });

      /**
       * Retrieve all objects for this object type.
       *
       * @param choiceUrl Optionally override the URL for filtering. If not set, the URL
       *                  from the DOM attributes is used.
       * @returns Data parsed into Choices.JS Choices.
       */
      async function getChoices(
        choiceUrl: string = url
      ): Promise<TChoices.Choice[]> {
        if (choiceUrl.includes(`{{`)) {
          return [];
        }
        return getApiData(choiceUrl).then((data) => {
          if (isApiError(data)) {
            const toast = createToast("danger", data.exception, data.error);
            toast.show();
            return [];
          }
          const { results } = data;
          const options = [] as TChoices.Choice[];

          if (results.length !== 0) {
            for (const result of results) {
              const choice = {
                value: result.id.toString(),
                label: result.name,
              } as TChoices.Choice;
              options.push(choice);
            }
          }
          return options;
        });
      }

      const filteredBy = getFilteredBy(element);

      if (filteredBy.length !== 0) {
        for (const filter of filteredBy) {
          // Find element with the `name` attribute matching this element's filtered-by attribute.
          const groupElem = document.querySelector(
            `[name=${filter}]`
          ) as HTMLSelectElement;

          if (groupElem !== null) {
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
                if (url.includes(`{{`)) {
                  /**
                   * If the URL contains a Django/Jinja template variable tag, we need to replace
                   * the tag with the event's value.
                   */
                  url = url.replaceAll(/\{\{(.+)\}\}/g, target.value);
                  element.setAttribute("data-url", url);
                }
                let queryKey = filter;
                if (filter?.includes("_group")) {
                  /**
                   * For example, a tenant's group relationship field is `group`, but the field
                   * name is `tenant_group`.
                   */
                  queryKey = "group";
                }
                filterUrl = queryString.stringifyUrl({
                  url,
                  query: { [`${queryKey}_id`]: groupElem.value },
                });
              }

              instance.setChoices(
                () => getChoices(filterUrl),
                undefined,
                undefined,
                true
              );
            }
            groupElem.addEventListener("addItem", handleEvent);
            groupElem.addEventListener("removeItem", handleEvent);
          }
        }
      }

      instance.setChoices(() => getChoices());
    }
  }
}
