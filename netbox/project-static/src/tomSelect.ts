import { getElements } from './util';
import { RecursivePartial, TomInput, TomOption, TomSettings } from 'tom-select/src/types';
import { addClasses } from 'tom-select/src/vanilla'
import queryString from 'query-string';
import TomSelect from 'tom-select';
import type { Stringifiable } from 'query-string';

// Transitional
import { QueryFilter } from './select/api/types'


class DynamicTomSelect extends TomSelect {

  /*
   * Transitional code from APISelect
   */
  private readonly queryParams: QueryFilter = new Map();
  private readonly staticParams: QueryFilter = new Map();

  /**
   * Overrides
   */

  constructor( input_arg: string|TomInput, user_settings: RecursivePartial<TomSettings> ) {
    super(input_arg, user_settings);

    this.api_url = this.input.getAttribute('data-url') as string;

    // Populate static query parameters.
    this.getStaticParams();
    for (const [key, value] of this.staticParams.entries()) {
      this.queryParams.set(key, value);
    }
  }

  load(value: string) {
    const self = this;

    // Automatically clear any cached options. (Only options included
    // in the API response should be present.)
    if (value) {
      self.clearOptions();
    }

    addClasses(self.wrapper, self.settings.loadingClass);
    self.loading++;

    const callback = self.loadCallback.bind(self);
    const url = self.getRequestUrl(value);

    // Make the API request
    fetch(url)
      .then(response => response.json())
      .then(json => {
          callback(json.results);
      }).catch(()=>{
          callback();
      });

  }

  /**
   * Custom methods
   */

  /**
   * Formulate and return the complete URL for an API request, including any query parameters.
   */
  getRequestUrl(search: string): string {
    const url = this.api_url;

    // Create new URL query parameters based on the current state of `queryParams` and create an
    // updated API query URL.
    const query = {} as Dict<Stringifiable[]>;
    for (const [key, value] of this.queryParams.entries()) {
      query[key] = value;
    }

    // Append the search query, if any
    if (search) {
      query['q'] = [search];
    }

    // Enable "brief" mode
    query['brief'] = ['True'];

    return queryString.stringifyUrl({ url, query });
  }

  /**
   * Transitional methods
   */

  /**
   * Determine if this instance's options should be filtered by static values passed from the
   * server.
   *
   * Looks for the DOM attribute `data-static-params`, the value of which is a JSON array of
   * objects containing key/value pairs to add to `this.staticParams`.
   */
  private getStaticParams(): void {
    const serialized = this.input.getAttribute('data-static-params');

    try {
      if (serialized) {
        const deserialized = JSON.parse(serialized);
        if (deserialized) {
          for (const { queryParam, queryValue } of deserialized) {
            if (Array.isArray(queryValue)) {
              this.staticParams.set(queryParam, queryValue);
            } else {
              this.staticParams.set(queryParam, [queryValue]);
            }
          }
        }
      }
    } catch (err) {
      console.group(`Unable to determine static query parameters for select field '${this.name}'`);
      console.warn(err);
      console.groupEnd();
    }
  }

}

// Initialize <select> elements with statically-defined options
function initStaticSelects(): void {

  for (const select of getElements<HTMLSelectElement>('select:not(.api-select):not(.color-select)')) {
    new TomSelect(select, {
      plugins: ['clear_button']
    });
  }

}

// Initialize <select> elements which are populated via a REST API call
function initDynamicSelects(): void {

  for (const select of getElements<HTMLSelectElement>('select.api-select')) {
    new DynamicTomSelect(select, {
      plugins: ['clear_button'],
      valueField: 'id',
      labelField: 'display',
      searchField: [],
      copyClassesToDropdown: false,
      dropdownParent: 'body',
      controlInput: '<input>',
      preload: 'focus',
	});
  }

}

// Initialize color selection fields
function initColorSelects(): void {

  for (const select of getElements<HTMLSelectElement>('select.color-select')) {
    new TomSelect(select, {
      render: {
        option: function(item: TomOption, escape: Function) {
          return `<div style="background-color: #${escape(item.value)}">${escape(item.text)}</div>`;
        }
      }
    });
  }

}

export function initSelects(): void {
  initStaticSelects();
  initDynamicSelects();
  initColorSelects();
}
