import queryString from 'query-string';
import { readableColor } from 'color2k';
import SlimSelect from 'slim-select';
import { createToast } from '../bs';
import { hasUrl, hasExclusions } from './util';
import {
  isTruthy,
  hasError,
  getElement,
  getApiData,
  isApiError,
  getElements,
  findFirstAdjacent,
} from '../util';

import type { Option } from 'slim-select/dist/data';

type QueryFilter = Map<string, string | number | boolean>;

// Various one-off patterns to replace in query param keys.
const REPLACE_PATTERNS = [
  // Don't query `termination_a_device=1`, but rather `device=1`.
  [new RegExp(/termination_(a|b)_(.+)/g), '$2_id'],
  // A tenant's group relationship field is `group`, but the field name is `tenant_group`.
  [new RegExp(/tenant_(group)/g), '$1_id'],
  // Append `_id` to any fields
  [new RegExp(/^([A-Za-z0-9]+)(_id)?$/g), '$1_id'],
] as [RegExp, string][];

// Empty placeholder option.
const PLACEHOLDER = {
  value: '',
  text: '',
  placeholder: true,
} as Option;

// Attributes which if truthy should render the option disabled.
const DISABLED_ATTRIBUTES = ['occupied'] as string[];

/**
 * Manage a single API-backed select element's state. Each API select element is likely controlled
 * or dynamically updated by one or more other API select (or static select) elements' values.
 */
class APISelect {
  /**
   * Base `<select/>` DOM element.
   */
  private readonly base: HTMLSelectElement;

  /**
   * Form field name.
   */
  public readonly name: string;

  /**
   * Form field placeholder.
   */
  public readonly placeholder: string;

  /**
   * This element's options come from the server pre-sorted and should not be sorted client-side.
   * Determined by the existence of the `pre-sorted` attribute on the base `<select/>` element.
   */
  private readonly preSorted: boolean = false;

  /**
   * Event to be dispatched when dependent fields' values change.
   */
  private readonly loadEvent: InstanceType<typeof Event>;

  /**
   * SlimSelect instance for this element.
   */
  private readonly slim: InstanceType<typeof SlimSelect>;

  /**
   * API query parameters that should be applied to API queries for this field. This will be
   * updated as other dependent fields' values change. This is a mapping of:
   *
   *     Form Field Names → Form Field Values
   *
   * This is/might be different than the query parameters themselves, as the form field names may
   * be different than the object model key names. For example, `tenant_group` would be the field
   * name, but `group` would be the query parameter. Query parameters themselves are tracked in
   * `queryParams`.
   */
  private readonly filterParams: QueryFilter = new Map();

  /**
   * Post-parsed URL query parameters for API queries.
   */
  private readonly queryParams: QueryFilter = new Map();

  /**
   * Mapping of URL template key/value pairs. If this element's URL contains Django template tags
   * (e.g., `{{key}}`), `key` will be added to `pathValue` and the `id_key` form element will be
   * tracked for changes. When the `id_key` element's value changes, the new value will be added
   * to this map. For example, if the template key is `rack`, and the `id_rack` field's value is
   * `1`, `pathValues` would be updated to reflect a `"rack" => 1` mapping. When the query URL is
   * updated, the URL would change from `/dcim/racks/{{rack}}/` to `/dcim/racks/1/`.
   */
  private readonly pathValues: QueryFilter = new Map();

  /**
   * Original API query URL passed via the `data-href` attribute from the server. This is kept so
   * that the URL can be reconstructed as form values change.
   */
  private readonly url: string = '';

  /**
   * API query URL. This will be updated dynamically to include any query parameters in `queryParameters`.
   */
  private queryUrl: string = '';

  /**
   * This instance's available options.
   */
  private _options: Option[] = [PLACEHOLDER];

  /**
   * Array of options values which should be considered disabled or static.
   */
  private disabledOptions: Array<string> = [];

  constructor(base: HTMLSelectElement) {
    // Initialize readonly properties.
    this.base = base;
    this.name = base.name;

    if (base.getAttribute('pre-sorted') !== null) {
      this.preSorted = true;
    }

    if (hasUrl(base)) {
      const url = base.getAttribute('data-url') as string;
      this.url = url;
      this.queryUrl = url;
    }

    this.loadEvent = new Event(`netbox.select.onload.${base.name}`);
    this.placeholder = this.getPlaceholder();
    this.disabledOptions = this.getDisabledOptions();

    this.slim = new SlimSelect({
      select: this.base,
      allowDeselect: true,
      deselectLabel: `<i class="mdi mdi-close-circle" style="color:currentColor;"></i>`,
      placeholder: this.placeholder,
      onChange: () => this.handleSlimChange(),
    });

    // Initialize API query properties.
    this.getFilteredBy();
    this.getPathKeys();

    for (const filter of this.filterParams.keys()) {
      this.updateQueryParams(filter);
    }

    for (const filter of this.pathValues.keys()) {
      this.updatePathValues(filter);
    }

    this.queryParams.set('brief', true);
    this.queryParams.set('limit', 0);
    this.updateQueryUrl();

    // Initialize element styling.
    this.resetClasses();
    this.setSlimStyles();

    // Initialize controlling elements.
    this.initResetButton();

    // Add dependency event listeners.
    this.addEventListeners();

    // Determine if this element is part of collapsible element.
    const collapse = this.base.closest('.content-container .collapse');
    if (collapse !== null) {
      // If this element is part of a collapsible element, only load the data when the
      // collapsible element is shown.
      // See: https://getbootstrap.com/docs/5.0/components/collapse/#events
      collapse.addEventListener('show.bs.collapse', () => this.loadData());
      collapse.addEventListener('hide.bs.collapse', () => this.resetOptions());
    } else {
      // Otherwise, load the data on render.
      Promise.all([this.loadData()]);
    }
  }

  /**
   * This instance's available options.
   */
  public get options(): Option[] {
    return this._options;
  }

  /**
   * Sort incoming options by label and apply the new options to both the SlimSelect instance and
   * this manager's state. If the `preSorted` attribute exists on the base `<select/>` element,
   * the options will *not* be sorted.
   */
  private set options(optionsIn: Option[]) {
    let newOptions = optionsIn;
    if (!this.preSorted) {
      newOptions = optionsIn.sort((a, b) => (a.text.toLowerCase() > b.text.toLowerCase() ? 1 : -1));
    }

    this._options = newOptions;
    this.slim.setData(newOptions);
  }

  /**
   * Remove all options and reset back to the generic placeholder.
   */
  private resetOptions(): void {
    this.options = [PLACEHOLDER];
  }

  /**
   * Add or remove a class to the SlimSelect element to match Bootstrap .form-select:disabled styles.
   */
  public disable(): void {
    if (this.slim.slim.singleSelected !== null) {
      if (!this.slim.slim.singleSelected.container.hasAttribute('disabled')) {
        this.slim.slim.singleSelected.container.setAttribute('disabled', '');
      }
    } else if (this.slim.slim.multiSelected !== null) {
      if (!this.slim.slim.multiSelected.container.hasAttribute('disabled')) {
        this.slim.slim.multiSelected.container.setAttribute('disabled', '');
      }
    }
  }

  /**
   * Add or remove a class to the SlimSelect element to match Bootstrap .form-select:disabled styles.
   */
  public enable(): void {
    if (this.slim.slim.singleSelected !== null) {
      if (this.slim.slim.singleSelected.container.hasAttribute('disabled')) {
        this.slim.slim.singleSelected.container.removeAttribute('disabled');
      }
    } else if (this.slim.slim.multiSelected !== null) {
      if (this.slim.slim.multiSelected.container.hasAttribute('disabled')) {
        this.slim.slim.multiSelected.container.removeAttribute('disabled');
      }
    }
  }

  /**
   * Add event listeners to this element and its dependencies so that when dependencies change
   * this element's options are updated.
   */
  private addEventListeners(): void {
    // Create a unique iterator of all possible form fields which, when changed, should cause this
    // element to update its API query.
    const dependencies = new Set([...this.filterParams.keys(), ...this.pathValues.keys()]);

    for (const dep of dependencies) {
      const filterElement = document.querySelector(`[name="${dep}"]`);
      if (filterElement !== null) {
        // Subscribe to dependency changes.
        filterElement.addEventListener('change', event => this.handleEvent(event));
      }
      // Subscribe to changes dispatched by this state manager.
      this.base.addEventListener(`netbox.select.onload.${dep}`, event => this.handleEvent(event));
    }
  }

  /**
   * Load this element's options from the NetBox API.
   */
  private async loadData(): Promise<void> {
    try {
      this.disable();
      await this.getOptions();
    } catch (err) {
      console.error(err);
    } finally {
      this.setOptionStyles();
      this.enable();
      this.base.dispatchEvent(this.loadEvent);
    }
  }

  /**
   * Query the NetBox API for this element's options.
   */
  private async getOptions(): Promise<void> {
    if (this.queryUrl.includes(`{{`)) {
      this.options = [PLACEHOLDER];
      return;
    }

    // Get all non-placeholder (empty) options' values. If any exist, it means we're editing an
    // existing object. When we fetch options from the API later, we can set any of the options
    // contained in this array to `selected`.
    const selectOptions = Array.from(this.base.options)
      .filter(option => option.selected)
      .map(option => option.getAttribute('value'))
      .filter(isTruthy);

    const data = await getApiData(this.queryUrl);

    if (hasError(data)) {
      if (isApiError(data)) {
        return this.handleError(data.exception, data.error);
      }
      return this.handleError(`Error Fetching Options for field '${this.name}'`, data.error);
    }

    const { results } = data;
    const options = [PLACEHOLDER] as Option[];

    for (const result of results) {
      const text = result.display;
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
      if (selectOptions.some(option => this.disabledOptions.includes(option))) {
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
    this.options = options;
  }

  /**
   * Event handler to be dispatched any time a dependency's value changes. For example, when the
   * value of `tenant_group` changes, `handleEvent` is called to get the current value of
   * `tenant_group` and update the query parameters and API query URL for the `tenant` field.
   */
  private handleEvent(event: Event): void {
    const target = event.target as HTMLSelectElement;
    // Update the element's URL after any changes to a dependency.
    this.updateQueryParams(target.name);
    this.updatePathValues(target.name);
    this.updateQueryUrl();
    // Load new data.
    Promise.all([this.loadData()]);
  }

  /**
   * When the API returns an error, show it to the user and reset this element's available options.
   *
   * @param title Error title
   * @param message Error message
   */
  private handleError(title: string, message: string): void {
    createToast('danger', title, message).show();
    this.resetOptions();
  }

  /**
   * `change` event callback to be called any time the value of a SlimSelect instance is changed.
   */
  private handleSlimChange(): void {
    const element = this.slim.slim;
    if (element) {
      // Toggle form validation classes when form values change. For example, if the field was
      // invalid and the value has now changed, remove the `.is-invalid` class.
      if (
        element.container.classList.contains('is-invalid') ||
        this.base.classList.contains('is-invalid')
      ) {
        element.container.classList.remove('is-invalid');
        this.base.classList.remove('is-invalid');
      }
    }
    this.base.dispatchEvent(this.loadEvent);
  }

  /**
   * Update the API query URL and underlying DOM element's `data-url` attribute.
   */
  private updateQueryUrl(): void {
    // Create new URL query parameters based on the current state of `queryParams` and create an
    // updated API query URL.
    const query = {} as Dict<string | number | boolean>;
    for (const [key, value] of this.queryParams.entries()) {
      query[key] = value;
    }

    let url = this.url;

    // Replace any Django template variables in the URL with values from `pathValues` if set.
    for (const [key, value] of this.pathValues.entries()) {
      for (const result of this.url.matchAll(new RegExp(`({{${key}}})`, 'g'))) {
        if (isTruthy(value)) {
          url = url.replaceAll(result[1], value.toString());
        }
      }
    }
    const newUrl = queryString.stringifyUrl({ url, query });
    if (this.queryUrl !== newUrl) {
      // Only update the URL if it has changed.
      this.queryUrl = newUrl;
      this.base.setAttribute('data-url', newUrl);
    }
  }

  /**
   * Update an element's API URL based on the value of another element on which this element
   * relies.
   *
   * @param id DOM ID of the other element.
   */
  private updateQueryParams(id: string): void {
    let key = id.replaceAll(/^id_/gi, '');
    // Find the element dependency.
    const element = getElement<HTMLSelectElement>(`id_${key}`);
    if (element !== null) {
      // If the dependency has a value, parse the dependency's name (form key) for any
      // required replacements.
      for (const [pattern, replacement] of REPLACE_PATTERNS) {
        if (key.match(pattern)) {
          key = key.replaceAll(pattern, replacement);
          break;
        }
      }

      if (isTruthy(element.value)) {
        // If the field has a value, add it to the map.
        if (this.filterParams.has(id)) {
          // If this element is tracking the neighbor element, add its value to the map.
          this.queryParams.set(key, element.value);
        }
      } else {
        // Otherwise, delete it (we don't want to send an empty query like `?site_id=`)
        this.queryParams.delete(key);
      }
    }
  }

  /**
   * Update `pathValues` based on the form value of another element.
   *
   * @param id DOM ID of the other element.
   */
  private updatePathValues(id: string): void {
    let key = id.replaceAll(/^id_/gi, '');
    const element = getElement<HTMLSelectElement>(`id_${key}`);
    if (element !== null) {
      // If this element's URL contains Django template tags ({{), replace the template tag
      // with the the dependency's value. For example, if the dependency is the `rack` field,
      // and the `rack` field's value is `1`, this element's URL would change from
      // `/dcim/racks/{{rack}}/` to `/dcim/racks/1/`.
      const hasReplacement =
        this.url.includes(`{{`) && Boolean(this.url.match(new RegExp(`({{(${id})}})`, 'g')));

      if (hasReplacement) {
        if (isTruthy(element.value)) {
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
   * Find the select element's placeholder text/label.
   */
  private getPlaceholder(): string {
    let placeholder = this.name;
    if (this.base.id) {
      const label = document.querySelector(`label[for=${this.base.id}]`) as HTMLLabelElement;
      // Set the placeholder text to the label value, if it exists.
      if (label !== null) {
        placeholder = `Select ${label.innerText.trim()}`;
      }
    }
    return placeholder;
  }

  /**
   * Get this element's disabled options by value. The `data-query-param-exclude` attribute will
   * contain a stringified JSON array of option values.
   */
  private getDisabledOptions(): string[] {
    let disabledOptions = [] as string[];
    if (hasExclusions(this.base)) {
      try {
        const exclusions = JSON.parse(
          this.base.getAttribute('data-query-param-exclude') ?? '[]',
        ) as string[];
        disabledOptions = [...disabledOptions, ...exclusions];
      } catch (err) {
        console.group(
          `Unable to parse data-query-param-exclude value on select element '${this.name}'`,
        );
        console.warn(err);
        console.groupEnd();
      }
    }
    return disabledOptions;
  }

  /**
   * Parse the `data-url` attribute to add any Django template variables to `pathValues` as keys
   * with empty values. As those keys' corresponding form fields' values change, `pathValues` will
   * be updated to reflect the new value.
   */
  private getPathKeys() {
    for (const result of this.url.matchAll(new RegExp(`{{(.+)}}`, 'g'))) {
      this.pathValues.set(result[1], '');
    }
  }

  /**
   * Determine if a select element should be filtered by the value of another select element.
   *
   * Looks for the DOM attribute `data-query-param-<name of other field>`, which would look like:
   * `["$<name>"]`
   *
   * If the attribute exists, parse out the raw value. In the above example, this would be `name`.
   */
  private getFilteredBy(): void {
    const pattern = new RegExp(/\[|\]|"|\$/g);
    const keyPattern = new RegExp(/data-query-param-/g);

    // Extract data attributes.
    const keys = Object.values(this.base.attributes)
      .map(v => v.name)
      .filter(v => v.includes('data'));

    for (const key of keys) {
      if (key.match(keyPattern) && key !== 'data-query-param-exclude') {
        const value = this.base.getAttribute(key);
        if (value !== null) {
          try {
            const parsed = JSON.parse(value) as string | string[];
            if (Array.isArray(parsed)) {
              for (const item of parsed) {
                if (item.match(/^\$.+$/g)) {
                  const replaced = item.replaceAll(pattern, '');
                  this.filterParams.set(replaced, '');
                } else {
                  this.filterParams.set(key.replaceAll(keyPattern, ''), item);
                }
              }
            } else {
              if (parsed.match(/^\$.+$/g)) {
                const replaced = parsed.replaceAll(pattern, '');
                this.filterParams.set(replaced, '');
              } else {
                this.filterParams.set(key.replaceAll(keyPattern, ''), parsed);
              }
            }
          } catch (err) {
            console.warn(err);
            if (value.match(/^\$.+$/g)) {
              const replaced = value.replaceAll(pattern, '');
              this.filterParams.set(replaced, '');
            } else {
              this.filterParams.set(key.replaceAll(keyPattern, ''), value);
            }
          }
        }
      }
    }
  }

  /**
   * Set the underlying select element to the same size as the SlimSelect instance. This is
   * primarily for built-in HTML form validation (which doesn't really work) but it also makes
   * things feel cleaner in the DOM.
   */
  private setSlimStyles(): void {
    const { width, height } = this.slim.slim.container.getBoundingClientRect();
    this.base.style.opacity = '0';
    this.base.style.width = `${width}px`;
    this.base.style.height = `${height}px`;
    this.base.style.display = 'block';
    this.base.style.position = 'absolute';
    this.base.style.pointerEvents = 'none';
  }

  /**
   * Add scoped style elements specific to each SlimSelect option, if the color property exists.
   * As of this writing, this attribute only exist on Tags. The color property is used as the
   * background color, and a foreground color is detected based on the luminosity of the background
   * color.
   */
  private setOptionStyles(): void {
    for (const option of this.options) {
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
   * Remove base element classes from SlimSelect instance.
   */
  private resetClasses(): void {
    const element = this.slim.slim;
    if (element) {
      for (const className of this.base.classList) {
        element.container.classList.remove(className);
      }
    }
  }

  /**
   * Initialize any adjacent reset buttons so that when clicked, the instance's selected value is cleared.
   */
  private initResetButton(): void {
    const resetButton = findFirstAdjacent<HTMLButtonElement>(this.base, 'button[data-reset-select');
    if (resetButton !== null) {
      resetButton.addEventListener('click', () => {
        this.base.value = '';
        if (this.base.multiple) {
          this.slim.setSelected([]);
        } else {
          this.slim.setSelected('');
        }
      });
    }
  }
}

export function initApiSelect() {
  for (const select of getElements<HTMLSelectElement>('.netbox-api-select')) {
    new APISelect(select);
  }
}
