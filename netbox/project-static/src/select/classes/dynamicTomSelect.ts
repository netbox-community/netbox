import type { RecursivePartial, TomOption, TomSettings, TomInput } from 'tom-select/dist/cjs/types';
import { addClasses, removeClasses } from 'tom-select/src/vanilla.ts';
import queryString from 'query-string';
import type { Stringifiable } from 'query-string';
import { DynamicParamsMap } from './dynamicParamsMap';
import { NetBoxTomSelect } from './netboxTomSelect';

// Transitional
import { QueryFilter, PathFilter } from '../types';
import { getElement, replaceAll } from '../../util';

// Extends NetBoxTomSelect to provide enhanced fetching of options via the REST API
export class DynamicTomSelect extends NetBoxTomSelect {
  public readonly nullOption: Nullable<TomOption> = null;

  // Transitional code from APISelect
  private readonly queryParams: QueryFilter = new Map();
  private readonly staticParams: QueryFilter = new Map();
  private readonly dynamicParams: DynamicParamsMap = new DynamicParamsMap();
  private readonly pathValues: PathFilter = new Map();

  // Incremented on every load() call. Lets us detect and discard stale responses: if a
  // newer load() has started (e.g. because two dependencies changed in quick succession)
  // before an older request's response arrives, the older response is out of date and
  // must not be allowed to overwrite state set by the newer one.
  private loadSequence = 0;

  // Tracks a previous selection that still needs to be restored once a settled request wins.
  // Stored on the instance rather than only as a `load()` parameter -- if the request carrying
  // it is itself superseded by a later cascading load() call before it resolves, the value
  // isn't lost; whichever request's response ultimately wins can still attempt to restore it.
  private pendingRestoreValue?: string | string[];

  /**
   * Overrides
   */

  constructor(input_arg: string | TomInput, user_settings: RecursivePartial<TomSettings>) {
    super(input_arg, user_settings);

    // Glean the REST API endpoint URL from the <select> element
    this.api_url = this.input.getAttribute('data-url') as string;

    // Override any field names set as widget attributes
    this.valueField = this.input.getAttribute('ts-value-field') || this.settings.valueField;
    this.labelField = this.input.getAttribute('ts-label-field') || this.settings.labelField;
    this.disabledField =
      this.input.getAttribute('ts-disabled-field') || this.settings.disabledField;
    this.descriptionField = this.input.getAttribute('ts-description-field') || 'description';
    this.depthField = this.input.getAttribute('ts-depth-field') || '_depth';
    this.parentField = this.input.getAttribute('ts-parent-field') || null;
    this.countField = this.input.getAttribute('ts-count-field') || null;

    // Set the null option (if any)
    const nullOption = this.input.getAttribute('data-null-option');
    if (nullOption) {
      const valueField = this.settings.valueField;
      const labelField = this.settings.labelField;
      this.nullOption = {};
      this.nullOption[valueField] = 'null';
      this.nullOption[labelField] = nullOption;
    }

    // Populate static query parameters.
    this.getStaticParams();
    for (const [key, value] of this.staticParams.entries()) {
      this.queryParams.set(key, value);
    }

    // Populate dynamic query parameters
    this.getDynamicParams();
    for (const filter of this.dynamicParams.keys()) {
      this.updateQueryParams(filter);
    }

    // Path values
    this.getPathKeys();
    for (const filter of this.pathValues.keys()) {
      this.updatePathValues(filter);
    }

    // Add dependency event listeners.
    this.addEventListeners();
  }

  load(value: string, preserveValue?: string | string[]) {
    const self = this;

    // Record which request this is. Incremented unconditionally, before any early return
    // below, so that an already-in-flight request from a previous call is always correctly
    // invalidated by any newer call to load() -- even one that itself aborts early (e.g. no
    // valid URL). If another load() call starts before this one's response comes back,
    // `self.loadSequence` will have moved on and this response is stale -- it must be
    // discarded rather than applied.
    self.loadSequence += 1;
    const sequence = self.loadSequence;

    // Remember any value that still needs to be restored, without erasing a value captured
    // by an earlier, still-in-flight call. If this particular call has nothing new to
    // preserve (e.g. its dependency was already cleared by a cascaded change), an earlier
    // call's pending value should still get a chance to be restored by whichever request
    // ends up winning. An empty array (e.g. a multi-select cleared by clear()) doesn't count
    // as something worth preserving.
    const hasValue = Array.isArray(preserveValue)
      ? preserveValue.length > 0
      : preserveValue !== undefined;
    if (hasValue) {
      self.pendingRestoreValue = preserveValue;
    }

    // Automatically clear any cached options. (Only options included
    // in the API response should be present.)
    self.clearOptions();

    // Populate the null option (if any) if not searching
    if (self.nullOption && !value) {
      self.addOption(self.nullOption);
    }

    // Get the API request URL. If none is provided, abort as no request can be made. No
    // options can be shown for this field under its current (invalid) filter, so any
    // pending value carried from an earlier call is no longer relevant to restore here.
    const url = self.getRequestUrl(value);
    if (!url) {
      self.pendingRestoreValue = undefined;
      return;
    }

    addClasses(self.wrapper, self.settings.loadingClass);
    self.loading++;

    // Make the API request
    fetch(url)
      .then(response => response.json())
      .then(apiData => {
        const results: Dict[] = apiData.results;
        const options: Dict[] = [];
        for (const result of results) {
          const option = self.getOptionFromData(result);
          options.push(option);
        }
        return options;
      })
      // Pass the options to the callback function
      .then(options => {
        // A newer load() has since been issued (e.g. two dependencies changed in quick
        // succession). This response is stale; applying it now would risk clobbering
        // state already set by the newer, still-in-flight or already-resolved request.
        if (sequence !== self.loadSequence) {
          self.finalizeStaleLoad();
          return;
        }
        self.loadCallback(options, []);
        // Restore the previous selection if it is still valid under the new filter.
        if (self.pendingRestoreValue !== undefined) {
          const values = Array.isArray(self.pendingRestoreValue)
            ? self.pendingRestoreValue
            : [self.pendingRestoreValue];
          const validValues = values.filter(v => v !== '' && v in self.options);
          if (validValues.length > 0) {
            self.setValue(validValues.length === 1 ? validValues[0] : validValues, true);
          }
          self.pendingRestoreValue = undefined;
        }
      })
      .catch(() => {
        if (sequence !== self.loadSequence) {
          self.finalizeStaleLoad();
          return;
        }
        self.pendingRestoreValue = undefined;
        self.loadCallback([], []);
      });
  }

  /**
   * Custom methods
   */

  // Finalizes Tom Select's loading state after a superseded (stale) response settles: clears
  // the loading counter and, once it reaches zero, removes the wrapper's loading class and
  // refreshes the dropdown to drop any stale loading indicator rendered internally.
  private finalizeStaleLoad(): void {
    this.loading = Math.max(this.loading - 1, 0);
    if (!this.loading) {
      removeClasses(this.wrapper, this.settings.loadingClass);
      this.refreshOptions(false);
    }
  }

  // Formulate and return the complete URL for an API request, including any query parameters.
  getRequestUrl(search: string): string {
    let url = this.api_url;

    // Create new URL query parameters based on the current state of `queryParams` and create an
    // updated API query URL.
    const query = {} as Dict<Stringifiable[]>;
    for (const [key, value] of this.queryParams.entries()) {
      query[key] = value;
    }

    // Replace any variables in the URL with values from `pathValues` if set.
    for (const [key, value] of this.pathValues.entries()) {
      for (const result of this.api_url.matchAll(new RegExp(`({{${key}}})`, 'g'))) {
        if (value) {
          url = replaceAll(url, result[1], value.toString());
        } else {
          // No value is available to replace the token; abort.
          return '';
        }
      }
    }

    // Append the search query, if any
    if (search) {
      query['q'] = [search];
    }

    // Add standard parameters
    query['brief'] = [true];
    query['limit'] = [this.settings.maxOptions];

    return queryString.stringifyUrl({ url, query });
  }

  // Compile TomOption data from an API result
  getOptionFromData(data: Dict) {
    const option: Dict = {
      id: data[this.valueField],
      display: data[this.labelField],
      depth: data[this.depthField] || null,
      description: data[this.descriptionField] || null,
    };
    if (data[this.parentField]) {
      const parent: Dict = data[this.parentField] as Dict;
      option['parent'] = parent[this.labelField];
    }
    if (data[this.countField]) {
      option['count'] = data[this.countField];
    }
    if (data[this.disabledField]) {
      option['disabled'] = data[this.disabledField];
    }
    return option;
  }

  /**
   * Transitional methods
   */

  // Determine if this instance's options should be filtered by static values passed from the
  // server. Looks for the DOM attribute `data-static-params`, the value of which is a JSON
  // array of objects containing key/value pairs to add to `this.staticParams`.
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

  // Determine if this instances' options should be filtered by the value of another select
  // element. Looks for the DOM attribute `data-dynamic-params`, the value of which is a JSON
  // array of objects containing information about how to handle the related field.
  private getDynamicParams(): void {
    const serialized = this.input.getAttribute('data-dynamic-params');
    try {
      this.dynamicParams.addFromJson(serialized);
    } catch (err) {
      console.group(`Unable to determine dynamic query parameters for select field '${this.name}'`);
      console.warn(err);
      console.groupEnd();
    }
  }

  // Parse the `data-url` attribute to add any variables to `pathValues` as keys with empty
  // values. As those keys' corresponding form fields' values change, `pathValues` will be
  // updated to reflect the new value.
  private getPathKeys() {
    for (const result of this.api_url.matchAll(new RegExp(`{{(.+)}}`, 'g'))) {
      this.pathValues.set(result[1], '');
    }
  }

  // Update an element's API URL based on the value of another element on which this element
  // relies.
  private updateQueryParams(fieldName: string): void {
    // Find the element dependency.
    const element = document.querySelector<HTMLSelectElement>(`[name="${fieldName}"]`);
    if (element !== null) {
      // Initialize the element value as an array, in case there are multiple values.
      let elementValue = [] as Stringifiable[];

      if (element.multiple) {
        // If this is a multi-select (form filters, tags, etc.), use all selected options as the value.
        elementValue = Array.from(element.options)
          .filter(o => o.selected)
          .map(o => o.value);
      } else if (element.value !== '') {
        // If this is single-select (most fields), use the element's value. This seemingly
        // redundant/verbose check is mainly for performance, so we're not running the above three
        // functions (`Array.from()`, `Array.filter()`, `Array.map()`) every time every select
        // field's value changes.
        elementValue = [element.value];
      }

      if (elementValue.length > 0) {
        // If the field has a value, add it to the map.
        this.dynamicParams.updateValue(fieldName, elementValue);
        // Get the updated value.
        const current = this.dynamicParams.get(fieldName);

        if (typeof current !== 'undefined') {
          const { queryParam, queryValue } = current;
          let value = [] as Stringifiable[];

          if (this.staticParams.has(queryParam)) {
            // If the field is defined in `staticParams`, we should merge the dynamic value with
            // the static value.
            const staticValue = this.staticParams.get(queryParam);
            if (typeof staticValue !== 'undefined') {
              value = [...staticValue, ...queryValue];
            }
          } else {
            // If the field is _not_ defined in `staticParams`, we should replace the current value
            // with the new dynamic value.
            value = queryValue;
          }
          if (value.length > 0) {
            this.queryParams.set(queryParam, value);
          } else {
            this.queryParams.delete(queryParam);
          }
        }
      } else {
        // Otherwise, delete it (we don't want to send an empty query like `?site_id=`)
        const queryParam = this.dynamicParams.queryParam(fieldName);
        if (queryParam !== null) {
          this.queryParams.delete(queryParam);
        }
      }
    }
  }

  // Update `pathValues` based on the form value of another element.
  private updatePathValues(id: string): void {
    const key = replaceAll(id, /^id_/i, '');
    const element = getElement<HTMLSelectElement>(`id_${key}`);
    if (element !== null) {
      // If this element's URL contains variable tags ({{), replace the tag with the dependency's
      // value. For example, if the dependency is the `rack` field, and the `rack` field's value
      // is `1`, this element's URL would change from `/dcim/racks/{{rack}}/` to `/dcim/racks/1/`.
      const hasReplacement =
        this.api_url.includes(`{{`) &&
        Boolean(this.api_url.match(new RegExp(`({{(${id})}})`, 'g')));

      if (hasReplacement) {
        if (element.value) {
          // If the field has a value, add it to the map.
          this.pathValues.set(id, element.value);
        } else {
          // Otherwise, reset the value.
          this.pathValues.set(id, '');
        }
      }
    }
  }

  /**
   * Events
   */

  // Add event listeners to this element and its dependencies so that when dependencies change
  //this element's options are updated.
  private addEventListeners(): void {
    // Create a unique iterator of all possible form fields which, when changed, should cause this
    // element to update its API query.
    const dependencies = new Set([...this.dynamicParams.keys(), ...this.pathValues.keys()]);

    for (const dep of dependencies) {
      const filterElement = document.querySelector(`[name="${dep}"]`);
      if (filterElement !== null) {
        // Subscribe to dependency changes.
        filterElement.addEventListener('change', event => this.handleEvent(event));
      }
      // Subscribe to changes dispatched by this state manager.
      this.input.addEventListener(`netbox.select.onload.${dep}`, event => this.handleEvent(event));
    }
  }

  // Event handler to be dispatched any time a dependency's value changes. For example, when the
  // value of `tenant_group` changes, `handleEvent` is called to get the current value of
  // `tenant_group` and update the query parameters and API query URL for the `tenant` field.
  private handleEvent(event: Event): void {
    const target = event.target as HTMLSelectElement;

    // Save the current selection so we can restore it after loading if it remains valid.
    const previousValue = this.getValue();

    // Update the element's URL after any changes to a dependency.
    this.updateQueryParams(target.name);
    this.updatePathValues(target.name);

    // Clear any previous selection(s) as the parent filter has changed
    this.clear();

    // Load new data, restoring the previous selection if it is still valid under the new filter.
    const preserve = previousValue !== '' && previousValue !== null ? previousValue : undefined;
    this.load(this.lastValue, preserve);
  }
}
